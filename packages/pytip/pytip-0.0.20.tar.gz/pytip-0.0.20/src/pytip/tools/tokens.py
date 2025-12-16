from .base import *


# 관련단어 찾기
def token_findall(
        token:str, comparison_list:list, slice:int=1, 
        token_check:dict=None, algorithm=True
    ):
    r""" Token 과 유사도 높은 순서대로 정렬하기
    token (str)            : 비교단어
    comparison_list (list) : 대조군
    slice (int)            : 갯수 slice
    token_check (dict)     : {'돈':'돼지'} 정확를 위해 변경할 단어 """

    assert type(comparison_list) == list, f'{comparison_list} is not `List[]`'
    assert type(token) == str, f'{token} is not `str`'

    # PreProcess : 윈활한 비교를 위해 단어 바꾸기
    ## 1 비교를 위해 단어만 추출
    map_cleaning = map(lambda x : "".join(re.findall(r'[A-zㄱ-힣]+', str(x))) , comparison_list)
    comparison_list_clean = list(map_cleaning)

    ## 2 비교율 높이기 위해 단어변경
    if type(token_check) == dict:
        for key in token_check.keys():
            if token.find(key) != -1:
                token = token.replace(key, token_check[key])

    # Main Process
    # :: Method 1
    # (len(set(token.strip())&set(comparison.strip())) / len(
    #     comparison.strip())) * (len(set(token.strip())&set(comparison.strip())))

    # :: Method 2
    # len(set(token)&set(comparison))**2 / (len(
    # comparison) + (len(comparison) - len(set(token)&set(comparison)) + 1 ))

    if algorithm:
        _list = [[number, len(set(token)&set(comparison)), 
            (len(set(token)&set(comparison)) / (len(comparison))) * (
                len(set(token)&set(comparison)) / (len(token))
            )]
            for number, comparison in enumerate(comparison_list_clean)
            if len(set(token)&set(comparison)) > 0      
        ]
        # Sort a list by multiple attributes?
        # https://stackoverflow.com/questions/4233476/sort-a-list-by-multiple-attributes
        _list = sorted(_list, key=lambda x:(x[1], x[2]), reverse=True)
        comparison_list = pandas.Series(comparison_list)
        return comparison_list.loc[[_[0] for _ in _list]].tolist()[:slice]

    else:
        result_list = []
        result_list += [_  for _ in comparison_list  if len(re.findall('^{token}', _))>0]
        result_list += [_  for _ in comparison_list  if len(re.findall('{token}$', _))>0]
        if len(result_list) == 0:
            result_list += [_  for _ in comparison_list  if _.find(token) != -1]
        return result_list[:slice]
