"""
문자 및 문단 구조

이 모듈은 HWP 파일의 문자(Char)와 문단(Paragraph) 데이터를 처리하는 데 사용됩니다.
HWP 파일의 구조를 분석하고, 각 문자의 타입과 데이터를 파싱하여 문자열로 변환하거나,
문단 데이터를 재구성하는 기능을 제공합니다.

참고: 한글문서파일형식_5.0_revision1.3.txt
"""

import io
import struct
from dataclasses import dataclass, field
from enum import Enum
from typing import BinaryIO, List, Optional, Tuple

from .constants import (
    CharConstants,
    CharControlCode,
    ExtendedControlCode,
    PageBreakType,
    ParagraphConstants,
    RecordTag,
)
from .models import Record


class CharType(Enum):
    """문자 타입 정의 (HWP 파일의 문자 데이터 구분)"""
    CHAR_CODE = "char_code"  # 일반 유니코드 문자
    CHAR_CONTROL = "char_control"  # 제어 문자 (줄바꿈, 공백 등)
    INLINE_CONTROL = "inline_control"  # 인라인 제어 코드
    EXTENDED_CONTROL = "extended_control"  # 확장 제어 코드 (테이블, 이미지 등)


@dataclass
class Char:
    """HWP 문자 클래스"""
    char_type: CharType  # 문자 타입
    code: int  # 문자 코드
    control_data: Optional[bytes] = None  # 제어 코드 데이터 (확장/인라인 제어용)

    @classmethod
    def read_from_stream(cls, stream: BinaryIO) -> Optional['Char']:
        """
        스트림에서 문자 데이터를 읽어 Char 객체 생성

        Args:
            stream (BinaryIO): 바이너리 스트림

        Returns:
            Optional[Char]: Char 객체 또는 None (스트림 끝)

        참고:
        - HWP 파일의 문자 데이터는 2바이트로 저장됩니다.
        - 제어 문자는 추가 데이터를 포함할 수 있습니다.
        """
        code_bytes = stream.read(2)
        if len(code_bytes) < 2:
            return None

        code = struct.unpack('<H', code_bytes)[0]

        # 일반 문자 처리
        if code > CharConstants.CONTROL_BOUNDARY:
            return cls(char_type=CharType.CHAR_CODE, code=code)

        # 제어 문자 처리
        char_controls = [
            CharControlCode.UNUSABLE,
            CharControlCode.LINE_BREAK,
            CharControlCode.PARA_BREAK,
            CharControlCode.HYPHEN,
            CharControlCode.RESERVED_25,
            CharControlCode.RESERVED_26,
            CharControlCode.RESERVED_27,
            CharControlCode.RESERVED_28,
            CharControlCode.RESERVED_29,
            CharControlCode.KEEP_WORD_SPACE,
            CharControlCode.FIXED_WIDTH_SPACE,
        ]
        if code in char_controls:
            return cls(char_type=CharType.CHAR_CONTROL, code=code)

        # 확장/인라인 제어 처리
        control_data = stream.read(CharConstants.CONTROL_DATA_SIZE)
        code_repeat = struct.unpack('<H', stream.read(2))[0]

        if code != code_repeat:
            raise ValueError(f"Control code mismatch: {code} != {code_repeat}")

        extended_codes = [
            ExtendedControlCode.TABLE,
            ExtendedControlCode.PICTURE,
            ExtendedControlCode.OLE,
            ExtendedControlCode.EQUATION,
            ExtendedControlCode.FOOTNOTE,
            ExtendedControlCode.ENDNOTE,
            ExtendedControlCode.HYPERLINK,
            ExtendedControlCode.FOOTNOTE_OR_ENDNOTE,
            ExtendedControlCode.HEADER_OR_FOOTER,
            ExtendedControlCode.COMMENT,
            ExtendedControlCode.SHAPE,
            ExtendedControlCode.SHAPE_COMPONENT,
        ]
        if code in extended_codes:
            return cls(char_type=CharType.EXTENDED_CONTROL, code=code, control_data=control_data)
        else:
            return cls(char_type=CharType.INLINE_CONTROL, code=code, control_data=control_data)

    def to_string(self) -> str:
        """
        Char 객체를 문자열로 변환

        Returns:
            str: 변환된 문자열

        참고:
        - 일반 문자는 유니코드로 변환됩니다.
        - 제어 문자는 줄바꿈, 공백 등으로 변환됩니다.
        """
        if self.char_type == CharType.CHAR_CODE:
            try:
                if CharConstants.SURROGATE_START <= self.code <= CharConstants.SURROGATE_END:
                    return ""
                return chr(self.code)
            except (ValueError, OverflowError):
                return ""
        elif self.char_type == CharType.CHAR_CONTROL:
            if self.code == CharControlCode.LINE_BREAK:
                return "\n"
            elif self.code == CharControlCode.PARA_BREAK:
                return "\n"
            elif self.code in (CharControlCode.KEEP_WORD_SPACE, CharControlCode.FIXED_WIDTH_SPACE):
                return " "
            return ""
        else:
            return ""


