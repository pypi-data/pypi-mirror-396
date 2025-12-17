"""
Example: iter_tags
문서 순회(`iter_tags`)의 모든 ElementType 출력을 확인하는 예제(MVP).
SEQUENTIAL 및 STRUCTURED 모드의 간단한 요약을 출력합니다.
"""
import sys
from pathlib import Path

# examples 폴더에서 직접 실행할 때도 패키지를 찾도록 상위 폴더를 경로에 추가
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from helper_hwp import ElementType, IterMode, open_hwp
from helper_hwp.parsed_elements import ParsedParagraph, ParsedTable

hwp_path = Path(__file__).resolve().parents[1] / 'tests' / 'test.hwp'
if not hwp_path.exists():
    print('샘플 HWP 파일을 찾을 수 없습니다:', hwp_path)
    raise SystemExit(1)

for mode in (IterMode.SEQUENTIAL, IterMode.STRUCTURED):
    print(f"\n{'='*60}")
    print(f"iter_tags mode: {mode.value}")
    print('='*60)
    counts = {}
    with open_hwp(str(hwp_path), iter_mode=mode) as doc:
        for elem_type, elem in doc.iter_tags(mode):
            counts[elem_type] = counts.get(elem_type, 0) + 1
            
            newline = '\n'
            space = ' '
            print(f"\n[{elem_type.value}]")
            
            # 공통 속성
            if hasattr(elem, '__dict__'):
                print(f"  전체 속성: {list(elem.__dict__.keys())}")
            
            if elem_type == ElementType.PARAGRAPH and isinstance(elem, ParsedParagraph):
                text_preview = (elem.text or '').strip().replace(newline, space)[:80]
                print(f"  text: {text_preview}")
                print(f"  is_page_first_line: {elem.is_page_first_line}")
                if elem.char_shape:
                    print(f"  char_shape:")
                    print(f"    font_size: {elem.char_shape.font_size}")
                    print(f"    font_id: {elem.char_shape.font_id}")
                    print(f"    bold: {elem.char_shape.bold}")
                    print(f"    italic: {elem.char_shape.italic}")
                    print(f"    underline: {elem.char_shape.underline}")
                    print(f"    expansion: {elem.char_shape.expansion}")
                    print(f"    spacing: {elem.char_shape.spacing}")
                    print(f"    color: {elem.char_shape.color}")
                if elem.char_shapes:
                    print(f"  char_shapes 개수: {len(elem.char_shapes)}")
                    for idx, (pos, shape) in enumerate(elem.char_shapes[:3]):
                        print(f"    [{idx}] pos={pos}, font_size={shape.font_size}, bold={shape.bold}")
                if elem.paragraph:
                    print(f"  paragraph 정보:")
                    print(f"    is_page_break: {elem.paragraph.is_page_break}")
                    print(f"    char_shape_id: {elem.paragraph.char_shape_id}")
                    if hasattr(elem.paragraph, 'line_count'):
                        print(f"    line_count: {elem.paragraph.line_count}")
            
            elif elem_type == ElementType.TABLE and isinstance(elem, ParsedTable):
                print(f"  code: {elem.code}")
                print(f"  control_id: {elem.control_id}")
                print(f"  table_index: {elem.table_index}")
                print(f"  rows: {elem.rows}")
                print(f"  cols: {elem.cols}")
                print(f"  width: {elem.width} (HWPUNIT)")
                print(f"  height: {elem.height} (HWPUNIT)")
                print(f"  width_cm: {elem.width_cm}")
                print(f"  height_cm: {elem.height_cm}")
                print(f"  margin_left: {elem.margin_left}")
                print(f"  margin_right: {elem.margin_right}")
                print(f"  margin_top: {elem.margin_top}")
                print(f"  margin_bottom: {elem.margin_bottom}")
                print(f"  cell_count: {elem.cell_count}")
                print(f"  cell_spacing: {elem.cell_spacing}")
                print(f"  cell_para_counts: {elem.cell_para_counts}")
                print(f"  row_sizes: {elem.row_sizes}")
                print(f"  cell_widths: {elem.cell_widths}")
                print(f"  cell_heights: {elem.cell_heights}")
                print(f"  cell_colspans: {elem.cell_colspans}")
                print(f"  cell_rowspans: {elem.cell_rowspans}")
                print(f"  calculated_width_cm: {elem.calculated_width_cm}")
                print(f"  calculated_height_cm: {elem.calculated_height_cm}")
                print(f"  data length: {len(elem.data) if elem.data else 0} bytes")
            
            elif isinstance(elem, ParsedTable):
                # 기타 ParsedTable 타입 (PICTURE, EQUATION, SHAPE, etc.)
                print(f"  code: {elem.code}")
                print(f"  control_id: {elem.control_id}")
                print(f"  data length: {len(elem.data) if elem.data else 0} bytes")
            
            else:
                print(f"  repr: {repr(elem)}")
    
    print(f"\n{'='*60}")
    print('요약 카운트')
    print('='*60)
    for k, v in counts.items():
        print(f"{k.value}: {v}")

