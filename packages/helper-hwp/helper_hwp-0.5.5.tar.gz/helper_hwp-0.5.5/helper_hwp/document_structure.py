"""
HWP 문서 구조 (Section, Body, HwpFile)
"""

import io
import struct
import zlib
from dataclasses import dataclass, field
from typing import List

import olefile

from .char_paragraph import Paragraph
from .constants import ControlID, RecordTag
from .models import Header
from .record_stream import RecordStream


@dataclass
class Section:
    """HWP 섹션"""
    paragraphs: List[Paragraph] = field(default_factory=list)
    table_metadata: List[dict] = field(default_factory=list)

    def to_string(self) -> str:
        """섹션을 문자열로 변환"""
        return "\n".join(para.to_string() for para in self.paragraphs)

@dataclass
class Body:
    """HWP 본문"""
    sections: List[Section] = field(default_factory=list)

    def to_string(self) -> str:
        """본문을 문자열로 변환"""
        return "\n\n".join(section.to_string() for section in self.sections)

@dataclass
class HwpFile:
    """HWP 파일 내부 구조"""
    header: Header
    body: Body
    char_shapes: dict = field(default_factory=dict)  # {char_shape_id: CharShapeInfo}

    @classmethod
    def from_file(cls, file_path: str) -> 'HwpFile':
        """파일 경로로부터 HWP 문서 로드"""
        with open(file_path, 'rb') as f:
            return cls.from_bytes(f.read())

    @classmethod
    def from_bytes(cls, data: bytes) -> 'HwpFile':
        """
        바이트 데이터로부터 HWP 문서 파싱

        참고: HWP 파일은 Compound File Binary (CFB) 형식을 따릅니다.
        주요 스트림:
        - FileHeader: 파일 인식 정보 (문서 버전, 압축 여부 등)
        - DocInfo: 문서 정보 (글꼴, 글자 모양, 문단 모양 등)
        - BodyText: 본문 데이터 (문단, 표, 개체 등)
        """
        # CFB 파일 열기
        ole = olefile.OleFileIO(data)

        # 1. 헤더 파싱
        header_stream = ole.openstream('FileHeader')
        header = Header.from_stream(header_stream)

        # 2. DocInfo 파싱 (글자 모양 정보)
        char_shapes = {}
        if ole.exists('DocInfo'):
            docinfo_stream = ole.openstream('DocInfo')
            docinfo_data = docinfo_stream.read()
            
            # 압축 해제
            if header.flags.compressed:
                try:
                    docinfo_data = zlib.decompress(docinfo_data, -zlib.MAX_WBITS)
                except zlib.error:
                    pass
            
            # CHAR_SHAPE 레코드 파싱
            char_shapes = cls._parse_char_shapes(docinfo_data)

        # 3. 본문 파싱
        body = Body()

        # distributed 플래그에 따라 ViewText 또는 BodyText 사용
        # distributed: 배포용 문서 (텍스트만 포함)
        body_path_prefix = 'ViewText' if header.flags.distributed else 'BodyText'

        # 섹션 개수 확인
        section_idx = 0
        while True:
            section_path = f'{body_path_prefix}/Section{section_idx}'
            if not ole.exists(section_path):
                break

            # 섹션 스트림 열기
            section_stream = ole.openstream(section_path)
            section_data = section_stream.read()

            # 압축 해제 (필요시)
            if header.flags.compressed:
                try:
                    section_data = zlib.decompress(section_data, -zlib.MAX_WBITS)
                except zlib.error:
                    # 압축 해제 실패시 원본 데이터 사용
                    pass

            # 레코드 파싱
            section = cls._parse_section(section_data)
            body.sections.append(section)

            section_idx += 1

        ole.close()
        return cls(header=header, body=body, char_shapes=char_shapes)

    @staticmethod
    def _parse_char_shapes(docinfo_data: bytes) -> dict:
        """
        DocInfo 스트림에서 CHAR_SHAPE 레코드 파싱

        CHAR_SHAPE 레코드 구조:
        - 글꼴 ID (WORD, 2바이트)
        - 장평 (UINT8, 1바이트, 50~200%)
        - 자간 (INT8, 1바이트, -50~50%)
        - 글자 크기 (INT32, 4바이트, 포인트 단위)
        - 속성 플래그 (UINT32, 4바이트, 굵게/기울임/밑줄 등)
        """
        char_shapes = {}
        stream = io.BytesIO(docinfo_data)
        cursor = RecordStream(stream)
        all_records = cursor.read_all_records()
        
        char_shape_id = 0
        for record in all_records:
            if record.tag_id == RecordTag.HWPTAG_CHAR_SHAPE:
                try:
                    # 글자 모양 데이터 파싱 (최소 72바이트)
                    if len(record.data) >= 56:
                        # 기준 크기 (offset 42, INT32, 포인트 * 100)
                        base_size = struct.unpack('<i', record.data[42:46])[0]
                        font_size = base_size / 100.0 if base_size > 0 else 10.0
                        
                        # 속성 (offset 46, UINT32, bit flags)
                        attr = struct.unpack('<I', record.data[46:50])[0]
                        bold = (attr & 0x1) != 0
                        italic = (attr & 0x2) != 0
                        underline = (attr & 0x4) != 0
                        
                        # 한글 글꼴 ID (offset 0, WORD)
                        font_id = struct.unpack('<H', record.data[0:2])[0]
                        
                        # 한글 장평 (offset 14, UINT8)
                        if len(record.data) > 20:
                            expansion = record.data[14]
                        else:
                            expansion = 100
                        
                        # 한글 자간 (offset 21, INT8)
                        if len(record.data) > 27:
                            spacing = struct.unpack('<b', bytes([record.data[21]]))[0]
                        else:
                            spacing = 0
                        
                        # 글자 색상 (offset 52, COLORREF)
                        color = struct.unpack('<I', record.data[52:56])[0] if len(record.data) >= 56 else 0
                        
                        char_shapes[char_shape_id] = CharShapeInfo(
                            font_size=font_size,
                            font_id=font_id,
                            bold=bold,
                            italic=italic,
                            underline=underline,
                            expansion=expansion,
                            spacing=spacing,
                            color=color
                        )
                        char_shape_id += 1
                except (struct.error, IndexError):
                    # 파싱 실패 시 기본값 사용
                    char_shapes[char_shape_id] = CharShapeInfo()
                    char_shape_id += 1
        
        return char_shapes

    @staticmethod
    def _parse_section(section_data: bytes) -> Section:
        """
        BodyText 스트림의 Section 데이터 파싱

        Section 데이터 구조:
        - 문단 (HWPTAG_PARA_HEADER, HWPTAG_PARA_TEXT 등)
        - 표, 개체 등 (HWPTAG_TABLE, HWPTAG_SHAPE_COMPONENT 등)
        """
        section = Section()
        stream = io.BytesIO(section_data)
        cursor = RecordStream(stream)

        # 모든 레코드 읽기
        all_records = cursor.read_all_records()

        # 단락 단위로 그룹화 (PARA_HEADER로 시작)
        current_para_records = []
        table_info_list = []  # 모든 테이블 정보 (리스트)
        current_table_idx = None  # 현재 처리 중인 테이블 인덱스

        for idx, record in enumerate(all_records):
            # 테이블 관련 레코드 파싱
            if record.tag_id == RecordTag.HWPTAG_CTRL_HEADER:
                # Control ID 확인 (TABLE = 0x74626C20)
                if len(record.data) >= 4:
                    ctrl_id = struct.unpack('<I', record.data[0:4])[0]
                    if ctrl_id == ControlID.TABLE:
                        # 새 테이블 항목 생성
                        table_info_list.append({
                            'ctrl_id': ctrl_id,
                            'idx': idx,
                            'level': record.level,
                            'cell_para_counts': []  # 각 셀의 문단 개수 배열
                        })
                        current_table_idx = len(table_info_list) - 1
                else:
                    current_table_idx = None
            
            elif record.tag_id == RecordTag.HWPTAG_SHAPE_COMPONENT:
                # 테이블 위치/크기/여백 정보 (46+ bytes)
                # SHAPE_COMPONENT는 현재 테이블에 속함
                if current_table_idx is not None and len(record.data) >= 46:
                    # Offset 8: Y position (HWPUNIT, 4 bytes)
                    y = struct.unpack('<i', record.data[8:12])[0]
                    # Offset 12: X position (HWPUNIT, 4 bytes)
                    x = struct.unpack('<i', record.data[12:16])[0]
                    # Offset 16: Width (HWPUNIT, 4 bytes)
                    width = struct.unpack('<I', record.data[16:20])[0]
                    # Offset 20: Height (HWPUNIT, 4 bytes)
                    height = struct.unpack('<I', record.data[20:24])[0]
                    # Offset 28: Margins (HWPUNIT16 array[4], 8 bytes)
                    margins = struct.unpack('<hhhh', record.data[28:36])
                    margin_left, margin_right, margin_top, margin_bottom = margins
                    
                    # 첫 번째 SHAPE_COMPONENT만 사용 (중복 방지)
                    if 'width' not in table_info_list[current_table_idx]:
                        table_info_list[current_table_idx].update({
                            'x': x, 'y': y,
                            'width': width, 'height': height,
                            'margin_left': margin_left, 'margin_right': margin_right,
                            'margin_top': margin_top, 'margin_bottom': margin_bottom
                        })
            
            elif record.tag_id == RecordTag.HWPTAG_LIST_HEADER:
                # LIST_HEADER 구조: 문단 개수(2) + 속성(4) + 패딩?(1) + 셀 속성(26)
                if current_table_idx is not None:
                    # 문단 개수 (각 셀마다 하나씩)
                    para_count = struct.unpack('<H', record.data[0:2])[0]
                    table_info_list[current_table_idx]['cell_para_counts'].append(para_count)
                    
                    # 셀 속성은 offset 7부터 시작 (6 bytes header + 1 byte padding)
                    cell_attr_offset = 7
                    if len(record.data) >= cell_attr_offset + 26:
                        # 표 80: 셀 속성 (26 bytes)
                        col = struct.unpack('<H', record.data[cell_attr_offset+1:cell_attr_offset+3])[0]
                        row = struct.unpack('<H', record.data[cell_attr_offset+3:cell_attr_offset+5])[0]
                        colspan = struct.unpack('<H', record.data[cell_attr_offset+5:cell_attr_offset+7])[0]
                        rowspan = struct.unpack('<H', record.data[cell_attr_offset+7:cell_attr_offset+9])[0]
                        width = struct.unpack('<I', record.data[cell_attr_offset+9:cell_attr_offset+13])[0]
                        height = struct.unpack('<I', record.data[cell_attr_offset+13:cell_attr_offset+17])[0]
                        
                        # 유효성 검사: col, row가 테이블 크기 내에 있는지
                        table_info = table_info_list[current_table_idx]
                        rows = table_info.get('rows', 999)
                        cols = table_info.get('cols', 999)
                        
                        if col < cols and row < rows:
                            # 셀별 크기 정보를 table_info에 추가
                            if 'cell_widths' not in table_info:
                                table_info['cell_widths'] = []
                                table_info['cell_heights'] = []
                                table_info['cell_colspans'] = []
                                table_info['cell_rowspans'] = []
                            
                            table_info['cell_widths'].append(width)
                            table_info['cell_heights'].append(height)
                            table_info['cell_colspans'].append(colspan)
                            table_info['cell_rowspans'].append(rowspan)
            
            elif record.tag_id == RecordTag.HWPTAG_TABLE:
                # 테이블 행/열 정보 및 Row Size 배열 파싱
                # Offset 0: 속성 (4 bytes), Offset 4: RowCount (2 bytes), Offset 6: nCols (2 bytes)
                # Offset 8: CellSpacing (2 bytes), Offset 10: 안쪽 여백 (8 bytes)
                # Offset 18: Row Size 배열 (2×rows bytes)
                if current_table_idx is not None and len(record.data) >= 10:
                    table_attr = struct.unpack('<I', record.data[0:4])[0]
                    rows = struct.unpack('<H', record.data[4:6])[0]
                    cols = struct.unpack('<H', record.data[6:8])[0]
                    cell_spacing = struct.unpack('<h', record.data[8:10])[0]
                    
                    # print(f"[DEBUG] HWPTAG_TABLE: table_idx={current_table_idx}, data_len={len(record.data)}")
                    # print(f"  attr={table_attr:08x}, rows={rows}, cols={cols}, spacing={cell_spacing}")
                    
                    if rows > 0 and cols > 0 and rows < 1000 and cols < 1000:
                        # Row Size 배열 파싱 (offset 18, 2 bytes × rows)
                        row_size_offset = 18
                        row_sizes = []
                        if len(record.data) >= row_size_offset + (2 * rows):
                            for i in range(rows):
                                offset = row_size_offset + (i * 2)
                                row_size = struct.unpack('<H', record.data[offset:offset+2])[0]
                                row_sizes.append(row_size)
                        
                        table_info_list[current_table_idx].update({
                            'rows': rows, 
                            'cols': cols,
                            'cell_spacing': cell_spacing,
                            'table_attr': table_attr,
                            'row_sizes': row_sizes if row_sizes else None,
                        })

            # 단락 그룹화
            if record.tag_id == RecordTag.HWPTAG_PARA_HEADER:
                # 이전 단락 완성
                if current_para_records:
                    paragraph = Paragraph.from_records(current_para_records)
                    section.paragraphs.append(paragraph)

                # 새 단락 시작
                current_para_records = [record]
            else:
                current_para_records.append(record)

        # 마지막 단락 추가
        if current_para_records:
            paragraph = Paragraph.from_records(current_para_records)
            section.paragraphs.append(paragraph)

        # 테이블 메타데이터 저장 (리스트)
        section.table_metadata = table_info_list

        return section

    def to_text(self) -> str:
        """HWP 문서를 텍스트로 변환"""
        return self.body.to_string()

@dataclass
class CharShapeInfo:
    """문자 서식 정보 (HWPTAG_CHAR_SHAPE 기반)"""
    font_size: float = 10.0  # 포인트 단위 (기준 크기 / 100)
    font_id: int = 0  # 한글 글꼴 ID (언어별 7개 중 첫번째)
    bold: bool = False  # 굵게
    italic: bool = False  # 기울임
    underline: bool = False  # 밑줄
    expansion: int = 100  # 장평 (50~200, 기본 100%)
    spacing: int = 0  # 자간 (-50~50, 기본 0%)
    color: int = 0x00000000  # RGB 색상 (0x00bbggrr)