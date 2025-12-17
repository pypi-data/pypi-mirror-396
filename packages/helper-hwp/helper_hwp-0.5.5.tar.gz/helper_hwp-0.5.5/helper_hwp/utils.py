"""
유틸리티 함수

HWP 파일 형식(5.0) 스펙 기반 단위 변환 및 파일 처리 함수
참고: 한글문서파일형식_5.0_revision1.3.txt
"""


def hwpunit_to_cm(hwpunit: int) -> float:
    """HWPUNIT을 cm로 변환.
    
    HWPUNIT은 HWP 문서의 기본 단위(1/7200 inch).
    스펙 정의: 자료형 설명 섹션 참조.
    
    Args:
        hwpunit: 변환할 HWPUNIT 값
    
    Returns:
        센티미터 단위로 변환된 값
    
    Examples:
        >>> hwpunit_to_cm(7200)  # 1 inch
        2.54
    """
    return hwpunit / 7200 * 2.54


def hwpunit_to_inch(hwpunit: int) -> float:
    """HWPUNIT을 inch로 변환.
    
    HWPUNIT은 1/7200 inch 단위로 표현됨.
    스펙 정의: 자료형 설명 섹션 참조.
    
    Args:
        hwpunit: 변환할 HWPUNIT 값
    
    Returns:
        인치 단위로 변환된 값
    
    Examples:
        >>> hwpunit_to_inch(7200)  # 1 inch
        1.0
    """
    return hwpunit / 7200


def hwpunit_to_px(hwpunit: int, dpi: int = 96) -> int:
    """HWPUNIT을 pixel로 변환.
    
    표준 96 DPI 기준(기본값). 다른 해상도는 dpi 파라미터로 지정.
    변환식: hwpunit / 7200 * dpi
    
    Args:
        hwpunit: 변환할 HWPUNIT 값
        dpi: 화면 해상도(기본값: 96 DPI)
    
    Returns:
        픽셀 단위로 변환된 정수값
    
    Examples:
        >>> hwpunit_to_px(7200)  # 1 inch at 96 DPI
        96
        >>> hwpunit_to_px(7200, dpi=72)  # 1 inch at 72 DPI
        72
    """
    return int(hwpunit / 7200 * dpi)


def hwpunit16_to_hwpunit(hwpunit16: int) -> int:
    """HWPUNIT16(INT16)을 HWPUNIT(INT32)로 변환.
    
    부호 있는 16비트 정수를 32비트로 확장.
    스펙 정의: 자료형 설명 섹션(HWPUNIT16 참조).
    
    음수 처리:
    - hwpunit16 >= 0x8000 → 음수(hwpunit16 - 0x10000)
    - hwpunit16 < 0x8000 → 양수(그대로)
    
    Args:
        hwpunit16: 변환할 INT16 값(범위: -32768 ~ 32767)
    
    Returns:
        INT32 범위의 HWPUNIT 값
    
    Examples:
        >>> hwpunit16_to_hwpunit(1000)
        1000
        >>> hwpunit16_to_hwpunit(0x8000)  # -32768
        -32768
    """
    if hwpunit16 >= 0x8000:
        return hwpunit16 - 0x10000
    return hwpunit16


def extract_text_from_hwp(file_path: str) -> str:
    """HWP 파일에서 텍스트 추출.
    
    HWP Compound File 구조에서 BodyText 스토리지의 문단 텍스트 추출.
    스펙 정의: 파일 구조 섹션 3.2.3(본문) 참조.
    
    처리 흐름:
    1. HwpFile로부터 문서 객체 생성
    2. BodyText의 모든 Section 스트림 순회
    3. 각 문단(HWPTAG_PARA_TEXT)에서 텍스트 추출
    4. 전체 텍스트 반환
    
    Args:
        file_path: HWP 파일의 절대 또는 상대 경로
    
    Returns:
        추출된 문서 전체 텍스트(문단 구분자 포함)
    
    Raises:
        FileNotFoundError: file_path가 존재하지 않음
        ValueError: 유효하지 않은 HWP 파일 형식
    """
    from .document_structure import HwpFile
    hwp = HwpFile.from_file(file_path)
    return hwp.to_text()