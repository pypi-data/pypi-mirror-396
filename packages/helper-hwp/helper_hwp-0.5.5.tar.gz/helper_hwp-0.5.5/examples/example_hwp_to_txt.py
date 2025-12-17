"""
Example: hwp_to_txt
HWP 파일에서 문단 텍스트만 추출하여 출력하는 간단한 예제(MVP).
"""
import sys
from pathlib import Path

# examples 폴더에서 직접 실행할 때도 패키지를 찾도록 상위 폴더를 경로에 추가
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from helper_hwp import hwp_to_txt

hwp_path = Path(__file__).resolve().parents[1] / 'tests' / 'test.hwp'
if not hwp_path.exists():
    print('샘플 HWP 파일을 찾을 수 없습니다:', hwp_path)
else:
    text = hwp_to_txt(str(hwp_path))
    # 출력 길이가 큰 경우 앞부분만 확인
    print(text[:200])

