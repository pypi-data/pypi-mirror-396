from .base import *

# matplotlib font & style
def plt_ko(
        font_list:list=['D2Coding', 'NanumGothic'], # 'NanumGothicCoding',
        index:int=-1,
        dpi=150, # style='seaborn',
    ) -> plt:

    r"""matplotlib 에 적용 가능한 한글폰트 검색기
    Args:
        font_list (list) : 한글폰트 예시 리스트
        index (int) : `font_list` 에서 우선 추천할 인덱스
        style (str) : matplotlib 스타일 default) seaborn
        dpi (int)   : matplotlib DPI 해상도
    Return
        matplotlib.pyplot """

    fm_list    = set([_.name for _ in fontManager.ttflist])
    check_list = list(fm_list & set(font_list))
    font_name  = check_list[index]
    # plt.style.use(style=style)
    mpl.rcParams['axes.unicode_minus'] = False  # 일반 하이픈(-) 사용
    plt.rc('font', family=font_name)
    plt.rcParams['figure.dpi'] = dpi
    return plt
