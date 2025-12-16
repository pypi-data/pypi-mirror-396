# # https://wikidiff.com/utility/tool
# # `utility` is a program designed to perform a single or a small range of tasks
# # `tool` is A mechanical device intended to make a task easier.

# # utility : 독립적 프로그램
# # tools   : 부가적


# # Cache file Check 함수
# def check_folder_file(file:str=None, folder:str=None):

#     r"""파일과 폴더 존재여부 확인 (폴더가 없으면 해당 폴더를 생성)
#     file (str) : 파일이름
#     folder (str) : 폴더명
#     :: return :: Boolean, file_path"""

#     # assert folder is not None, "확인할 folder 를 지정하지 않았습니다."
#     if folder is not None:
#         str_folder = os.path.abspath(os.path.join(folder, ''))

#         # Check Folder 
#         if not os.path.exists(str_folder):
#             os.makedirs(str_folder)

#         # Check File (생성 날짜가 동일한지 확인)
#         file_name = os.path.abspath(os.path.join(folder, file))
#     else:
#         file_name = file

#     if os.path.exists(file_name) == True:
#         file_creation_date = datetime.datetime.fromtimestamp(os.path.getatime(file_name)).date()
#         if file_creation_date == datetime.datetime.today().date():
#             return True
#     return False


# # file + folder 함께 확인가능
# def check_file_path(file_path:str=None, refresh:bool=False):
#     r"""Cache 파일 재활용에 필요한 조건충족(폴더생성) 및 확인하기
#     >> 동일날짜 생성일 땐, 파일 재활용 하기
#     : return : True(재활용 가능), False(재활용 불가능) """

#     # Pre processing ... (path of Folder)
#     ## 조건 1 : 경로에 포함된 폴더 확인 및 생성
#     folder_path_count = re.findall('/', file_path)
#     folder_path_count = len(folder_path_count)
#     assert folder_path_count == 1,\
#         f"{file_path} 는 1 아닌 {folder_path_count} 경로값이 있습니다"
#     folder, _ = file_path.split('/')

#     if os.path.isdir(folder) == False:
#         os.mkdir(folder)

#     ## 조건 2 : 동일날짜 존재시, 생성날짜 확인
#     CHECK = False
#     if refresh == False:
#         if os.path.exists(file_path):
#             time_stamp = os.path.getctime(file_path)
#             datetime_obj = datetime.datetime.fromtimestamp(time_stamp)
#             if datetime_obj.date() == datetime.date.today():
#                 CHECK = True
#     return CHECK
