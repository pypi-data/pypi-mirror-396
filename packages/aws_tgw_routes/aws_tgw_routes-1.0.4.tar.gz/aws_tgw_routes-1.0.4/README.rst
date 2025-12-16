==================
**aws_tgw_routes**
==================

Overview
--------

Manage AWS Transit Gateway routes.

Functions
---------

- get_tgw_routes
   - Filter by:
      - Transit Gateway Route Table IDs.
      - [Optional] Resource Types (vpc, vpn, direct-connect-gateway, peering, connect).
      - [Optional] States (active, blackhole).
      - [Optional] Types (static, propagated).
- add_tgw_routes
   - Add static routes: specify CIDR in route dictionary.
   - Add propagated routes: don't specify CIDR in route dictionary.

Usage
-----

- Installation:

.. code-block:: BASH

   pip3 install aws_tgw_routes
   # or
   python3 -m pip install aws_tgw_routes

- Set common environment variables (or use them as function arguments):

.. code-block:: BASH

   export AWS_ACCESS_KEY_ID=your_access_key_id
   export AWS_SECRET_ACCESS_KEY=your_secret_access_key
   export AWS_SESSION_TOKEN=your_session_token
   export AWS_REGION=your_aws_region

- GET examples:

Set environment variables (or use them as function arguments):

.. code-block:: BASH

   export AWS_TGW_RT_IDS=comma-separated_tgw_route_table_ids
   export RESOURCE_TYPES=comma-separated_resource_types
   export STATES=comma-separated_states
   export TYPES=comma-separated_types

Execute function:

.. code-block:: PYTHON

   from pprint import pprint
   from aws_tgw_routes import get_tgw_routes

   response = get_tgw_routes.main()
   pprint(response, indent=2)

- ADD examples:

Set function arguments and execute function:

.. code-block:: PYTHON

   from aws_tgw_routes import add_tgw_routes

   routes = [
      {
         "rt": "tgw-rtb-0123456789abcdef0",
         "att": "tgw-attach-0123456789abcdef0",
         "cidr": "10.0.0.0/16"
      },
      {
         "rt": "tgw-rtb-0123456789abcdef0",
         "att": "tgw-attach-0fedcba9876543210"
      }
   ]

   add_tgw_routes.main(routes=routes)
