from .base import *


class Excel:

    r"""다중 Sheet 를 갖는 Excel 파일 데이터 불러오기
    filepath : 엑셀파일
    @files -> (list) :: 폴더내 파일 가져오기
    @names -> (list) :: sheet 이름목록
    @sheet -> (DataFrame) """

    def __init__(self, file:str):
        self.file = file
        self.token = re.compile(".xls[x]?")
        self.except_list = [None, '  ', ' ', '', '-', '.', ',']

    def __repr__(self) -> str:
        return 'Openpyxl Excel by worksheet'

    @property
    def _check_xls(self):
        r"""xls 확장자 확인"""
        name = "".join(self.token.findall(self.file)).replace('.','')
        if name == 'xls': 
            return True
        else: return False

    @property
    def names(self) -> list:
        r"""Excel WorkSheet 목록 가져오기"""
        return pandas.ExcelFile(self.file).sheet_names
        # if self._check_xls:
        #     wb = xlrd.open_workbook_xls(self.file)
        #     return wb.sheet_names()
        # else:
        #     wb = openpyxl.load_workbook(self.file)
        #     return wb.sheetnames

    def sheet(self, name=None, header:int=None):
        r"""시트 데이터 가져오기
        wb = openpyxl.load_workbook(self.file)
        df = pandas.DataFrame(wb[name].values)        
        """
        if name:
            df = pandas.read_excel(self.file, sheet_name=name)
        else:
            df = pandas.read_excel(self.file)
        # Column (Unnamed:숫자) 를 숫자로 변환 
        _map = map(lambda x : x , range(df.shape[1]))
        df.columns = list(_map) 
        return df.replace(to_replace=self.except_list, value=numpy.NaN)
