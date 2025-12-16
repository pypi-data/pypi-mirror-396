from .base import *


# Bookmark -> outline 객체 생성하기
def parse_markdown_outline(md_path: Path) -> List[Tuple[int, str, Optional[int]]]:
    r""" Markdown 파일에서 헤더(제목)를 파싱
    Args:
        md_path : Markdown 문서경로
    Notes:
        다음과 같은 튜플 리스트를 반환합니다: (level, title, page_number)
        - level (int): '#' 기호의 개수에 따른 북마크 깊이 (1..6)
        - title (str): [p:NN] 부분이 제거된 제목 텍스트
        - page_number (Optional[int]): [p:NN] 형식으로 제공된 페이지 번호 (없으면 None) """

    # Markdown 헤더 패턴 정의 (정규표현식)
    # r'^(#{1,6})\s+(.*?)\s*(?:\[\s*p\s*:\s*(\d+)\s*\])?\s*$'
    # 1. (r'^(#{1,6})'): #이 1개에서 6개까지 나오는 부분 (북마크 레벨)
    # 2. (\s+(.*?)\s*): 제목 텍스트 (Title)
    # 3. (?:\[\s*p\s*:\s*(\d+)\s*\])?: 선택적 페이지 번호 [p:NN]
    MD_HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.*?)\s*(?:\[\s*p\s*:\s*(\d+)\s*\])?\s*$')

    # 결과값을 저장할 객체
    outline_entries: List[Tuple[int, str, Optional[int]]] = []
    
    # Markdown 파일을 UTF-8 인코딩으로 읽어와 줄 단위로 처리
    for raw in md_path.read_text(encoding="utf-8").splitlines():
        mark_down_raw = MD_HEADING_PATTERN.match(raw)
        
        # 정규표현식 패턴과 일치하지 않으면 건너뜁니다. (일반 텍스트 줄)
        if not mark_down_raw:
            continue

        hashes, title, page = mark_down_raw.groups() # 정규표식 그룹으로부터 '#', 제목, 페이지 번호를 추출
        level = len(hashes)                          # '#' 개수를 세어 북마크 레벨(깊이)을 결정
        
        # 페이지 번호가 있으면 정수로 변환, 없으면 None
        page_num = int(page) if page is not None else None
        title = title.strip()                            # 제목 텍스트의 앞뒤 공백을 정리
        outline_entries.append((level, title, page_num)) # 추출된 정보를 리스트에 추가
        
    return outline_entries


