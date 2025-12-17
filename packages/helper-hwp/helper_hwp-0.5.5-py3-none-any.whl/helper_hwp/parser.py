"""
HWP 문서 파서 (고수준 API)

이 모듈은 한글(HWP) 문서 파일 형식 5.0 스펙을 참고하여 문서 구조(Section, Paragraph,
컨트롤 등)를 Pythonic하게 접근할 수 있도록 래핑한 고수준 API를 제공합니다.

참고:
- "한글문서파일형식_5.0_revision1.3.txt" (프로젝트 docs/) — HWP 5.0 스펙
  주요 참조 항목:
    * 본문(BodyText) / Section 스트림(표 5)
    * 문단 헤더(HWPTAG_PARA_HEADER) 및 문단 내 제어문자(표 58, 4.3.1 ~ 4.3.3)
    * 제어 문자 종류: char / inline control / extended control (본문 설명)
    * 컨트롤 헤더(HWPTAG_CTRL_HEADER)와 컨트롤 데이터 매핑(4.3.6)
    * 표(Table) 메타데이터: Section.table_metadata 사용(본문/스펙 참조)

설계 노트 (요약)
- 문단 내 제어문자: 코드 0-31 영역을 특수용도로 사용. (HWP 스펙 4.3)
  - Inline Control: 별도 오브젝트 포인터 미사용, size=8 (예: 쪽 번호)
  - Extended Control: 별도 오브젝트를 가리키는 확장 제어, size=8 (예: 표, 그림)
- 본 구현은 문단 수준에서 다음을 제공:
  - Paragraph 단위 텍스트/글자모양 추출 (ParsedParagraph)
  - Section 레벨의 테이블 메타데이터를 이용한 표(ParsedTable) 매핑
  - iter_tags()로 SEQUENTIAL / STRUCTURED 순회 지원

주의
- 주석/문서화만 추가했으며 코드 동작은 변경하지 않았습니다.
"""

import os
import struct
from typing import List, Optional, Union

from .char_paragraph import CharType, Paragraph
from .constants import (
    ControlID,
    ElementType,
    ExtendedControlCode,
    IterMode,
    ParagraphConstants,
)
from .document_structure import CharShapeInfo, HwpFile, Section
from .models import Version
from .parsed_elements import ParsedPage, ParsedParagraph, ParsedTable


