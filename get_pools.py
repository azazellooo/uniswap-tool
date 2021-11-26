from gql.transport.requests import RequestsHTTPTransport
from pprint import pprint

from scrap.collect_pools import PoolsCollector
from scrap.gql_queries import GQLQuery
from scrap.utils import get_last_24_h_timestamps

transport = RequestsHTTPTransport(
    url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
    verify=True,
    retries=3
)

start, end = get_last_24_h_timestamps()
query_string = f"""
    {{
    pools(first:3 where: {{ createdAtTimestamp_gte:{start},
    createdAtTimestamp_lte:{end} }}) {{
        id
        liquidity
        createdAtTimestamp
        token0 {{
            symbol
            volumeUSD
        }}
        token1 {{
            symbol
            volumeUSD
        }}
        volumeToken0
        volumeToken1

    }}
    }}
"""


def main():
    gql_query = GQLQuery(transport=transport)
    response_data = gql_query.make_request(query_string=query_string)
    pool_list = response_data.get('pools')
    pprint(pool_list)
    collector = PoolsCollector(raw_pool_list=pool_list)
    new_pools = collector.collect_pool_list()
    collector.write_excel(new_pools)


if __name__ == '__main__':
    main()

