"""
Example: iter_tags to JSON
문서 순회(`iter_tags`)의 모든 ElementType을 JSON 파일로 변환하는 예제.
SEQUENTIAL 및 STRUCTURED 모드의 결과를 각각 JSON 파일로 저장합니다.
"""
import json
import sys
from pathlib import Path
from typing import Any, Dict

# examples 폴더에서 직접 실행할 때도 패키지를 찾도록 상위 폴더를 경로에 추가
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from helper_hwp import ElementType, IterMode, open_hwp
from helper_hwp.parsed_elements import ParsedParagraph, ParsedTable


def serialize_element(elem_type: ElementType, elem: Any) -> Dict[str, Any]:
    """요소를 JSON 직렬화 가능한 dict로 변환"""
    result: Dict[str, Any] = {
        'element_type': elem_type.value,
    }
    
    if elem_type == ElementType.PARAGRAPH and isinstance(elem, ParsedParagraph):
        result.update({
            'text': elem.text or '',
            'is_page_first_line': elem.is_page_first_line,
        })
        
        if elem.char_shape:
            result['char_shape'] = {
                'font_size': elem.char_shape.font_size,
                'font_id': elem.char_shape.font_id,
                'bold': elem.char_shape.bold,
                'italic': elem.char_shape.italic,
                'underline': elem.char_shape.underline,
                'expansion': elem.char_shape.expansion,
                'spacing': elem.char_shape.spacing,
                'color': elem.char_shape.color,
            }
        
        if elem.char_shapes:
            result['char_shapes'] = [
                {
                    'position': pos,
                    'font_size': shape.font_size,
                    'font_id': shape.font_id,
                    'bold': shape.bold,
                    'italic': shape.italic,
                    'underline': shape.underline,
                    'expansion': shape.expansion,
                    'spacing': shape.spacing,
                    'color': shape.color,
                }
                for pos, shape in elem.char_shapes
            ]
        
        if elem.paragraph:
            result['paragraph_info'] = {
                'is_page_break': elem.paragraph.is_page_break,
                'char_shape_id': elem.paragraph.char_shape_id,
            }
    
    elif elem_type == ElementType.TABLE and isinstance(elem, ParsedTable):
        result.update({
            'code': elem.code,
            'control_id': elem.control_id,
            'table_index': elem.table_index,
            'rows': elem.rows,
            'cols': elem.cols,
            'width_hwpunit': elem.width,
            'height_hwpunit': elem.height,
            'width_cm': elem.width_cm,
            'height_cm': elem.height_cm,
            'margin_left': elem.margin_left,
            'margin_right': elem.margin_right,
            'margin_top': elem.margin_top,
            'margin_bottom': elem.margin_bottom,
            'cell_count': elem.cell_count,
            'cell_spacing': elem.cell_spacing,
            'cell_para_counts': elem.cell_para_counts,
            'row_sizes': elem.row_sizes,
            'cell_widths': elem.cell_widths,
            'cell_heights': elem.cell_heights,
            'cell_colspans': elem.cell_colspans,
            'cell_rowspans': elem.cell_rowspans,
            'calculated_width_cm': elem.calculated_width_cm,
            'calculated_height_cm': elem.calculated_height_cm,
            'data_length': len(elem.data) if elem.data else 0,
        })
    
    elif isinstance(elem, ParsedTable):
        # 기타 ParsedTable 타입 (PICTURE, EQUATION, SHAPE, etc.)
        result.update({
            'code': elem.code,
            'control_id': elem.control_id,
            'data_length': len(elem.data) if elem.data else 0,
        })
    
    else:
        result['repr'] = repr(elem)
    
    return result


def main():
    hwp_path = Path(__file__).resolve().parents[1] / 'tests' / 'test.hwp'
    if not hwp_path.exists():
        print(f'샘플 HWP 파일을 찾을 수 없습니다: {hwp_path}')
        raise SystemExit(1)
    
    output_dir = Path(__file__).resolve().parent
    
    for mode in (IterMode.SEQUENTIAL, IterMode.STRUCTURED):
        print(f"\n처리 중: {mode.value} 모드")
        
        elements = []
        counts = {}
        
        with open_hwp(str(hwp_path), iter_mode=mode) as doc:
            for elem_type, elem in doc.iter_tags(mode):
                counts[elem_type] = counts.get(elem_type, 0) + 1
                serialized = serialize_element(elem_type, elem)
                elements.append(serialized)
        
        # JSON 파일로 저장
        output_file = output_dir / f'output_{mode.value}.json'
        output_data = {
            'mode': mode.value,
            'hwp_file': str(hwp_path.name),
            'total_elements': len(elements),
            'element_counts': {k.value: v for k, v in counts.items()},
            'elements': elements,
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"저장 완료: {output_file}")
        print(f"  총 요소 개수: {len(elements)}")
        print(f"  요소 타입별 개수:")
        for k, v in counts.items():
            print(f"    {k.value}: {v}")


if __name__ == '__main__':
    main()

