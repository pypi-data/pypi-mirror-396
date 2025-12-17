"""
파싱된 요소 클래스

이 파일은 한글 문서 파일 형식 5.0 (revision 1.3)을 참고하여
문단, 테이블, 페이지 등의 요소를 파싱하고 구조화하는 데 사용됩니다.
"""

import struct
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .char_paragraph import Paragraph
from .constants import ParagraphConstants
from .document_structure import CharShapeInfo


@dataclass
class ParsedParagraph:
    """파싱된 문단

    Attributes:
        text (str): 문단의 텍스트 내용.
        paragraph (Paragraph): 문단의 구조적 정보.
        char_shape (Optional[CharShapeInfo]): 문단의 대표 글자 서식 정보.
        char_shapes (List[Tuple[int, CharShapeInfo]]): 글자별 서식 정보 리스트.
    """
    text: str
    paragraph: Paragraph
    char_shape: Optional[CharShapeInfo] = None  # 문단 대표 서식 (max 기준)
    char_shapes: List[Tuple[int, CharShapeInfo]] = field(default_factory=list)  # 글자별 서식 [(pos, shape), ...]
    
    @property
    def is_page_first_line(self) -> bool:
        """페이지의 첫 줄 여부 (Paragraph 객체에서 전달)"""
        return self.paragraph.is_page_first_line

    def __str__(self):
        return self.text

    def __repr__(self):
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"ParsedParagraph(text='{preview}')"

@dataclass
class TableCell:
    """테이블 셀 정보

    Attributes:
        row (int): 셀의 행 번호 (0부터 시작).
        col (int): 셀의 열 번호 (0부터 시작).
        rowspan (int): 행 병합 개수.
        colspan (int): 열 병합 개수.
        paragraphs (List[Paragraph]): 셀에 포함된 문단 리스트.
    """
    row: int  # 행 번호 (0-based)
    col: int  # 열 번호 (0-based)
    rowspan: int = 1  # 행 병합 (기본 1)
    colspan: int = 1  # 열 병합 (기본 1)
    paragraphs: List[Paragraph] = field(default_factory=list)  # 셀 내용

    @property
    def text(self) -> str:
        """셀 텍스트"""
        return "\n".join(p.to_string() for p in self.paragraphs)

    def __repr__(self):
        return f"TableCell(row={self.row}, col={self.col}, text='{self.text[:20]}...')"

