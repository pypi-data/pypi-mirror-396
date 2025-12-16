from .base import *


# KOSCOM, KRX 캘린더 데이터
class Calender:

    r"""KOSCOM, KRX 캘린더 데이터
    [KRX (연간)] https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp
    [KOSCOM (월간)] https://datamall.koscom.co.kr/kor/checkCalendar/view.do?menuNo=200085
    (str) name  : `KRX, KOSCOM` 캘린더 출처
    (int) year  : 캘린더 검색할 연도
    (int) month : 캘린더 검색할 월"""

    def __init__(self, year:str=None):
        self.year = year
        self.url_krx = "https://open.krx.co.kr/contents/OPN/99/OPN99000001.jspx"
        self.column_dict_krx = {"calnd_dd_dy":'date',"holdy_nm":'content'}
        self.headers = {
            "Referer":"https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp",
            "User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        }

    @property
    def _opt(self):
        r"""KRX 데이터 호출을 위한 OPT 데이터 수집기"""
        url = "https://open.krx.co.kr/contents/COM/GenerateOTP.jspx"
        params = {"bld":"MKD/01/0110/01100305/mkd01100305_01", "name":"form", "_":"1649824884457",}
        return requests.get(url, headers=self.headers, params=params).content

    @property
    def df(self):
        r"""휴장일 데이터 수집기"""
        if self.year == None: self.year = datetime.date.today().strftime('%Y')
        else: self.year = f'{str(self.year):0>2}'
        data = {"search_bas_yy":self.year, "gridTp":"KRX", "pageFirstCall":"Y",
            "pagePath":"/contents/MKD/01/0110/01100305/MKD01100305.jsp","code":self._opt}
        response = requests.post(self.url_krx, headers=self.headers, data=data).json()
        r"""수집 데이터를 DataFrame 으로 변환 및 `self.column_dict` 기준으로 필터링"""
        df = pandas.DataFrame(response['block1'])
        df = df.loc[:,['calnd_dd','holdy_nm']].rename(columns={
            'calnd_dd':'locdate', 'holdy_nm':'dateName'})
        df['isHoliday'] = 'Y'
        df['locdate'] = pandas.DatetimeIndex(df['locdate'])
        return df
