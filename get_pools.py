import sys

from setup import transport, make_pools_querystring
from scrap.collect_pools import PoolsCollector
from scrap.gql_queries import GQLQuery
from scrap.utils import get_last_24_h_timestamps, get_timestamp_range

dates = sys.argv[1:]
start, end = get_last_24_h_timestamps()

if dates:
    try:
        start, end = get_timestamp_range(dates[0], dates[1])
    except ValueError:
        sys.exit('Error! Enter valid dates. Enter dates in format "year-month-day"')


query_string = make_pools_querystring(start, end)


def main():
    gql_query = GQLQuery(transport=transport)
    response_data = gql_query.make_request(query_string=query_string)
    pair_list = response_data.get('swaps')
    collector = PoolsCollector(raw_pair_list=pair_list)
    new_pools = collector.collect_pool_list()
    collector.write_excel(new_pools)


if __name__ == '__main__':
    main()

