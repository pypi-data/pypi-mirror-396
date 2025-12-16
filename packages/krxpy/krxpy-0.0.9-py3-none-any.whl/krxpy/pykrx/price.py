from .base import *
from ._krxio import KrxWebIo
from .ticker import get_ticker
from ._tools import df_number_column


class Price(KrxWebIo):

    @property
    def bld(self):
        return "dbms/MDC/STAT/standard/MDCSTAT01501"

    def fetch(self, date:str) -> pandas.DataFrame:

        result = self.read(
            mktId = "ALL",
            trdDd = date.replace('-',''),
            share=1, money="1",
        )
        return pandas.DataFrame(result['OutBlock_1'])


def get_price(date:str=None):
    r"""전종목 가격정보 : 20분 지연"""

    menu_url  = "http://data.krx.co.kr/contents"
    menu_url += "/MDC/MDI/mdiLoader/index.cmd?menuId"
    price = Price({
        "Referer":f"{menu_url}=MDC0201020101"
    })
    column_dict = {
        'ISU_SRT_CD':'ticker',
        'TDD_OPNPRC':'open', 'TDD_HGPRC':'high','TDD_LWPRC':'low','TDD_CLSPRC':'close',
        'ACC_TRDVOL':'volume', 'LIST_SHRS':'shares',
        #'ISU_ABBRV':'name','MKT_NM':'market','ACC_TRDVAL':'volume_price','ISU_CD':'code_full',
        #'MKTCAP':'market_cap', 'FLUC_RT':'change','CMPPREVDD_PRC':'change_price', 
    }

    date = date_to_string(date)
    df = price.fetch(date=date)

    df = df.loc[:, list(column_dict.keys())]
    df = df.rename(columns=column_dict)
    df = df.set_index('ticker')
    df = df_number_column(df, df.columns.tolist())
    df = df.astype({_:'int32'  for _ in df.select_dtypes(numpy.float32).columns})
    df = df.astype({_:'int64'  for _ in df.select_dtypes(numpy.float64).columns})
    return df
