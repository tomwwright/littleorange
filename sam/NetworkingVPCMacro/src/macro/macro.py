import ipaddress
import re
from typing import Dict

from . import util
from .vpc import VPC

REGEX_IPV4 = re.compile(
    r'^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))?$')


def isValidIPv4CIDR(cidr):
  """
  Returns if passed CIDR matches regex for an IPv4 CIDR, e.g. 192.168.1.0/24
  """
  return REGEX_IPV4.match(cidr)


def buildNACLEntry(naclResourceName, nacl):
  (ingressOrEgress, ruleId, action, protocol,
   fromPortOrIcmpCode, toPortOrIcmpType, cidr) = nacl
  isEgress = ingressOrEgress == "EGRESS"

  resourceName = f"{naclResourceName}Egress{ruleId}" if isEgress else f"{naclResourceName}Ingress{ruleId}"

  protocols = {
      "ICMP": 1,
      "TCP": 6,
      "UDP": 17
  }

  resource = {
      "Type": "AWS::EC2::NetworkAclEntry",
      "Properties": {
          "NetworkAclId": {"Ref": naclResourceName},
          "CidrBlock": cidr,
          "Egress": isEgress,
          "Protocol": protocols.get(protocol, -1),
          "RuleAction": action.lower(),
          "RuleNumber": ruleId
      }
  }
  if protocol in ["TCP", "UDP"]:
    resource["Properties"]["PortRange"] = {
        "To": toPortOrIcmpType,
        "From": fromPortOrIcmpCode
    }
  elif protocol == "ICMP":
    resource["Properties"]["Icmp"] = {
        "Code": fromPortOrIcmpCode,
        "Type": toPortOrIcmpType
    }

  return resourceName, resource