@dataclass
class Paragraph:
    """HWP 문단 클래스"""
    chars: List[Char] = field(default_factory=list)  # 문단 내 문자 리스트
    page_break_type: int = 0  # 페이지 나누기 타입 (0: 일반, 1: 단 나누기, 2: 쪽 나누기, 3: 구역 나누기)
    char_shape_id: Optional[int] = None  # 문단 첫 글자의 글자 모양 ID
    char_shape_ids: List[Tuple[int, int]] = field(default_factory=list)  # 글자별 모양 ID 리스트
    is_page_first_line: bool = False  # 페이지 첫 줄 여부
    ctrl_headers: List[Tuple[int, bytes]] = field(default_factory=list)  # 컨트롤 헤더 리스트
    ctrl_data: List[bytes] = field(default_factory=list)  # 컨트롤 데이터 리스트

    @classmethod
    def from_records(cls, records: List[Record]) -> 'Paragraph':
        """
        레코드 리스트로부터 Paragraph 객체 생성

        Args:
            records (List[Record]): 레코드 리스트

        Returns:
            Paragraph: 생성된 Paragraph 객체

        참고:
        - HWP 문단은 여러 레코드로 구성됩니다.
        - 각 레코드는 문단 헤더, 텍스트, 글자 모양, 컨트롤 데이터 등을 포함합니다.
        """
        paragraph = cls()

        for record in records:
            if record.tag_id == RecordTag.HWPTAG_PARA_HEADER:
                if len(record.data) >= ParagraphConstants.MIN_HEADER_SIZE:
                    paragraph.page_break_type = record.data[ParagraphConstants.PAGE_BREAK_TYPE_OFFSET]
            elif record.tag_id == RecordTag.HWPTAG_PARA_CHAR_SHAPE:
                data_len = len(record.data)
                for offset in range(0, data_len, 8):
                    if offset + 8 <= data_len:
                        position = struct.unpack('<I', record.data[offset:offset+4])[0]
                        shape_id = struct.unpack('<I', record.data[offset+4:offset+8])[0]
                        paragraph.char_shape_ids.append((position, shape_id))
                if paragraph.char_shape_ids:
                    paragraph.char_shape_id = paragraph.char_shape_ids[0][1]
            elif record.tag_id == RecordTag.HWPTAG_PARA_TEXT:
                stream = io.BytesIO(record.data)
                while True:
                    char = Char.read_from_stream(stream)
                    if char is None:
                        break
                    paragraph.chars.append(char)
            elif record.tag_id == RecordTag.HWPTAG_PARA_LINE_SEG:
                if len(record.data) >= 36:
                    tag_flags = struct.unpack('<I', record.data[32:36])[0]
                    paragraph.is_page_first_line = bool(tag_flags & 0x01)
            elif record.tag_id == RecordTag.HWPTAG_CTRL_HEADER:
                if len(record.data) >= 4:
                    ctrl_id = struct.unpack('<I', record.data[0:4])[0]
                    paragraph.ctrl_headers.append((ctrl_id, record.data))
            elif record.tag_id == RecordTag.HWPTAG_CTRL_DATA:
                paragraph.ctrl_data.append(record.data)

        return paragraph

    @property
    def is_page_break(self) -> bool:
        """페이지 나누기 여부 확인"""
        return self.page_break_type == PageBreakType.PAGE_BREAK

    @property
    def text(self) -> str:
        """문단 텍스트 반환"""
        return self.to_string()

    def to_string(self) -> str:
        """문단을 문자열로 변환"""
        return "".join(char.to_string() for char in self.chars)

    def __str__(self) -> str:
        """문자열 표현"""
        return self.to_string()