# PDF 객체생성
def build_pdf_outline(
        pdf_input: Path, 
        pdf_output: Path, 
        outline_entries: List[Tuple[int, str, Optional[int]]], 
        page_gap: int = -1
    ) -> None:

    r""" 파싱된 Markdown 헤더를 기반으로 PDF에 북마크(Outline) 적용
    Args:
        pdf_input  (Path) : 원본 PDF 파일 경로
        pdf_output (Path) : 북마크가 적용된 출력 PDF 파일 경로 (Path 객체)
        outline_entries (Path) : parse_markdown_outline()에서 반환된 북마크 정보 리스트
        page_gap (int) : 독자 기준 1-based 페이지 번호를 pikepdf의 0-based 인덱스로 변환하기 위한 오프셋.
            일반적으로 page_gap = -1 (예: 1페이지 -> 인덱스 0) 입니다."""

    # PDF 파일을 읽기 모드로 엽니다. (pikepdf는 Path 객체를 str로 변환해야 할 수 있습니다.)
    with Pdf.open(str(pdf_input)) as pdf:
        # 북마크(Outline) 구조를 조작하기 위한 컨텍스트 매니저를 엽니다.
        with pdf.open_outline() as outline:        
            # --- 계층 구조 관리를 위한 스택(Stack) 설정 ---
            # stack[i]는 레벨 i+1에서 새로운 항목을 추가할 부모의 'children' 리스트를 저장합니다.
            # 초기값: [outline.root] -> 레벨 1 항목의 부모 리스트(root)
            stack: List[List[OutlineItem]] = [outline.root]  # 레벨 0: PDF의 최상위 루트 리스트
            
            # 현재 레벨에서 가장 마지막으로 추가된 OutlineItem을 추적합니다. 
            # 이를 통해 다음 하위 레벨 항목의 부모를 결정합니다.
            current_items: List[Optional[OutlineItem]] = [None] # 레벨 0: None

            # --- 북마크 항목 순회 및 적용 ---
            for level, title, page_num in outline_entries:
                # 새로운 항목의 레벨에 맞게 stack과 current_items의 크기를 조정/초기화합니다.
                # 현재 레벨까지 stack이 확장되었는지 확인하고, 필요하다면 빈 리스트로 확장합니다.
                while len(stack) < level:
                    stack.append([])  # 임시 placeholder; 실제로는 item.children으로 대체될 것입니다.
                    current_items.append(None)

                # 현재 레벨보다 더 깊은 레벨의 스택 정보를 제거합니다. (상위 레벨로 이동했으므로)
                stack = stack[:level]
                current_items = current_items[:level]

                # --- 페이지 인덱스 계산 및 검증 ---                
                page_index = None
                if page_num is not None:
                    # 독자 페이지 번호에 오프셋(page_gap)을 적용하여 0-based 인덱스를 계산합니다.
                    page_index = page_num + page_gap

                    # 페이지 인덱스가 PDF의 유효 범위 내에 있는지 간단히 검증합니다.
                    if not (0 <= page_index < len(pdf.pages)):
                        # 유효 범위를 벗어나면 페이지 연결 없이 북마크만 생성합니다.
                        print(f"⚠️ 경고: '{title}'의 페이지 번호({page_num})가 PDF 범위 밖입니다. 페이지 연결 없이 북마크만 생성합니다.")
                        page_index = None

                # OutlineItem 객체 생성
                item = OutlineItem(title, page_index) if page_index is not None else OutlineItem(title)

                # --- 부모 항목 결정 및 자식 리스트에 추가 ---
                if level == 1:
                    outline.root.append(item)  # 최상위 레벨 항목은 PDF 루트에 직접 추가합니다.
                else:
                    # 부모 항목은 'level - 1'에서 가장 마지막에 추가된 항목입니다.
                    # level-1의 인덱스는 level-2 입니다.
                    parent_item = current_items[level - 1 - 1]                     
                    if parent_item is None:
                        # 구조가 잘못되어 상위 레벨 항목이 없는 경우, 오류 방지를 위해 루트에 붙입니다.
                        print(f"⚠️ 경고: '{title}' (레벨 {level})의 부모 항목을 찾을 수 없습니다. 루트에 추가합니다.")
                        outline.root.append(item)
                    else:
                        # 정상적인 경우, 부모 항목의 자식 리스트에 새 항목을 추가합니다.
                        parent_item.children.append(item)

                # --- 스택 업데이트 ---
                # 현재 레벨에 새 항목을 등록하여 다음에 같은 레벨이 나오면 그 다음 항목으로 지정되게 합니다.
                if len(current_items) < level + 1:
                    current_items.append(None)
                current_items[level - 1] = item

                # 다음 하위 레벨(level+1)의 항목이 추가될 때, 이 항목의 children 리스트를 사용하도록 stack에 추가합니다.
                if len(stack) == level:
                    stack.append(item.children)

        # 모든 북마크 생성이 완료된 후, 수정된 PDF를 저장합니다.
        pdf.save(str(pdf_output))


# 종합실행 함수
def bookmark_md_to_pdf(
        md_path: Path,
        pdf_input: Path, 
        pdf_output: Path,
        page_gap: int = -1
    ):
    r""" 파싱된 Markdown 문서 기반으로 PDF에 북마크(Outline) 적용
    Args:
        md_path  (Path) : 원본 PDF 파일 경로 
        pdf_input  (Path) : 원본 PDF 파일 경로 
        pdf_output (Path) : 북마크가 적용된 출력 PDF 파일 경로 (Path 객체)
        outline_entries (Path) : parse_markdown_outline()에서 반환된 북마크 정보 리스트
        page_gap (int) : 독자 기준 1-based 페이지 번호를 pikepdf의 0-based 인덱스로 변환하기 위한 오프셋.
            일반적으로 page_gap = -1 (예: 1페이지 -> 인덱스 0) 입니다."""
    md_path   = Path(md_path)     # markdown 문서 경로 (utf-8)
    pdf_input = Path(pdf_input)   # 북마크를 추가할 원본 PDF 파일 경로
    pdf_output = Path(pdf_output) # 북마크가 적용된 PDF 파일이 저장될 경로

    try:
        # 1. Markdown 파일 파싱
        entries = parse_markdown_outline(md_path)
        if not entries:
            raise SystemExit("No headings found in markdown. Ensure lines use # and [p:NN].")
            
        # 2. PDF에 북마크 적용
        build_pdf_outline(pdf_input, pdf_output, entries, page_gap=page_gap)
        print(f"✅ 북마크 생성 완료: {pdf_output}")
        
    except FileNotFoundError as e:
        print(f"❌ 오류: 지정된 파일 중 하나를 찾을 수 없습니다. 경로를 확인하세요: {e}")
    except SystemExit as e:
        print(f"❌ 오류: {e}")
    except Exception as e:
        print(f"❌ 예상치 못한 오류 발생: {e}")