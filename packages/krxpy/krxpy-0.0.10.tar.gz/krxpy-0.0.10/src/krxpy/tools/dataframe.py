from .base import *


# @ KRX `기업정보`의 "한글종목명' 중복해결
def duplicate_name(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        df = function(*args, **kwargs)
        column_check  = "한글종목명"     # 중복이 발생한 컬럼명
        column_rename = "한글종목약명"   # 중복을 해결할 텍스트 원본 컬럼명
        items_duplicated = [k for k,v in dict(Counter(df[column_check])).items()  if v != 1]
        items_index = df[df[column_check].isin(items_duplicated)].index.tolist()

        for index in items_index:
            df.loc[index, column_check] = df.loc[index, column_rename]
        items_duplicated = [k for k,v in dict(Counter(df[column_check])).items()  if v != 1]
        return df
    return wrapper


# @ DataFrame 에서 NaT 을 `1900/1/1` 로 보간
def dataframe_fill_nat(column:str):
    r"""Pandas DataTime 의 1) NaT 필드를 채우고 2) 내림차순 정렬"""
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            df = function(*args, **kwargs)
            df[column] = pandas.to_datetime(df[column])
            df[column] = list(
                map(lambda x: pandas.to_datetime(datetime.date(1900,1,1)).date() if(pandas.isnull(x)) 
                        else x.date(), df[column]))
            df[column] = pandas.to_datetime(df[column])
            return df.sort_values(column, ascending=False).reset_index(drop=True)
        return wrapper
    return decorator


# @ DataFrame 필드값 `gap` 미만을 None 변환
def dataframe_blank_to_nan(gap:int=0):
    r""" DataFrame Column's blank to Numpy NaN
    :: blank_gap :: 2글자 미만은 NaN 으로 변환"""
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            df = function(*args, **kwargs)
            for column in df.columns[1:]:
                df[column] = list(map(
                    lambda x: x if(len(str(x).strip()) > gap)
                        else None, df[column].tolist()))
            return df
        return wrapper
    return decorator
