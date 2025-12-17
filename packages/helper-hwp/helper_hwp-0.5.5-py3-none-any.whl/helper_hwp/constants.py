"""
HWP 파일 포맷 상수 정의

한글문서파일형식_5.0_revision1.3.txt 참고
"""

from enum import Enum, IntEnum


class RecordTag(IntEnum):
    """레코드 태그 ID (HWP 5.0 스펙 기준)

    각 태그는 HWP 파일의 특정 데이터 구조를 나타냅니다.
    태그 ID는 10비트로 표현되며, 문서의 구조를 정의하는 데 사용됩니다.
    """
    
    HWPTAG_BEGIN = 0x10

    # DocInfo 레코드 (0x10~0x1B)
    HWPTAG_DOCUMENT_PROPERTIES = 0x10  # 16: 문서 속성
    HWPTAG_ID_MAPPINGS = 0x11          # 17: 아이디 매핑 헤더
    HWPTAG_BIN_DATA = 0x12             # 18: 바이너리 데이터
    HWPTAG_FACE_NAME = 0x13            # 19: 글꼴
    HWPTAG_BORDER_FILL = 0x14          # 20: 테두리/배경
    HWPTAG_CHAR_SHAPE = 0x15           # 21: 글자 모양
    HWPTAG_TAB_DEF = 0x16              # 22: 탭 정의
    HWPTAG_NUMBERING = 0x17            # 23: 문단 번호
    HWPTAG_BULLET = 0x18               # 24: 글머리표
    HWPTAG_PARA_SHAPE = 0x19           # 25: 문단 모양
    HWPTAG_STYLE = 0x1A                # 26: 스타일
    HWPTAG_DOC_DATA = 0x1B             # 27: 문서 데이터

    # BodyText 레코드 (실제: 0x42~, 문서 스펙: 0x40~)
    # 주의: 문서 스펙과 실제 구현이 다름. 실제 HWP 파일은 아래 값 사용
    HWPTAG_PARA_HEADER = 0x42          # 66: 문단 헤더 (실제: 0x42, 스펙: 0x40)
    HWPTAG_PARA_TEXT = 0x43            # 67: 문단 텍스트 (실제: 0x43, 스펙: 0x41)
    HWPTAG_PARA_CHAR_SHAPE = 0x44      # 68: 문단의 글자 모양 (실제: 0x44, 스펙: 0x42)
    HWPTAG_PARA_LINE_SEG = 0x45        # 69: 문단의 레이아웃 (실제: 0x45, 스펙: 0x43)
    HWPTAG_PARA_RANGE_TAG = 0x46       # 70: 문단의 영역 태그 (실제: 0x46, 스펙: 0x44)
    HWPTAG_CTRL_HEADER = 0x47          # 71: 컨트롤 헤더 (실제: 0x47, 스펙: 0x4B)
    HWPTAG_LIST_HEADER = 0x48          # 72: 문단 리스트 헤더 (실제: 0x48, 스펙: 0x4C)
    HWPTAG_PAGE_DEF = 0x49             # 73: 페이지 정의
    HWPTAG_FOOTNOTE_SHAPE = 0x4A       # 74: 각주 모양
    HWPTAG_PAGE_BORDER_FILL = 0x4B     # 75: 페이지 테두리/배경
    HWPTAG_SHAPE_COMPONENT = 0x4C      # 76: 개체 공통 속성
    HWPTAG_TABLE = 0x4D                # 77: 표 개체
    
    # 개체별 상세 태그 (Tag ID 추정)
    HWPTAG_SHAPE_COMPONENT_PICTURE = 0x4E  # 78: 그림 개체 속성
    HWPTAG_SHAPE_COMPONENT_OLE = 0x50      # 80: OLE 개체 속성
    HWPTAG_EQEDIT = 0x51                   # 81: 수식 개체
    HWPTAG_CTRL_DATA = 0x52                # 82: 컨트롤 임의의 데이터 (스펙: 0x4D, 중복 방지로 분리)

