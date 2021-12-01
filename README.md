# Getting pools/transaction-fees from UniswapV3 


#Commands:
Get pools statistics of traded pairs for the last 24 hours
```bash
python3 get_pools.py
```
You can get same info in some date range, enter date from and date to in format year-month-day
```bash
python3 get_pools.py your_date_from your_date_to
```

Same commands for getting fees data
```bash
python3 get_fees.py
```
```bash
python3 get_fees.py your_date_from your_date_to
```


Commands will create .xlsx files with data you got.
