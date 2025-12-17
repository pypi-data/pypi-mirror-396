from .base import *
from ._krxio import KrxWebIo


class Ticker(KrxWebIo):

    @property
    def bld(self):
        return "dbms/comm/finder/finder_stkisu"

    def fetch(
            self, token:str=""
        ) -> pandas.DataFrame:

        result = self.read(
            locale="ko_KR",
            mktsel="ALL",
            typeNo="0",
            searchText=token,
        )
        return pandas.DataFrame(result['block1'])


def get_ticker(ticker:str=None):
    r"""ticker 변환정보 ticker 출력"""

    # 확장자가 없으면 `check_file` 에서 오류발생
    # working directory : Path 를 활용
    # folder_os = os.path.dirname(os.path.realpath(''))
    # print(f"Folder (Path) : {folder}\nFolder (os) : {folder_os}")
    file_path = "krx_pickle.pkl" # ".krx_pickle"
    folder    = str(Path().resolve())
    file_path = f"{folder}/{file_path}" # 작업폴더까지 경로명에 포함하기
    CHECK     = os.path.isfile(file_path)
    # print(f"File Path : {file_path}")

    # 수집한 날짜가 1일 이상 차이날때, 갱신작업 진행여부 확인하기
    if CHECK:
        date_now  = datetime.datetime.today()
        date_file = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        date_gap  = (date_now - date_file).days
        # print(f"Date Gap : {date_gap}")

        if date_gap > 1:
            CHECK = False

    if CHECK:
        # df = file_pickle(file_path, 'r')
        with open(file_path, 'rb') as f:
            df = pickle.load(f)

    else:
        menu_url  = "http://data.krx.co.kr/contents"
        menu_url += "/MDC/MDI/mdiLoader/index.cmd?menuId"
        ticker_instance = Ticker({
            "Referer":f"{menu_url}=MDC0201020201"
        })
        df = ticker_instance.fetch()
        # file_pickle(file_path, 'w', df)
        with open(file_path, 'wb') as f:
            pickle.dump(df, f, pickle.HIGHEST_PROTOCOL)
        print(f"ticker saved :: {file_path}")

    df = df.loc[:,['short_code','full_code']]
    code_dict = {_[0]:_[1]  for _ in df.to_dict('split')['data']}
    if ticker is not None: 
        return code_dict.get(ticker)
    else: 
        return code_dict
