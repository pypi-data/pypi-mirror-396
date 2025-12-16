#!/usr/bin/env python3
# -*- coding: latin-1 -*-
"""Get routes from AWS Transit Gateway Route Tables."""

import os
from typing import Union
import boto3
import aws_authenticator


__version__ = "1.0.4"
__author__ = "Ahmad Ferdaus Abd Razak"
__application__ = "get_tgw_routes"


def get_routes(
    client: boto3.client,
    tgw_rt_id: str,
    resource_types: list,
    states: list,
    types: list
) -> dict:
    """Get routes from a Transit Gateway Route Table."""
    response = client.search_transit_gateway_routes(
        TransitGatewayRouteTableId=tgw_rt_id,
        MaxResults=1000,
        DryRun=False,
        Filters=[
            {"Name": "attachment.resource-type", "Values": resource_types},
            {"Name": "state", "Values": states},
            {"Name": "type", "Values": types}
        ]
    )
    routes = [
        {
            "cidr": route.get("DestinationCidrBlock"),
            "type": route.get("Type"),
            "state": route.get("State"),
            "attachment_id": (
                route
                .get("TransitGatewayAttachments")[0]
                .get("TransitGatewayAttachmentId")
                if route.get("TransitGatewayAttachments")
                else None
            ),
            "resource_type": (
                route
                .get("TransitGatewayAttachments")[0]
                .get("ResourceType")
                if route.get("TransitGatewayAttachments")
                else None
            )
        } for route in response.get("Routes", [])
    ]
    return routes


def main(
    access_key_id: Union[str, None] = os.getenv("AWS_ACCESS_KEY_ID"),
    secret_access_key: Union[str, None] = os.getenv("AWS_SECRET_ACCESS_KEY"),
    session_token: Union[str, None] = os.getenv("AWS_SESSION_TOKEN"),
    region_name: Union[str, None] = os.getenv("AWS_REGION"),
    tgw_rt_ids: list = os.getenv("AWS_TGW_RT_IDS", "").replace(" ", "").split(","),
    resource_types: list = os.getenv(
        "RESOURCE_TYPES",
        "vpc,vpn,direct-connect-gateway,peering,connect"
    ).replace(" ", "").split(","),
    states: list = os.getenv("STATES", "active,blackhole").replace(" ", "").split(","),
    types: list = os.getenv("TYPES", "static,propagated").replace(" ", "").split(",")
) -> dict:
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

    # Get routes.
    for tgw_rt_id in tgw_rt_ids:
        response = get_routes(
            client,
            tgw_rt_id,
            resource_types,
            states,
            types
        )

    return response