class HwpDocument:
    """
    HWP 문서 - 고수준 Pythonic API

    이 클래스는 HwpFile 객체를 래핑하여 문서 요소(문단, 표, 페이지 구분 등)를
    쉽게 순회하고 추출할 수 있도록 합니다.

    주요 기능:
    - pages: 페이지 단위로 문단을 그룹화 (문단의 is_page_break 플래그 사용)
    - get_elements_by_type: ElementType 기반 요소 검색 (문단/표/쪽나누기 등)
    - iter_tags: 제너레이터 형태의 문서 태그 순회 (SEQUENTIAL / STRUCTURED)
    - to_text: 문서 전체 텍스트 추출

    구현 세부:
    - 글자 모양(char_shape) 추출은 paragraph.char_shape_ids(범위별 모양) 또는
      paragraph.char_shape_id(단일 모양)을 기준으로 하며, 여러 글자모양이 존재할 경우
      '최대(font_size 기준) 우선'으로 대표 값을 선택합니다. (스펙: DocInfo 내 CHAR_SHAPE)
    - 표(Table)는 본문(Section) 레벨의 table_metadata에서 상세 정보를 참조하여
      확장 제어(EXTENDED_CONTROL)로 나타나는 위치 기반 제어와 매핑합니다.
    """

    def __init__(self, file_path: str, iter_mode: IterMode = IterMode.SEQUENTIAL):
        """
        HWP 파일 로드

        Args:
            file_path: HWP 파일 경로
            iter_mode: 순회 모드 (SEQUENTIAL: 문서 출현 순서, STRUCTURED: 계층 구조)
        """
        self._hwp = HwpFile.from_file(file_path)
        self.file_path = file_path
        self.iter_mode = iter_mode

    @property
    def compressed(self) -> bool:
        """압축 여부"""
        return self._hwp.header.flags.compressed

    @property
    def encrypted(self) -> bool:
        """암호화 여부"""
        return self._hwp.header.flags.encrypted

    @property
    def pages(self) -> List[ParsedPage]:
        """페이지별로 그룹화된 문단 리스트

        동작:
        - 섹션을 순회하면서 문단을 누적
        - paragraph.is_page_break가 True이면 현재 페이지를 종료하고 다음 페이지로 이동
        - 각 문단에 대해 글자 모양 정보를 요약하여 ParsedParagraph로 반환
        """
        pages = []
        current_page_paragraphs = []
        page_number = 1

        for section in self.sections:
            for paragraph in section.paragraphs:
                para_text = paragraph.to_string().strip()
                # 빈 문단도 포함 (테이블 셀 구조 보존)
                # 글자 모양 정보 추출 (max 기준)
                char_shape = None
                char_shapes_list = []

                if paragraph.char_shape_ids:
                    all_shapes = []
                    for pos, shape_id in paragraph.char_shape_ids:
                        shape = self._hwp.char_shapes.get(shape_id)
                        if shape:
                            all_shapes.append(shape)
                            char_shapes_list.append((pos, shape))

                    if all_shapes:
                        # 여러 글자모양이 존재하면 대표값을 선택 (스펙/문서 정보 기반)
                        max_font_size = max(s.font_size for s in all_shapes)
                        max_expansion = max(s.expansion for s in all_shapes)
                        any_bold = any(s.bold for s in all_shapes)
                        any_italic = any(s.italic for s in all_shapes)
                        any_underline = any(s.underline for s in all_shapes)
                        char_shape = CharShapeInfo(
                            font_size=max_font_size,
                            font_id=all_shapes[0].font_id,
                            bold=any_bold,
                            italic=any_italic,
                            underline=any_underline,
                            expansion=max_expansion,
                            spacing=all_shapes[0].spacing,
                            color=all_shapes[0].color,
                        )
                elif paragraph.char_shape_id is not None:
                    # 단일 글자 모양 참조
                    char_shape = self._hwp.char_shapes.get(paragraph.char_shape_id)
                    if char_shape:
                        char_shapes_list = [(0, char_shape)]

                parsed_para = ParsedParagraph(
                    text=para_text,
                    paragraph=paragraph,
                    char_shape=char_shape,
                    char_shapes=char_shapes_list,
                )
                current_page_paragraphs.append(parsed_para)

                # 페이지 구분 체크 (쪽 나누기)
                # 스펙: 문단 내 페이지 제어는 인라인/확장 제어 또는 문단 속성으로 표현될 수 있음
                if paragraph.is_page_break:
                    if current_page_paragraphs:
                        pages.append(
                            ParsedPage(page_number=page_number, paragraphs=current_page_paragraphs)
                        )
                        current_page_paragraphs = []
                        page_number += 1

        # 마지막 페이지 추가
        if current_page_paragraphs:
            pages.append(ParsedPage(page_number=page_number, paragraphs=current_page_paragraphs))

        return pages

    @property
    def sections(self) -> List[Section]:
        """문서 섹션 리스트"""
        return self._hwp.body.sections

    @property
    def tags(self):
        """iter_tags()의 간편 접근 (기본 모드 사용)"""
        return self.iter_tags()

    @property
    def version(self) -> Version:
        """문서 버전"""
        return self._hwp.header.version

    def get_elements_by_type(self, element_type: Union[ElementType, str]) -> List:
        """
        문서 내 특정 타입의 요소를 검색 (HWP 5.0 스펙 기반)

        설명:
        - element_type이 'paragraph'인 경우 문단 단위로 순회하여 ParsedParagraph 리스트 반환
        - 'table'인 경우 Section.table_metadata를 사용하여 문서에 저장된 테이블 메타데이터를 읽어 반환
        - 'page_break'는 paragraph.is_page_break 기반으로 검사

        주의:
        - 표(Table)는 확장 제어(문단 내 EXTENDED_CONTROL)로도 존재할 수 있으며,
          본 메서드는 문서에 저장된 메타데이터 중심으로 결과를 구성합니다.

        Args:
            element_type: 검색할 요소 타입
                - ElementType.PARAGRAPH 또는 'paragraph': 문단 (HWPTAG_PARA_HEADER)
                - ElementType.TABLE 또는 'table': 표 (HWPTAG_TABLE)
                - ElementType.PAGE_BREAK 또는 'page_break': 페이지 구분 (쪽 나누기)
                - ElementType.PICTURE 또는 'picture': 그림
                - ElementType.EQUATION 또는 'equation': 수식 (미구현)
                - ElementType.FOOTNOTE 또는 'footnote': 각주 (미구현)
                - ElementType.ENDNOTE 또는 'endnote': 미주 (미구현)
                - ElementType.HEADER 또는 'header': 머리글 (미구현)
                - ElementType.FOOTER 또는 'footer': 바닥글 (미구현)
                - ElementType.CAPTION 또는 'caption': 캡션 (미구현)

        Returns:
            검색된 요소 리스트

        Examples:
            >>> doc.get_elements_by_type(ElementType.PARAGRAPH)
            >>> doc.get_elements_by_type('paragraph')  # 하위 호환
            >>> doc.get_elements_by_type(ElementType.PAGE_BREAK)  # 페이지 구분자 검색
        """
        # 문자열 입력 시 Enum으로 변환
        if isinstance(element_type, str):
            element_type = ElementType.from_string(element_type)

        results = []

        if element_type == ElementType.PARAGRAPH:
            # 모든 문단 검색
            for section in self.sections:
                for paragraph in section.paragraphs:
                    para_text = paragraph.to_string().strip()
                    # 빈 문단도 포함 (테이블 셀 구조 보존)
                    # 글자 모양 정보 추출 (max 기준)
                    char_shape = None
                    char_shapes_list = []

                    if paragraph.char_shape_ids:
                        all_shapes = []
                        for pos, shape_id in paragraph.char_shape_ids:
                            shape = self._hwp.char_shapes.get(shape_id)
                            if shape:
                                all_shapes.append(shape)
                                char_shapes_list.append((pos, shape))

                        if all_shapes:
                            max_font_size = max(s.font_size for s in all_shapes)
                            max_expansion = max(s.expansion for s in all_shapes)
                            any_bold = any(s.bold for s in all_shapes)
                            any_italic = any(s.italic for s in all_shapes)
                            any_underline = any(s.underline for s in all_shapes)
                            char_shape = CharShapeInfo(
                                font_size=max_font_size,
                                font_id=all_shapes[0].font_id,
                                bold=any_bold,
                                italic=any_italic,
                                underline=any_underline,
                                expansion=max_expansion,
                                spacing=all_shapes[0].spacing,
                                color=all_shapes[0].color,
                            )
                    elif paragraph.char_shape_id is not None:
                        char_shape = self._hwp.char_shapes.get(paragraph.char_shape_id)
                        if char_shape:
                            char_shapes_list = [(0, char_shape)]

                    results.append(
                        ParsedParagraph(
                            text=para_text,
                            paragraph=paragraph,
                            char_shape=char_shape,
                            char_shapes=char_shapes_list,
                        )
                    )

        elif element_type == ElementType.TABLE:
            # 테이블 검색 (table_metadata 직접 사용)
            # 스펙: Section.stream의 HWPTAG_TABLE / 컨트롤 헤더와 연계된 표 객체 정보
            table_counter = 0
            for section_idx, section in enumerate(self.sections):
                for table_idx, info in enumerate(section.table_metadata):
                    # section.table_metadata는 본 구현의 내부 표현(스펙의 표 메타데이터를 파싱한 결과)
                    if info.get("ctrl_id") == ControlID.TABLE:
                        table_counter += 1
                        table = ParsedTable(
                            code=ExtendedControlCode.TABLE,
                            data=None,
                            control_id=info.get("ctrl_id"),
                            x=info.get("x"),
                            y=info.get("y"),
                            width=info.get("width"),
                            height=info.get("height"),
                            margin_left=info.get("margin_left"),
                            margin_right=info.get("margin_right"),
                            margin_top=info.get("margin_top"),
                            margin_bottom=info.get("margin_bottom"),
                            rows=info.get("rows"),
                            cols=info.get("cols"),
                            cell_count=(
                                info.get("cell_para_counts", [])[-1]
                                if info.get("cell_para_counts")
                                else None
                            ),
                            cell_para_counts=info.get("cell_para_counts"),
                            cell_spacing=info.get("cell_spacing"),
                            row_sizes=info.get("row_sizes"),
                            cell_widths=info.get("cell_widths"),
                            cell_heights=info.get("cell_heights"),
                            cell_colspans=info.get("cell_colspans"),
                            cell_rowspans=info.get("cell_rowspans"),
                            table_index=table_counter,
                        )
                        results.append(table)

        elif element_type == ElementType.PAGE_BREAK:
            # 페이지 구분자 검색 (쪽 나누기)
            for section in self.sections:
                for paragraph in section.paragraphs:
                    if paragraph.is_page_break:
                        results.append(
                            ParsedParagraph(text=paragraph.to_string().strip(), paragraph=paragraph)
                        )

        else:
            # 다른 타입은 아직 미구현
            pass

        return results

    def iter_tags(self, mode: Optional[IterMode] = None):
        """
        문서 요소를 순회하는 제너레이터 (속도 우선)

        mode:
          - IterMode.SEQUENTIAL: 문서 출현 순서 기반 순회 (빠름, 기본)
          - IterMode.STRUCTURED: Section → Paragraph → Char 계층 구조로 상세 순회

        반환:
          (ElementType, ParsedElement) 튜플을 순차적으로 yield

        구현 참고:
        - SEQUENTIAL 모드는 문단 단위로 먼저 yield하고, 문단 내부의 문자(char)들을 검사하여
          인라인/확장 제어를 추가적으로 yield합니다.
        - STRUCTURED 모드는 구조적(계층적) 순회를 수행하여 각 섹션/문단/문자 위치 정보를 유지합니다.

        Examples:
            >>> for element_type, element in hwp.iter_tags():
            ...     if element_type == ElementType.PARAGRAPH:
            ...         print(element.text)
            ...     elif element_type == ElementType.TABLE:
            ...         print(f"표: {element.code}")
        """
        mode = mode or self.iter_mode

        if mode == IterMode.SEQUENTIAL:
            yield from self._iter_sequential()
        else:
            yield from self._iter_structured()

    def _iter_sequential(self):
        """SEQUENTIAL 모드: 문서 출현 순서 (속도 우선)

        동작 요약:
        - 문단 단위로 ParsedParagraph를 yield
        - 문단 내부의 chars를 검사하여 Inline/Extended control을 ElementType별로 yield
        - 표(Table)는 paragraph 내 확장 제어와 Section.table_metadata의 매핑을 통해 table_index를 부여
        """

        table_counter = 0  # 테이블 순서 추적

        # 섹션별 테이블 메타데이터를 미리 리스트로 구성
        # 목적: 문단 내 확장 제어를 발견했을 때 table_metadata와 매칭하여 상세 정보 제공
        all_table_metadata = []
        for section in self.sections:
            for info in section.table_metadata:
                if info.get("ctrl_id") == ControlID.TABLE:
                    all_table_metadata.append(info)

        for section in self.sections:
            for paragraph in section.paragraphs:
                # 페이지 구분 체크
                if paragraph.is_page_break:
                    yield (
                        ElementType.PAGE_BREAK,
                        ParsedParagraph(text=paragraph.to_string().strip(), paragraph=paragraph),
                    )

                # 문단 텍스트
                para_text = paragraph.to_string().strip()
                # 빈 문단도 포함 (테이블 셀 구조 보존)
                # 글자 모양 정보 추출 (max 기준)
                char_shape = None
                char_shapes_list = []

                if paragraph.char_shape_ids:
                    all_shapes = []
                    for pos, shape_id in paragraph.char_shape_ids:
                        shape = self._hwp.char_shapes.get(shape_id)
                        if shape:
                            all_shapes.append(shape)
                            char_shapes_list.append((pos, shape))

                    if all_shapes:
                        max_font_size = max(s.font_size for s in all_shapes)
                        max_expansion = max(s.expansion for s in all_shapes)
                        any_bold = any(s.bold for s in all_shapes)
                        any_italic = any(s.italic for s in all_shapes)
                        any_underline = any(s.underline for s in all_shapes)
                        char_shape = CharShapeInfo(
                            font_size=max_font_size,
                            font_id=all_shapes[0].font_id,
                            bold=any_bold,
                            italic=any_italic,
                            underline=any_underline,
                            expansion=max_expansion,
                            spacing=all_shapes[0].spacing,
                            color=all_shapes[0].color,
                        )
                elif paragraph.char_shape_id is not None:
                    char_shape = self._hwp.char_shapes.get(paragraph.char_shape_id)
                    if char_shape:
                        char_shapes_list = [(0, char_shape)]

                yield (
                    ElementType.PARAGRAPH,
                    ParsedParagraph(
                        text=para_text,
                        paragraph=paragraph,
                        char_shape=char_shape,
                        char_shapes=char_shapes_list,
                    ),
                )

                # 인라인 제어 및 확장 제어 (테이블, 그림, 수식, 쪽 번호 등)
                # 스펙: 문단 내 제어문자는 char.char_type으로 구분 (CharType.INLINE_CONTROL / EXTENDED_CONTROL)
                for char in paragraph.chars:
                    # 인라인 제어 문자 처리 (쪽 번호 등)
                    if char.char_type == CharType.INLINE_CONTROL:
                        from .constants import InlineControlCode

                        # InlineControlCode.PAGE_NUMBER (19) 처리
                        if char.code == InlineControlCode.PAGE_NUMBER:
                            yield (
                                ElementType.AUTO_NUMBER,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=None
                                ),
                            )

                    elif char.char_type == CharType.EXTENDED_CONTROL:
                        # control_data의 첫 4바이트에서 Control ID 추출
                        # (스펙: CTRL_HEADER 또는 확장 제어의 첫 필드에 컨트롤 ID 포함)
                        control_id = None
                        if (
                            char.control_data
                            and len(char.control_data) >= ParagraphConstants.CONTROL_ID_SIZE
                        ):
                            control_id = struct.unpack(
                                "<I", char.control_data[0 : ParagraphConstants.CONTROL_ID_SIZE]
                            )[0]

                        # 컨트롤 ID / 코드 기반으로 타입 결정 및 yield
                        # 일부 컨트롤은 ctrl_headers(문단의 CTRL_HEADER 레코드)로도 존재하므로
                        # 둘을 모두 처리해야 정확한 매핑이 됨.
                        if control_id == ControlID.AUTO_NUMBER:
                            yield (
                                ElementType.AUTO_NUMBER,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        # 쪽 번호 위치 컨트롤 ('pgnp')
                        elif control_id == ControlID.PAGE_NUM_POS:
                            yield (
                                ElementType.PAGE_NUM_POS,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        # 머리말 컨트롤 ('head')
                        elif control_id == ControlID.HEADER:
                            yield (
                                ElementType.HEADER,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        # 꼬리말 컨트롤 ('foot')
                        elif control_id == ControlID.FOOTER:
                            yield (
                                ElementType.FOOTER,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        # Control ID 기반 타입 결정
                        elif (
                            control_id == ControlID.TABLE or char.code == ExtendedControlCode.TABLE
                        ):
                            # 표 발견: table_metadata에서 상세 정보를 찾아 매핑
                            table_counter += 1

                            # table_metadata에서 상세 정보 찾기
                            table_info = (
                                all_table_metadata[table_counter - 1]
                                if table_counter <= len(all_table_metadata)
                                else {}
                            )

                            table = ParsedTable(
                                code=char.code,
                                data=char.control_data,
                                control_id=control_id,
                                table_index=table_counter,
                                x=table_info.get("x"),
                                y=table_info.get("y"),
                                width=table_info.get("width"),
                                height=table_info.get("height"),
                                margin_left=table_info.get("margin_left"),
                                margin_right=table_info.get("margin_right"),
                                margin_top=table_info.get("margin_top"),
                                margin_bottom=table_info.get("margin_bottom"),
                                rows=table_info.get("rows"),
                                cols=table_info.get("cols"),
                                cell_count=(
                                    table_info.get("cell_para_counts", [])[-1]
                                    if table_info.get("cell_para_counts")
                                    else None
                                ),
                                cell_para_counts=table_info.get("cell_para_counts"),
                                cell_spacing=table_info.get("cell_spacing"),
                                row_sizes=table_info.get("row_sizes"),
                                cell_widths=table_info.get("cell_widths"),
                                cell_heights=table_info.get("cell_heights"),
                                cell_colspans=table_info.get("cell_colspans"),
                                cell_rowspans=table_info.get("cell_rowspans"),
                            )
                            yield (ElementType.TABLE, table)
                        elif char.code == ExtendedControlCode.PICTURE:
                            yield (
                                ElementType.PICTURE,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.OLE:
                            yield (
                                ElementType.OLE,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.EQUATION:
                            yield (
                                ElementType.EQUATION,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.FOOTNOTE:
                            yield (
                                ElementType.FOOTNOTE,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.ENDNOTE:
                            yield (
                                ElementType.ENDNOTE,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.HYPERLINK:
                            yield (
                                ElementType.HYPERLINK,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.COMMENT:
                            yield (
                                ElementType.COMMENT,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.SHAPE:
                            yield (
                                ElementType.SHAPE,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        else:
                            # 기타 확장 제어는 SHAPE_COMPONENT로 처리(기본 매핑)
                            yield (
                                ElementType.SHAPE_COMPONENT,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )

                # 문단 내 ctrl_headers 확인 (확장 제어에 대응하는 CTRL_HEADER 레코드)
                # 스펙: 컨트롤 헤더 레코드는 문단에 대응하는 별도의 레코드로 저장될 수 있으며,
                # 이 데이터는 컨트롤의 초기 데이터(예: 자동 번호, 머리말/꼬리말 등)를 포함.
                for ctrl_id, ctrl_header_data in paragraph.ctrl_headers:
                    # 자동 번호 컨트롤 ('atno')
                    if ctrl_id == ControlID.AUTO_NUMBER:
                        yield (
                            ElementType.AUTO_NUMBER,
                            ParsedTable(
                                code=21,  # 페이지 컨트롤 코드 (문서 표현상 코드 표기)
                                data=ctrl_header_data[4:],  # 컨트롤 ID 이후 데이터
                                control_id=ctrl_id,
                            ),
                        )
                    # 새 번호 지정 컨트롤 ('nwno')
                    elif ctrl_id == ControlID.NEW_NUMBER:
                        yield (
                            ElementType.NEW_NUMBER,
                            ParsedTable(code=21, data=ctrl_header_data[4:], control_id=ctrl_id),
                        )
                    # 쪽 번호 위치 컨트롤 ('pgnp')
                    elif ctrl_id == ControlID.PAGE_NUM_POS:
                        yield (
                            ElementType.PAGE_NUM_POS,
                            ParsedTable(code=21, data=ctrl_header_data[4:], control_id=ctrl_id),
                        )
                    # 머리말 컨트롤 ('head')
                    elif ctrl_id == ControlID.HEADER:
                        yield (
                            ElementType.HEADER,
                            ParsedTable(
                                code=16,  # 머리말/꼬리말 코드
                                data=ctrl_header_data[4:],
                                control_id=ctrl_id,
                            ),
                        )
                    # 꼬리말 컨트롤 ('foot')
                    elif ctrl_id == ControlID.FOOTER:
                        yield (
                            ElementType.FOOTER,
                            ParsedTable(code=16, data=ctrl_header_data[4:], control_id=ctrl_id),
                        )

    def _iter_structured(self):
        """STRUCTURED 모드: Section → Paragraph → Char 계층 구조

        동작:
        - 각 섹션을 시작으로 섹션 레벨 이벤트를 yield
        - 문단을 yield 한 뒤 문단 내부의 문자(특히 EXTENDED_CONTROL)를 위치 정보와 함께 yield
        - 테이블 메타데이터와의 매칭을 통해 표 정보를 제공
        """
        table_counter = 0  # 테이블 순서 추적

        # 섹션별 테이블 메타데이터를 미리 리스트로 구성
        all_table_metadata = []
        for section in self.sections:
            for info in section.table_metadata:
                if info.get("ctrl_id") == ControlID.TABLE:
                    all_table_metadata.append(info)

        for section_idx, section in enumerate(self.sections):
            yield (
                ElementType.SECTION,
                ParsedParagraph(text=f"[Section {section_idx}]", paragraph=Paragraph()),
            )

            for para_idx, paragraph in enumerate(section.paragraphs):
                # 페이지 구분
                if paragraph.is_page_break:
                    yield (
                        ElementType.PAGE_BREAK,
                        ParsedParagraph(
                            text=f"[Section {section_idx}, Para {para_idx}] PAGE_BREAK",
                            paragraph=paragraph,
                        ),
                    )

                # 문단
                para_text = paragraph.to_string().strip()
                # 빈 문단도 포함 (테이블 셀 구조 보존)
                # 글자 모양 정보 추출 (max 기준)
                char_shape = None
                char_shapes_list = []

                if paragraph.char_shape_ids:
                    all_shapes = []
                    for pos, shape_id in paragraph.char_shape_ids:
                        shape = self._hwp.char_shapes.get(shape_id)
                        if shape:
                            all_shapes.append(shape)
                            char_shapes_list.append((pos, shape))

                    if all_shapes:
                        max_font_size = max(s.font_size for s in all_shapes)
                        max_expansion = max(s.expansion for s in all_shapes)
                        any_bold = any(s.bold for s in all_shapes)
                        any_italic = any(s.italic for s in all_shapes)
                        any_underline = any(s.underline for s in all_shapes)
                        char_shape = CharShapeInfo(
                            font_size=max_font_size,
                            font_id=all_shapes[0].font_id,
                            bold=any_bold,
                            italic=any_italic,
                            underline=any_underline,
                            expansion=max_expansion,
                            spacing=all_shapes[0].spacing,
                            color=all_shapes[0].color,
                        )
                elif paragraph.char_shape_id is not None:
                    char_shape = self._hwp.char_shapes.get(paragraph.char_shape_id)
                    if char_shape:
                        char_shapes_list = [(0, char_shape)]

                yield (
                    ElementType.PARAGRAPH,
                    ParsedParagraph(
                        text=para_text,
                        paragraph=paragraph,
                        char_shape=char_shape,
                        char_shapes=char_shapes_list,
                    ),
                )

                # 문단 내 문자별 확장 제어
                for char_idx, char in enumerate(paragraph.chars):
                    if char.char_type == CharType.EXTENDED_CONTROL:
                        # control_data의 첫 4바이트에서 Control ID 추출
                        control_id = None
                        if (
                            char.control_data
                            and len(char.control_data) >= ParagraphConstants.CONTROL_ID_SIZE
                        ):
                            control_id = struct.unpack(
                                "<I", char.control_data[0 : ParagraphConstants.CONTROL_ID_SIZE]
                            )[0]

                        # Control ID 기반 타입 결정
                        if control_id == ControlID.TABLE:
                            table_counter += 1

                            # table_metadata에서 상세 정보 찾기
                            table_info = (
                                all_table_metadata[table_counter - 1]
                                if table_counter <= len(all_table_metadata)
                                else {}
                            )

                            yield (
                                ElementType.TABLE,
                                ParsedTable(
                                    code=char.code,
                                    data=char.control_data,
                                    control_id=control_id,
                                    table_index=table_counter,
                                    x=table_info.get("x"),
                                    y=table_info.get("y"),
                                    width=table_info.get("width"),
                                    height=table_info.get("height"),
                                    margin_left=table_info.get("margin_left"),
                                    margin_right=table_info.get("margin_right"),
                                    margin_top=table_info.get("margin_top"),
                                    margin_bottom=table_info.get("margin_bottom"),
                                    rows=table_info.get("rows"),
                                    cols=table_info.get("cols"),
                                    cell_count=(
                                        table_info.get("cell_para_counts", [])[-1]
                                        if table_info.get("cell_para_counts")
                                        else None
                                    ),
                                    cell_para_counts=table_info.get("cell_para_counts"),
                                    cell_spacing=table_info.get("cell_spacing"),
                                    row_sizes=table_info.get("row_sizes"),
                                    cell_widths=table_info.get("cell_widths"),
                                    cell_heights=table_info.get("cell_heights"),
                                    cell_colspans=table_info.get("cell_colspans"),
                                    cell_rowspans=table_info.get("cell_rowspans"),
                                ),
                            )
                        elif char.code == ExtendedControlCode.TABLE:
                            table_counter += 1

                            # table_metadata에서 상세 정보 찾기
                            table_info = (
                                all_table_metadata[table_counter - 1]
                                if table_counter <= len(all_table_metadata)
                                else {}
                            )

                            yield (
                                ElementType.TABLE,
                                ParsedTable(
                                    code=char.code,
                                    data=char.control_data,
                                    control_id=control_id,
                                    table_index=table_counter,
                                    x=table_info.get("x"),
                                    y=table_info.get("y"),
                                    width=table_info.get("width"),
                                    height=table_info.get("height"),
                                    margin_left=table_info.get("margin_left"),
                                    margin_right=table_info.get("margin_right"),
                                    margin_top=table_info.get("margin_top"),
                                    margin_bottom=table_info.get("margin_bottom"),
                                    rows=table_info.get("rows"),
                                    cols=table_info.get("cols"),
                                    cell_count=(
                                        table_info.get("cell_para_counts", [])[-1]
                                        if table_info.get("cell_para_counts")
                                        else None
                                    ),
                                    cell_para_counts=table_info.get("cell_para_counts"),
                                    cell_spacing=table_info.get("cell_spacing"),
                                    row_sizes=table_info.get("row_sizes"),
                                    cell_widths=table_info.get("cell_widths"),
                                    cell_heights=table_info.get("cell_heights"),
                                    cell_colspans=table_info.get("cell_colspans"),
                                    cell_rowspans=table_info.get("cell_rowspans"),
                                ),
                            )
                        elif char.code == ExtendedControlCode.PICTURE:
                            yield (
                                ElementType.PICTURE,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.OLE:
                            yield (
                                ElementType.OLE,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.EQUATION:
                            yield (
                                ElementType.EQUATION,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.FOOTNOTE:
                            yield (
                                ElementType.FOOTNOTE,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.ENDNOTE:
                            yield (
                                ElementType.ENDNOTE,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.HYPERLINK:
                            yield (
                                ElementType.HYPERLINK,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.COMMENT:
                            yield (
                                ElementType.COMMENT,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        elif char.code == ExtendedControlCode.SHAPE:
                            yield (
                                ElementType.SHAPE,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )
                        else:
                            yield (
                                ElementType.SHAPE_COMPONENT,
                                ParsedTable(
                                    code=char.code, data=char.control_data, control_id=control_id
                                ),
                            )

    def to_text(self) -> str:
        """전체 텍스트 추출"""
        return self._hwp.to_text()

    def __enter__(self):
        """Context Manager 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager 종료"""
        # 필요시 리소스 정리
        return False

    def __repr__(self):
        return f"HwpDocument(file='{self.file_path}', version={self.version}, sections={len(self.sections)})"


def open_hwp(file_path: str, iter_mode: IterMode = IterMode.SEQUENTIAL) -> HwpDocument:
    """
    HWP 파일을 여는 Pythonic API

    반환되는 HwpDocument는 with 문으로 사용 가능하며 내부적으로 HwpFile.from_file을 호출합니다.
    Context Manager를 반환하여 with 문으로 사용할 수 있습니다.

    사용 예:
        # 기본 모드 (SEQUENTIAL, 속도 우선)
        with open_hwp('document.hwp') as doc:
            for element_type, element in doc.tags:
                if element_type == ElementType.PARAGRAPH:
                    print(element.text)

        # STRUCTURED 모드 (계층 구조)
        with open_hwp('document.hwp', IterMode.STRUCTURED) as doc:
            for element_type, element in doc.iter_tags():
                print(element_type, element)

    Args:
        file_path: HWP 파일 경로
        iter_mode: 순회 모드 (기본: SEQUENTIAL)

    Returns:
        HwpDocument 인스턴스
    """
    return HwpDocument(file_path, iter_mode)


def hwp_to_txt(hwp_path: str):
    return hwp_to_text(hwp_path)


def hwp_to_text(hwp_path: str) -> str:
    """
    HWP 파일에서 문단 텍스트만 추출하여 반환합니다.
    - 본 함수는 Paragraph 요소만 필터링하여 줄 단위로 반환합니다.

    Args:
        hwp_path: 입력 HWP 파일 경로

    Returns:
        추출된 텍스트 문자열
    """
    lines = []
    with open_hwp(hwp_path) as doc:
        for element_type, element in doc.tags:
            if element_type == ElementType.PARAGRAPH:
                if element.text.strip():
                    lines.append(element.text)
    return "\n".join(lines)


def hwp_to_markdown(hwp_path: str) -> str:
    """
    HWP 파일을 간단한 마크다운으로 변환합니다.
    - 표 변환은 Section.table_metadata에 포함된 cell_para_counts 등을 사용하여 구성합니다.
    - 본 구현은 문단의 폰트 크기/굵기를 간단히 헤더/볼드로 매핑합니다.

    Args:
        hwp_path: 입력 HWP 파일 경로

    Returns:
        마크다운 형식 문자열
    """
    from typing import List, Optional, Set, Tuple

    def format_text_to_markdown(text: str, font_size: float, bold: bool) -> str:
        """폰트 크기와 굵기를 마크다운으로 변환"""
        if not text:
            return ""
        if font_size >= 28:
            return f"# {text}"
        elif font_size >= 20:
            return f"## {text}"
        elif font_size >= 14:
            return f"### {text}"
        elif bold:
            return f"**{text}**"
        return text

    def create_markdown_table(
        paragraphs: List[str],
        rows: int,
        cols: int,
        cell_para_counts: List[int],
        cell_colspans: Optional[List[int]] = None,
        cell_rowspans: Optional[List[int]] = None,
    ) -> str:
        """셀 정보를 기반으로 마크다운 테이블 생성"""
        if not paragraphs or rows == 0 or cols == 0:
            return ""

        # 병합된 셀 추적
        skip_cells: Set[Tuple[int, int]] = set()

        if cell_colspans and cell_rowspans:
            parsed_cell_idx = 0
            logical_row = 0
            logical_col = 0

            while parsed_cell_idx < len(cell_para_counts):
                while (logical_row, logical_col) in skip_cells:
                    logical_col += 1
                    if logical_col >= cols:
                        logical_col = 0
                        logical_row += 1

                colspan = (
                    cell_colspans[parsed_cell_idx] if parsed_cell_idx < len(cell_colspans) else 1
                )
                rowspan = (
                    cell_rowspans[parsed_cell_idx] if parsed_cell_idx < len(cell_rowspans) else 1
                )

                for r in range(logical_row, logical_row + rowspan):
                    for c in range(logical_col, logical_col + colspan):
                        if not (r == logical_row and c == logical_col):
                            skip_cells.add((r, c))

                logical_col += 1
                if logical_col >= cols:
                    logical_col = 0
                    logical_row += 1
                parsed_cell_idx += 1

        table_lines = []
        para_idx = 0
        parsed_cell_idx = 0

        for row_idx in range(rows):
            row_cells = []
            for col_idx in range(cols):
                if (row_idx, col_idx) in skip_cells:
                    row_cells.append("")
                    continue

                cell_para_count = (
                    cell_para_counts[parsed_cell_idx]
                    if parsed_cell_idx < len(cell_para_counts)
                    else 0
                )
                cell_text_parts = []
                for _ in range(cell_para_count):
                    if para_idx < len(paragraphs):
                        text = paragraphs[para_idx].lstrip("#").strip().replace("**", "")
                        cell_text_parts.append(text)
                        para_idx += 1

                row_cells.append(" ".join(cell_text_parts) if cell_text_parts else "")
                parsed_cell_idx += 1

            table_lines.append("| " + " | ".join(row_cells) + " |")
            if row_idx == 0:
                table_lines.append("| " + " | ".join(["---"] * cols) + " |")

        return "\n".join(table_lines)

    markdown_lines = []
    table_paragraphs = []
    in_table = False
    current_table_rows = 0
    current_table_cols = 0
    current_table_cell_para_counts = []
    current_table_element = None

    with open_hwp(hwp_path) as doc:
        for element_type, element in doc.tags:
            if element_type in [
                ElementType.PICTURE,
                ElementType.COMMENT,
                ElementType.FOOTNOTE,
                ElementType.ENDNOTE,
            ]:
                continue

            elif element_type == ElementType.TABLE:
                if in_table and table_paragraphs:
                    table_md = create_markdown_table(
                        table_paragraphs,
                        current_table_rows,
                        current_table_cols,
                        current_table_cell_para_counts,
                        (
                            current_table_element.cell_colspans
                            if current_table_element
                            and hasattr(current_table_element, "cell_colspans")
                            else None
                        ),
                        (
                            current_table_element.cell_rowspans
                            if current_table_element
                            and hasattr(current_table_element, "cell_rowspans")
                            else None
                        ),
                    )
                    markdown_lines.append(table_md)
                    markdown_lines.append("")

                in_table = True
                table_paragraphs = []
                current_table_rows = element.rows if element.rows else 0
                current_table_cols = element.cols if element.cols else 0
                current_table_cell_para_counts = (
                    element.cell_para_counts if element.cell_para_counts else []
                )
                current_table_element = element

            elif element_type == ElementType.PARAGRAPH:
                text = element.text.strip() if element.text else ""

                if element.char_shape:
                    markdown_text = format_text_to_markdown(
                        text, element.char_shape.font_size, element.char_shape.bold
                    )
                else:
                    markdown_text = text

                if in_table:
                    markdown_text_clean = markdown_text.replace("\n", " ").replace("\r", " ")
                    table_paragraphs.append(markdown_text_clean)

                    if current_table_cell_para_counts:
                        expected_paras = sum(current_table_cell_para_counts)
                        if len(table_paragraphs) >= expected_paras:
                            table_md = create_markdown_table(
                                table_paragraphs[:expected_paras],
                                current_table_rows,
                                current_table_cols,
                                current_table_cell_para_counts,
                                (
                                    current_table_element.cell_colspans
                                    if current_table_element
                                    and hasattr(current_table_element, "cell_colspans")
                                    else None
                                ),
                                (
                                    current_table_element.cell_rowspans
                                    if current_table_element
                                    and hasattr(current_table_element, "cell_rowspans")
                                    else None
                                ),
                            )
                            markdown_lines.append(table_md)
                            markdown_lines.append("")

                            in_table = False
                            table_paragraphs = []
                            current_table_cell_para_counts = []
                else:
                    if text:
                        markdown_lines.append(markdown_text)
                        markdown_lines.append("")

        if in_table and table_paragraphs:
            table_md = create_markdown_table(
                table_paragraphs,
                current_table_rows,
                current_table_cols,
                current_table_cell_para_counts,
                (
                    current_table_element.cell_colspans
                    if current_table_element and hasattr(current_table_element, "cell_colspans")
                    else None
                ),
                (
                    current_table_element.cell_rowspans
                    if current_table_element and hasattr(current_table_element, "cell_rowspans")
                    else None
                ),
            )
            markdown_lines.append(table_md)
            markdown_lines.append("")

    return "\n".join(markdown_lines)


def hwp_to_md(hwp_path: str):
    return hwp_to_markdown(hwp_path)


def hwp_to_pdf(hwp_path: str, output_pdf_path: Optional[str] = None):
    """HWP 파일을 PDF로 변환 (playwright 사용 - Windows/Linux/Mac 공통)"""
    from helper_md_doc import md_to_html
    from playwright.sync_api import sync_playwright

    if not os.path.isfile(hwp_path):
        raise FileNotFoundError(f"HWP 파일을 찾을 수 없습니다: {hwp_path}")

    # HWP -> Markdown -> HTML
    strmd = hwp_to_markdown(hwp_path)
    strhtml = md_to_html(strmd, use_base64=True)

    if output_pdf_path is None:
        output_pdf_path = hwp_path.rsplit(".", 1)[0] + ".pdf"

    # HTML -> PDF (playwright 사용)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(strhtml)
        page.pdf(path=output_pdf_path, format="A4", print_background=True)
        browser.close()

    return output_pdf_path
