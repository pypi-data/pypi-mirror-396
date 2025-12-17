"""
Example: hwp_to_markdown
HWP 파일을 간단한 마크다운으로 변환하는 사용 예제(MVP).
"""
import sys
from pathlib import Path

# examples 폴더에서 직접 실행할 때도 패키지를 찾도록 상위 폴더를 경로에 추가
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from helper_hwp import hwp_to_markdown

hwp_path = Path(__file__).resolve().parents[1] / 'tests' / 'test.hwp'
if not hwp_path.exists():
    print('샘플 HWP 파일을 찾을 수 없습니다:', hwp_path)
else:
    md = hwp_to_markdown(str(hwp_path))
    print(md[:400])

