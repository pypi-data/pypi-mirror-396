from .base import *


# Input params 전처리 작업용
def date_to_string(
        date:any=None,
        datetime_obj:bool=False,
        only_number:bool=False,
        business_day:bool=False,
        time_delta:int=0,
    ):

    r"""date 객체를 string 으로 자동변환
    date        : 날짜객체
    datetime_obj : datetime 객체로 출력
    only_number  : 날짜 구분자 없이 숫자로만 출력 
    business_day : 주말 -> 해당 주차 평일로 변환
    time_delta   : 날짜에 Gap 추가 (+/-)
    """

    # Pre Processing
    _return = None
    token_list = ')월화수목금토일연월일년('
    
    # Main Processing : object to datetime
    if date is None:
        _return = datetime.date.today().isoformat()
    elif type(date) == datetime.date:
        _return = date.isoformat()
    elif type(date) == datetime.datetime:
        _return = date.date().isoformat()
    elif type(date) == pandas._libs.tslibs.timestamps.Timestamp:
        _return = str(date.to_pydatetime().date())
    elif type(date) == str:
        _check = "".join(re.findall(r'[\d]{8}', date))
        _check_re = re.findall(f'[,-//.{token_list}]', date)
        if len(_check) == 8:
            _return = f"{_check[:4]}-{_check[4:6]}-{_check[6:]}"

        elif len(_check_re) > 0:
            for punct_string in ['-','/',',', '.'] + list(token_list):
                if date.find(punct_string) != -1:
                    _date = list(map(
                        lambda x : (f'{x:0>2}'), date.split(punct_string)))
                    if len(_date[0]) == 2:
                        if int(_date[0]) < 50:
                            _date[0] = '20'+_date[0] # 연도가 50보다 작을 땐, 2000년대
                        else:
                            _date[0] = '19'+_date[0] # 연도가 50보다 클 땐, 2000년대
                    _return = "-".join(_date) 
                else:
                    pass

    # Post Processing
    # :: Output 형태에 따른 조건값 추가
    # datetime.datetime.strptime('09/19/22 13:55:26', '%m/%d/%y %H:%M:%S')
    assert _return is not None, f'TypeError : {date} 를 분석할 수 없습니다'
    ## 평일값으로 변환
    if business_day:
        _return = datetime.datetime.strptime(_return, '%Y-%m-%d').date()
        if (_return.weekday() - 4) > 0: # 주말일 때만 해당함수 적용
            _return = _return - datetime.timedelta(_return.weekday() - 4)
        _return = _return.isoformat()

    ## 숫자만 출력
    if only_number:
        _return = _return.replace('-','')

    ## timedelta 적용한 결과 값
    if time_delta != 0:
        _return = datetime.datetime.strptime(_return, '%Y-%m-%d').date()
        _return = _return + datetime.timedelta(days=time_delta)
        _return = _return.isoformat() # 문자열로 결과값 변환

    ## datetime Object 로 변환
    if datetime_obj:
        _return = datetime.datetime.strptime(_return, '%Y-%m-%d').date()

    return _return


# Date Range to Split
def split_date_range(start, end, freq='2Y'):
    r"""날짜구간 분할하기"""
    date_list_raw = pandas.date_range(start, end, freq=f'{freq}S')
    date_list_raw = list(map(lambda x : date_to_string(x), date_list_raw))
    date_list = [[_,
        date_to_string(
            date_to_string(date_list_raw[no+1], datetime_obj=True) - \
                datetime.timedelta(days=1)
        )
    ]  for no,_ in enumerate(date_list_raw[:-1])]
    date_list += [[date_list_raw[-1], end]]
    return date_list


# items to split lists
def divide_chunks(items:list=None, n:int=None):
    r"""Split items
    (list) items : 객체 나누기
    (int)  n : Number"""
    if type(items) == list:
        for i in range(0, len(items), n): # looping till length l
            yield items[i:i + n]          # list should have
    
    elif type(items) == dict:
        for i in range(0, len(items), n):
            yield dict(itertools.islice(items.items(), i ,i+n))


# 문자 난수생성 (비밀번호 생성기)
def password(length:int=12, not_punct=False) -> str:
    r"""난수문자 생성기 (ex> 비밀번호)
    length    : 생성문자 길이
    not_punct : 특수문자 비포함"""
    if not_punct == True:
        letters = string.ascii_letters + string.digits
    else:
        letters = string.ascii_letters + string.digits + "!#$%&*+-?@" # string.punctuation
    return "".join([random.choice(letters)  for _ in range(length)])


# 텍스트를 datetime 객체로 해석 (REGEX_DATETIME)
def string_to_datetime(text:str):
    r"""text -> datetime.str
    regex 추출값에 따라 `time regex format` 개별적용"""

    format = ''
    time_regex = REGEX_DATETIME
    for regex, time_string in time_regex.items():
        check = re.findall(regex, text)
        if len(check) > 0:
            format = time_string

    # regex 분석결과 없을 때, 원본 그대로 출력
    if format == '':
        return text
    return datetime.datetime.strptime(text, format)