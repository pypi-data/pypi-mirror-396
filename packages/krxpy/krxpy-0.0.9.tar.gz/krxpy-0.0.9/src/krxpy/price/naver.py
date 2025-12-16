from .base import *
from .daum import Daum


# 네이버 금융 실시간 가격 (모바일버젼)
# https://m.stock.naver.com/domestic/capitalization/KOSPI
class NaverFinance():
    
    def __init__(self, market:str='KOSPI', lastpage:int=1, worker=4):
        self.market = market
        self.lastpage = lastpage
        self.worker = worker
        self.headers = {
            "Host": "m.stock.naver.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Access-Control-Max-Age": "86400",
            "X-XSRF-TOKEN": "14ea18ea-73fc-4acf-8296-e4696fb16115",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        self.columns = ['close','change','changePrice','trade','tradevalue','marketcap']
        self.keys = "itemCode","stockName",'closePrice','compareToPreviousClosePrice','fluctuationsRatio',\
            'accumulatedTradingVolume','accumulatedTradingValue','marketValue'
        self.column_dict = {
            'itemCode':'code', 'stockName':'name', 'closePrice':'close',
            'compareToPreviousClosePrice':'changePrice',
            'fluctuationsRatio':'change', 'accumulatedTradingVolume':'trade',
            'accumulatedTradingValue':'tradevalue', 
            'accumulatedTradingValueKrwHangeul':'tradevalueKor',
            'marketValue':'marketcap', 'marketValueHangeul':'markatcapKor'
        }

    def _url(self, page:int):
        market = self.market.upper()
        assert market in ['KOSPI','KOSDAQ'], f"{market} 은 ['KOSPI','KOSDAQ'] 만 가능합니다"
        url = f"https://m.stock.naver.com/api/stocks/marketValue/{market}?page={page}&pageSize=50"
        headers = self.headers
        headers["Referer"] = f"https://m.stock.naver.com/domestic/capitalization/{market}"
        return url, headers
    
    def _response(self, page:int):
        url, headers = self._url(page)
        response = requests.get(url=url, headers=headers)
        return response.json()

    def _item(self, page:int, raw:bool=False):
        response = self._response(page)
        if raw:
            return response
        return [dict(zip(self.keys, itemgetter(*self.keys)(item))) for item in response['stocks']]

    def _items(self, display=True):
        r"""`self.lastpage` 만큼 반복하며 수집 합니다."""
        page_list = list(range(1, self.lastpage + 2))
        items = multiprocess_items(self._item, page_list, worker=self.worker, display=display)
        items = reduce(lambda x,y:x+y, items)
        items = [_  for _ in items  if len(_)>0] # 수집된 데이터가 없는 인덱스 제거
        df = pandas.DataFrame(items).rename(columns=self.column_dict)
        df['code'] = df['code'].map(lambda x: f'{x:0>6}')
        df = df_number_column(
            df,self.columns, except_list=['-']
        )
        return df

    def _page_info(self, display=True):
        response = self._response(1)
        total, size, page = response['totalCount'], response['pageSize'], response['page']
        lastpage = math.ceil(total / 50)
        self.lastpage = lastpage
        if display:
            print(f"Last Page:{lastpage} Total:{total}, Size:{size}\n `self.lastpage` updated")
        return lastpage


def get_price_naver(filter:bool=True, display:bool=False):
    r"""Market Sector from `Naver`
    filter (bool)  : DataFrame 필터링
    display (bool) : 수집과정 화면으로 출력
    cf) df.trade.isna() -> 거래정지 종목"""
    items = []
    datetime_check = Daum().check_time         # 작업시간 기록하기
    for _ in ['KOSPI','KOSDAQ']:
        naver_finance = NaverFinance(market=_)
        naver_finance._page_info(display=display)
        items.append(naver_finance._items(display=display))
    
    # print(df_krx[df_krx.trade.isna()].shape) # 거래정지 종목들
    df = pandas.concat(items).sort_values(
        ['marketcap'], ascending=False).reset_index(drop=True)

    # [if] DataFrame 필터링            
    if filter == False: 
        return df

    # Filtering DataFrame
    df = df.loc[:,['code','close','trade']]
    df = df.rename(columns={'code':'ticker','close':'price','trade':'volume'})

    # https://medium.com/@felipecaballero/deciphering-the-cryptic-futurewarning-for-fillna-in-pandas-2-01deb4e411a1
    # df.volume = df.volume.fillna(0).infer_objects(copy=False)
    df[['volume']] = df[['volume']].infer_objects().fillna(0)
    df.insert(0, 'datetime', datetime_check)
    df = df.astype({'price':'int32', 'volume':'int32'})
    return df
