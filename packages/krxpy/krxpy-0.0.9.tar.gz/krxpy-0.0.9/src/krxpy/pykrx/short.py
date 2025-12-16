# 공매도 데이터
# 상장폐지종목 조회
from .base import *
from ._krxio import KrxWebIo
from .ticker import get_ticker
from ._tools import df_number_column


def get_short_function(
        start:str=None, 
        end:str=None, 
        ticker:str=None,  # ticker 코드
    ):

    r"""공매도 데이터 수집기
    Args:
        start : 수집기 시작일 
        end : 수집기 종료일
        ticker : krx ticker
    Return:
        pandas.DataFrame """

    headers = {
        "Host":"data.krx.co.kr",
        "Origin":"https://data.krx.co.kr",
        "Pragma":"no-cache",
        "Referer":"https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC02030101",
        "Sec-Fetch-Dest":"empty",
        "Sec-Fetch-Mode":"cors",
        "Sec-Fetch-Site":"same-origin",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0",
        "X-Requested-With":"XMLHttpRequest"
    }
    json_data = {
        "bld":	"dbms/MDC/STAT/srt/MDCSTAT30001",
        "locale":	"ko_KR",
        "isuCd":	get_ticker(ticker), # "KR7086520004",
        "strtDd":	date_to_string(start, only_number=True),
        "endDd":    date_to_string(end, only_number=True),
        "share":"1",
        "money":"1",
        "csvxls_isNo":"false",
    }
    url_short = "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    try:
        response  = requests.post(url_short, headers=headers, data=json_data)
        data_list =  response.json().get('OutBlock_1')
        df = pandas.DataFrame(data_list)

        column_dict = {
            'TRD_DD':'date',
            'CVSRTSELL_TRDVOL':'value',
            'UPTICKRULE_APPL_TRDVOL':'value_uptick',
            'UPTICKRULE_EXCPT_TRDVOL':'value_except',
            'STR_CONST_VAL1':'value_const',
            'CVSRTSELL_TRDVAL':'valueprice',
            'UPTICKRULE_APPL_TRDVAL':'valueprice_uptick',
            'UPTICKRULE_EXCPT_TRDVAL':'valueprice_except',
            'STR_CONST_VAL2':'valueprice_const'
        }
        df = df.loc[:, list(column_dict.keys())]
        df = df.rename(columns=column_dict)
        df['date'] = df['date'].map(lambda x : x.replace('/','-'))
        df['date'] = df['date'].map(date_to_string)
        df['date'] = pandas.to_datetime(df['date'])
        df = df.sort_values(
            by="date", 
            ascending=True, # 오름차순 정렬
        ).reset_index(drop=True) 
        df = df.set_index('date')

        df = df_number_column(df, df.columns.tolist())
        df = df.rename(columns=column_dict)
        df = df.astype({_:'int32'  for _ in df.select_dtypes(numpy.float32).columns})
        df = df.astype({_:'int64'  for _ in df.select_dtypes(numpy.float64).columns})
        return df

    except Exception as e:
        print(e)
        return None



