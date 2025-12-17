"""
test.hwp를 open_hwp()로 문단 단위로 텍스트 추출하는 데모

사용법:
    python test_helper_hwp.py
"""

import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# UTF-8 출력 설정 (Windows 콘솔 대응)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from helper_hwp import ElementType, IterMode, open_hwp


def estimate_table_size(table) -> tuple:
    """일반 텍스트 테이블 크기 추정"""
    if table.rows and table.cols:
        # 기본 셀 크기 가정
        default_cell_width = 3.0  # cm
        default_cell_height = 0.8  # cm
        
        estimated_width = table.cols * default_cell_width
        estimated_height = table.rows * default_cell_height
        
        return (estimated_width, estimated_height)
    return (None, None)


def main():
    # test.hwp 파일 경로
    test_file =  str(Path(__file__).parent / "test.hwp")

    # 파일 존재 확인
    if not os.path.exists(test_file):
        print(f"오류: {test_file} 파일을 찾을 수 없습니다.")
        print(f"현재 디렉토리: {os.getcwd()}")
        print(f"\n사용 가능한 HWP 파일:")
        for file in os.listdir('.'):
            if file.endswith('.hwp'):
                print(f"  - {file}")
        return

    print("=" * 80)
    print("open_hwp() 데모 - test.hwp 태그 기반 순회")
    print("=" * 80)

    output_file = str(Path(__file__).parent / "test_hwp_iter_tags.txt")
    with open(output_file, 'w', encoding='utf-8') as f:

        # Context Manager로 파일 로드
        f.write(f"\n[1] 파일 로딩: {test_file}")
        with open_hwp(test_file) as hwp:
            # 파일 정보 출력
            f.write(f"\n[2] 파일 정보")
            f.write(f"  - 버전: {hwp.version}")
            f.write(f"  - 압축: {hwp.compressed}")
            f.write(f"  - 암호화: {hwp.encrypted}")
            f.write(f"  - 섹션 수: {len(hwp.sections)}")
            f.write(f"  - 순회 모드: {hwp.iter_mode.value}")
            f.write(f"  - 글자 모양 수: {len(hwp._hwp.char_shapes)}개")

            # iter_tags()로 문서 요소 순회
            f.write(f"\n[3] 태그 기반 순회 - iter_tags()")
            element_counts = {}
            paragraphs = []
            tables = []
            page_breaks = []
            footers = []
            headers = []
            page_defs = []

            for element_type, element in hwp.iter_tags():
                element_counts[element_type] = element_counts.get(element_type, 0) + 1
                
                if element_type == ElementType.PARAGRAPH:
                    paragraphs.append(element)
                elif element_type == ElementType.TABLE:
                    tables.append(element)
                elif element_type == ElementType.PAGE_BREAK:
                    page_breaks.append(element)
                elif element_type == ElementType.FOOTER:
                    footers.append(element)
                elif element_type == ElementType.HEADER:
                    headers.append(element)
                elif element_type == ElementType.PAGE_DEF:
                    page_defs.append(element)

            f.write(f"  > 요소 통계:")
            for elem_type, count in element_counts.items():
                f.write(f"    - {elem_type.value}: {count}개")

            # 문단 통계
            f.write(f"\n[4] 문단 통계")
            total_chars = sum(len(p.text) for p in paragraphs)
            avg_chars = total_chars / len(paragraphs) if paragraphs else 0
            max_chars = max(len(p.text) for p in paragraphs) if paragraphs else 0
            min_chars = min(len(p.text) for p in paragraphs) if paragraphs else 0
            
            # 서식 정보 통계
            font_sizes = [p.char_shape.font_size for p in paragraphs if p.char_shape]
            bold_count = sum(1 for p in paragraphs if p.char_shape and p.char_shape.bold)
            italic_count = sum(1 for p in paragraphs if p.char_shape and p.char_shape.italic)

            f.write(f"  - 총 문자 수: {total_chars:,}자")
            f.write(f"  - 평균 문단 길이: {avg_chars:.1f}자")
            f.write(f"  - 최대 문단 길이: {max_chars}자")
            f.write(f"  - 최소 문단 길이: {min_chars}자")
            if font_sizes:
                f.write(f"  - 평균 글꼴 크기: {sum(font_sizes)/len(font_sizes):.1f}pt")
                f.write(f"  - 굵게 문단: {bold_count}개")
                f.write(f"  - 기울임 문단: {italic_count}개")

            # 문단별 텍스트 출력 (처음 5개만)
            f.write(f"\n[5] 문단별 텍스트 출력 (처음 5개)")
            f.write("=" * 80)

            for i, para in enumerate(paragraphs[:5], 1):
                f.write(f"\n문단 {i} ({len(para.text)}자):")
                if para.char_shape:
                    f.write(f"  [글꼴: {para.char_shape.font_size}pt, 굵게: {para.char_shape.bold}, 기울임: {para.char_shape.italic}]")
                # 확장 속성: 글자별 서식 정보
                if para.char_shapes:
                    f.write(f"  [확장] 글자별 서식 ({len(para.char_shapes)}개):")
                    for pos, shape in para.char_shapes:
                        f.write(f"    위치 {pos}: {shape.font_size}pt, 굵게 {shape.bold}, 기울임 {shape.italic}")
                f.write(f"{para.text}")
                f.write("-" * 80)

            if len(paragraphs) > 5:
                f.write(f"\n... ({len(paragraphs) - 5}개 문단 생략)")

            # 테이블 정보
            if tables:
                f.write(f"\n[6] 테이블 정보")
                f.write(f"  > 총 {len(tables)}개 테이블 발견")
                for i, table in enumerate(tables, 1):
                    f.write(f"    테이블 {i}: code={table.code}")
            
            # 페이지 구분
            if page_breaks:
                f.write(f"\n[7] 페이지 구분")
                f.write(f"  > 총 {len(page_breaks)}개 페이지 구분 발견")

            # 머리말 정보
            if headers:
                f.write(f"\n[8] 머리말 정보")
                f.write(f"  > 총 {len(headers)}개 머리말 발견")
                for i, header in enumerate(headers, 1):
                    f.write(f"    머리말 {i}: code={header.code}")
                    if hasattr(header, 'control_id'):
                        f.write(f", control_id=0x{header.control_id:08X}")

            # 꼬리말 정보
            if footers:
                f.write(f"\n[9] 꼬리말 정보")
                f.write(f"  > 총 {len(footers)}개 꼬리말 발견")
                for i, footer in enumerate(footers, 1):
                    f.write(f"    꼬리말 {i}: code={footer.code}")
                    if hasattr(footer, 'control_id'):
                        f.write(f", control_id=0x{footer.control_id:08X}")

            # 페이지 정의 정보
            if page_defs:
                f.write(f"\n[10] 페이지 정의 (PAGE_DEF)")
                f.write(f"  > 총 {len(page_defs)}개 페이지 정의 발견")
                for i, page_def in enumerate(page_defs, 1):
                    f.write(f"    페이지 정의 {i}: code={page_def.code}")

            # 전체 텍스트 추출
            f.write(f"\n[11] 전체 텍스트 추출 - to_text()")
            full_text = hwp.to_text()
            f.write(f"  > 총 {len(full_text):,}자 추출")

            index = 1
            for element_type, element in hwp.iter_tags():
                # 확장 제어 디버깅 정보 출력
                # if element_type in [ElementType.TABLE, ElementType.EQUATION, ElementType.PICTURE]:
                #     control_id = element.control_id if hasattr(element, 'control_id') else None
                #     control_id_str = f"0x{control_id:08X}" if control_id else "None"
                #     f.write(f"*** 타입: {element_type.value}, 코드: {element.code}, Control ID: {control_id_str}, 데이터: {element.data[:20] if element.data else None}\n")
                
                if element_type == ElementType.PARAGRAPH:
                    f.write(f"[문단 {index}]\n")
                    if hasattr(element, 'char_shape') and element.char_shape:
                        f.write(f"[서식(max): {element.char_shape.font_size}pt, 굵게: {element.char_shape.bold}]\n")
                    # 확장 속성: 글자별 상세 서식
                    if hasattr(element, 'char_shapes') and element.char_shapes and len(element.char_shapes) > 1:
                        f.write(f"[상세] 글자별 서식 변경 지점:\n")
                        for pos, shape in element.char_shapes:
                            f.write(f"  위치 {pos}: {shape.font_size}pt, 굵게 {shape.bold}\n")
                    f.write(f"{element.text}\n\n")
                elif element_type == ElementType.TABLE:
                    # tables.append(element)
                    f.write(f"[표 {index}]\n")
                    f.write(f"  - Table Index: {element.table_index}\n")
                    f.write(f"  - Control ID: {element.control_id or element.get_control_id()}\n")
                    f.write(f"  - code: {element.code}\n")
                    if element.rows is not None:
                        f.write(f"  - 행/열: {element.rows} x {element.cols} (cell_count={element.cell_count})\n")
                    
                    # 크기 출력 (실제 크기 또는 추정 크기)
                    if element.width is not None:
                        # 실제 크기 (도형 개체 테이블)
                        width_px = element.to_px(element.width, dpi=96)
                        height_px = element.to_px(element.height, dpi=96)
                        f.write(f"  - 크기(cm): {element.width_cm:.2f}cm x {element.height_cm:.2f}cm\n")
                        f.write(f"  - 크기(px): {width_px}px x {height_px}px (96 DPI)\n")
                    else:
                        # 추정 크기 (일반 텍스트 테이블)
                        est_width, est_height = estimate_table_size(element)
                        if est_width:
                            # cm를 픽셀로 변환 (1 inch = 2.54 cm, 96 DPI)
                            est_width_px = int(est_width / 2.54 * 96)
                            est_height_px = int(est_height / 2.54 * 96)
                            f.write(f"  - 크기(추정cm): ~{est_width:.2f}cm x ~{est_height:.2f}cm\n")
                            f.write(f"  - 크기(추정px): ~{est_width_px}px x ~{est_height_px}px (96 DPI)\n")
                    
                    # 위치 출력 (cm와 픽셀 둘 다)
                    if element.x is not None:
                        x_px = element.to_px(element.x, dpi=96)
                        y_px = element.to_px(element.y, dpi=96)
                        f.write(f"  - 위치(cm): X={element.to_cm(element.x):.2f}cm, Y={element.to_cm(element.y):.2f}cm\n")
                        f.write(f"  - 위치(px): X={x_px}px, Y={y_px}px (96 DPI)\n")
                    else:
                        f.write(f"  - 위치: 텍스트 흐름 (자동 배치)\n")
                    
                    f.write(f"\n")
                elif element_type == ElementType.PAGE_BREAK:
                    f.write(f"[페이지구분 {index}]\n")
                elif element_type == ElementType.SECTION:
                    f.write(f"[섹션 {index}]\n")
                elif element_type == ElementType.HEADER:
                    f.write(f"[머리말 {index}]\n")
                elif element_type == ElementType.FOOTER:
                    f.write(f"[꼬리말 {index}]\n")
                    if hasattr(element, 'control_id'):
                        f.write(f"  - Control ID: 0x{element.control_id:08X}\n")
                    f.write(f"  - code: {element.code}\n")
                    # 꼬리말 내용이 있는지 확인
                    if hasattr(element, 'data') and element.data:
                        f.write(f"  - 데이터 길이: {len(element.data)} bytes\n")
                elif element_type == ElementType.FOOTNOTE:
                    f.write(f"[각주 {index}]\n")
                elif element_type == ElementType.ENDNOTE:
                    f.write(f"[미주 {index}]\n")
                elif element_type == ElementType.COMMENT:
                    f.write(f"[메모 {index}]\n")
                elif element_type == ElementType.SHAPE:
                    f.write(f"[도형 {index}]\n")
                elif element_type == ElementType.PICTURE:
                    f.write(f"[그림 {index}]\n")
                elif element_type == ElementType.OLE:
                    f.write(f"[OLE {index}]\n")
                elif element_type == ElementType.EQUATION:
                    f.write(f"[수식 {index}]\n")
                elif element_type == ElementType.HYPERLINK:
                    f.write(f"[하이퍼링크 {index}]\n")
                elif element_type == ElementType.SHAPE_COMPONENT:
                    f.write(f"[도형요소 {index}]\n")
                elif element_type == ElementType.LIST_HEADER:
                    f.write(f"[리스트헤더 {index}]\n")
                elif element_type == ElementType.PAGE_DEF:
                    f.write(f"[페이지정의 {index}]\n")
                    f.write(f"  - code: {element.code}\n")
                    if hasattr(element, 'data') and element.data:
                        f.write(f"  - 데이터 길이: {len(element.data)} bytes\n")
                        # 꼬리말 여백 정보 (offset 16-19, HWPUNIT 4 bytes)
                        if len(element.data) >= 20:
                            footer_margin = struct.unpack('<I', element.data[16:20])[0]
                            f.write(f"  - 꼬리말 여백: {footer_margin} HWPUNIT\n")
                elif element_type == ElementType.CTRL_HEADER:
                    f.write(f"[컨트롤헤더 {index}]\n")
                elif element_type == ElementType.CTRL_DATA:
                    f.write(f"[컨트롤데이터 {index}]\n")
                elif element_type == ElementType.CAPTION:
                    f.write(f"[캡션 {index}]\n")
                elif element_type == ElementType.BOOKMARK:
                    f.write(f"[책갈피 {index}]\n")
                elif element_type == ElementType.FIELD:
                    f.write(f"[필드 {index}]\n")
                elif element_type == ElementType.AUTO_NUMBER:
                    f.write(f"[자동번호/쪽번호 {index}]\n")
                    if hasattr(element, 'control_id') and element.control_id:
                        f.write(f"  - Control ID: 0x{element.control_id:08X}\n")
                    f.write(f"  - code: {element.code}\n")
                    if hasattr(element, 'data') and element.data:
                        # 자동 번호 데이터 파싱 (12 bytes: 속성 4 + 번호 2 + 기호들 6)
                        if len(element.data) >= 12:
                            attrs = struct.unpack('<I', element.data[0:4])[0]
                            number = struct.unpack('<H', element.data[4:6])[0]
                            number_type = attrs & 0xF  # bit 0~3: 번호 종류
                            number_format = (attrs >> 4) & 0xFF  # bit 4~11: 번호 모양
                            
                            type_names = {0: "쪽 번호", 1: "각주 번호", 2: "미주 번호", 
                                         3: "그림 번호", 4: "표 번호", 5: "수식 번호"}
                            f.write(f"  - 번호 종류: {type_names.get(number_type, f'알수없음({number_type})')}\n")
                            f.write(f"  - 번호: {number}\n")
                            f.write(f"  - 번호 모양: {number_format}\n")
                elif element_type == ElementType.NEW_NUMBER:
                    f.write(f"[새번호지정 {index}]\n")
                    if hasattr(element, 'control_id') and element.control_id:
                        f.write(f"  - Control ID: 0x{element.control_id:08X}\n")
                    f.write(f"  - code: {element.code}\n")
                    if hasattr(element, 'data') and element.data:
                        # 새 번호 지정 데이터 파싱 (8 bytes: 속성 4 + 번호 2)
                        if len(element.data) >= 6:
                            attrs = struct.unpack('<I', element.data[0:4])[0]
                            number = struct.unpack('<H', element.data[4:6])[0]
                            number_type = attrs & 0xF  # bit 0~3: 번호 종류
                            
                            type_names = {0: "쪽 번호", 1: "각주 번호", 2: "미주 번호", 
                                         3: "그림 번호", 4: "표 번호", 5: "수식 번호"}
                            f.write(f"  - 번호 종류: {type_names.get(number_type, f'알수없음({number_type})')}\n")
                            f.write(f"  - 새 시작 번호: {number}\n")
                elif element_type == ElementType.PAGE_NUM_POS:
                    f.write(f"[쪽번호위치 {index}]\n")
                    if hasattr(element, 'control_id') and element.control_id:
                        f.write(f"  - Control ID: 0x{element.control_id:08X}\n")
                    f.write(f"  - code: {element.code}\n")
                    if hasattr(element, 'data') and element.data:
                        # 쪽 번호 위치 데이터 파싱 (12 bytes)
                        if len(element.data) >= 12:
                            attrs = struct.unpack('<I', element.data[0:4])[0]
                            position = (attrs >> 8) & 0xF  # bit 8~11: 위치
                            positions = {0: "없음", 1: "왼쪽 위", 2: "가운데 위", 3: "오른쪽 위",
                                        4: "왼쪽 아래", 5: "가운데 아래", 6: "오른쪽 아래",
                                        7: "바깥쪽 위", 8: "바깥쪽 아래", 9: "안쪽 위", 10: "안쪽 아래"}
                            f.write(f"  - 표시 위치: {positions.get(position, f'알수없음({position})')}\n")
                else:
                    f.write(f"[알수없음 {element_type.value} {index}]\n")
                
                index += 1

            f.write(f"\n[12] 파일 저장")
            f.write(f"  > 저장 완료: {output_file}")

    print("\n" + "=" * 80)
    print("완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()
