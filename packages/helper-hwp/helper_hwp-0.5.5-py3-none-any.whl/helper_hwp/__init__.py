"""
HWP Parser for Python

HWP (Hangul Word Processor) 파일 파싱 라이브러리
CFB (Compound File Binary) 기반 HWP 5.x 포맷 지원

주요 기능:
- HWP 5.x 파일 구조 분석 및 파싱
- 텍스트, 표, 페이지 단위 추출
- Markdown, Plain Text 변환 지원
- 단위 변환 유틸리티 (HWPUNIT ↔ cm/inch/px)

기본 사용법:
    >>> from helper_hwp import open_hwp, hwp_to_txt, hwp_to_markdown
    >>>
    >>> # HWP 문서 열기
    >>> doc = open_hwp('example.hwp')
    >>>
    >>> # 텍스트 추출
    >>> text = hwp_to_txt('example.hwp')
    >>>
    >>> # 마크다운 변환
    >>> markdown = hwp_to_markdown('example.hwp')

주요 클래스:
    - HwpDocument: HWP 문서 파싱 및 순회
    - HwpFile: HWP 파일 구조 (CFB 스토리지)
    - ParsedParagraph: 파싱된 문단
    - ParsedTable: 파싱된 표
    - ParsedPage: 파싱된 페이지

상수:
    - ElementType: 요소 타입 (PARAGRAPH, TABLE, PAGE)
    - IterMode: 순회 모드 (PARAGRAPH, TABLE, PAGE)
"""

import importlib.util
import os
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[1]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

spec = importlib.util.spec_from_file_location(
    "requirements_rnac", os.path.join(os.path.dirname(__file__), "requirements_rnac.py")
)
requirements_rnac = importlib.util.module_from_spec(spec)
spec.loader.exec_module(requirements_rnac)
requirements_rnac.check_and_print_dependencies()

from .constants import ElementType, IterMode
from .document_structure import HwpFile
from .models import Header, Version
from .parsed_elements import ParsedPage, ParsedParagraph, ParsedTable
from .parser import (
    HwpDocument,
    hwp_to_markdown,
    hwp_to_md,
    hwp_to_pdf,
    hwp_to_txt,
    open_hwp,
)
from .utils import hwpunit_to_cm, hwpunit_to_inch, hwpunit_to_px

__all__ = [
    # 상수
    "ElementType",
    "IterMode",
    # 모델
    "Version",
    "Header",
    "HwpFile",
    # 파싱된 요소
    "ParsedParagraph",
    "ParsedTable",
    "ParsedPage",
    # 메인 API
    "HwpDocument",
    "open_hwp",
    "hwp_to_txt",
    "hwp_to_markdown",
    "hwp_to_md",
    "hwp_to_pdf",
    # 유틸리티
    "hwpunit_to_cm",
    "hwpunit_to_inch",
    "hwpunit_to_px",
]

__version__ = "0.5.5"

# GitHub Repository URL
GITHUB_URL = "https://github.com/c0z0c-helper/helper_hwp"

# 패키지 로드 시 GitHub URL 출력
print(f"GITHUB_URL = {GITHUB_URL}")
