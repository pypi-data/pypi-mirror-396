# 상장폐지종목 조회
from .base import *
from ._krxio import KrxWebIo

# 상장폐지 기업내용

class DeList(KrxWebIo):

    @property
    def bld(self):
        return "dbms/MDC/STAT/issue/MDCSTAT23801"

    def fetch(
            self, strtDd: str, endDd: str
        ) -> pandas.DataFrame:

        result = self.read(
            mktId = "ALL",
            isuCd = "ALL",
            strtDd = strtDd, 
            endDd = endDd,
            share="1",
            # trdVolVal=1, 
            # askBid = askBid,
            # detailView = 1,
        )
        return pandas.DataFrame(result['output'])


@convert_code_market(column="시장구분") 
def get_de_list(start:str=None, end:str=None):
    r"""기간내 상장폐지 종목조회
    start  : '2020-01-01' 
    end    : '2021-01-01' """

    ## Pre Processing : Params
    # ticker code -> krx full code 호출하기 (cache 파일활용)
    start, end = date_to_string(start), date_to_string(end)
    menu_url  = "http://data.krx.co.kr/contents"
    menu_url += "/MDC/MDI/mdiLoader/index.cmd?menuId"
    # 크롤링에 필요한 Json 정보 호출하기
    invest = DeList({
        "Referer":f"{menu_url}=MDC02021301"
    })

    ## Main Processing : Crawling ...
    # 크롤링에 필요한 Web 파라미터 정보 & 후가공 정보
    column_dict = { # 컬럼명 한글로 변경
        "ISU_CD": "종목코드",
        "ISU_NM": "종목명",
        "MKT_NM": "시장구분",
        "SECUGRP_NM": "증권구분",
        "KIND_STKCERT_TP_NM": "주식종류",
        "LIST_DD": "상장일",
        "DELIST_DD": "폐지일",
        "DELIST_RSN_DSC": "폐지사유",
        "IDX_IND_NM": "업종명",
        "PARVAL": "액면가",
        "LIST_SHRS": "상장주식수",
    }
    try:
        df = invest.fetch(
            strtDd=start, endDd=end, 
        ).loc[:, column_dict.keys()].rename(columns=column_dict)
        return df
    except Exception as E:
        print(E)
        return None
