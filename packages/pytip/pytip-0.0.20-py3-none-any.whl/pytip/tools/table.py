from .base import *


def df_number_column(
        df          : pandas.DataFrame=None, 
        columns     : list=None, 
        except_list : list=['-','','.'],
        none_value  : any=numpy.nan,
    ):

    r"""DataFrame 데이터를, 숫자 데이터 int/float 으로 변경
    df (DataFrame)     : 작업할 DataFrame
    columns (list)     : 작업할 대상 Column list
    except_item (list) : NaN 으로 변환할 예외처리 값 `ex) '-', '' ...
    none_value (any)   : NaN 대신 입력할 데이터 값 default) Numpy.NaN"""
    
    # Removing thousand comma
    # Converting `int` or `float`
    # [ (조건 만족 시 출력값)  if 조건 else (조건 불만족 시 출력 값)  for i in data ]
    # isdigit() : `integer` 를 구분해서 True 출력하는 기본 메서드

    lambda_to_number = lambda x: x \
        if type(x) in [int, float] else int(x.replace(',','')) \
        if x.replace(',','').isdigit() else float(x.replace(',','')) \
        if x not in except_list + ['-','','.'] else none_value

    if len(columns) > 0:
        for column in columns:
            df[column]  = list(map(lambda_to_number, df[column].tolist()))

    # https://stackoverflow.com/questions/14162723/replacing-pandas-or-numpy-nan-with-a-none-to-use-with-mysqldb
    # https://stackoverflow.com/questions/59967429/convert-all-columns-from-int64-to-int32
    df = df.astype({_:'int32'  for _ in df.select_dtypes(numpy.int64).columns})
    df = df.astype({_:'float32'  for _ in df.select_dtypes(numpy.float64).columns})
    df = df.replace({numpy.nan: None})
    return df


def df_int(df):
    r"""int64 필드값을 int32 로 변경하기"""
    d = dict.fromkeys(df.select_dtypes(numpy.int64).columns, numpy.int32)
    df = df.astype(d)
    return df
