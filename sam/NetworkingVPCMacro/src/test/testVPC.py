import ipaddress
from unittest import TestCase

from ..macro.vpc import allocateSubnets, VPC


class Test(TestCase):

  def testVPCSubnets2AZ(self):

    vpc = VPC(
        CIDR="10.1.2.0/23",
        Name="TestVPC",
        AvailabilityZoneCount=2,
        InternetGateway=True,
        InternetGatewayRouteCIDR="0.0.0.0/0",
        NATGateways=True,
        TransitGatewayId="tgw-xxxx",
        TransitGatewayRouteCIDR="10.0.0.0/8"
    )

    assert vpc.name == "TestVPC"
    assert {
        tier["Name"]: {**tier, "Subnets": len(tier["Subnets"])}
        for tier in vpc.tiers
    } == {
        "Public":     {"Name": "Public",     "ResourceName": "TestVPCPublic",     "Size": 0.25, "PrefixLength": 25, "CIDR": ipaddress.IPv4Network("10.1.2.0/25"), "Subnets": 2, "NACLs": [(100, "ALLOW", "ALL", 0, 0, "0.0.0.0/0")]},
        "Private":    {"Name": "Private",    "ResourceName": "TestVPCPrivate",    "Size": 0.25, "PrefixLength": 25, "CIDR": ipaddress.IPv4Network("10.1.2.128/25"), "Subnets": 2, "NACLs": [(100, "ALLOW", "TCP", 1024, 65535, "0.0.0.0/0"), (200, "ALLOW", "UDP", 1024, 65535, "0.0.0.0/0"), (300, "ALLOW", "ALL", 0, 0, "10.1.2.0/23"), (400, "ALLOW", "ALL", 0, 0, "10.0.0.0/8")]},
        "Restricted": {"Name": "Restricted", "ResourceName": "TestVPCRestricted", "Size": 0.25, "PrefixLength": 25, "CIDR": ipaddress.IPv4Network("10.1.3.0/25"), "Subnets": 2, "NACLs": [(100, "ALLOW", "ALL", 0, 0, "10.1.2.128/25")]},
        "Networking": {"Name": "Networking", "ResourceName": "TestVPCNetworking", "Size": 0.25, "PrefixLength": 25, "CIDR": ipaddress.IPv4Network("10.1.3.128/25"), "Subnets": 2, "NACLs": [(100, "ALLOW", "ALL", 0, 0, "10.1.2.0/23")]}
    }

    assert {
        f"{subnet['Tier']['Name']}{subnet['Name']}": {**subnet, "Tier": subnet["Tier"]["Name"]}
        for subnet in vpc.subnets
    } == {
        "PublicA": {"Name": "A", "ResourceName": "TestVPCPublicA", "AvailabilityZoneIndex": 0, "Tier": "Public", "Routes": [("IGW", "0.0.0.0/0", {"GatewayId": {"Ref": "TestVPCIGW"}}), ("TGW", "10.0.0.0/8", {"TransitGatewayId": "tgw-xxxx"})], "CIDR": ipaddress.IPv4Network("10.1.2.0/26")},
        "PublicB": {"Name": "B", "ResourceName": "TestVPCPublicB", "AvailabilityZoneIndex": 1, "Tier": "Public", "Routes": [("IGW", "0.0.0.0/0", {"GatewayId": {"Ref": "TestVPCIGW"}}), ("TGW", "10.0.0.0/8", {"TransitGatewayId": "tgw-xxxx"})], "CIDR": ipaddress.IPv4Network("10.1.2.64/26")},
        "PrivateA": {"Name": "A", "ResourceName": "TestVPCPrivateA", "AvailabilityZoneIndex": 0, "Tier": "Private", "Routes": [("NAT", "0.0.0.0/0", {"NatGatewayId": {"Ref": "TestVPCNATA"}}), ("TGW", "10.0.0.0/8", {"TransitGatewayId": "tgw-xxxx"})], "CIDR": ipaddress.IPv4Network("10.1.2.128/26")},
        "PrivateB": {"Name": "B", "ResourceName": "TestVPCPrivateB", "AvailabilityZoneIndex": 1, "Tier": "Private", "Routes": [("NAT", "0.0.0.0/0", {"NatGatewayId": {"Ref": "TestVPCNATB"}}), ("TGW", "10.0.0.0/8", {"TransitGatewayId": "tgw-xxxx"})], "CIDR": ipaddress.IPv4Network("10.1.2.192/26")},
        "RestrictedA": {"Name": "A", "ResourceName": "TestVPCRestrictedA", "AvailabilityZoneIndex": 0, "Tier": "Restricted", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.0/26")},
        "RestrictedB": {"Name": "B", "ResourceName": "TestVPCRestrictedB", "AvailabilityZoneIndex": 1, "Tier": "Restricted", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.64/26")},
        "NetworkingA": {"Name": "A", "ResourceName": "TestVPCNetworkingA", "AvailabilityZoneIndex": 0, "Tier": "Networking", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.128/26")},
        "NetworkingB": {"Name": "B", "ResourceName": "TestVPCNetworkingB", "AvailabilityZoneIndex": 1, "Tier": "Networking", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.192/26")}
    }

  def testVPCSubnets3AZ(self):

    vpc = VPC(
        CIDR="10.1.2.0/23",
        Name="TestVPC",
        AvailabilityZoneCount=3,
        InternetGateway=True,
        InternetGatewayRouteCIDR="0.0.0.0/0",
        NATGateways=False
    )

    assert vpc.name == "TestVPC"
    assert {
        tier["Name"]: {**tier, "Subnets": len(tier["Subnets"])}
        for tier in vpc.tiers
    } == {
        "Public":     {"Name": "Public",     "ResourceName": "TestVPCPublic",     "Size": 0.25, "PrefixLength": 25, "CIDR": ipaddress.IPv4Network("10.1.2.0/25"), "Subnets": 3, "NACLs": [(100, "ALLOW", "ALL", 0, 0, "0.0.0.0/0")]},
        "Private":    {"Name": "Private",    "ResourceName": "TestVPCPrivate",    "Size": 0.25, "PrefixLength": 25, "CIDR": ipaddress.IPv4Network("10.1.2.128/25"), "Subnets": 3, "NACLs": [(100, "ALLOW", "TCP", 1024, 65535, "0.0.0.0/0"), (200, "ALLOW", "UDP", 1024, 65535, "0.0.0.0/0"), (300, "ALLOW", "ALL", 0, 0, "10.1.2.0/23")]},
        "Restricted": {"Name": "Restricted", "ResourceName": "TestVPCRestricted", "Size": 0.25, "PrefixLength": 25, "CIDR": ipaddress.IPv4Network("10.1.3.0/25"), "Subnets": 3, "NACLs": [(100, "ALLOW", "ALL", 0, 0, "10.1.2.128/25")]},
        "Networking": {"Name": "Networking", "ResourceName": "TestVPCNetworking", "Size": 0.25, "PrefixLength": 25, "CIDR": ipaddress.IPv4Network("10.1.3.128/25"), "Subnets": 3, "NACLs": [(100, "ALLOW", "ALL", 0, 0, "10.1.2.0/23")]}
    }

    assert {
        f"{subnet['Tier']['Name']}{subnet['Name']}": {**subnet, "Tier": subnet["Tier"]["Name"]}
        for subnet in vpc.subnets
    } == {
        "PublicA": {"Name": "A", "ResourceName": "TestVPCPublicA", "AvailabilityZoneIndex": 0, "Tier": "Public", "Routes": [("IGW", "0.0.0.0/0", {"GatewayId": {"Ref": "TestVPCIGW"}})], "CIDR": ipaddress.IPv4Network("10.1.2.0/27")},
        "PublicB": {"Name": "B", "ResourceName": "TestVPCPublicB", "AvailabilityZoneIndex": 1, "Tier": "Public", "Routes": [("IGW", "0.0.0.0/0", {"GatewayId": {"Ref": "TestVPCIGW"}})], "CIDR": ipaddress.IPv4Network("10.1.2.32/27")},
        "PublicC": {"Name": "C", "ResourceName": "TestVPCPublicC", "AvailabilityZoneIndex": 2, "Tier": "Public", "Routes": [("IGW", "0.0.0.0/0", {"GatewayId": {"Ref": "TestVPCIGW"}})], "CIDR": ipaddress.IPv4Network("10.1.2.64/27")},
        "PrivateA": {"Name": "A", "ResourceName": "TestVPCPrivateA", "AvailabilityZoneIndex": 0, "Tier": "Private", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.2.128/27")},
        "PrivateB": {"Name": "B", "ResourceName": "TestVPCPrivateB", "AvailabilityZoneIndex": 1, "Tier": "Private", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.2.160/27")},
        "PrivateC": {"Name": "C", "ResourceName": "TestVPCPrivateC", "AvailabilityZoneIndex": 2, "Tier": "Private", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.2.192/27")},
        "RestrictedA": {"Name": "A", "ResourceName": "TestVPCRestrictedA", "AvailabilityZoneIndex": 0, "Tier": "Restricted", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.0/27")},
        "RestrictedB": {"Name": "B", "ResourceName": "TestVPCRestrictedB", "AvailabilityZoneIndex": 1, "Tier": "Restricted", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.32/27")},
        "RestrictedC": {"Name": "C", "ResourceName": "TestVPCRestrictedC", "AvailabilityZoneIndex": 2, "Tier": "Restricted", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.64/27")},
        "NetworkingA": {"Name": "A", "ResourceName": "TestVPCNetworkingA", "AvailabilityZoneIndex": 0, "Tier": "Networking", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.128/27")},
        "NetworkingB": {"Name": "B", "ResourceName": "TestVPCNetworkingB", "AvailabilityZoneIndex": 1, "Tier": "Networking", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.160/27")},
        "NetworkingC": {"Name": "C", "ResourceName": "TestVPCNetworkingC", "AvailabilityZoneIndex": 2, "Tier": "Networking", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.192/27")}
    }

  def testVPCSubnets4AZ(self):

    vpc = VPC(
        CIDR="10.1.2.0/23",
        Name="TestVPC",
        AvailabilityZoneCount=4
    )

    assert vpc.name == "TestVPC"
    assert {
        tier["Name"]: {**tier, "Subnets": len(tier["Subnets"])}
        for tier in vpc.tiers
    } == {
        "Public":     {"Name": "Public",     "ResourceName": "TestVPCPublic",     "Size": 0.25, "PrefixLength": 25, "CIDR": ipaddress.IPv4Network("10.1.2.0/25"), "Subnets": 4, "NACLs": [(100, "ALLOW", "ALL", 0, 0, "0.0.0.0/0")]},
        "Private":    {"Name": "Private",    "ResourceName": "TestVPCPrivate",    "Size": 0.25, "PrefixLength": 25, "CIDR": ipaddress.IPv4Network("10.1.2.128/25"), "Subnets": 4, "NACLs": [(100, "ALLOW", "TCP", 1024, 65535, "0.0.0.0/0"), (200, "ALLOW", "UDP", 1024, 65535, "0.0.0.0/0"), (300, "ALLOW", "ALL", 0, 0, "10.1.2.0/23")]},
        "Restricted": {"Name": "Restricted", "ResourceName": "TestVPCRestricted", "Size": 0.25, "PrefixLength": 25, "CIDR": ipaddress.IPv4Network("10.1.3.0/25"), "Subnets": 4, "NACLs": [(100, "ALLOW", "ALL", 0, 0, "10.1.2.128/25")]},
        "Networking": {"Name": "Networking", "ResourceName": "TestVPCNetworking", "Size": 0.25, "PrefixLength": 25, "CIDR": ipaddress.IPv4Network("10.1.3.128/25"), "Subnets": 4, "NACLs": [(100, "ALLOW", "ALL", 0, 0, "10.1.2.0/23")]}
    }

    assert {
        f"{subnet['Tier']['Name']}{subnet['Name']}": {**subnet, "Tier": subnet["Tier"]["Name"]}
        for subnet in vpc.subnets
    } == {
        "PublicA": {"Name": "A", "ResourceName": "TestVPCPublicA", "AvailabilityZoneIndex": 0, "Tier": "Public", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.2.0/27")},
        "PublicB": {"Name": "B", "ResourceName": "TestVPCPublicB", "AvailabilityZoneIndex": 1, "Tier": "Public", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.2.32/27")},
        "PublicC": {"Name": "C", "ResourceName": "TestVPCPublicC", "AvailabilityZoneIndex": 2, "Tier": "Public", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.2.64/27")},
        "PublicD": {"Name": "D", "ResourceName": "TestVPCPublicD", "AvailabilityZoneIndex": 3, "Tier": "Public", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.2.96/27")},
        "PrivateA": {"Name": "A", "ResourceName": "TestVPCPrivateA", "AvailabilityZoneIndex": 0, "Tier": "Private", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.2.128/27")},
        "PrivateB": {"Name": "B", "ResourceName": "TestVPCPrivateB", "AvailabilityZoneIndex": 1, "Tier": "Private", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.2.160/27")},
        "PrivateC": {"Name": "C", "ResourceName": "TestVPCPrivateC", "AvailabilityZoneIndex": 2, "Tier": "Private", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.2.192/27")},
        "PrivateD": {"Name": "D", "ResourceName": "TestVPCPrivateD", "AvailabilityZoneIndex": 3, "Tier": "Private", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.2.224/27")},
        "RestrictedA": {"Name": "A", "ResourceName": "TestVPCRestrictedA", "AvailabilityZoneIndex": 0, "Tier": "Restricted", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.0/27")},
        "RestrictedB": {"Name": "B", "ResourceName": "TestVPCRestrictedB", "AvailabilityZoneIndex": 1, "Tier": "Restricted", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.32/27")},
        "RestrictedC": {"Name": "C", "ResourceName": "TestVPCRestrictedC", "AvailabilityZoneIndex": 2, "Tier": "Restricted", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.64/27")},
        "RestrictedD": {"Name": "D", "ResourceName": "TestVPCRestrictedD", "AvailabilityZoneIndex": 3, "Tier": "Restricted", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.96/27")},
        "NetworkingA": {"Name": "A", "ResourceName": "TestVPCNetworkingA", "AvailabilityZoneIndex": 0, "Tier": "Networking", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.128/27")},
        "NetworkingB": {"Name": "B", "ResourceName": "TestVPCNetworkingB", "AvailabilityZoneIndex": 1, "Tier": "Networking", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.160/27")},
        "NetworkingC": {"Name": "C", "ResourceName": "TestVPCNetworkingC", "AvailabilityZoneIndex": 2, "Tier": "Networking", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.192/27")},
        "NetworkingD": {"Name": "D", "ResourceName": "TestVPCNetworkingD", "AvailabilityZoneIndex": 3, "Tier": "Networking", "Routes": [], "CIDR": ipaddress.IPv4Network("10.1.3.224/27")}
    }

  def testAllocateSubnetsEqual(self):

    divisions = [
        ("A", 25),
        ("B", 25),
        ("C", 25),
        ("D", 25)
    ]
    subnet = ipaddress.IPv4Network("10.0.0.0/23")

    allocations = allocateSubnets(subnet, divisions)

    assert allocations == [
        ("A", ipaddress.IPv4Network("10.0.0.0/25")),
        ("B", ipaddress.IPv4Network("10.0.0.128/25")),
        ("C", ipaddress.IPv4Network("10.0.1.0/25")),
        ("D", ipaddress.IPv4Network("10.0.1.128/25"))
    ]

  def testAllocateSubnets(self):

    divisions = [
        ("A", 25),
        ("B", 26),
        ("C", 24),
        ("D", 26)
    ]
    subnet = ipaddress.IPv4Network("10.0.0.0/23")

    allocations = allocateSubnets(subnet, divisions)

    assert allocations == [
        ("C", ipaddress.IPv4Network("10.0.0.0/24")),
        ("A", ipaddress.IPv4Network("10.0.1.0/25")),
        ("B", ipaddress.IPv4Network("10.0.1.128/26")),
        ("D", ipaddress.IPv4Network("10.0.1.192/26"))
    ]


  def testAllocateSubnetsTwo(self):

    divisions = [
        ("A", 26),
        ("B", 24),
        ("C", 26),
        ("D", 25)
    ]
    subnet = ipaddress.IPv4Network("10.0.0.0/23")

    allocations = allocateSubnets(subnet, divisions)

    assert allocations == [
        ("B", ipaddress.IPv4Network("10.0.0.0/24")),
        ("D", ipaddress.IPv4Network("10.0.1.0/25")),
        ("A", ipaddress.IPv4Network("10.0.1.128/26")),
        ("C", ipaddress.IPv4Network("10.0.1.192/26"))
    ]

  def testAllocateSubnetsOddSubnets(self):

    divisions = [
        ("A", 19),
        ("B", 18),
        ("C", 21),
        ("D", 24),
        ("E", 21)
    ]
    subnet = ipaddress.IPv4Network("10.254.0.0/16")

    allocations = allocateSubnets(subnet, divisions)

    assert allocations == [
        ("B", ipaddress.IPv4Network("10.254.0.0/18")),
        ("A", ipaddress.IPv4Network("10.254.64.0/19")),
        ("C", ipaddress.IPv4Network("10.254.96.0/21")),
        ("E", ipaddress.IPv4Network("10.254.104.0/21")),
        ("D", ipaddress.IPv4Network("10.254.112.0/24"))
    ]
