import sys

from setup import transport, make_fees_querystring
from scrap.collect_fees import FeesCollector
from scrap.gql_queries import GQLQuery
from scrap.utils import get_last_24_h_timestamps, get_timestamp_range

dates = sys.argv[1:]
start, end = get_last_24_h_timestamps()

if dates:
    try:
        start, end = get_timestamp_range(dates[0], dates[1])
    except ValueError:
        sys.exit('Error! Enter valid dates. Enter dates in format "year-month-day"')


query_string = make_fees_querystring(start, end)


def main():
    gql_query = GQLQuery(transport=transport)
    response_data = gql_query.make_request(query_string=query_string)
    raw_positions = response_data.get('positionSnapshots')
    collector = FeesCollector(raw_positions=raw_positions)
    fees = collector.collect_fees()
    collector.write_excel(fees)


if __name__ == '__main__':
    main()

