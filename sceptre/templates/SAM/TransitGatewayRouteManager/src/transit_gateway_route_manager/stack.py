from aws_cdk import (
    core as Cdk,
    aws_ec2 as Ec2
)

class TransitGatewayAttachmentStack(Cdk.Stack):

  def __init__(self, scope: Cdk.Construct, id: str,
    transit_gateway_attachment_id: str,
    association_route_table_id: str,
    propagation_route_table_ids: list,
    **kwargs) -> None:
    super().__init__(
        scope,
        id,
        description=f"Transit Gateway Route Manager stack for {transit_gateway_attachment_id}",
        **kwargs
    )

    Ec2.CfnTransitGatewayRouteTableAssociation(self, "RouteTableAssociation",
      transit_gateway_attachment_id=transit_gateway_attachment_id,
      transit_gateway_route_table_id=association_route_table_id
    )

    for i, route_table_id in enumerate(propagation_route_table_ids):
      Ec2.CfnTransitGatewayRouteTablePropagation(self, f"RouteTablePropagation{i}",
        transit_gateway_attachment_id=transit_gateway_attachment_id,
        transit_gateway_route_table_id=route_table_id
      )


def generate_cdk_stack_template(transit_gateway_attachment_id, association_route_table_id, propagation_route_table_ids):

  app = Cdk.App()

  TransitGatewayAttachmentStack(
    app, "Stack",
    transit_gateway_attachment_id=transit_gateway_attachment_id,
    association_route_table_id=association_route_table_id,
    propagation_route_table_ids=propagation_route_table_ids
  )

  return app.synth().get_stack_by_name("Stack").template