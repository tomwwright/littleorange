from . import util
import ipaddress
import math

AVAILABILITY_ZONE_LABELS = ["A", "B", "C", "D", "E", "F"]


def allocateSubnets(subnet, divisions):
  """
  Allocates subnets from a given subnet by a list of tuples that form labelled subnet prefixes to allocate
  e.g. [("Name", 25), ("NameA", 24), ("NameB", 25)]
  """

  sortedByPrefixLength = sorted(divisions, key=lambda d: d[1])

  availableSubnets = [subnet]
  allocatedSubnets = []

  for name, prefixLength in sortedByPrefixLength:
    if prefixLength > availableSubnets[-1].prefixlen:
      toSubnets = availableSubnets.pop()
      availableSubnets += sorted(toSubnets.subnets(new_prefix=prefixLength), reverse=True)

    while prefixLength < availableSubnets[-1].prefixlen:
      availableSubnets.pop()

    subnet = availableSubnets.pop()
    allocatedSubnets.append((name, subnet))

  return allocatedSubnets


def calculateSubnetMaskPrefixIncrease(subnets):
  """
  Calculates the extra bits that need to be added to subnet mask to accommodate the given number of subnets
  """
  return int(math.ceil(math.log(subnets, 2)))


class VPC(object):

  def __init__(self, **kwargs):
    self.cidr = ipaddress.IPv4Network(kwargs["CIDR"])
    self.name = kwargs["Name"]
    self.availabilityZoneCount = kwargs["AvailabilityZoneCount"]
    self.internetGatewayRouteCIDR = kwargs.get("InternetGatewayRouteCIDR", None)
    self.useInternetGateway = kwargs.get("InternetGateway", None)
    self.useNatGateways = kwargs.get("NATGateways", None)
    self.tierSettings = kwargs.get("Tiers", [])
    self.transitGatewayId = kwargs.get("TransitGatewayId", None)
    self.transitGatewayRouteCIDR = kwargs.get("TransitGatewayRouteCIDR", None)

    self.tiers = []
    self.subnets = []
    self.calculateTiers()
    self.calculateNACLs()
    self.calculateRoutes()

  def calculateNACLs(self):
    publicTier = [tier for tier in self.tiers if tier["Name"] == "Public"][0]
    privateTier = [tier for tier in self.tiers if tier["Name"] == "Private"][0]
    restrictedTier = [tier for tier in self.tiers if tier["Name"] == "Restricted"][0]
    networkingTier = [tier for tier in self.tiers if tier["Name"] == "Networking"][0]

    publicTier["NACLs"] = [
        (100, "ALLOW", "ALL", 0, 0, "0.0.0.0/0")
    ]

    privateTier["NACLs"] = [
        (100, "ALLOW", "TCP", 1024, 65535, "0.0.0.0/0"),
        (200, "ALLOW", "UDP", 1024, 65535, "0.0.0.0/0"),
        (300, "ALLOW", "ALL", 0, 0, str(self.cidr))
    ]

    restrictedTier["NACLs"] = [
        (100, "ALLOW", "ALL", 0, 0, str(privateTier["CIDR"]))
    ]

    networkingTier["NACLs"] = [
        (100, "ALLOW", "ALL", 0, 0, str(self.cidr))
    ]

  def calculateRoutes(self):
    publicTier = [tier for tier in self.tiers if tier["Name"] == "Public"][0]
    privateTier = [tier for tier in self.tiers if tier["Name"] == "Private"][0]
    restrictedTier = [tier for tier in self.tiers if tier["Name"] == "Restricted"][0]

    for subnet in publicTier["Subnets"]:
      if self.useInternetGateway:
        internetGatewayResourceName = self.name + "IGW"
        subnet["Routes"].append(("IGW", self.internetGatewayRouteCIDR, {"GatewayId": {"Ref": f"{self.name}IGW"}}))
      if self.transitGatewayId:
        subnet["Routes"].append(("TGW", self.transitGatewayRouteCIDR, {"TransitGatewayId": self.transitGatewayId}))

    for subnet in privateTier["Subnets"]:
      if self.useInternetGateway and self.useNatGateways:
        natGatewayResourceName = "{}NAT{}".format(self.name, subnet["Name"])
        subnet["Routes"].append(("NAT", self.internetGatewayRouteCIDR, {"NatGatewayId": {"Ref": natGatewayResourceName}}))
      if self.transitGatewayId:
        subnet["Routes"].append(("TGW", self.transitGatewayRouteCIDR, {"TransitGatewayId": self.transitGatewayId}))

  def calculateTiers(self):

    tiers = self.tierSettings
    if not tiers:
      tiers = [
          {
              "Name": "Public",
              "Size": 0.25
          },
          {
              "Name": "Private",
              "Size": 0.25
          },
          {
              "Name": "Restricted",
              "Size": 0.25
          },
          {
              "Name": "Networking",
              "Size": 0.25
          }
      ]

    # check all tiers are present
    presentTiers = [tier["Name"] for tier in tiers]
    if set(presentTiers) != set(["Public", "Private", "Restricted", "Networking"]):
      raise ValueError("If Tiers defined, must contain settings for all tiers: [Public, Private, Restricted, Networking]")

    # validate and complete tier settings
    total = 0
    for tier in tiers:
      if "Size" in tier and "PrefixLength" in tier:
        raise ValueError("Only one of Size and PrefixLength can be set for tier settings!")

      if "Size" in tier:
        if tier["Size"] not in (0.5, 0.25, 0.125, 0.0625, 0.03125):
          raise ValueError("Size must be defined as member of (0.5, 0.25, 0.125, 0.0625, 0.03125)")
        tier["PrefixLength"] = int(self.cidr.prefixlen - math.log(tier["Size"], 2))
      elif "PrefixLength" in tier:
        if type(tier["PrefixLength"]) != int:
          raise ValueError("PrefixLength must be defined as integer")
        tier["Size"] = 1 / math.pow(2, tier["PrefixLength"] - self.cidr.prefixlen)
      else:
        raise ValueError("Tier settings must contain Size or PrefixLength")

      total += tier["Size"]

    if total > 1.0:
      raise ValueError("Tier sizes combined > 1")

    subnetAllocations = allocateSubnets(self.cidr, [
        (tier["Name"], tier["PrefixLength"]) for tier in tiers
    ])

    for tier in tiers:
      subnet = util.find(subnetAllocations, lambda alloc: alloc[0] == tier["Name"])[1]

      tier["CIDR"] = subnet
      tier["ResourceName"] = self.name + tier["Name"]
      tier["Subnets"] = []

      self.tiers.append(tier)

      self.calculateTierSubnets(tier)

  def calculateTierSubnets(self, tier):
    subnetPrefix = tier["CIDR"].prefixlen
    subnetPrefixIncreaseForAZs = calculateSubnetMaskPrefixIncrease(self.availabilityZoneCount)
    subnets = list(tier["CIDR"].subnets(prefixlen_diff=subnetPrefixIncreaseForAZs))

    for i in range(self.availabilityZoneCount):
      label = AVAILABILITY_ZONE_LABELS[i]
      subnet = {
          "AvailabilityZoneIndex": i,
          "CIDR": subnets[i],
          "Name": label,
          "ResourceName": tier["ResourceName"] + label,
          "Routes": [],
          "Tier": tier,
      }

      tier["Subnets"].append(subnet)
      self.subnets.append(subnet)
