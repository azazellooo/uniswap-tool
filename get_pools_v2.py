import pandas as pd
import json
import sys
from datetime import datetime

from scrap.collecting_v2 import scraping

dates = sys.argv[1:]


def main():
    result = scraping()
    # result = [i for n, i in enumerate(result) if i not in result[n + 1:]]
    if dates:
        try:
            start = datetime.strptime(f'{dates[0]} 00:00:00', '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(f'{dates[1]} 00:00:00', '%Y-%m-%d %H:%M:%S')
        except ValueError:
            sys.exit('Error! Enter valid dates. Enter dates in format "year-month-day"')
        result = list(filter((lambda d: start <= datetime.strptime(d['pair_created'], '%Y-%m-%d %H:%M:%S') <= end), result))
    pools_json = json.dumps(result)
    df_json = pd.read_json(pools_json)
    df_json.to_excel('pools.xlsx', sheet_name='liquidity-pools')
    print('Done!')


if __name__ == '__main__':
    main()
