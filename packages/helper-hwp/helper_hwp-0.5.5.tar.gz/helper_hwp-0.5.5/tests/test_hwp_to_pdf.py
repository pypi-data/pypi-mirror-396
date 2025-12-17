import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from helper_hwp import hwp_to_pdf


def test_hwp_to_pdf() -> None:
    """HWP → PDF 변환 테스트 (한글 지원)"""

    hwp_path = Path(__file__).parent / "test.hwp"
    pdf_path = Path(__file__).parent / "test_hwp_to_pdf.pdf"

    pdf_path = hwp_to_pdf(str(hwp_path), str(pdf_path))

    print(f"변환 완료: {pdf_path}")


if __name__ == "__main__":
    test_hwp_to_pdf()
