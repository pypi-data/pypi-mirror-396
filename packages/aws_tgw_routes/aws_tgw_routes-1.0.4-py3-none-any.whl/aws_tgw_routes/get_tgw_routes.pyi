import boto3

__version__: str
__application__: str

def get_routes(client: boto3.client, tgw_rt_id: str, resource_types: list = ['vpc', 'vpn', 'direct-connect-gateway', 'peering', 'connect'], states: list = ['active', 'blackhole'], types: list = ['static', 'propagated']) -> dict: ...
def main(access_key_id: str | None = ..., secret_access_key: str | None = ..., session_token: str | None = ..., region_name: str | None = ..., tgw_rt_ids: list = ..., resource_types: list = ..., states: list = ..., types: list = ...) -> dict: ...
