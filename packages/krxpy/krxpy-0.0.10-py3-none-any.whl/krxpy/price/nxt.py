# NextTrader 실시간 가격정보
from .base import *


class NXT:
    
    def __init__(self):
        r""" NextTrade | 시장정보 -> 실시간 크롤링
        https://www.nextrade.co.kr/menu/transactionStatusMain/menuList.do """
        self.site_visit_uri = "https://www.nextrade.co.kr/menu/transactionStatusMain/menuList.do" # 방문할 주소
        self.uri = "https://www.nextrade.co.kr/brdinfoTime/brdinfoTimeList.do" # 크롤링 정보
        # 시장정보 수집 QuerySet
        self.data = {
            "_search":False,
            "pageUnit":"200",
            "pageIndex":"4",
        }
        self.headers = {
            "Host": "www.nextrade.co.kr",
            "Origin": "https://www.nextrade.co.kr",
            "Referer": "https://www.nextrade.co.kr/menu/transactionStatusMain/menuList.do",
            "Alt-Used": "www.nextrade.co.kr",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "69",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Connection": "keep-alive",
        }

    def __repr__(self) -> str:
        r""" 공식적인 문자열 표현을 반환"""
        # 관례적인 형식: ClassName(attribute1=value, attribute2=value)
        return f"Site('www.nextrade.co.kr) 시장정보 \n{self.site_visit_uri}"

    def _rename_column(self):
        r"""크롤링 데이터 -> 사용자 컬럼명으로 변경"""
        # 수집한 데이터 컬럼
        column_raw  = ["nowDd","nowTime","mktNm","isuCd","isuSrdCd"]#,"isuAbwdNm","isuEnawNm"]
        column_raw += ["curPrc","contrastPrc","upDownRate","oppr","hgpr","lwpr","accTdQty","accTrval"]
        # 사용자 변경할 컬럼        
        column_kor  = ["날짜","시간","시장","KRX코드","종목코드"]#,"종목명","종목명 영어"]
        column_kor += ["현재가","변동값","등락률","시가","고가","저가","거래량","거래대금"]
        column_rename = {key:value for key,value in zip(column_raw, column_kor)}
        return column_rename

    def _str_to_datetime(self, x):
        r"""날짜와 시간 문자열 -> datetime 객체로 변환 
        Args:
            x (str) : `20251215:1629` 
        Return:
            datetime 
        Notes:
            입력 문자열
            - %Y: 연도 (4자리, e.g., 2025)
            - %m: 월 (01~12, e.g., 12)
            - %d: 일 (01~31, e.g., 15)
            - : : 구분자 (콜론)
            - %H: 시 (24시간제, 00~23, e.g., 16)
            - %M: 분 (00~59, e.g., 29) """
        datetime_object = datetime.datetime.strptime(x, '%Y%m%d:%H%M')
        return datetime_object

    def _response(self, uri, headers, data):
        r"""URI 에서 수집한 Response -> List 변환"""
        response_raw = requests.post(uri, headers=headers, data=data)
        response = json.loads(response_raw.text)
        return response

    @property
    def get(self):
        r"""Response -> List -> DataFrame """
        items = self._response(self.uri, self.headers, self.data).get('brdinfoTimeList')
        if items is None:
            print(f"Response Error: {item}")
            return None
        else:
            column_rename = self._rename_column()
            df = pandas.DataFrame(items).rename(columns=column_rename).loc[:,list(column_rename.values())]
            df['datetime'] = df['날짜']+":"+df['시간']
            df = df.drop(['날짜','시간'], axis=1)
            df['datetime'] = df['datetime'].map(self._str_to_datetime)
            df = df.set_index('datetime')
            return df


def get_price_nxt() -> pandas.DataFrame:
    r"""NexTrade 실시간 시장정보 크롤링
    https://www.nextrade.co.kr/menu/transactionStatusMain/menuList.do """
    return NXT().get