class HistoryRecordType(IntEnum):
    """문서 이력 관리 레코드 타입 (DocHistory Storage)"""
    STAG = 0x10        # 16: 히스토리 아이템 정보 시작
    ETAG = 0x11        # 17: 히스토리 아이템 정보 끝
    VERSION = 0x20     # 32: 히스토리 아이템 버전
    DATE = 0x21        # 33: 히스토리 날짜
    WRITER = 0x22      # 34: 히스토리 작성자
    DESCRIPTION = 0x23 # 35: 히스토리 설명
    DIFFDATA = 0x30    # 48: 비교 정보 (DiffML)
    LASTDOCDATA = 0x31 # 49: 가장 마지막 문서 (HWPML)

class ExtendedControlCode(IntEnum):
    """확장 제어 문자 코드 (16바이트 구조: 2바이트 코드 + 12바이트 데이터 + 2바이트 반복)"""
    TABLE = 1                   # 테이블/표
    PICTURE = 2                 # 그림
    OLE = 3                     # OLE 객체
    EQUATION = 11               # 수식
    FOOTNOTE = 14               # 각주
    ENDNOTE = 15                # 미주
    HYPERLINK = 16              # 하이퍼링크
    FOOTNOTE_OR_ENDNOTE = 17    # 각주/미주 (HWP 3.x 호환)
    HEADER_OR_FOOTER = 18       # 머리말/꼬리말 (HWP 3.x 호환)
    COMMENT = 21                # 메모/주석
    SHAPE = 22                  # 도형/그리기 개체
    SHAPE_COMPONENT = 23        # 도형 구성 요소

class CharControlCode(IntEnum):
    """제어 문자 코드 (2바이트만 사용)"""
    UNUSABLE = 0                # 사용 불가 문자
    LINE_BREAK = 10             # 줄바꿈 (\n)
    PARA_BREAK = 13             # 문단바꿈 (\r, CR)
    HYPHEN = 24                 # 하이픈
    RESERVED_25 = 25            # 예약
    RESERVED_26 = 26            # 예약
    RESERVED_27 = 27            # 예약
    RESERVED_28 = 28            # 예약
    RESERVED_29 = 29            # 예약
    KEEP_WORD_SPACE = 30        # 묶음 빈칸
    FIXED_WIDTH_SPACE = 31      # 고정폭 빈칸

class InlineControlCode(IntEnum):
    """인라인 제어 문자 코드 (16바이트 구조, 별도 객체 불필요)"""
    FIELD_START = 4             # 필드 시작
    FIELD_END = 5               # 필드 끝
    BOOKMARK = 6                # 책갈피
    FIELD_UNKNOWN = 7           # 필드 관련
    FIELD_DATE = 8              # 날짜 필드
    TAB = 9                     # 탭
    PAGE_HIDE = 12              # 쪽 번호 위치
    PAGE_NUMBER = 19            # 쪽 번호
    PAGE_COUNT = 20             # 총 쪽 수

class HeaderConstants(IntEnum):
    """FileHeader 스트림 관련 상수"""
    TOTAL_SIZE = 256          # 헤더 전체 크기
    SIGNATURE_SIZE = 32       # 서명 크기
    VERSION_OFFSET = 0x20     # 버전 정보 오프셋 (32)
    FLAGS_OFFSET = 0x24       # 플래그 정보 오프셋 (36)
    FLAGS_END = 0x28          # 플래그 읽기 종료 (40)

class RecordBitMask(IntEnum):
    """레코드 헤더 비트 마스크 상수"""
    TAG_ID_MASK = 0x3FF       # 10비트 마스크 (Tag ID)
    LEVEL_MASK = 0x3FF        # 10비트 마스크 (Level)
    SIZE_MASK = 0xFFF         # 12비트 마스크 (Size)
    SIZE_EXTENDED = 0xFFF     # 확장 크기 플래그
    LEVEL_SHIFT = 10          # Level 비트 시프트
    SIZE_SHIFT = 20           # Size 비트 시프트

class CharConstants(IntEnum):
    """문자 처리 관련 상수"""
    CONTROL_BOUNDARY = 31     # 제어 문자 경계 (> 31: 일반 문자)
    CONTROL_DATA_SIZE = 12    # 확장/인라인 제어 데이터 크기
    CODE_SIZE = 2             # 문자 코드 크기 (UTF-16)
    SURROGATE_START = 0xD800  # UTF-16 Surrogate 시작
    SURROGATE_END = 0xDFFF    # UTF-16 Surrogate 끝

