from .base import *


def stockplus(ticker:str):
    url = f"https://mweb-api.stockplus.com/api/securities/KOREA-A{ticker}/recent_trader.json"
    headers = {
        "Host":"mweb-api.stockplus.com",
        "Origin":"https://stockplus.com",
        "Referer":"https://stockplus.com/",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    }
    response  = requests.get(url, headers)
    json_data = json.loads(response.text).get('recentTrader')
    # print(json_data.keys())
    df_list = [pandas.DataFrame(json_data.get(key)).iloc[:,1:].rename(columns={'accTradeVolume':column})
        for key,column in [('bidTraders', 'bidAccTradeVolume'),('askTraders', 'askAccTradeVolume')]]
    df = pandas.merge(df_list[0], df_list[1], on=['traderName','traderNo'], how='outer').fillna(0)
    df = df.loc[:,['traderName','traderNo','askAccTradeVolume','bidAccTradeVolume']]
    return df # , json_data


def daum(ticker:str, today:bool=True):
    r"""Daum 투자자 거래
    ticker : 기업 ticker
    today  : True (오늘), False (어제날짜)
    """
    url_header = "https://finance.daum.net/api/trader/ranks"
    interval_type = 'TODAY' if today else "YESTERDAY"
    query = {
        "AskFieldName":"askAccTradeVolume",
        "AskOrder":"desc",
        "BidFieldName":"bidAccTradeVolume",
        "BidOrder":"desc",
        "symbolCode":f"A{ticker}",
        "limit":10,
        "intervalType":interval_type, # "TODAY", "YESTERDAY"
    }
    query_url = parse.urlencode(query, encoding='UTF-8', doseq=True)
    url = f"{url_header}?{query_url}"
    headers = {
        "Host":"finance.daum.net",
        "Referer":f"https://finance.daum.net/quotes/A{ticker}",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    }
    try:
        result = []
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        assert type(data) == dict, f"{type(data)} is not dict"
        for key in ['BID','ASK']:
            _data = data.get(key).get('data')
            _df   = pandas.DataFrame(_data)
            result.append(_df)
        df = pandas.concat(result).reset_index(drop=True)
        df.insert(0,'ticker',ticker)
        return df
    except Exception as E:
        return None


def daum_yesterday(ticker:str):
    url_header = "https://finance.daum.net/api/trader/ranks"
    query = {
        "AskFieldName":"askAccTradeVolume",
        "AskOrder":"desc",
        "BidFieldName":"bidAccTradeVolume",
        "BidOrder":"desc",
        "symbolCode":f"A{ticker}",
        "limit":10,
        "intervalType":"YESTERDAY" # "TODAY", # YESTERDAY
    }
    query_url = parse.urlencode(query, encoding='UTF-8', doseq=True)
    url = f"{url_header}?{query_url}"
    headers = {
        "Host":"finance.daum.net",
        "Referer":f"https://finance.daum.net/quotes/A{ticker}",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    }
    try:
        result = []
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        assert type(data) == dict, f"{type(data)} is not dict"
        for key in ['BID','ASK']:
            _data = data.get(key).get('data')
            _df   = pandas.DataFrame(_data)
            result.append(_df)
        df = pandas.concat(result).reset_index(drop=True)
        df.insert(0,'ticker',ticker)
        return df
    except Exception as E:
        return None


def mk(ticker:str): # KR7005930003
    r"""매일경제 증권사 거래 증권사
    ticker : KR7005930003"""
    assert len(ticker) == 12, f"{len(ticker)} is not 12"
    url = f"https://stock.mk.co.kr/price/dealer/{ticker}"
    headers = {
        "Host":"stock.mk.co.kr",
        "Referer":f"https://stock.mk.co.kr/price/home/{ticker}",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    }
    
    html_source = ""
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html_source = response.text    
    
    results = {}
    html_table = ""
    if html_source != "":
        response_lxml = fromstring(html_source)
        table_list = response_lxml.xpath('.//section[@class="stock_sec"]//div[@class="col col_6"]//section')
        if len(table_list) > 0:
            for table in table_list:
                title = ""
                title_source = table.xpath('./header/h2/text()')
                if len(title_source) > 0:
                    title = title_source[0]
                html_table = tostring(table, encoding='unicode')
                _df = pandas.read_html(html_table)[0]
                results[title] = _df

    data = results
    _df_ask     = data.get('매도상위회원사')
    _df_ask_out = data.get('매도상위 이탈 회원사')
    df  = pandas.merge(_df_ask, _df_ask_out, on=['회원사','수량','비중'], how='outer').loc[:,\
        ['회원사','수량']].rename(columns={'수량':'askAccTradeVolume'})
    _df_bid     = data.get('매수상위회원사')
    _df_bid_out = data.get('매수상위 이탈 회원사')
    _df = pandas.merge(_df_bid, _df_bid_out, on=['회원사','수량','비중'], how='outer').loc[:,\
        ['회원사','수량']].rename(columns={'수량':'bidAccTradeVolume'})
    df = pandas.merge(df, _df, on=['회원사'], how='outer')
    df = df[~df['회원사'].isin(['합계'])].fillna(0).reset_index(drop=True)
    return df.rename(columns={'회원사':'traderName'})
