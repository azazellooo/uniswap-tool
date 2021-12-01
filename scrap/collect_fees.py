import sys
from datetime import datetime
import pandas as pd
import json


class FeesCollector:
    def __init__(self, raw_positions):
        self.raw_positions = raw_positions

    def collect_fees(self):
        print('Collecting fees...')
        fees = []
        for position in self.raw_positions:
            fee_data = {}
            fee_data['created_at'] = str(datetime.fromtimestamp(float(position.get('timestamp'))))
            fee_data['pool_id'] = position.get('pool').get('id')
            fee_data['feesUSD'] = position.get('pool').get('feesUSD')
            fees.append(fee_data)
        print('Done!')
        return fees

    def write_excel(self, fees):
        print('Writing exel...')
        if len(fees) == 0:
            sys.exit('Warning: Nothing to write, maybe you entered invalid date range. ')
        fees_json = json.dumps(fees)
        df_json = pd.read_json(fees_json)
        df_json.to_excel('fees.xlsx')
        print('Done!')

