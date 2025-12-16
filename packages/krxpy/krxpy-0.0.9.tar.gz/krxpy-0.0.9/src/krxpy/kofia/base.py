# 데이터 호출용 파라미터 생성 공용 클래스
import re
import numpy
import pandas
import requests
import datetime
from urllib.parse import urlparse, urlencode


class Header:

    r"""웹사이트 수집을 위한 공용 Header
    - `_now_date()`    : 현재 날짜 생성
    - `_date_string()` : 날짜 텍스트 유효성 검사
    - `_df_number()`   : thousand Comma 및 `-` 등 공백문자 예외처리"""

    def _now_date(self):
        r"""Bussiness Day 를 기준으로 `현재일자` 생성"""
        datetime_now = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
        day_check = datetime_now.weekday() - 4
        if day_check > 0:
            datetime_now = datetime_now - datetime.timedelta(day_check)
            datetime_now = datetime_now.replace(hour=15, minute=30, second=0)
        return datetime_now


    def _date_string(self, string:str = None):

        r"""`2022-1-2` -> `20220102` 날짜 텍스트 변환기
        string : 날짜 텍스트, 숫자형태 입력도 가능"""

        if string != None:
            string = str(string)
            for punct_string in ['-','/',',']:
                if string.find(punct_string) != -1:
                    string = "".join(list(map(lambda x : (f'{x:0>2}'), string.split(punct_string))))
                    assert "".join(re.findall(r'[\d]+', string)) == string, "string 은 숫자만 가능합니다"
                    assert len(string) == 8, "ex) 20221112 형태로 다시 입력해 주세요"
        return string


    def _df_number(self, 
            df:pandas.DataFrame=None, 
            except_column:list=[],
            except_item:list=[], 
        ) -> pandas.DataFrame:

        r"""DataFrame 데이터를, 숫자 데이터 int/float 으로 변경
        (DataFrame) df : 작업할 DataFrame
        (list) except_column : 작업에서 제외할 컬럼
        (list) except_item   : NaN 으로 변환할 대상 `ex) '-', '' ..."""

        token_regex      = r'^[-]{0,1}[(\d){1,3}]*[.\d]*$'
        number_lambda    = lambda x : x == "".join(re.findall(token_regex, x))
        assert df is not None, "변환작업을 진행할 `DataFrame` 이 없습니다."

        ## Pre Processing
        # 1 object 필드만 대상으로 진행
        column_names = [_ for _ in df.columns  if str(df[_].dtype) == 'object' ]

        # 2 숫자 데이터 정수 또는 실수로 구성된 컬럼 찾기
        column_names = [column  for column in column_names 
            if len(df[column]) == sum(list(map(number_lambda, df[column]))) # if 정규식을 활용한 컬럼 필터링
            if column not in except_column]                                 # if 사용자 컬럼 필터링

        # 3 숫자로 구성된 날짜 데이터 컬럼 중 `날짜 데이터` 는 예외 목록으로 추가하기
        # check 1 : 동일한 길이를 갖는가?
        # check 2 : regex 판단시 해당 데이터가 날짜 데이터 형식인가?
        for column in column_names:
            check_items_list = df[column].tolist()

            # check 1
            items_length = map(lambda x : len(x), list(set(check_items_list)))
            items_length = len(set(list(items_length)))

            if items_length < 4:
                # check 2
                token_regex_date = r'[\d]{2,4}[-./\//]{0,1}[\d]{1,2}[-./\//]{0,1}[\d]{1,2}[-./\//]{0,1}[\d]{1,2}'
                date_check_lambda = lambda x : len("".join(re.findall(token_regex_date, x))) > 0

                if len(check_items_list) == sum(list(map(date_check_lambda, check_items_list))):
                    except_item.append(column)
                    column_names = [_  for _ in column_names  if _ not in except_item]

        ## Main Process : float / int 로 변경
        # 필터링 결과 중 numpy.NaN 으로 처리될 데이터 필터링 및 작업
        except_item_list = ['-', '', ' '] + except_item  # NaN 으로 변환 적용할 데이터

        # Removing thousand comma
        # Converting `int` or `float`
        lambda_to_number = lambda x: int(x.replace(',','')) if x.replace(',','').isdigit() \
            else float(x.replace(',','')) if x not in except_item_list else numpy.nan

        if len(column_names) > 0:
            for column in column_names:
                df[column]  = list(map(lambda_to_number, df[column].tolist()))
        return df


    def _to_number(self, df:pandas.DataFrame=None, column_list:list=[], except_list:list=[]):
        r"""DataFrame 의 컬럼 숫자로 변경작업 강제로 진행
        (DataFrame)      df : 작업을 위한 DataFrame
        (list)  column_list : 컬럼명
        (list)  except_list : 숫자변환 제외 데이터로 NaN 으로 변경"""

        except_item_list = ['-', ''] + except_list  # NaN 으로 변환 적용할 데이터
        lambda_to_number = lambda x: int(x.replace(',','')) if x.replace(',','').isdigit() \
            else float(x.replace(',','')) if x not in except_item_list else numpy.nan

        # column list - 
        for column in column_list:
            df[column]  = list(map(lambda_to_number, df[column].tolist()))
        return df
