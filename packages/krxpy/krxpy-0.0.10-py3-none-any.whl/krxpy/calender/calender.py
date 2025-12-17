from .base import *
user_agent = FakeAgent.random


class Calender:

    def __init__(self, date=None):
        self.url_koscom = "https://checkmall.koscom.co.kr/checkmall/checkCalendar/list.json"
        self.url_paxnet = "http://www.paxnet.co.kr/stock/infoStock/issueCalendarMonthAjax?scheduleDate="
        self.date = date_to_string(date).replace('-','')
        self.headers = {
            "Accept":"application/json, text/javascript, */*; q=0.01",
            "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent":user_agent, # "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "X-Requested-With":"XMLHttpRequest"
        }

    @property
    def koscom(self):
        r"""코스콤 증시일정"""
        data = {
            "disType":"m", "onDate":self.date, "searchWrd":"",
            "eventGroup":'[{"group":"G101","cls":""},{"group":"G102","cls":""},{"group":"G103","cls":""}]',
        }
        headers  = self.headers
        headers['Host'] = "checkmall.koscom.co.kr"
        headers["Origin"] = "https://checkmall.koscom.co.kr"
        headers["Referer"] = "https://checkmall.koscom.co.kr/checkmall/checkCalendar/view.do"

        response = requests.post(self.url_koscom, headers=self.headers, data=data)

        if response.status_code == 200:
            data = json.loads(response.text)['eventList']
            df   = pandas.DataFrame(data)
            df['eventDate'] = f'{self.date[:4]}/' + df['eventDate']
            df['eventDate'] = ["-".join(re.findall(r'[\d]+',_))   for _ in df['eventDate'].tolist()]
            df = df[~df.groupCd.isna()].reset_index(drop=True)

            # Post Processing ...
            df = df.loc[:,['eventDate','eventContent','groupNm','classNm']]
            df = df.rename(columns={
                'eventDate':'date','eventContent':'name','groupNm':'type','classNm':'class'})
            return df
        else:
            return None


    @property
    def holiday(self):
        # https://financedata.github.io/posts/pandas-market-days-krx.html
        r"""주식시장 휴장일 데이터
        (str) year : 휴장일 검색연도"""
        year = self.date[:4]
        # OPT 값 호출
        url_otp = "https://open.krx.co.kr/contents/COM/GenerateOTP.jspx"
        params  = {"bld":"MKD/01/0110/01100305/mkd01100305_01", "name":"form", "_":"1649824884457",}
        headers = {
            "Referer":"https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp",
            "User-Agent":user_agent }
        # OPT Coockie 를 포함한 Data 호출
        data = {
            "search_bas_yy":year, "gridTp":"KRX", "pageFirstCall":"Y",
            "pagePath":"/contents/MKD/01/0110/01100305/MKD01100305.jsp",
            "code":requests.get(url_otp, headers=headers, params=params).content }
        url = "https://open.krx.co.kr/contents/OPN/99/OPN99000001.jspx"
        response = requests.post(url, headers=headers, data=data).content.decode('utf-8')
        df = pandas.DataFrame(json.loads(response)['block1'])

        column_dict = {
            "calnd_dd_dy":'date',
            "holdy_nm":'name'}
        df = df.loc[:, list(column_dict.keys())].rename(columns=column_dict)
        df['date'] = pandas.DatetimeIndex(df['date'])
        df['date'] = list(map(lambda x : date_to_string(x), df["date"]))
        df['type'] = '휴장'
        return df


def holiday(date:str=None):
    r"""연간 증시휴장 캘린더
    date : ex)'2020-01-01' """
    return Calender(date).holiday


