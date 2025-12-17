from .base import *


class HEADERS:
    r"""data.krx 수집을 위한 공통 데이터 생성"""
    
    def __new__(cls, *args):
        return super().__new__(cls)

    def __init__(self):
        self.data = self.set_data()
        self.headers = self.set_headers()
        self.url = 'http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd'
        self.column_krx_info = {'ISU_CD':'표준코드', 'ISU_SRT_CD':'단축코드', 'ISU_NM':'한글종목명', 
            'ISU_ABBRV':'한글종목약명','ISU_ENG_NM':'영문종목명', 'LIST_DD':'상장일','MKT_TP_NM':'시장구분',
            'SECUGRP_NM':'증권구분', 'SECT_TP_NM':'소속부','KIND_STKCERT_TP_NM':'주식종류',
            'PARVAL':'액면가','LIST_SHRS':'상장주식수'}
        
    def set_headers(self):
        r"""https://reqbin.com/req/python/gplpbyk6/get-request-like-mozilla-firefox
        mozilla firefox header setting"""
        headers = requests.structures.CaseInsensitiveDict()
        headers["Connection"] = "keep-alive"
        headers["Origin"] = "http://data.krx.co.kr"
        headers["Host"] = "data.krx.co.kr"
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0"
        headers["Accept"] = "application/json, text/javascript, */*; q=0.01"
        headers["Accept-Language"] = "en-US,en;q=0.5"
        headers["Accept-Encoding"] = "gzip, deflate"
        headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers["Content-Length"] = "88"
        headers["Pragma"] = "no-cache"
        headers["Cache-Control"] = "no-cache"
        return headers

    def set_data(self):
        data = {}
        data['share']="1"
        data['mktId']="ALL"
        data['locale']="ko_KR"
        data['csvxls_isNo']="false"
        data['bld']="dbms/MDC/STAT/standard/MDCSTAT01901"
        return data
