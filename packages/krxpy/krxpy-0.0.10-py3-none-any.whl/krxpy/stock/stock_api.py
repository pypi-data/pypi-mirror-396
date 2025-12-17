from ._headers import HEADERS as KRX_HEADERS
from .base import *
instance = KRX_HEADERS()


# KRX Info Params
def krx_params():
    r"""파라미터값 출력하기"""
    referer = "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201010101"
    HEADER = instance.headers
    HEADER["Referer"] = referer
    params = {
        "url":instance.url, 
        "headers":HEADER, 
        "data":instance.data,
        "timeout":10,
    }
    return params



@duplicate_name
@convert_code_market(column="시장구분")
@dataframe_fill_nat(column="상장일")
def krx_post_process(df):
    # columns 한글로 변경
    df.columns = list(map(lambda x : instance.column_krx_info[x], df.columns))
    # "액면가", "상장주식수" 컬럼의 데이터 "integer" 변환
    tokenizer = re.compile('[.A-zㄱ-힣]+')
    for column_name in ["액면가", "상장주식수"]:

        df[column_name] = list(map(
            lambda x : '1' if(len("".join(tokenizer.findall(x)))>0) else x,
            df[column_name]))

        df[column_name] = list(map(
            lambda x : int(x.replace(',','')) , df[column_name]))
    return df


@elapsed_time
def info_krx():

    r"""전종목 기업정보"""

    # Ready
    df = None
    params = krx_params()

    # Crawling
    response = requests.post(**params)
    # if response.status_code != 200:
    #     print(f'response status : {response.status_code}'); 
    #     return None
    response = response.json()

    # Post Processing
    # : json to DataFrame
    if response.get('OutBlock_1') is not None:
        df = pandas.DataFrame(response['OutBlock_1'])
        df = krx_post_process(df)
    
    # : Yahoo Finance 의 ticker 값 덧붙이기
    if df is not None:
        df['상장일'] = df['상장일'].map(lambda x :date_to_string(x))

        # Yahoo Finance 
        df['yahoo'] = df['단축코드'] + df['시장구분'].map(
            lambda x : {'K':'.KQ','Y':'.KS','N':'None'}.get(x)
        )
        index_list = df[df['yahoo'].str.contains('None')].index.tolist()
        df.loc[index_list, 'yahoo'] = None

    return df


# @elapsed_time
# def info_krx_tor(port=9050):    
#     r"""전종목 기업정보
#     tor : Tor Browser 의 Proxy 활용"""
#     proxies = {
#         'http': f'socks5h://127.0.0.1:{port}',
#         'https': f'socks5h://127.0.0.1:{port}'
#     }
#     socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", port)
#     socket.socket = socks.socksocket
#     params   = krx_params()
#     response = requests.post(**params)
#     if response.status_code != 200:
#         print(f'response status : {response.status_code}'); 
#         time.sleep(4)
#         return None

#     response = response.json()
#     if response.get('OutBlock_1') is not None:
#         df = pandas.DataFrame(response['OutBlock_1'])
#         df = krx_post_process(df)
#         df['상장일'] = list(map(lambda x :date_to_string(x), df['상장일']))
#         return df
#     else:
#         return None