def info(date:str=None):
    r"""월간 증시 캘린더
    date : ex)'2020-01-01'
    :: `휴장` 정보는 `휴일 캘린더` 에서 활용위해 제거하기"""

    df = None
    calender  = Calender(date)
    df_list   = []

    # Koscom 증시일정 수집 및 필터링
    try:
        df = calender.koscom

        if len(df) > 0:

            # 국내 경제지표 필터링
            _df = df[df['type'].isin(['경제지표'])].reset_index(drop=True)
            index_df = list(_df[_df['class'].isin(['한국'])].index)
            _df.loc[index_df,'type'] = '경제지표(국내)'
            _df_nation = _df[_df['type'].isin(['경제지표(국내)'])].reset_index(drop=True)

            # 해외 경제지표 필터링
            _df_country = _df[_df['type'].isin(['경제지표'])].reset_index(drop=True)
            _df_country['name_new'] = _df_country['class'] + " - " + _df_country['name']
            del _df_country['name']
            _df_country = _df_country.rename(columns={'name_new':'name'})
            _df_country['type'] = '경제지표(국외)'
            _df_country = _df_country.loc[:, list(_df_nation.columns)]

            # 국내 국외 합치기
            _df_merge = pandas.concat([_df_nation, _df_country], axis=0)
            del _df_merge['class']

            # `선물옵션` 관련내용 필터링
            class_list = ['선물/옵션','K200옵션','주식선물','주식옵션','미니K200선물',
                '미니K200옵션', '코스닥150','변동성지수선물','USD선물','JPY선물','EUR선물']
            _df_trade = df[df['class'].isin(class_list)].reset_index(drop=True)
            _df_trade['type'] = '선물옵션'
            del _df_trade['class']
            df_koscom_new = pandas.concat([_df_merge, _df_trade], axis=0)
            df_koscom_new = df_koscom_new.sort_values('date').reset_index(drop=True)

            df_list.append(df_koscom_new)
            # df = pandas.concat([df, df_koscom_new], axis=0)

    except Exception as E:
        print(E)

    # Post Processing ...
    df = pandas.concat(df_list, axis=0)
    df = df.drop_duplicates(subset=['date','name']).sort_values('date')
    df = df[~df.type.isin(['휴장','스포츠'])].reset_index(drop=True)
    return df




    # @property
    # def paxnet(self):
    #     r"""팍스넷 증시일정"""

    #     url = f"{self.url_paxnet}{self.date[:6]}"
    #     headers = self.headers
    #     headers['Host'] = "www.paxnet.co.kr"
    #     headers["Referer"] = f"https://www.paxnet.co.kr/stock/infoStock/issueCalendarMonth?mainChk=Y&mainSendDate={self.date}"

    #     response = requests.get(url, headers=headers, verify = False)
    #     type_dict = {
    #         'FORIDC':'경제지표(국외)', 
    #         'FORISS':'경제일정(국외)',
    #         'FORSTK':'실적발표(국외)',
    #         'KORIDC':'경제지표(국내)', 
    #         'KORISS':'경제일정(국내)',
    #         'KORSTK':'실적발표(국내)',
    #         'ETCEVT':'경제일정(국내)', 
    #         'HOLIDT':'휴장', 
    #         'SPORTS':'스포츠',
    #         'OTHERS':'증시일정'
    #     }

    #     if response.status_code == 200:
    #         data = json.loads(response.text)
    #         df = pandas.DataFrame(data)
    #         df['scheduleDate'] = list(map(lambda x:date_to_string(x),  df['scheduleDate'].tolist()))
    #         columns = [_ for _ in df.columns   if df[_].unique().tolist() == ['']]
    #         df = df.drop(columns=columns)

    #         # Post Processing : 컬럼명 변경
    #         df = df.loc[:,['scheduleDate','title','categorySymbol']]
    #         df = df.rename(columns={'scheduleDate':'date','categorySymbol':'type','title':'name'})
    #         df['type'] = list(map(lambda x : type_dict[x], df['type'].tolist()))
    #         return df

    #     else:
    #         return None

    # # 팍스넷 수집 및 필터링
    # try:
    #     df = calender.paxnet

    #     if len(df) > 0:
    #         # Post Processing : type 내용 보완
    #         # 증시일정 Tab 중, `실적발표(국내)` 수정하기
    #         index = df[(df['type'] == '증시일정') & (df.name.str.contains('실적발표'))].index
    #         if len(index) > 0:
    #             df.loc[index,'type'] = '실적발표(국내)'

    #     df_list.append(df)
    # except Exception as E: 
    #     print(E)

