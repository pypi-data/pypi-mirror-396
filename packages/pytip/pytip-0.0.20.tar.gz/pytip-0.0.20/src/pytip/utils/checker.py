from .base import *


def check_ip(url='https://api.ipify.org?format=json'):

    r"""인터넷 접속확인
    Args:
        url (str, optional): ip 주소 확인용 서비스
    Return:
        str: 외부 ip 주소 (오류시 내부 IP 주소)"""

    response = request.urlopen(url).read()

    try:
        response = json.loads(response)
        return response['ip']

    except Exception as E:
        print(termcolor.colored(E, 'red'))
        return request.META.get('REMOTE_ADDR')


# 파일 생성내용 확인
# https://www.python-engineer.com/posts/check-if-file-exists/
def check_file(file_path:str=None, days:int=1, display=False):
    r"""경로폴더 및 파일확인 : 동일날짜 생성시 확인
    file_path  : `./data/backup/file.pkl`
    days (int) : 파일 생성일 간격날짜 """
    # params
    foler_path_list = file_path.split('/')
    folders, _file  = foler_path_list[:-1], foler_path_list[-1]
    folders = list(filter(lambda x : x !=".", folders))

    # folder depth : 다중 폴더 확인 및 생성
    path_start = os.getcwd()
    for folder in folders:
        if os.path.isdir(folder) == False:
            print(f"{folder} Created")
            os.mkdir(folder)
        os.chdir(folder)
    os.chdir(path_start)

    # check exists file
    if os.path.exists(file_path) == True:
        date_now  = datetime.datetime.today()
        date_file = datetime.datetime.fromtimestamp(os.path.getatime(file_path))
        date_gap  = (date_now - date_file).days
        if days > date_gap:
            return True
        else:
            return False
            # if display:
            #     message  = f"Now  : {date_now}\nFile : "
            #     message += f"{date_file}\nDate Gap : {date_gap}"
            #     print(message)
    return False


# # 패키지 설치여부 확인
# def pkg_missed(pkgs:list):
#     r"""missing pkg checker -> list"""
#     if type(pkgs) == str: 
#         pkgs = [pkgs]
#     required  = set(pkgs)
#     installed = {pkg.key for pkg in pkg_resources.working_set}
#     missing   = required - installed
#     return list(missing)


# 터미널 메세지 출력기
# http://www.dreamy.pe.kr/zbxe/CodeClip/165424
class Message:

    r"""Text Message Color"""
    # grey, red, green, yellow, blue, magenta, cyan, white
    def __repr__(self): 
        return """Text 내용을 상황별 칼라로 출력\n[process, done, alert, warning]"""

    def __new__(cls, text:str=''):
        cls.text = text
        return super().__new__(cls)

    @property
    def process(self):
        text = "<"*3 + "  " + self.text + "  " + "<"*5
        termcolor.cprint(self.text, 'magenta')

    @property
    def done(self):
        text = ">"*10 + "  " + self.text + "  " + "<"*10
        termcolor.cprint(text, 'cyan')

    @property
    def alert(self):
        text = "!"*5 + "  " + self.text + "  " + "!"*5
        termcolor.cprint(text, 'red')

    @property
    def warning(self):
        text = "!"*3 + "  " + self.text + "  " + "."*3
        termcolor.cprint(text, 'grey')

