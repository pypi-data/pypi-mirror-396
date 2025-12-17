from .base import *
import requests
from pytip import FakeAgent


def get_shinhan(
        ticker:str=None,
        start:str=None, end:str=None,
        flavor='lxml', display=True
    ):
    r"""신한증권 데이터로 투자자 매매데이터 수집기
    ticker (str) : 005930
    start  (str) : 시작날짜 
    end    (str) : 종료날짜
    flavor       : 'lxml'(default) 
    display(bool): True - 작업 진행과정 출력하기    
    """

    # http://open.shinhaninvest.com/goodicyber/mk/1206.jsp?code=005930'
    url = f"https://open.shinhansec.com/goodicyber/mk/1206.jsp?code={ticker}"
    headers = {"User-Agent":FakeAgent.random}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            response_io = StringIO(response.text)
            df = pandas.read_html(response_io, flavor=flavor)[-1]
            ## Post Processing
            # `날짜` 컬럼찾기 및 테이블 재조정 하기
            for no,_ in enumerate(df[0]):
                if _ != '날짜':
                    break

            df_new = df.iloc[no:,:]
            df_new.columns = df.iloc[no-1,:].tolist()
            df_new = df_new.set_index('날짜')
            df_new.index = pandas.to_datetime(df_new.index)
            df_new = df_new.apply(pandas.to_numeric)

            ## Append Data : 보여지지 않은 데이터 연산으로 추출하기
            # '기관계' 데이터를 근거로 '사모' 와 '기타외국인' 추출하기
            df_new = df_new.rename(columns={
                '외국인계':'외국인','증권':'금융투자','종금':'기타금융',
                '기금':'연기금','기타':'기타법인'
            })
            df_new = df_new.loc[:,[
                '기관계','금융투자','보험','투신','은행',
                '기타금융','연기금','기타법인','개인','외국인'
            ]]

            # 사모펀드 데이터 추출하기
            samo = [
                df_new.iloc[_,0] - df_new.iloc[_,1:7].sum()    
                for _ in range(len(df_new))
            ]
            df_new.insert(4, '사모', samo)
            del df_new['기관계']

            # 기타외국인 데이터 추출하기
            etc_f = [
                (df_new.iloc[_,:].sum() * (-1))    
                for _ in range(len(df_new))
            ]
            df_new.insert(10, '기타외국인', etc_f)
            _data = [df_new.iloc[idx,:].sum()  for idx in range(len(df_new))]
            df_new.insert(11,'총합', _data)

            ## Post Processing ...
            # 날짜를 기준으로 필터링 하기
            df_new = df_new[::-1]
            return df_new.loc[start:end, :][::-1]

        except Exception as E:
            if display:
                print(f"{ticker} has Error : {E}")
            pass
    return None
