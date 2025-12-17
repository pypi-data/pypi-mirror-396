from .base import *
from ._tools import df_number_column
from ._krxio import KrxWebIo
from .ticker import get_ticker


# 투자자 매매 데이터
class Foreign(KrxWebIo):

    @property
    def bld(self):
        return "dbms/MDC/STAT/standard/MDCSTAT03701"

    def fetch(
            self, date: str
        ) -> pandas.DataFrame:

        result = self.read(
            trdDd = date,
            mktId = "ALL",
            csvxls_isNo = False, 
            share = "1",
        )

        # print(f"CURRENT_DATETIME: {result['CURRENT_DATETIME']}")
        return pandas.DataFrame(result['output'])


def get_foreign(date:str=None):

    r"""투자자별 매매현황 데이터
    date  : '2020-01-01' """

    ## Pre Processing : Params
    # 크롤링에 필요한 Web 파라미터 정보 & 후가공 정보
    column_eng = ["ISU_SRT_CD","ISU_ABBRV","TDD_CLSPRC","FLUC_TP_CD","CMPPREVDD_PRC","FLUC_RT","LIST_SHRS","FORN_HD_QTY","FORN_SHR_RT","FORN_ORD_LMT_QTY","FORN_LMT_EXHST_RT"]
    column_kor = ["종목코드","종목명","종가","변동구분","가격변동","등락률","상장주식수","외국인 보유수량","외국인 지분율","외국인 한도수량","외국인 한도소진율"]
    column_dict = {eng:kor for eng,kor in zip(column_eng, column_kor)}

    # Referer URI 주소값
    menu_url  = "https://data.krx.co.kr/contents"
    menu_url += "/MDC/MDI/mdiLoader/index.cmd?menuId"
    date = date_to_string(date, only_number=True)
    data_uri = Foreign({
        "Referer":f"{menu_url}=MDC0201"
    })


    ## Main Processing : Crawling ...
    df = data_uri.fetch(
        date = date
    )

    ## Post Processing ...
    if len(df) > 0:
        df = df_number_column(df, df.columns.tolist()[2:])
        df = df.rename(columns=column_dict)
        # df = df.astype({_:'int32'  for _ in df.select_dtypes(numpy.float32).columns})
        # df = df.astype({_:'int64'  for _ in df.select_dtypes(numpy.float64).columns})
        # df['날짜'] = df['날짜'].map(lambda x : date_to_string(x))
        df = df.drop('종목명', axis=1).set_index('종목코드')
        return df
    return None
