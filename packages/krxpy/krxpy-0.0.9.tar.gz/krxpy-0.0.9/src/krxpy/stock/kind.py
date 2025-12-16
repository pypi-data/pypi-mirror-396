from .base import *


# 거래현황정보
# 크롤링 : https://kind.krx.co.kr
# https://comdoc.tistory.com/entry/%EC%83%81%EC%9E%A5-%EB%B2%95%EC%9D%B8-%EB%AA%A9%EB%A1%9D-KIND
class KindInfo:

    url_code:str = "https://kind.krx.co.kr/corpgeneral/corpList.do"
    url_ipo:str  = "https://kind.krx.co.kr/listinvstg/pubofrprogcom.do"
    url_halt:str = "https://kind.krx.co.kr/investwarn/tradinghaltissue.do"
    url_warn:str = "https://kind.krx.co.kr/investwarn/investattentwarnrisky.do"
    url_ipo_v1:str  = "https://kind.krx.co.kr/disclosure/details.do"
    headers:dict = {
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, br, zstd",
        "Accept-Language":"en-US,en;q=0.5",
        "Cache-Control":"no-cache",
        "Connection":"keep-alive",
        "Content-Type":"application/x-www-form-urlencoded",
        "Pragma":"no-cache",
        "Sec-Fetch-Dest":"document",
        "Sec-Fetch-Mode":"navigate",
        "Sec-Fetch-Site":"same-origin",
        "TE":"trailers",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":FakeAgent.random,
        "Host":"kind.krx.co.kr",
        "Origin":"https://kind.krx.co.kr",
    }

    # Class Nameing ..
    def __repr__(self) -> str:
        return f"기업공시채널 : kind.krx.co.kr"

    # Crawling to DataFrame
    def _df(self, url:str="", headers:dict={}, form_data:dict={}):
        time.sleep(2)
        response = requests.post(url, headers=headers, data=form_data)
        if response.status_code == 200:
            response_io = StringIO(response.text)
            df = pandas.read_html(response_io, converters={'종목코드':str}, flavor='lxml')[0]
        else:
            df = pandas.DataFrame()

        # Post Processing ... : 불필요한 컬럼 삭제
        for column_name in ['번호']:
            if column_name in df.columns.tolist():
                del df[column_name]
        return df

    # 상장법인목록
    def corpList(self):
        r"""상장법인목록"""
        headers = self.headers
        headers["Referer"]="https://kind.krx.co.kr/corpgeneral/corpList.do?method=loadInitPage"
        form_data = {}
        form_data["method"] = "download"
        form_data["pageIndex"] = "1"
        form_data["currentPageSize"] = "4500"
        form_data["beginIndex"] = ""
        form_data["orderMode"] = "3"
        form_data["orderStat"] = "D"
        form_data["fiscalYearEnd"] = "all"
        form_data["location"] =	"all"
        return self._df(self.url_code, headers, form_data)

    # 신규상장기업
    def ipo(self, _from:str=None, _to=None, split:bool=False):
        r"""신규상장기업
        _from : 상장 예정일 (조회시작)
        _to   : 상장 예정일 (조회종료) """
        _from, _to = date_to_string(_from), date_to_string(_to)
        if _from == _to:
            _from = date_to_string(_from, datetime_obj=True)
            _from = _from - timedelta(days=95)

        headers  = self.headers
        headers["Referer"] = f"{self.url_ipo}?method=searchPubofrProgComMain"
        form_data = {
            "method":"searchPubofrProgComSub",
            "currentPageSize":"3000",
            "pageIndex":"1",
            "orderMode":"1",
            "orderStat":"D",
            "forward":"pubofrprogcom_down",
            "fromDate":date_to_string(_from),
            "toDate":date_to_string(_to)
        }
        df = self._df(self.url_ipo, headers, form_data)

        # Post Processing
        ## :: Split Date
        ## :: `청약일정`,`수요예측일정` 날짜구간으로 나누기
        if split:
            for _column in ['청약일정','수요예측일정']:
                _index      = df.columns.tolist().index(_column)
                df[_column] = df[_column].map(
                    lambda x : x.replace('  ',' ')
                ) # 공백2개 제거하기
                _data_split = [
                    [_.strip()  for _ in _.split('~')] 
                    for _ in df[_column].tolist()
                ]
                df = df.drop(_column, axis=1)
                df.insert(
                    _index, _column.replace('일정','종료'), 
                    list(map(lambda x : x[1], _data_split))
                )
                df.insert(
                    _index, _column.replace('일정','시작'), 
                    list(map(lambda x : x[0], _data_split))
                )

        ## :: Sorting & Value Dtype
        df = df.sort_values('상장예정일', ascending=False).reset_index(drop=True)
        df = df[df['상장예정일'] > date_to_string()]
        df = df.sort_values('상장예정일').reset_index(drop=True)
        for column in ['확정공모가',"공모금액(백만원)"]:
            df[column] = list(map(lambda x : 0 if x == '-' else int(x), df[column]))
        return df

    # 신규상장기업 현황
    def ipo_v1(self, _from:str=None, _to=None):
        r"""신슈상장기업
        _from : 상장 예정일 (조회시작)
        _to   : 상장 예정일 (조회종료) """
        _from, _to = date_to_string(_from), date_to_string(_to)
        if _from == _to:
            _from = date_to_string(_from, datetime_obj=True)
            _from = _from - timedelta(days=30)

        refer_params = {
            "method":"searchDetailsMain",
            "disclosureType":"02",
            "disTypevalue":"0321",
            "disTypename":"6",
        }
        headers  = self.headers
        headers["Referer"] = f"{self.url_ipo_v1}?{parse.urlencode(refer_params, encoding='utf-8')}"
        form_data = {
            "method":	"searchDetailsSub",
            "currentPageSize":	"15",
            "pageIndex":	"1",
            "orderMode":	"1",
            "orderStat":	"D",
            "forward":	"details_down",
            "disclosureType02":	"0321|",
            "pDisclosureType02":	"0321|",
            "repIsuSrtCd":	"",
            "allRepIsuSrtCd":	"",
            "oldSearchCorpName":	"",
            "disclosureType":	"6",
            "disTypevalue":	"",
            "reportNm":	"신규상장",
            "fromDate":	date_to_string(_from), # 신고서 제출시기
            "toDate":	date_to_string(_to), # 
            "reportNmTemp":	"신규상장",
            "reportNmPop":	"",
            "disclosureTypeArr02":	"0321"
        }
        return self._df(self.url_ipo_v1, headers, form_data)

    # 거래정지종목
    def halt(self):
        header = self.headers
        header['Referer'] = f"{self.url_halt}?method=searchTradingHaltIssueMain"
        form_data = {
            "method":"searchTradingHaltIssueSub",
            "currentPageSize":"3000",
            "pageIndex":"1",
            "forward":"tradinghaltissue_down",
            "marketType":"1",
        }
        df_list = []
        for market_no in ['1','2']:
            form_data['marketType'] = market_no
            df_list.append(self._df(self.url_halt, header, form_data))
        df = pandas.concat(df_list, axis=0).reset_index(drop=True)
        return df

    # 투자주의/경고/위험 종목
    def warnrisky(self, type_name:str=None, date:str=None):
        r"""투자주의/경고/위험 종목
        date : 조회기준 날짜
        type_name : """
        type_dict = {}
        type_dict['caution'] = {'orderMode':"4","menuIndex":"1","forward":"invstcautnisu_down"}
        type_dict['warning'] = {'orderMode':"3","menuIndex":"2","forward":"invstwarnisu_down"}
        type_dict['risky']   = {'orderMode':"3","menuIndex":"3","forward":"invstriskisu_down"}
        date = date_to_string(date)
        form_data = {
            "method":"investattentwarnriskySub",
            "currentPageSize":"3000",
            "pageIndex":"1",
            "orderStat":"D",
            "searchFromDate": date,
            "startDate": date,
            "endDate": date
        }
        assert type_dict.get(type_name) is not None, f"{type_name} is not in {type_dict.keys()}"
        form_data.update(type_dict[type_name])
        headers = self.headers
        headers['Referer'] = f"{self.url_warn}?method=investattentwarnriskyMain"
        return self._df(self.url_warn, headers, form_data)


# kind.krx.co.kr 수집기
def info_kind(name:str='code', date:str=None, split:bool=False):

    r"""kind.krx.co.kr 크롤링 함수
    name : 'code','ipo','halt','risky','caution','warning'
    date : 기준날짜 """

    # Params
    kind = KindInfo()
    name_list = ['code','ipo','halt','risky','caution','warning']
    name_dict = {
        'halt':"거래정지", 'caution':"투자주의",
        'warning':'투자경고', 'risky':'투자위험' }
    assert name in name_list, f"{name} not in {name_list}"

    # Main Processing
    df = None
    try:
        if name == 'code':
            df = kind.corpList()
        elif name == 'ipo':
            df = kind.ipo(date, split=split)
        elif name == 'halt':
            df = kind.halt()
        else:
            df = kind.warnrisky(name, date)
    except Exception as e:
        print(e)

    if df is None:
        return df

    # Post Processing
    if name_dict.get(name) is not None:
        df.insert(0,'구분',name_dict.get(name))
    return df