@dataclass
class ParsedTable:
    """파싱된 테이블

    Attributes:
        code (int): 테이블 코드.
        data (Optional[bytes]): 테이블의 바이너리 데이터.
        control_id (Optional[int]): 테이블 컨트롤 ID.
        x, y, width, height (Optional[int]): 테이블의 위치 및 크기 정보 (HWPUNIT 단위).
        rows, cols (Optional[int]): 테이블의 행과 열 개수.
        cells (Optional[List[TableCell]]): 테이블의 셀 정보 리스트.
    """
    code: int
    data: Optional[bytes]
    control_id: Optional[int] = None
    
    # HWPTAG_SHAPE_COMPONENT 정보 (HWPUNIT)
    x: Optional[int] = None  # 가로 오프셋 (HWPUNIT, 1/7200 inch)
    y: Optional[int] = None  # 세로 오프셋 (HWPUNIT, 1/7200 inch)
    width: Optional[int] = None  # 폭 (HWPUNIT)
    height: Optional[int] = None  # 높이 (HWPUNIT)
    margin_left: Optional[int] = None  # 왼쪽 여백 (HWPUNIT16)
    margin_right: Optional[int] = None  # 오른쪽 여백 (HWPUNIT16)
    margin_top: Optional[int] = None  # 위쪽 여백 (HWPUNIT16)
    margin_bottom: Optional[int] = None  # 아래쪽 여백 (HWPUNIT16)
    
    # HWPTAG_LIST_HEADER 정보
    cell_count: Optional[int] = None  # 셀 개수 (호환성 유지, 마지막 셀의 문단 개수)
    cell_para_counts: Optional[List[int]] = None  # 각 셀의 문단 개수 배열
    
    # HWPTAG_TABLE 정보
    rows: Optional[int] = None  # 행 개수
    cols: Optional[int] = None  # 열 개수
    cell_spacing: Optional[int] = None  # 셀 간격 (HWPUNIT16)
    row_sizes: Optional[List[int]] = None  # 행별 높이 배열 (HWPUNIT16)
    
    # 셀별 크기 및 병합 정보 (셀 리스트 파싱)
    cell_widths: Optional[List[int]] = None  # 셀별 폭 (HWPUNIT)
    cell_heights: Optional[List[int]] = None  # 셀별 높이 (HWPUNIT)
    cell_colspans: Optional[List[int]] = None  # 셀별 열 병합 개수
    cell_rowspans: Optional[List[int]] = None  # 셀별 행 병합 개수
    
    # 셀 정보 (확장)
    cells: Optional[List[TableCell]] = None
    
    # 테이블 인덱스 (문서 내 순서)
    table_index: Optional[int] = None

    def get_control_id(self) -> Optional[int]:
        """control_data의 첫 4바이트에서 Control ID 추출"""
        if self.data and len(self.data) >= ParagraphConstants.CONTROL_ID_SIZE:
            return struct.unpack('<I', self.data[0:ParagraphConstants.CONTROL_ID_SIZE])[0]
        return None

    def to_cm(self, hwpunit: Optional[int]) -> Optional[float]:
        """HWPUNIT을 cm로 변환"""
        if hwpunit is None:
            return None
        return hwpunit / 7200 * 2.54

    def to_inch(self, hwpunit: Optional[int]) -> Optional[float]:
        """HWPUNIT을 inch로 변환"""
        if hwpunit is None:
            return None
        return hwpunit / 7200

    def to_px(self, hwpunit: Optional[int], dpi: int = 96) -> Optional[int]:
        """HWPUNIT을 pixel로 변환 (기본 96 DPI)"""
        if hwpunit is None:
            return None
        return int(hwpunit / 7200 * dpi)

    @property
    def width_cm(self) -> Optional[float]:
        """폭 (cm)"""
        return self.to_cm(self.width)

    @property
    def height_cm(self) -> Optional[float]:
        """높이 (cm)"""
        return self.to_cm(self.height)

    @property
    def total_width(self) -> Optional[int]:
        """여백 포함 전체 폭 (HWPUNIT)"""
        if self.width is None:
            return None
        margin_h = (self.margin_left or 0) + (self.margin_right or 0)
        return self.width + margin_h

    @property
    def total_height(self) -> Optional[int]:
        """여백 포함 전체 높이 (HWPUNIT)"""
        if self.height is None:
            return None
        margin_v = (self.margin_top or 0) + (self.margin_bottom or 0)
        return self.height + margin_v

    def calculate_table_size_from_cells(self) -> Tuple[Optional[int], Optional[int]]:
        """셀 크기 기반 테이블 전체 크기 계산 (폭, 높이) - HWPUNIT 단위
        
        Returns:
            (width, height): 테이블 전체 크기 (HWPUNIT), 계산 불가시 (None, None)
        """
        # 1. 셀 높이 기반 계산 (Row Size는 높이가 아님)
        calc_height = None
        if self.cell_heights and self.rows and self.cols:
            # 각 행의 대표 높이 계산 (첫 번째 열 기준)
            heights_by_row = {}
            for row in range(self.rows):
                cell_idx = row * self.cols  # 첫 번째 열의 셀
                if cell_idx < len(self.cell_heights):
                    heights_by_row[row] = self.cell_heights[cell_idx]
            
            if heights_by_row:
                calc_height = sum(heights_by_row.values())
                if self.cell_spacing and self.cell_spacing > 0:
                    calc_height += self.cell_spacing * (self.rows - 1)
        
        # 2. 폭 계산: 첫 번째 행의 셀 폭 합산
        calc_width = None
        if self.cell_widths and self.cols:
            widths_by_col = {}
            for col in range(self.cols):
                cell_idx = col  # 첫 번째 행의 셀
                if cell_idx < len(self.cell_widths):
                    widths_by_col[col] = self.cell_widths[cell_idx]
            
            if widths_by_col:
                calc_width = sum(widths_by_col.values())
                # cell_spacing 추가 (열 사이 간격)
                if self.cell_spacing and self.cell_spacing > 0:
                    calc_width += self.cell_spacing * (self.cols - 1)
        
        return (int(calc_width) if calc_width else None, int(calc_height) if calc_height else None)

    @property
    def calculated_width_cm(self) -> Optional[float]:
        """셀 기반 계산된 폭 (cm)"""
        width, _ = self.calculate_table_size_from_cells()
        return self.to_cm(width)

    @property
    def calculated_height_cm(self) -> Optional[float]:
        """셀 기반 계산된 높이 (cm)"""
        _, height = self.calculate_table_size_from_cells()
        return self.to_cm(height)

    def __repr__(self):
        info = f"code={self.code}, control_id={self.control_id or self.get_control_id()}"
        if self.rows is not None and self.cols is not None:
            info += f", rows={self.rows}, cols={self.cols}"
        if self.width is not None and self.height is not None:
            info += f", size=({self.width_cm:.2f}cm x {self.height_cm:.2f}cm)"
        return f"ParsedTable({info})"

@dataclass
class ParsedPage:
    """파싱된 페이지

    Attributes:
        page_number (int): 페이지 번호.
        paragraphs (List[ParsedParagraph]): 페이지에 포함된 문단 리스트.
    """
    page_number: int
    paragraphs: List['ParsedParagraph']

    def to_text(self) -> str:
        """페이지의 모든 문단을 텍스트로 변환하여 반환합니다."""
        return "\n".join(p.text for p in self.paragraphs)

    def __repr__(self):
        return f"ParsedPage(page={self.page_number}, paragraphs={len(self.paragraphs)})"