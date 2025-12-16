# 휴일 캘린더 수집기
from .base import *


# (월간) 천문 연구원 특일정보
# https://www.data.go.kr/iim/api/selectAPIAcountView.do
class Holiday():
    r"""(월간) 천문 연구원 특일정보
    https://www.data.go.kr/iim/api/selectAPIAcountView.do
    (int) year  : 연도
    (int) month : 월
    (type_name) 타입 : 국경일, 공휴일, 기념일, 24절기, 잡절"""

    def __init__(self, year:int=None, month:int=None, type_name:str="공휴일", raw=False):
        self.token = ''
        self.raw = raw
        self.key_name = "holiday"
        self.url_root = "http://apis.data.go.kr"
        self.url_base = '/B090041/openapi/service/SpcdeInfoService/'
        self.type_name = type_name
        self.year = year
        self.month = month
        self.info_dict = {
            "국경일":"getHoliDeInfo","공휴일":"getRestDeInfo","기념일":"getAnniversaryInfo",
            "24절기":"get24DivisionsInfo", "잡절":"getSundryDayInfo"
        }

    def __repr__(self) -> str:
        return f"{self.year}{self.month} .data : 개별 데이터, .data_total : 모든 휴일정보"

    @property
    def _get(self):
        today = datetime.datetime.today()
        if self.year is None: self.year = today.year
        if self.month is None: self.month = today.month
        query = {
            '_type': 'json',
            'numOfRows': '50',
            'solYear': int(self.year),
            'solMonth': f"{int(self.month):02d}",
            'ServiceKey': self.token
        }
        url_query = "".join([f"&{key}={value}"  for key, value in query.items()])
        url = self.url_root + self.url_base + self.info_dict[self.type_name] + "?" + url_query
        assert self.type_name in list(self.info_dict.keys()),\
            f"`type_name` = {list(self.info_dict.keys())} 중 하나를 입력하세요"
        try:
            return requests.get(url).json()
        except:
            print(f"Response : {requests.get(url)}")
            return None

    @property
    def data(self):
        response = self._get
        if response is None:
            return None

        items = response.get('response').get('body').get('items')
        if items != "":
            data = response.get('response').get('body').get('items').get('item')
            # 결과값이 1개일 때, (x)Array (o)Object : Array 1개로 변환하기
            if type(data) == dict:
                data = [data]
            data = pandas.DataFrame(data)
            date_lambda = lambda x : datetime.datetime.strptime(str(x), '%Y%m%d')
            data['locdate'] = list(map(date_lambda, data['locdate']))
            return data
        return None

    @property
    def data_total(self):
        items = []
        for _ in '국경일,공휴일,24절기,잡절'.split(','): # 기념일,
            self.type_name = _
            _data = self.data
            if _data is not None:
                items.append(_data)
        df = pandas.concat(items).sort_values('locdate').drop_duplicates()
        if self.raw:
            return df
        return df.fillna('').loc[:,['locdate','dateName','isHoliday']]