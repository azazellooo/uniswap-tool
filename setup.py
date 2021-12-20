from gql.transport.requests import RequestsHTTPTransport

transport = RequestsHTTPTransport(
    url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
    verify=True,
    retries=3
)
ether_url = 'https://cn.etherscan.com/dex#tradingpairs'
exec_path = 'paste_here_your_path_to_geckodriver'

def make_pools_querystring(start, end):
    query_string = f"""
        {{
        swaps(first:1000 where: {{ timestamp_gte:{start},
        timestamp_lte:{end} }}) {{
            id
            pool {{
                liquidity
                volumeUSD
                }}
            timestamp
            token0 {{
                symbol
                derivedETH
            }}
            token1 {{
                symbol
                derivedETH
            }}

        }}
        bundles(first: 5) {{
            id
            ethPriceUSD
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
