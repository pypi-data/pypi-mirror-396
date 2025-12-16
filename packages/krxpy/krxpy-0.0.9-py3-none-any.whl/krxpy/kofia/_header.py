from .base import *


class HeaderOfKofia(Header):
    r"""kofia 금융투자협회 수집을 위한 공용 데이터 클래스
    - `_header()` : 웹 크롤링을 위한 url & header
    - `_json()`   : Post 호출을 위한 Form Data
    - `_get()`    : 모든 데이터를 활용하여 호출작업 진행"""

    def _header(self) -> dict:
        r"""Post url 파라미터 정의"""

        # Params : Referer 사이트 주소값 조합을 위한 파라미터
        url = "https://freesis.kofia.or.kr/meta/getMetaDataList.do"
        ref_path = 'stat/FreeSIS.do'
        ref_queryset = {
            'parentDivId':'MSIS10000000000000',
            'serviceId':'STATSCU0100000060'
        }

        # Process : 웹 수집을 위한 Header
        url_parts = urlparse(url)
        headers: dict = {}
        headers["Content-Type"] = "application/json; charset=utf-8"
        headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
        headers["Host"] = url_parts.netloc
        headers["Origin"] = "http://" + url_parts.netloc
        headers["Referer"] = url_parts._replace(
            path = ref_path, 
            query = urlencode(ref_queryset)
        ).geturl()
        
        content = {
            "url": url,
            "headers": headers
        }
        return content

    def _json(self, 
            start:str=None, end:str=None, gap:int=7, 
            code:str=None, ticker:str=None, market:int=None
        ):
        r"""날짜 파라미터 내용확인 및 Post 수집을 위한 Json Data 생성
        (str) start : 데이터 수집 시작날짜
        (str) end   : 데이터 수집 종료날짜
        (int) gap   : 현재로 부터 시작날짜 간격
        (str) code  : API 호출을 위한 작업구분 코드
        (int) market: Kospi, Kosdaq 구분자
        """

        # 날짜 파라미터 생성 및 유효성 검사
        if start == None:
            start = (self._now_date() - datetime.timedelta(gap)).date()
        if end == None:
            end = self._now_date().date()
        start, end = self._date_string(start), self._date_string(end)
        
        # Post 호출을 위한 Json 데이터 생성
        json_data: dict = {"dmSearch":{"tmpV40":"1","tmpV41":"1","tmpV1":"D"}}
        json_data["dmSearch"]["tmpV45"] = start
        json_data["dmSearch"]["tmpV46"] = end

        # 추가작업 Case 1
        # self.credit() : 증시동향 (일간) 데이터  
        if code == 'STATSCU0100000130BO':
            if market in [1,2]:  # market : KOSPI, KOSDAQ
                del json_data["dmSearch"]["tmpV46"]
                json_data["dmSearch"]["tmpV74"] = f"{market},0,,1"

        # 추가작업 Case 2
        # self.credit_trader() : 참여자별 대차거래
        if code == 'STATSCU0100000150BO':
            del json_data["dmSearch"]["tmpV1"]
            del json_data["dmSearch"]["tmpV45"]
            del json_data["dmSearch"]["tmpV46"]
            json_data["dmSearch"]["tmpV30"] = start
            json_data["dmSearch"]["tmpV31"] = end

        # 추가작업 Case 3
        # self.short_ticker() : 대차거래 by Ticker
        if code == 'STATSCU0100000140BO':
            json_data['dmSearch']['tmpV40'] = "1000000"
            json_data['dmSearch']['tmpV72'] = ticker

        # 보정작업을 마친 날짜 데이터 출력
        json_data["dmSearch"]["OBJ_NM"] = code
        content = {
            'start':start,
            'end':end,
            'jsonData':json_data,
        }
        return content

    def _get(self, 
            start:str = None, end:str = None, gap:int = 7, 
            code:str = '', 
            ticker:str = None,
            column:dict = None, market:str = None
        ) -> pandas.DataFrame:

        r"""웹 수집한 Response 데이터를 Pandas DataFrame 으로 출력
        (str) start : 데이터 수집 시작날짜
        (str) end   : 데이터 수집 종료날짜
        (int) gap   : 현재로 부터 시작날짜 간격
        (str) code  : API 호출을 위한 작업구분 코드
        (int) market: Kospi, Kosdaq 구분자"""

        # Get Response
        url_data = self._header()
        content  = self._json(start=start, end=end, gap=gap, code=code, ticker=ticker, market=market)
        start, end, json_data = content['start'], content['end'], content['jsonData']
        response = requests.post(url_data['url'], json=json_data, headers=url_data['headers']).json()
        assert len(response['ds1']) != 0, f'{response}' # False 일 때 메세지 출력

        # Response to DataFrame
        df = pandas.DataFrame(response['ds1'])
        df = self._df_number(df).rename(columns=column)

        # Case 1 (일간) 데이터
        if '날짜' not in list(df.columns):
            df.insert(0, '날짜', start)
            df['날짜'] = pandas.DatetimeIndex(df['날짜'])

        # Case 2 (구간) 데이터
        else:
            # 문자가 포함된 `날짜` Index 제거하기
            txt_list = list(filter(lambda x : len(re.findall('[ㄱ-힣]+',x)) > 0, df['날짜'].tolist()))
            df = df[~df['날짜'].isin(txt_list)].reset_index(drop=True) 
            df['날짜'] = pandas.DatetimeIndex(df['날짜'])

        # Case 3 (구간) 데이터 : 참여자별 거래내역 구간
        # self.credit_trader()
        if code == "STATSCU0100000150BO":
            if start == end:
                df['날짜'] = f'{start}'
            else:
                df['날짜'] = f'{start}~{end}'

        # df = df.set_index('날짜')
        return df
