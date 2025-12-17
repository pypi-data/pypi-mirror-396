from .base import *
# Market 프로젝트에서 새롭게 추가한 함수들


# @ Django 키워드 변경 : Market 
def convert_code_market(column:str):
    r"""column 데이터를 Market KeyWord 로 변경"""
    MARKET_DICT = {
        'KOSPI':'Y', 'KOSDAQ':'K', 'KOSDAQ GLOBAL':'K',
        'KONEX':'N',
        '거래소':'Y', '코스피':'Y', '코스닥':'K', '코넥스':'N'
    }
    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):
            df = function(*args, **kwargs)
            try:
                df[column] = list(map(lambda x : 
                    MARKET_DICT[x.strip()] if x.strip() in list(MARKET_DICT.keys())
                    else 'E', df[column]
                ))
                return df
            except Exception as E:
                print(E)
                return None

        return wrapper
    return decorator


# @ Django 키워드 변경 : Trader
def convert_invest_type(column:str):
    r"""column 데이터를 Market KeyWord 로 변경"""
    TYPE_DICT = { 
        "매수상위회원사":'B1', "매수상위이탈회원사":'B2',
        "매도상위회원사":'S1', "매도상위이탈회원사":'S2' 
    }
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            df = function(*args, **kwargs)
            df[column] = list(map(lambda x : 
                TYPE_DICT[x.strip()] if x.strip() in list(TYPE_DICT.keys())
                else 'E', df[column]
            ))
            return df
        return wrapper
    return decorator
