from ._header import *


class KofiaData(HeaderOfKofia):

    r"""금융투자협회 크롤링 : http://freesis.kofia.or.kr/
    > 대차거래의 차입자는 차입한 주식으로 시장에서 매도하는 `공매도` 뿐 아니라 
        `매매거래의 결제, 차익 해지거래` 등 다양한 투자전략 목적으로 활용 가능함
    > Header(class) 수집을 위한 파라미터 값 모음
    :: 수집을 위한 `연산 메서드` 는 자식 클래스에서 별도로 작업하기
    - `_json()`  : Post 수집을 위한 Json Data 생성함수
    - `_get()`   : Response to DataFrame 작동함수

    - `market()`        : 증시동향(코스닥, 코스피)
    - `around()`        : 증시 주변자금 현황
    - `short()`        : 일간 종목별 대차거래 내역
    - `short_balance()`: 신용공여(신용대출) 잔고(공매도) 추이
    - `short_trader()` : 참여자별 대차거래 내역
    """
    # - `credit_deal()`   : 신용거래 체결주수 추이

    # 증시동향
    def market(self, start:str=None, end:str=None, gap:int=7, market:str='KOSPI'):
        r"""증시동향 : 유가증권, 코스닥 현황"""
        assert market.upper() in ['KOSPI', 'KOSDAQ'], "KOSPI, KOSDAQ 을 입력해 주세요"
        code = {'KOSPI':"STATSCU0100000020BO", 'KOSDAQ':"STATSCU0100000030BO"}[market.upper()]
        column = {"TMPV1":'날짜','TMPV2':f'{market.upper()}지수','TMPV3':'거래량',
            'TMPV4':'거래대금','TMPV5':'시가총액','TMPV6':'외국인시총','TMPV7':'외국인비중'}
        return self._get(start=start, end=end, gap=gap, code=code, column=column)

    # 증시 주변자금 현황
    def around(self, start:str=None, end:str=None, gap:int=7) -> pandas.DataFrame:
        r"""(구간) 증시 주변자금 현황
        (str)start : 시작날짜
        (str)end   : 종료날짜
        (int)gap   : 날짜 입력이 없는경우 현재로 부터 수집 기준일"""

        column = {'TMPV1':'날짜', 'TMPV2':'투자자예탁금(파생예수금제외)', 'TMPV3':'파생예수금',
            'TMPV4':'RP매도잔고', 'TMPV5':'위탁매매미수금', 'TMPV6':'위탁매매미수금대비실제반대금액', 
            'TMPV7':'미수금대비반대매매비중(%)'}
        code = "STATSCU0100000060BO"
        return self._get(start=start, end=end, gap=gap, code=code, column=column)


    # 종목별 (ticker) 대차거래 내역
    def short_ticker(self, start:str=None, end:str=None, ticker:str=None) -> pandas.DataFrame:
        r"""(일간) 종목별 대차거래내역
        (str) date_string : 기준날짜
        (str) market      : KOSPI, KOSDAQ"""
        column = {'TMPV1':'날짜','TMPV2':'종목명','TMPV3':'체결(주식)',
            'TMPV4':'상환(주식)','TMPV5':'잔고(주식)','TMPV6':'잔고(금액)'}
        code      = "STATSCU0100000140BO"
        # OBJ_NM	"STATSCU0100000140BO"

        return self._get(start=start,end=end, code=code, ticker=ticker, column=column)


        # dmSearch	{…}
        # OBJ_NM	"STATSCU0100000140BO"
        # tmpV1	"D"
        # tmpV40	"1000000"
        # tmpV41	"1"
        # tmpV45	"20250608"
        # tmpV46	"20250908"
        # tmpV72	"086520"



    # 일별 마켓 (market) 대차거래 내역
    def short_market(self, date:str=None, market='KOSPI') -> pandas.DataFrame:
        r"""(일간) 종목별 대차거래내역
        (str) date_string : 기준날짜
        (str) market      : KOSPI, KOSDAQ"""

        column = {'TMPV1':'종목명','TMPV2':'종목코드','TMPV3':'체결(주식수)',
            'TMPV4':'상환(주식수)','TMPV5':'잔고(주식)','TMPV6':'잔고(금액)'}
        code = "STATSCU0100000130BO"
        assert market.upper() in ['KOSPI', 'KOSDAQ'], "KOSPI, KOSDAQ 을 입력해 주세요"
        market = {'KOSPI':1, 'KOSDAQ':2}[market.upper()]
        return self._get(start=date, code=code, column=column, market=market)


    # 신용공여 잔고추이
    def short_balance(self, start:str=None, end:str=None, gap:int=7) -> pandas.DataFrame:
        r"""(구간) 신용공여 잔고추이
        (str)start : 시작날짜
        (str)end   : 종료날짜
        (int)gap   : 날짜 입력이 없는경우 현재로 부터 수집 기준일"""

        column = {'TMPV1':'날짜', 'TMPV2':'신용융자잔고(전체)', 'TMPV3':'신용융자잔고(KOSPI)',
            'TMPV4':'신용융자잔고(KOSDAQ)', 'TMPV5':'신용대차잔고(전체)', 'TMPV6':'신용대차잔고(KOSPI)', 
            'TMPV7':'신용대차잔고(KOSDAQ)', 'TMPV8':'청약자금대출', 'TMPV9':'예탁증권담보증권'}
        code = "STATSCU0100000070BO"
        return self._get(start=start, end=end, gap=gap, code=code, column=column)


    # 신용거래 체결주수
    def short_trader(self, start:str=None, end:str=None, gap:int=7) -> pandas.DataFrame:
        r"""(구간) 신용거래 체결주수
        (str) start : 시작날짜
        (str) end   : 종료날짜
        (int) gap   : 날짜 입력이 없는경우 현재로 부터 수집 기준일"""
        column = {'TMPV1':'구분','TMPV2':'거래원',
            'TMPV3':'체결규모(대여)','TMPV4':'비중(대여)','TMPV5':'체결규모(차입)','TMPV6':'비중(차입)'}
        code = "STATSCU0100000150BO"
        df = self._get(start=start, end=end, gap=gap, code=code, column=column)

        # Post Processing ...
        df['구분'] = list(map(lambda x : numpy.NaN if x in ['',' '] else x,  df['구분'].tolist()))
        df['구분'] = df['구분'].ffill() # fillna(method='ffill')
        return df


    # def credit_deal(self, start:str=None, end:str=None, gap:int=7) -> pandas.DataFrame:
    #     r"""(구간) 신용거래 체결주수
    #     (str) start : 시작날짜
    #     (str) end   : 종료날짜
    #     (int) gap   : 날짜 입력이 없는경우 현재로 부터 수집 기준일"""

    #     column = {'TMPV1':'날짜', 'TMPV2':'신용융자거래(전체)', 'TMPV3':'신용융자거래(KOSPI)',
    #         'TMPV4':'신용융자거래(KOSDAQ)', 'TMPV5':'신용대차거래(전체)', 'TMPV6':'신용대차거래(KOSPI)', 
    #         'TMPV7':'신용대차거래(KOSDAQ)', 'TMPV8':'청약자금대출', 'TMPV9':'예탁증권담보증권'}
    #     code = "STATSCU0100000080BO"
    #     df =  self._get(start=start, end=end, gap=gap, code=code, column=column)
    #     return df.dropna(axis=1, how='all')

# class method ...

def short(date:str=None, market='KOSPI'):
    return KofiaData().short_market(date=date, market=market)


def short_ticker(start:str=None, end:str=None, ticker:str=None):
    # KofiaData().short_ticker(start=start, end=end, ticker=ticker)
    df = KofiaData().short_ticker(start=start, end=end, ticker=ticker)
    # sort value by '날짜'
    df['날짜'] = pandas.to_datetime(df['날짜'])
    df = df.sort_values(
        by="날짜", 
        ascending=True, # 오름차순 정렬
    ).reset_index(drop=True)
    return df