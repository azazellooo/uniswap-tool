from gql.transport.requests import RequestsHTTPTransport
import sys

from scrap.collect_pools import PoolsCollector
from scrap.gql_queries import GQLQuery
from scrap.utils import get_last_24_h_timestamps, get_timestamp_range

transport = RequestsHTTPTransport(
    url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
    verify=True,
    retries=3
)
dates = sys.argv[1:]
start, end = get_last_24_h_timestamps()

if dates:
    try:
        start, end = get_timestamp_range(dates[0], dates[1])
    except ValueError:
        sys.exit('Error! Enter valid dates. Enter dates in format "year-month-day"')


query_string = f"""
    {{
    pools(first:1000 where: {{ createdAtTimestamp_gte:{start},
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
    collector = PoolsCollector(raw_pool_list=pool_list)
    new_pools = collector.collect_pool_list()
    collector.write_excel(new_pools)


if __name__ == '__main__':
    main()

