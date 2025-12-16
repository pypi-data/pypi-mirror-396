from .base import *
from ._tools import df_number_column
from ._krxio import KrxWebIo
from .ticker import get_ticker


# 투자자 매매 데이터
class Investor(KrxWebIo):

    @property
    def bld(self):
        return "dbms/MDC/STAT/standard/MDCSTAT02303"

    def fetch(
            self, ticker:str,
            strtDd: str, endDd: str, askBid: int
        ) -> pandas.DataFrame:

        result = self.read(
            isuCd = ticker,
            strtDd = strtDd, endDd = endDd,
            askBid = askBid, detailView = 1, 
            trdVolVal=1, share="1",
        )
        return pandas.DataFrame(result['output'])


def get_invest(
        start:str=None, end:str=None, 
        ticker:str=None, askBid:int='순매매', 
        krx_code:str=None
    ):

    r"""투자자별 매매현황 데이터
    start  : '2020-01-01' 
    end    : '2021-01-01'
    ticker : '005930'
    askBid : 매도, 매수, 순매매
    krx full : krx ticker 고유번호 직접입력 """

    ## Pre Processing : Params
    # ticker code -> krx full code 호출하기 (cache 파일활용)
    # `krx full`
    if krx_code is None:
        ticker_full = get_ticker(ticker)
    else:
        ticker_full = krx_code

    # 크롤링에 필요한 Web 파라미터 정보 & 후가공 정보
    column_dict = {"TRD_DD":"날짜", "TRDVAL_TOT":'총합',\
        'TRDVAL1':'금융투자', 'TRDVAL2':'보험', 'TRDVAL3':'투신',\
        'TRDVAL4':'사모', 'TRDVAL5':'은행', 'TRDVAL6':'기타금융','TRDVAL7':'연기금',\
        'TRDVAL8':'기타법인', 'TRDVAL9':'개인', 'TRDVAL10':'외국인', 'TRDVAL11':'기타외국인'
    }
    start, end = date_to_string(start), date_to_string(end)
    menu_url  = "http://data.krx.co.kr/contents"
    menu_url += "/MDC/MDI/mdiLoader/index.cmd?menuId"

    # 크롤링에 필요한 Json 정보 호출하기
    invest = Investor({
        "Referer":f"{menu_url}=MDC0201020301"
    })

    askbid_list = ['매도','매수','순매매']
    askBid_dict = {_:no+1  for no,_ in enumerate(askbid_list)}
    askBid      = askBid_dict.get(askBid)

    ## Main Processing : Crawling ...
    df = invest.fetch(
        ticker=ticker_full, 
        strtDd=start, endDd=end, 
        askBid=askBid
    )

    ## Post Processing ...
    if len(df) > 0:
        df = df_number_column(df, df.columns.tolist()[1:])
        df = df.rename(columns=column_dict)
        df = df.astype({_:'int32'  for _ in df.select_dtypes(numpy.float32).columns})
        df = df.astype({_:'int64'  for _ in df.select_dtypes(numpy.float64).columns})
        df['날짜'] = df['날짜'].map(lambda x : date_to_string(x))
        df = df.set_index('날짜')
        return df
    return None
