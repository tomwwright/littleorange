from . import util
from .vpc import VPC
import ipaddress
import re
from typing import Dict

REGEX_IPV4 = re.compile(r'^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))?$')


def isValidIPv4CIDR(cidr):
  """
  Returns if passed CIDR matches regex for an IPv4 CIDR, e.g. 192.168.1.0/24
  """
  return REGEX_IPV4.match(cidr)


def buildNACLEntry(naclResourceName, nacl):
  (ruleId, action, protocol, fromPortOrIcmpCode, toPortOrIcmpType, cidr) = nacl
  resourceName = f"{naclResourceName}Ingress{ruleId}"

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
          "Egress": False,
          "Protocol": protocols.get(protocol, -1),
          "RuleAction": action.lower(),
          "RuleNumber": ruleId
      }
  }
  if protocol in ["TCP", "UDP"]:
    resource["PortRange"] = {
        "To": toPortOrIcmpType,
        "From": fromPortOrIcmpCode
    }
  elif protocol == "ICMP":
    resource["Icmp"] = {
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

  def buildInternetGateway(self, vpcName):
    self.template["Resources"][f"{vpcName}IGW"] = {
        "Type": "AWS::EC2::InternetGateway",
        "Properties": {}
    }

    self.template["Resources"][f"{vpcName}IGWAttachment"] = {
        "Type": "AWS::EC2::VPCGatewayAttachment",
        "Properties": {
            "InternetGatewayId": {"Ref": f"{vpcName}IGW"},
            "VpcId": {"Ref": vpcName},
        }
    }

  def buildNATGateways(self, vpcName, availabilityZones):
    for i in range(availabilityZones):
      label = self.availabilityZoneLabels[i]
      publicSubnetResourceName = "{}Public{}".format(vpcName, label)
      natGatewayResourceName = "{}NAT{}".format(vpcName, label)
      natGatewayIPResourceName = "{}NATIP{}".format(vpcName, label)

      self.template["Resources"][natGatewayIPResourceName] = {
          "Type": "AWS::EC2::EIP",
          "Properties": {
              "Domain": "vpc"
          }
      }

      self.template["Resources"][natGatewayResourceName] = {
          "Type": "AWS::EC2::NatGateway",
          "Properties": {
              "AllocationId": {"Fn::GetAtt": f"{natGatewayIPResourceName}.AllocationId"},
              "SubnetId": {"Ref": publicSubnetResourceName}
          }
      }

  def buildSubnets(self, vpc):
    for subnet in vpc.subnets:
      self.template["Resources"][subnet["ResourceName"]] = {
          "Type": "AWS::EC2::Subnet",
          "Properties": {
              "AvailabilityZone": {"Fn::Select": [str(subnet["AvailabilityZoneIndex"]), {"Fn::GetAZs": ""}]},
              "CidrBlock": str(subnet["CIDR"]),
              "VpcId": {"Ref": vpc.name}
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
              "VpcId": {"Ref": vpc.name}
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
        routeResourceName = "{}Route{}".format(subnet["ResourceName"], name)
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

      naclResourceName = f"{tier['ResourceName']}NACL"
      self.template["Resources"][naclResourceName] = {
          "Type": "AWS::EC2::NetworkAcl",
          "Properties": {
              "VpcId": {"Ref": vpc.name}
          }
      }
      self.template["Outputs"][f"{tier['ResourceName']}NACLId"] = {
          "Description": f"NACL ID of the {tier['Name']} Tier of {vpc.name}",
          "Value": {"Ref": naclResourceName}
      }

      for nacl in tier["NACLs"]:
        (naclEntryResourceName, naclEntryResource) = buildNACLEntry(naclResourceName, nacl)
        self.template["Resources"][naclEntryResourceName] = naclEntryResource

  def buildVPC(self, name, resource):
    cidr = self.resolveParameter(resource["Properties"]["CIDR"])
    if not isValidIPv4CIDR(cidr):
      raise Exception(f"Invalid IPv4 VPC CIDR: {cidr}")

    availabilityZones = self.resolveParameter(resource["Properties"]["AvailabilityZones"])
    useInternetGateway = self.resolveParameter(resource["Properties"].get("InternetGateway", True))
    useNATGateways = self.resolveParameter(resource["Properties"].get("NATGateways", False))
    internetGatewayRouteCIDR = self.resolveParameter(resource["Properties"].get("InternetGatewayRouteCIDR", "0.0.0.0/0"))

    vpc = VPC(
        CIDR=cidr,
        Name=name,
        AvailabilityZoneCount=availabilityZones,
        InternetGateway=useInternetGateway,
        InternetGatewayRouteCIDR=internetGatewayRouteCIDR,
        NATGateways=useNATGateways,
    )

    self.template["Resources"][name] = {
        "Type": "AWS::EC2::VPC",
        "Properties": {
            "CidrBlock": cidr,
            "EnableDnsHostnames": True,
            "EnableDnsSupport": True,
            "InstanceTenancy": "default"
        }
    }

    if useInternetGateway:
      self.buildInternetGateway(name)

    self.buildTiers(vpc)
    self.buildSubnets(vpc)

    if useNATGateways:
      self.buildNATGateways(name, availabilityZones)

  def resolveParameter(self, value):
    if not isinstance(value, dict):
      return value

    if "Ref" in value:
      key = value["Ref"]
    if "Fn::Ref" in value:
      key = value["Fn::Ref"]
    if not key:
      raise Exception("Intrinsic functions other than Fn::Ref unsupported for resolving parameter!")

    resolvedValue = self.parameters.get(key)
    if not resolvedValue:
      raise Exception("Intrinsic Fn::Ref must resolve from Parameters!")
    return resolvedValue

  def transformVPCResource(self, name):
    resources = self.template.get("Resources", {})
    resource = resources[name]
    del resources[name]

    self.buildVPC(name, resource)

  def transform(self, template, parameters):

    self.template = dict(template)
    self.parameters = dict(parameters)

    if "Outputs" not in self.template:
      self.template["Outputs"] = {}

    resources = self.template.get("Resources", {})
    initialResourceNames = list(resources.keys())
    for name in initialResourceNames:
      if resources[name]["Type"] == "LittleOrange::Networking::VPC":
        self.transformVPCResource(name)

    return self.template
