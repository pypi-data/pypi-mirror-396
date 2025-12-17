from .base import *

MARKET_CLOSE_HOUR = 15
MARKET_CLOSE_MINUTE = 50


# 업데이트 잘 되나?..
# 다음의 API 를 활용하여 마켓정보 수집
class Daum:
    r"""Daum Finance 의 전종목 시세수집"""

    def __init__(self):
        self.url_krx_real = "https://finance.daum.net/api/quotes/sectors" #market=KOSPI,market=KOSDAQ
        self.url_krx_market = "https://finance.daum.net/api/quotes/today"

    # Web Crawling Parametors
    def params(self, option:str):
        r"""request params
        option : 마켓옵션
        :: return :: url link"""

        market_options = ['KOSPI', 'KOSDAQ']
        type_options   = ["DOMESTIC"]
        
        # Validation Check Exception..
        option = option.upper()
        if option not in market_options + type_options:
            print(f"{option} Option is Not available. choose one of {market_options + type_options}")
            return None

        # Main Process
        # Market 정보를 수집한 경우
        if option in market_options:
            params = {"market": option}
            url = self.url_krx_real + "?" + parse.urlencode(params, encoding='utf-8', doseq=True)

        # Type 정보를 수집한 경우
        elif option in type_options:
            params = {"type": option}
            url = self.url_krx_market + "?" + parse.urlencode(params, encoding='utf-8', doseq=True)
        return url

    # Web Crawling Response
    def response(self, url:str):
        r"""Get Response to Json"""
        url_request = request.Request(url)
        url_request.add_header('User-Agent', FakeAgent.random)
        url_request.add_header('Referer', url)
        response = request.urlopen(url_request)
        response_text = parse.quote_plus(response.read()) # UTF8 Decoding
        response_text = parse.unquote_plus(response_text)  
        return json.loads(response_text)


    # 수집 데이터 필터링
    @elapsed_time
    def get(self) -> list:
        r"""수집 데이터 필터링"""

        def get_market(option:str) -> list:
            r"""Sector 에서 중복되는 기업명 필터링
            option (str) : 마켓구분 ex) KOSPI, KOSDAQ """
            items = []
            url  = self.params(option=option)
            data = self.response(url)

            # API 수집된 원본을 출력
            # if raw:
            #     return data

            # 반복하며 개별 기업정보만 필터링
            for _ in data['data']:
                try: 
                    items += _['includedStocks']
                except:
                    pass
            
            # 수집된 내용 중 중복 기업정보 필터링
            ## :: item_names [] :: 필터링 목록
            ## :: result [] :: 상세정보 수집 및 출력
            result, item_names = [], []
            for item in items:
                name = item['name']
                if name not in item_names:
                    item_names.append(name)
                    result.append(item)
                else:
                    pass
            return result

        result = [] 
        for _ in ['kospi', 'kosdaq']:
            items = get_market(_)
            for item in items:
                item['market'] = _.upper()
            result += items
        return result

    @property
    def check_time(self):
        r"""장 마감시간 확인"""

        # 시간 값 재조정 
        # :: 초 와 밀리세컨드 삭제
        # :: 장 마감 이후인 경우, 마감시간으로 변경
        # https://code.luasoftware.com/tutorials/python/python-datetime-remove-millliseconds-and-seconds/

        # 1 `MARKET_OVER` 장 마감여부 확인
        MARKET_OVER = False
        datetime_now = datetime.datetime.now().replace(second=0, microsecond=0)
        if (datetime_now.hour >= MARKET_CLOSE_HOUR + 1):
            MARKET_OVER = True
            if (datetime_now.hour == MARKET_CLOSE_HOUR):
                if (datetime_now.minute >= MARKET_CLOSE_MINUTE):
                    MARKET_OVER = True

        # 2 DataTime 데이터 재조정
        # :: 2-1 시간의 재조정
        if MARKET_OVER == True:
            datetime_now = datetime.datetime(datetime_now.year, datetime_now.month, datetime_now.day, 15, 30, 00)
        
        # :: 2-2 요일 재조정
        day_check = datetime_now.weekday() - 4
        if day_check > 0:
            datetime_now = datetime_now - datetime.timedelta(day_check)
        return datetime_now


# Daum Sector Infos
def get_price_daum(filter=True) -> pandas.DataFrame:

    r"""Market Price from `Daum`
    filter (bool) : DataFrame 필터링 """

    datetime_check = Daum().check_time # 작업시간 기록하기
    json_data = Daum().get()           # 크롤링 실행
    df = pandas.DataFrame(json_data)
    df = df.sort_values(['marketCap'], ascending=False).reset_index(drop=True)

    # [if] DataFrame 필터링            
    if filter == False: 
        return df

    # Post Processing ...
    column_dict = {'symbolCode':'ticker','tradePrice':'price','accTradeVolume':'volume'}
    df = df.loc[:, column_dict.keys()]
    df.columns = list(map(lambda x : column_dict.get(x), df.columns))
    df.ticker  = list(map(lambda x : x[1:], df.ticker))
    ## Datetime Insert
    df.insert(0, 'datetime', datetime_check)

    # https://stackoverflow.com/questions/21291259/convert-floats-to-ints-in-pandas
    df = df.astype({'price':'int32', 'volume':'int32'})
    return df