class NetworkingVPCMacro(object):
  """
  Transforms LittleOrange::Networking::VPC Resources into native CloudFormation Resources. Expects to operate on the full template.
  """

  template: Dict[str, Dict] = {}
  parameters: Dict[str, Dict] = {}

  availabilityZoneLabels = ["A", "B", "C", "D", "E", "F"]

  def buildRoute53ResolverRuleAssociations(self, vpcName, resolverRuleIds):
    for ruleId in resolverRuleIds:
      resolverRuleAssociationResourceName = "{}ResolverRule{}".format(
          vpcName, ruleId.replace("rslvr-rr-", ""))
      self.template["Resources"][resolverRuleAssociationResourceName] = {
          "Type": "AWS::Route53Resolver::ResolverRuleAssociation",
          "Properties": {
              "ResolverRuleId": ruleId,
              "VPCId": {"Ref": vpcName}
          }
      }

  def buildInternetGateway(self, vpcName):
    self.template["Resources"][f"{vpcName}IGW"] = {
        "Type": "AWS::EC2::InternetGateway",
        "Properties": {
            "Tags": [
                {
                    "Key": "Name",
                    "Value": f"{vpcName}IGW"
                }
            ]
        }
    }

    self.template["Resources"][f"{vpcName}IGWAttachment"] = {
        "Type": "AWS::EC2::VPCGatewayAttachment",
        "Properties": {
            "InternetGatewayId": {"Ref": f"{vpcName}IGW"},
            "VpcId": {"Ref": vpcName},
        }
    }

  def buildNATGateways(self, vpcName, availabilityZoneCount):
    for i in range(availabilityZoneCount):
      label = self.availabilityZoneLabels[i]
      publicSubnetResourceName = "{}Public{}".format(vpcName, label)
      natGatewayResourceName = "{}NAT{}".format(vpcName, label)
      natGatewayIPResourceName = "{}NATIP{}".format(vpcName, label)

      self.template["Resources"][natGatewayIPResourceName] = {
          "Type": "AWS::EC2::EIP",
          "Properties": {
              "Domain": "vpc",
              "Tags": [
                  {
                      "Key": "Name",
                      "Value": natGatewayIPResourceName
                  }
              ]
          }
      }

      self.template["Resources"][natGatewayResourceName] = {
          "Type": "AWS::EC2::NatGateway",
          "Properties": {
              "AllocationId": {"Fn::GetAtt": f"{natGatewayIPResourceName}.AllocationId"},
              "SubnetId": {"Ref": publicSubnetResourceName},
              "Tags": [
                  {
                      "Key": "Name",
                      "Value": natGatewayResourceName
                  }
              ]
          }
      }

  def buildSubnets(self, vpc):
    for subnet in vpc.subnets:
      self.template["Resources"][subnet["ResourceName"]] = {
          "Type": "AWS::EC2::Subnet",
          "Properties": {
              "AvailabilityZone": {"Fn::Select": [str(subnet["AvailabilityZoneIndex"]), {"Fn::GetAZs": ""}]},
              "CidrBlock": str(subnet["CIDR"]),
              "VpcId": {"Ref": vpc.name},
              "Tags": [
                  {
                      "Key": "Name",
                      "Value": subnet["ResourceName"]
                  }
              ]
          }
      }

      self.template["Resources"][subnet["ResourceName"] + "NACLAssoc"] = {
          "Type": "AWS::EC2::SubnetNetworkAclAssociation",
          "Properties": {
              "NetworkAclId": {"Ref": subnet["Tier"]["ResourceName"] + "NACL"},
              "SubnetId": {"Ref": subnet["ResourceName"]}
          }
      }

      self.template["Resources"][subnet["ResourceName"] + "RouteTable"] = {
          "Type": "AWS::EC2::RouteTable",
          "Properties": {
              "VpcId": {"Ref": vpc.name},
              "Tags": [
                  {
                      "Key": "Name",
                      "Value": subnet["ResourceName"]
                  }
              ]
          }
      }

      self.template["Resources"][subnet["ResourceName"] + "RouteTableAssoc"] = {
          "Type": "AWS::EC2::SubnetRouteTableAssociation",
          "Properties": {
              "RouteTableId": {"Ref": subnet["ResourceName"] + "RouteTable"},
              "SubnetId": {"Ref": subnet["ResourceName"]}
          }
      }

      for route in subnet["Routes"]:
        (name, cidr, parameters) = route
        routeResourceName = "{}Route{}".format(
            subnet["ResourceName"], name)
        self.template["Resources"][routeResourceName] = {
            "Type": "AWS::EC2::Route",
            "Properties": {
                "DestinationCidrBlock": cidr,
                "RouteTableId": {"Ref": subnet["ResourceName"] + "RouteTable"},
                **parameters
            }
        }

  def buildTiers(self, vpc):
    for tier in vpc.tiers:
      name = tier["Name"]
      self.template["Outputs"][f"{tier['ResourceName']}TierCIDR"] = {
          "Description": f"IPv4 CIDR of the {tier['Name']} Tier of {vpc.name}",
          "Value": str(tier["CIDR"])
      }

      self.template["Outputs"][f"{tier['ResourceName']}SubnetIds"] = {
          "Description": f"Subnet IDs of the {tier['Name']} Tier of {vpc.name}",
          "Value": {
              "Fn::Join": [
                  ",",
                  [
                      {"Ref": f"{subnet['ResourceName']}"} for subnet in tier["Subnets"]
                  ]
              ]
          }
      }

      naclResourceName = f"{tier['ResourceName']}NACL"
      self.template["Resources"][naclResourceName] = {
          "Type": "AWS::EC2::NetworkAcl",
          "Properties": {
              "VpcId": {"Ref": vpc.name},
              "Tags": [
                  {
                      "Key": "Name",
                      "Value": tier['ResourceName']
                  }
              ]
          }
      }
      self.template["Outputs"][f"{tier['ResourceName']}NACLId"] = {
          "Description": f"NACL ID of the {tier['Name']} Tier of {vpc.name}",
          "Value": {"Ref": naclResourceName}
      }

      for nacl in tier["NACLs"]:
        (naclEntryResourceName, naclEntryResource) = buildNACLEntry(
            naclResourceName, nacl)
        self.template["Resources"][naclEntryResourceName] = naclEntryResource

  def buildTransitGatewayAttachment(self, vpcName, availabilityZoneCount, transitGatewayId):

    networkingSubnetIds = [
        {"Ref": "{}Networking{}".format(
            vpcName, self.availabilityZoneLabels[i])}
        for i in range(availabilityZoneCount)
    ]
    transitGatewayAttachmentResourceName = "{}TGWAttachment".format(
        vpcName)

    self.template["Resources"][transitGatewayAttachmentResourceName] = {
        "Type": "AWS::EC2::TransitGatewayAttachment",
        "Properties": {
            "SubnetIds": networkingSubnetIds,
            "TransitGatewayId": transitGatewayId,
            "VpcId": {"Ref": vpcName}
        }
    }

  def buildVPC(self, name, resource):
    cidr = self.parameters.resolve(resource["Properties"]["CIDR"])
    if not isValidIPv4CIDR(cidr):
      raise Exception(f"Invalid IPv4 VPC CIDR: {cidr}")

    availabilityZones = self.parameters.resolve(
        resource["Properties"]["AvailabilityZones"])
    useInternetGateway = self.parameters.resolve(
        resource["Properties"].get("InternetGateway", True))
    useNATGateways = self.parameters.resolve(
        resource["Properties"].get("NATGateways", False))
    internetGatewayRouteCIDR = self.parameters.resolve(
        resource["Properties"].get("InternetGatewayRouteCIDR", "0.0.0.0/0"))
    transitGatewayId = self.parameters.resolve(
        resource["Properties"].get("TransitGatewayId", None))
    transitGatewayRouteCIDR = self.parameters.resolve(
        resource["Properties"].get("TransitGatewayRouteCIDR", "0.0.0.0/0"))
    tiers = self.parameters.resolve(
        resource["Properties"].get("Tiers", None))
    resolverRuleIds = self.parameters.resolve(
        resource["Properties"].get("ResolverRuleIds", []))

    if useInternetGateway and transitGatewayId and transitGatewayRouteCIDR == internetGatewayRouteCIDR:
      raise Exception(
          f"Conflicting route CIDRs for internet and transit gateway: {internetGatewayRouteCIDR}")

    vpc = VPC(
        CIDR=cidr,
        Name=name,
        AvailabilityZoneCount=availabilityZones,
        InternetGateway=useInternetGateway,
        InternetGatewayRouteCIDR=internetGatewayRouteCIDR,
        NATGateways=useNATGateways,
        TransitGatewayId=transitGatewayId,
        TransitGatewayRouteCIDR=transitGatewayRouteCIDR,
        Tiers=tiers
    )

    self.template["Resources"][name] = {
        "Type": "AWS::EC2::VPC",
        "Properties": {
            "CidrBlock": cidr,
            "EnableDnsHostnames": True,
            "EnableDnsSupport": True,
            "InstanceTenancy": "default",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": name
                }
            ]
        }
    }

    self.template["Outputs"][name + "Id"] = {
        "Description": f"VPC ID of {vpc.name}",
        "Value": {"Ref": name}
    }

    if useInternetGateway:
      self.buildInternetGateway(name)

    self.buildTiers(vpc)
    self.buildSubnets(vpc)

    if useNATGateways:
      self.buildNATGateways(name, availabilityZones)

    if transitGatewayId:
      self.buildTransitGatewayAttachment(
          name, availabilityZones, transitGatewayId)

    self.buildRoute53ResolverRuleAssociations(name, resolverRuleIds)

  def transformVPCResource(self, name):
    resources = self.template.get("Resources", {})
    resource = resources[name]
    del resources[name]

    self.buildVPC(name, resource)

  def transformVpcAttributeLookups(self, name):
    resources = self.template.get("Resources", {})
    resource = resources[name]
    self.enumerateAndTransformProperties(resource, "Properties")

  def enumerateAndTransformProperties(self, properties, key):
    if isinstance(properties[key], list):
      for index, _ in enumerate(properties[key]):
        self.enumerateAndTransformProperties(properties[key], index)
    elif isinstance(properties[key], dict):
      attributeLookupOrFalse = self.isVpcAttributeLookup(properties[key])
      if attributeLookupOrFalse != False:
        self.transformVpcAttributeLookupProperty(properties, key)
      else:
        for innerKey in properties[key].keys():
          self.enumerateAndTransformProperties(
              properties[key], innerKey)

  def transformVpcAttributeLookupProperty(self, properties, key):
    (resource, attribute) = util.unpackGetAtt(properties[key]["Fn::GetAtt"])

    if attribute in ["CidrBlock", "CidrBlockAssociations", "DefaultNetworkAcl", "DefaultSecurityGroup", "Ipv6CidrBlocks"]:
      return  # leave unchanged as to resolve attributes of AWS::EC2::VPC resource type

    tiers = "(Public|Private|Restricted|Networking)"
    azs = "(A|B|C|D|E|F)"

    mapping = {
        re.compile(f"{tiers}NACLId"): lambda match: {"Ref": f"{resource}{match.group(1)}NACL"},
        re.compile(f"{tiers}Subnet{azs}Id"): lambda match: {"Ref": f"{resource}{match.group(1)}{match.group(2)}"},
        re.compile(f"{tiers}Subnet{azs}RouteTableId"): lambda match: {"Ref": f"{resource}{match.group(1)}{match.group(2)}RouteTable"}
    }

    for pattern, resolver in mapping.items():
      match = pattern.match(attribute)
      if match:
        properties[key] = resolver(match)
        return

  def isVpcAttributeLookup(self, property):
    if not isinstance(property, dict) or "Fn::GetAtt" not in property:
      return False
    (resource, _) = util.unpackGetAtt(property["Fn::GetAtt"])
    if not self.isResourceVpc(resource):
      return False
    return True

  def isResourceVpc(self, name):
    resources = self.template.get("Resources", {})
    resource = resources[name]
    return resource["Type"] == "LittleOrange::Networking::VPC"

  def transform(self, template, parameters):

    self.template = dict(template)
    self.parameters = util.StackParameters(dict(parameters))

    if "Outputs" not in self.template:
      self.template["Outputs"] = {}

    resources = self.template.get("Resources", {})
    initialResourceNames = list(resources.keys())
    for name in initialResourceNames:  # perform all attribute transforms before VPC transforms
      self.transformVpcAttributeLookups(name)
    for name in initialResourceNames:
      if self.isResourceVpc(name):
        self.transformVPCResource(name)

    return self.template
