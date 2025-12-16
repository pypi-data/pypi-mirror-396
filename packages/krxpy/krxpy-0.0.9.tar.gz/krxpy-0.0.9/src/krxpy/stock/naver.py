from .base import *


def get_exchange(market:str=None, page:int=None, step:int=100):

    r"""Naver 해외금융 (Exchange) Infos"""
    # url = "https://api.stock.naver.com/stock/exchange/NASDAQ/marketValue?page=227&pageSize=20"
    market_list = ['NASDAQ','SHANGHAI','HONG_KONG','TOKYO','HOCHIMINH',]
    assert market in market_list, f"{market=} is not in {market_list}"
    url = f"https://api.stock.naver.com/stock/exchange/{market}/marketValue?page={page}&pageSize={step}"
    headers = {
        "Host": "api.stock.naver.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://m.stock.naver.com/worldstock/home/USA/marketValue/NASDAQ",
        "Access-Control-Max-Age": "86400",
        "X-XSRF-TOKEN": "bd596940-65a3-406a-88a2-e18ad41aa0c4",
        "Origin": "https://m.stock.naver.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
    }
    response = requests.get(url=url, headers=headers)
    return response.json()