from datetime import datetime, timedelta


def get_usd_price(token0usd, token1usd, token0amount, token1amount):
    token0sum = float(token0usd) * float(token0amount)
    token1sum = float(token1usd) * float(token1amount)
    return token0sum + token1sum


def get_last_24_h_timestamps():
    now = datetime.now()
    yesterday = now - timedelta(hours=24)

    start_timestamp = str(yesterday.timestamp())
    end_timestamp = str(now.timestamp())
    return int(float(start_timestamp)), int(float(end_timestamp))


def get_timestamp_range(start_date, end_date):
    start_timestamp = datetime.strptime(f'{start_date} 00:00:00', '%Y-%m-%d %H:%M:%S').timestamp()
    end_timestamp = datetime.strptime(f'{end_date} 00:00:00', '%Y-%m-%d %H:%M:%S').timestamp()
    return int(float(start_timestamp)), int(float(end_timestamp))

