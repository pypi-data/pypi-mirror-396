# from .base import *

# # matplotlib font & style
# def plt_ko(
#         font_list:list=['D2Coding', 'NanumGothicCoding', 'NanumGothic'],
#         index:int=-1,
#         style='seaborn',
#         dpi=150,
#     ) -> plt:

#     r"""matplotlib 에 적용 가능한 한글폰트 검색기
#     font_list (list) : 한글폰트 예시 리스트
#     index (int) : `font_list` 에서 우선 추천할 인덱스
#     style (str) : matplotlib 스타일 default) seaborn
#     dpi (int)   : matplotlib DPI 해상도
#     :: return :: matplotlib.pyplot """

#     fm_list    = set([_.name for _ in fontManager.ttflist])
#     check_list = list(fm_list & set(font_list))
#     font_name  = check_list[index]
#     plt.style.use(style=style)
#     plt.rc('font', family=font_name)
#     plt.rcParams['figure.dpi'] = dpi
#     return plt
