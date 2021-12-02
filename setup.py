from gql.transport.requests import RequestsHTTPTransport

transport = RequestsHTTPTransport(
    url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
    verify=True,
    retries=3
)


def make_pools_querystring(start, end):
    query_string = f"""
        {{
        swaps(first:1000 where: {{ timestamp_gte:{start},
        timestamp_lte:{end} }}) {{
            id
            pool {{
                liquidity
                }}
            timestamp
            token0 {{
                symbol
                volumeUSD
            }}
            token1 {{
                symbol
                volumeUSD
            }}
            amount0
            amount1

        }}
        }}
    """
    return query_string


def make_fees_querystring(start, end):
    query_string = f"""
        {{
        positionSnapshots(first: 1000 where: {{ timestamp_gte: {start}, timestamp_lte: {end} }}) {{
            id
            pool {{
                id
                feesUSD
            }}
            timestamp
        }}
        }}
    """
    return query_string