class ParagraphConstants(IntEnum):
    """문단 관련 상수"""
    PAGE_BREAK_TYPE_OFFSET = 7    # page_break_type 오프셋
    MIN_HEADER_SIZE = 8           # 헤더 최소 크기
    CONTROL_ID_SIZE = 4           # control_id 크기

class PageBreakType(IntEnum):
    """페이지 구분 타입 (단 나누기 종류)"""
    NORMAL = 0            # 일반 문단
    COLUMN_BREAK = 1      # 단 나누기
    PAGE_BREAK = 2        # 쪽 나누기
    SECTION_BREAK = 3     # 구역 나누기

class ControlID(IntEnum):
    """확장 제어 Control ID (control_data 첫 4바이트, 리틀엔디언 UINT32)"""
    TABLE = 0x74626C20    # ' lbt' → 'tbl ' (리틀엔디언)
    AUTO_NUMBER = 0x61746E6F  # 'onta' → 'atno' (리틀엔디언) 자동 번호
    NEW_NUMBER = 0x6E776E6F   # 'onwn' → 'nwno' (리틀엔디언) 새 번호 지정
    PAGE_NUM_POS = 0x70676E70  # 'pngp' → 'pgnp' (리틀엔디언) 쪽 번호 위치
    HEADER = 0x64616568   # 'daeh' → 'head' (리틀엔디언) 머리말
    FOOTER = 0x746F6F66   # 'toof' → 'foot' (리틀엔디언) 꼬리말

class ElementType(Enum):
    """문서 요소 타입 (HWP 5.0 스펙 기반)"""
    PARAGRAPH = "paragraph"  # 문단 (HWPTAG_PARA_HEADER)
    TABLE = "table"  # 표 (HWPTAG_TABLE)
    SHAPE_COMPONENT = "shape_component"  # 도형 요소 (HWPTAG_SHAPE_COMPONENT)
    PICTURE = "picture"  # 그림
    EQUATION = "equation"  # 수식
    FOOTNOTE = "footnote"  # 각주 (HWPTAG_FOOTNOTE_SHAPE)
    ENDNOTE = "endnote"  # 미주
    HEADER = "header"  # 머리글
    FOOTER = "footer"  # 바닥글
    CAPTION = "caption"  # 캡션
    LIST_HEADER = "list_header"  # 리스트 헤더 (HWPTAG_LIST_HEADER)
    PAGE_DEF = "page_def"  # 페이지 정의 (HWPTAG_PAGE_DEF)
    CTRL_HEADER = "ctrl_header"  # 컨트롤 헤더 (HWPTAG_CTRL_HEADER)
    CTRL_DATA = "ctrl_data"  # 컨트롤 데이터 (HWPTAG_CTRL_DATA)
    PAGE_BREAK = "page_break"  # 페이지 구분 (쪽 나누기)
    SECTION = "section"  # 섹션
    COMMENT = "comment"  # 메모
    SHAPE = "shape"  # 도형
    OLE = "ole"  # OLE 객체
    HYPERLINK = "hyperlink"  # 하이퍼링크
    BOOKMARK = "bookmark"  # 책갈피
    FIELD = "field"  # 필드
    AUTO_NUMBER = "auto_number"  # 자동 번호 (쪽 번호 등)
    NEW_NUMBER = "new_number"  # 새 번호 지정
    PAGE_NUM_POS = "page_num_pos"  # 쪽 번호 위치

    @classmethod
    def from_string(cls, value: str) -> 'ElementType':
        """문자열을 ElementType으로 변환 (하위 호환성)"""
        value_lower = value.lower()
        for member in cls:
            if member.value == value_lower:
                return member
        raise ValueError(f"Unknown element type: {value}")

class IterMode(Enum):
    """문서 순회 모드"""
    SEQUENTIAL = "sequential"  # 문서 출현 순서 (기본, 속도 우선)
    STRUCTURED = "structured"  # Section → Paragraph → Char 계층 구조