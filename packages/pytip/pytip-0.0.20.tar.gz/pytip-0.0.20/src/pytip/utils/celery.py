# from .base import *
# from ..tools.item import string_to_datetime


# # Celery Log 파일 분석기
# class Celery:

#     def __init__(self, file_path:str=None):
#         self.file_path = file_path
#         self.re_id = "\[[0-9A-z.]+\]"
#         self.re_time = "^[0-9]{4}/[0-9]{1,2}/[0-9]{1,2} [0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}"
#         self.re_celery_name = "\[celery\.[\w.]+\]"
#         self.re_function_beat = "\([\w.]+\)"
#         self.re_function = "Task [/.A-z_]+"

#     def __repr__(self) -> str:
#         return f"Celery Log Analytics with `{self.file_path}`"

#     @property
#     def _open(self):
#         with open("data/celery.log", "r") as f:
#             logs = f.readlines()
#         return logs

#     @property
#     def df(self):

#         item_dict = {}
#         assert self.file_path is not None, f"`file_path` is not specified ..."
#         logs = self._open

#         # celery.beat : Scheduler : 스케줄러 등록 (함수등록)
#         # celery.worker : Task : 함수의 실행
#         # celery.app.trace : Task : 실행결과
#         for _index, text in enumerate(logs):

#             # celery init
#             celery_name = "".join(re.findall(self.re_celery_name, text))
#             if celery_name.find("celery.worker.strategy") != -1:
#                 _time = "".join(re.findall(self.re_time, text))
#                 _name = "".join(re.findall(self.re_function, text)).split('[')[0].replace('Task ','')
#                 text  = text.replace(celery_name, '').replace(_time, '').replace(_name, '')
#                 _id   = "".join(re.findall("\[[\w.-]+\]", text)[0]).replace('[','').replace(']','')
#                 item_dict[_id] = {}
#                 item_dict[_id]['name'] = _name
#                 item_dict[_id]['init'] = _time

#             # celery result
#             if celery_name.find("celery.app.trace") != -1:
#                 _time = "".join(re.findall(self.re_time, text))
#                 _name = "".join(re.findall(self.re_function, text)).split('[')[0].replace('Task ','')
#                 text  = text.replace(celery_name, '').replace(_time, '').replace(_name, '')
#                 _id   = "".join(re.findall("\[[\w.-]+\]", text)[0]).replace('[','').replace(']','')

#                 if _id in list(item_dict.keys()):
#                     if text.find('Task') != -1:
#                         text = text.replace(_id, '').split('Task []')[1]#.split(":")[0]
#                     else:
#                         text = text.replace(_id, '')#.split(":")[0]

#                     # filtering result
#                     # success
#                     if text.find('succeeded') != -1:
#                         _working = re.findall('[\d\.]+' ,text.split('succeeded')[1])[0]
#                         _working = float(_working)
#                         result = text

#                     # Error Message
#                     ## while True 일 때 반복, False 일 때 종료
#                     if text.find('succeeded') == -1:
#                         _working = 0
#                         result = text
#                         while "".join(re.findall(self.re_time, logs[_index + 1])) == "": # 시간 데이터
#                             _index += 1
#                             result += logs[_index]

#                     item_dict[_id]['finish'] = _time
#                     item_dict[_id]['time'] = _working
#                     item_dict[_id]['result'] = result

#         # time id app_name result
#         df = pandas.DataFrame(item_dict).T.reset_index()

#         # fillna & datetime
#         df['time'] = df['time'].fillna(0)
#         df['result'] = df['result'].fillna('not Working')
#         _index_list = df[df.finish.isna()].index.values

#         for _index in _index_list:
#             df.loc[_index,'finish'] = df.loc[_index,'init']

#         for column in ['init', 'finish']: # 
#             df[column] = df[column].map(lambda x : string_to_datetime(x))
#         return df
