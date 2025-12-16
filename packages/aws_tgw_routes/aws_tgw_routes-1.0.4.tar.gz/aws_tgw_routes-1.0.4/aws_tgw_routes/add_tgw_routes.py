#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""Add routes to AWS Transit Gateway Route Tables."""

import os
from pprint import pprint
from typing import Union
import boto3
import aws_authenticator


__version__ = "1.0.4"
__author__ = "Ahmad Ferdaus Abd Razak"
__application__ = "add_tgw_routes"


def add_propagation(
    client: boto3.client,
    transit_gateway_route_table_id: str,
    transit_gateway_attachment_id: str
) -> dict:
    """Add propagation to a Transit Gateway Route Table."""
    response = client.enable_transit_gateway_route_table_propagation(
        TransitGatewayRouteTableId=transit_gateway_route_table_id,
        TransitGatewayAttachmentId=transit_gateway_attachment_id,
        DryRun=False
    )
    return response


def add_static_route(
    client: boto3.client,
    transit_gateway_route_table_id: str,
    transit_gateway_attachment_id: str,
    destination_cidr_block: str
) -> dict:
    """Add static route to a Transit Gateway Route Table."""
    response = client.create_transit_gateway_route(
        DestinationCidrBlock=destination_cidr_block,
        TransitGatewayRouteTableId=transit_gateway_route_table_id,
        TransitGatewayAttachmentId=transit_gateway_attachment_id,
        Blackhole=False,
        DryRun=False
    )
    return response


def main(
    access_key_id: Union[str, None] = os.getenv("AWS_ACCESS_KEY_ID"),
    secret_access_key: Union[str, None] = os.getenv("AWS_SECRET_ACCESS_KEY"),
    session_token: Union[str, None] = os.getenv("AWS_SESSION_TOKEN"),
    region_name: Union[str, None] = os.getenv("AWS_REGION"),
    routes: list[dict] = []
) -> None:
    """Execute main function."""
    # Authenticate to AWS.
    auth = aws_authenticator.AWSAuthenticator(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        session_token=session_token,
        region_name=region_name
    )
    session = auth.iam()
    client = session.client("ec2")

    # Add routes.
    for route in routes:
        if "cidr" in route.keys():
            response = add_static_route(
                client,
                route["rt"],
                route["att"],
                route["cidr"]
            )
        else:
            response = add_propagation(
                client,
                route["rt"],
                route["att"]
            )
        pprint(response, indent=2)
