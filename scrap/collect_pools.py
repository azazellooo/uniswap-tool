from datetime import datetime
import pandas as pd
import json

from scrap.utils import get_usd_price


class PoolsCollector:
    def __init__(self, raw_pool_list):
        self.raw_pool_list = raw_pool_list

    def collect_pool_list(self):
        print('Collecting pools...')
        new_pools = []
        for pool in self.raw_pool_list:
            new_pool = {}
            for key, value in pool.items():
                if key == 'token0' or key == 'token1':
                    new_pool[f'{key}symbol'] = value.get('symbol')
                    new_pool[f'token{key[-1]}USDrate'] = value.get('volumeUSD')
                elif key == 'createdAtTimestamp':
                    new_pool['created_at'] = str(datetime.fromtimestamp(float(value)))
                else:
                    new_pool[key] = value
            new_pool['USDPrice'] = get_usd_price(
                token0usd=new_pool.get('token0USDrate'),
                token0amount=new_pool.get('volumeToken0'),
                token1usd=new_pool.get('token1USDrate'),
                token1amount=new_pool.get('volumeToken1'))
            new_pools.append(new_pool)
        print('Done!')
        return new_pools

    def write_excel(self, pool_list):
        print('Writing exel...')
        pools_json = json.dumps(pool_list)
        df_json = pd.read_json(pools_json)
        df_json.to_excel('pools.xlsx', sheet_name='liquiity-pools')
        print('Done!')

