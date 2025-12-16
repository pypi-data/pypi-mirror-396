from .base import *


# MultiProcess
def multiprocess_items(funcion, items:int, worker:list, display=False):
    r"""list() 데이터를  function 에 multiprocessing 반복적용
    function : 반복적용할 함수
    items    : function 에 입력할 데이터"""

    with Pool(worker) as pool:
        if display:
            items = list(tqdm(pool.imap(funcion, items), total=len(items)))
        else:
            items = pool.map(funcion, items)
        return items


# http://taewan.kim/tip/python_pickle/
def file_pickle(
        file_path:str=None,
        option='w', 
        data=None,
        exist=False,
        display=True,
    ):
    r"""파이썬 객체를 Pickle 로 저장하고 호출
    file (str)   : 파일이름
    option (str) : w,r (Write / Read)
    data (any)   : pickle 로 저장할 변수
    exist (bool) : 해당 파일이 있으면 저장
    """

    assert option in ['w', 'r'], f"`option` 은 `w`,`r` 하나를 입력하세요."
    if (option == 'w') & (data is None):
        return None

    option = {'w':'wb', 'r':'rb'}[option]
    with open(file_path, option) as f:
        if option == 'wb': # 저장하기
            if data is None:
                return None
            else:
                assert data is not None, f"{data} 값을 저장 할 수 없습니다."
                pickle.dump(data, f)
                if display:
                    print(f"{file_path} saving done.")
                return None

        elif option == 'rb':
            assert data is None, f"불러오는 경우, {data}는 필요 없습니다."
            return pickle.load(f)


# requests with `multiprocessing``
class RequestsMultiprocess():
    r"""multiprocessing 을 활용한 requests 의 Get 크롤링
    (int) worker : 수집 process worker 갯수를 정의"""

    session = None

    def __init__(self, worker=4):
        self.worker = worker

    def _session(self): # https://wikidocs.net/13945 : hasattr() 변수내 맴버 확인
        if not self.session:
            self.session = requests.Session()
        return self.session

    def _response(self, url:str=None):
        headers: dict = {}
        headers["Content-Type"] = "application/json; charset=utf-8"
        headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
        session = self._session()
        try:
            with session.get(url, headers=headers) as response:
                return response
        except:
            return url

    def _multi_response(self, sites:list=None, display=True) -> list:
        r"""multiprocessing 을 활용한 크롤링
        (list) sites   : 사이트 url list() 목록
        (bool) display : tqdm 을 활용한 Progress bar 표시여부
        :: return :: `requests` response item list"""
        items = None
        assert type(sites) == list, "sites 는 list 목록을 입력해야 합니다."

        max_cpu = multiprocessing.cpu_count()
        assert self.worker < max_cpu, f"활용 가능한 worker 갯수는 {max_cpu} 입니다"
        start_time = time.time()

        with multiprocessing.Pool(initializer=self._session, processes=self.worker) as pool:
            if display:
                items = list(tqdm(pool.imap(self._response, sites), total=len(sites)))
            else:
                items = pool.map(self._response, sites)

        # time check
        duration = time.time() - start_time
        duration_minute = duration // 60
        if duration_minute == 0:
            print(f"Response {len(sites)} in {round(duration, 3)} seconds")
        else:
            duration_second = duration % 60
            print(f"Response {len(sites)} in {duration_minute} minute {round(duration_second, 3)} seconds")
        return items

