"""hwp_to_markdown 함수 테스트"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from helper_hwp import hwp_to_markdown


def test_hwp_to_markdown():
    hwp_path = Path(__file__).parent / "test.hwp"
    md_path = Path(__file__).parent / "test_hwp_to_markdown.md"
    
    # HWP에서 마크다운 추출
    markdown = hwp_to_markdown(str(hwp_path))
    
    # 파일로 저장
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"변환 완료: {md_path}")
    print(f"\n=== 출력 내용 ({len(markdown)} 글자) ===")
    print(markdown[:1000])

if __name__ == "__main__":
    test_hwp_to_markdown()