def get_short(
        start:str=None, 
        end:str=None, 
        ticker:str=None,  # ticker 코드
        freq:str='6ME',   # 6개월 단위로 수집
    ):

    r"""공매도 데이터 수집기
    > https://data.krx.co.kr/contents/MMC/SRTS/srts/MMCSRTS009.cmd
    Args:
        start : 수집기 시작일 
        end : 수집기 종료일
        ticker : krx ticker
        freq   : default(6ME) - 6개월 단위로 수집
    Return:
        pandas.DataFrame """

    # `freq` 단위로 기간 나누기
    time_steps = pandas.date_range(start, end, freq=freq).tolist()
    time_steps = [start] + time_steps + [end]
    dates = list(map(lambda x : date_to_string(x), time_steps))
    dates = pandas.to_datetime(dates) # 문자열 → datetime 변환

    # 구간 List[] 데이터를 수집 구간별 (start, end) 나누기
    intervals = []
    for i in range(0, len(dates) - 1):
        start = dates[i] if i == 0 else dates[i] + pandas.Timedelta(days=1)
        end = dates[i + 1]
        intervals.append((start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")))

    # 수집기 작동
    df_list = []
    for start, end in intervals:
        _df = get_short_function(start, end, ticker)
        time.sleep(.8) # Robot 차단기 방지기
        df_list.append(_df)

    df = pandas.concat(df_list)

    # None 값으로만 마지막 데이터가 구성되었을 때, 확인하는 함수
    _df_non    = df.sum(axis=1)
    index_list = _df_non[_df_non==0].index.tolist()
    index_list = [df.index.tolist().index(_index)  for _index in index_list]

    # 마지막 줄을 제외하는 함수
    if (len(df.index) -1) in index_list:
        df = df.iloc[:-1, :]
    return df


class Short(KrxWebIo):

    @property
    def bld(self):
        return "dbms/MDC/STAT/srt/MDCSTAT30001"

    def fetch(
            self, ticker:str,
            strtDd: str, 
            endDd: str,
            raw:bool = False
        ) -> pandas.DataFrame:

        result = self.read(
            isuCd = ticker,
            strtDd = strtDd, 
            endDd = endDd,
            share="1",
            money="1"
        )
        if raw:
            return result
        else:
            return pandas.DataFrame(result['output'])


def get_short_old(
        start:str=None, 
        end:str=None, 
        ticker:str=None,  # ticker 코드
        krx_code:str=None # krx 원본코드 ()
    ):
    r"""종목별 공매도 데이터
    Args:
        start  : '2020-01-01' 
        end    : '2025-12-31'
        ticker : krx ticker
        krx_code : krx ticker 고유번호 
    """

    ## Pre Processing : Params
    # ticker code -> krx full code 호출하기 (cache 파일활용)
    if krx_code is None:
        ticker_full = get_ticker(ticker)
    else:
        ticker_full = krx_code


    start, end = date_to_string(start), date_to_string(end)
    menu_url  = "http://data.krx.co.kr/contents"
    menu_url += "/MDC/MDI/mdiLoader/index.cmd?menuId"

    short = Short({
        "Referer":f"{menu_url}=MDC02030101"
    })
    df = short.fetch(
        ticker=ticker_full, 
        strtDd=start, 
        endDd=end
    )

    # Post Processing
    column_dict = {
        'TRD_DD':'date',
        'CVSRTSELL_TRDVOL':'value',
        'UPTICKRULE_APPL_TRDVOL':'value_uptick',
        'UPTICKRULE_EXCPT_TRDVOL':'value_except',
        'STR_CONST_VAL1':'value_const',
        'CVSRTSELL_TRDVAL':'valueprice',
        'UPTICKRULE_APPL_TRDVAL':'valueprice_uptick',
        'UPTICKRULE_EXCPT_TRDVAL':'valueprice_except',
        'STR_CONST_VAL2':'valueprice_const'
    }
    df = df_number_column(df, df.columns.tolist())
    return df

    column_dict = {
        'ISU_SRT_CD':'ticker',
        'TDD_OPNPRC':'open', 'TDD_HGPRC':'high','TDD_LWPRC':'low','TDD_CLSPRC':'close',
        'ACC_TRDVOL':'volume', 'LIST_SHRS':'shares',
        #'ISU_ABBRV':'name','MKT_NM':'market','ACC_TRDVAL':'volume_price','ISU_CD':'code_full',
        #'MKTCAP':'market_cap', 'FLUC_RT':'change','CMPPREVDD_PRC':'change_price', 
    }

    date = date_to_string(date)

    df = df.loc[:, list(column_dict.keys())]
    df = df.rename(columns=column_dict)
    df = df.set_index('ticker')
    df = df_number_column(df, df.columns.tolist())
    df = df.astype({_:'int32'  for _ in df.select_dtypes(numpy.float32).columns})
    df = df.astype({_:'int64'  for _ in df.select_dtypes(numpy.float64).columns})
    return df
