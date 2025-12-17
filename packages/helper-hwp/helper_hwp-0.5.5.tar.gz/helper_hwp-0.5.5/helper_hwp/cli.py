"""
CLI entry points for helper-hwp

명령어:
- hwp2txt: HWP → Plain Text
- hwp2md: HWP → Markdown
- hwp2html: HWP → HTML (helper_md_doc 필요)
- hwp2doc: HWP → DOCX (helper_md_doc 필요)
- hwp2pdf: HWP → PDF (helper_md_doc + weasyprint 필요)
"""

import argparse
import importlib.util
import os
import sys
import pypandoc
from pathlib import Path
from typing import Optional

_project_root = Path(__file__).resolve().parents[1]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

spec = importlib.util.spec_from_file_location(
    "requirements_rnac", os.path.join(os.path.dirname(__file__), "requirements_rnac.py")
)
requirements_rnac = importlib.util.module_from_spec(spec)
spec.loader.exec_module(requirements_rnac)
requirements_rnac.check_and_print_dependencies()


def _get_output_path(input_path: str, output_path: Optional[str], extension: str) -> str:
    """출력 파일 경로 생성"""
    if output_path:
        return output_path
    input_pathobj = Path(input_path)
    return str(input_pathobj.with_suffix(extension))


def hwp2txt_main():
    """hwp2txt CLI 엔트리포인트"""
    parser = argparse.ArgumentParser(description="HWP 파일을 텍스트로 변환")
    parser.add_argument("input", help="입력 HWP 파일 경로")
    parser.add_argument("-o", "--output", help="출력 텍스트 파일 경로 (기본: 입력파일명.txt)")

    args = parser.parse_args()

    try:
        from helper_hwp import hwp_to_txt

        text = hwp_to_txt(args.input)
        output_path = _get_output_path(args.input, args.output, ".txt")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"변환 완료: {output_path}")
    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
        sys.exit(1)


def hwp2md_main():
    """hwp2md CLI 엔트리포인트"""
    parser = argparse.ArgumentParser(description="HWP 파일을 마크다운으로 변환")
    parser.add_argument("input", help="입력 HWP 파일 경로")
    parser.add_argument("-o", "--output", help="출력 마크다운 파일 경로 (기본: 입력파일명.md)")

    args = parser.parse_args()

    try:
        from helper_hwp import hwp_to_markdown

        markdown = hwp_to_markdown(args.input)
        output_path = _get_output_path(args.input, args.output, ".md")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        print(f"변환 완료: {output_path}")
    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
        sys.exit(1)


def hwp2html_main():
    """hwp2html CLI 엔트리포인트 (helper_md_doc 필요)"""
    parser = argparse.ArgumentParser(description="HWP 파일을 HTML로 변환")
    parser.add_argument("input", help="입력 HWP 파일 경로")
    parser.add_argument("-o", "--output", help="출력 HTML 파일 경로 (기본: 입력파일명.html)")
    parser.add_argument(
        "--base64", action="store_true", help="이미지를 Base64로 인코딩 (기본: False)"
    )

    args = parser.parse_args()

    try:
        from helper_md_doc import md_to_html

        from helper_hwp import hwp_to_markdown

        markdown = hwp_to_markdown(args.input)
        html = md_to_html(markdown, use_base64=args.base64)
        output_path = _get_output_path(args.input, args.output, ".html")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"변환 완료: {output_path}")
    except ImportError:
        print("오류: helper_md_doc 패키지가 필요합니다.", file=sys.stderr)
        print("설치: pip install helper-hwp[doc]", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
        sys.exit(1)


def hwp2doc_main():
    """hwp2doc CLI 엔트리포인트 (helper_md_doc 필요)"""
    parser = argparse.ArgumentParser(description="HWP 파일을 DOCX로 변환")
    parser.add_argument("input", help="입력 HWP 파일 경로")
    parser.add_argument("-o", "--output", help="출력 DOCX 파일 경로 (기본: 입력파일명.docx)")

    args = parser.parse_args()

    try:
        from helper_md_doc import md_to_doc, md_to_html
        from helper_hwp import hwp_to_markdown

        markdown = hwp_to_markdown(args.input)
        output_path = _get_output_path(args.input, args.output, ".docx")
        html_text = md_to_html(markdown, title=None, use_base64=True)
        pypandoc.convert_text(
            html_text, "docx", format="html", outputfile=output_path, extra_args=["--standalone"]
        )

        print(f"변환 완료: {output_path}")
    except ImportError:
        print("오류: helper_md_doc 패키지가 필요합니다.", file=sys.stderr)
        print("설치: pip install helper-hwp[doc]", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
        sys.exit(1)


def hwp2pdf_main():
    """hwp2pdf CLI 엔트리포인트 (helper_md_doc + weasyprint 필요)"""
    parser = argparse.ArgumentParser(description="HWP 파일을 PDF로 변환")
    parser.add_argument("input", help="입력 HWP 파일 경로")
    parser.add_argument("-o", "--output", help="출력 PDF 파일 경로 (기본: 입력파일명.pdf)")

    args = parser.parse_args()

    try:
        from helper_hwp import hwp_to_pdf

        output_path = hwp_to_pdf(args.input, args.output)

        print(f"변환 완료: {output_path}")
    except ImportError as e:
        if "helper_md_doc" in str(e):
            print("오류: helper_md_doc 패키지가 필요합니다.", file=sys.stderr)
            print("설치: pip install helper-hwp[pdf]", file=sys.stderr)
        elif "weasyprint" in str(e):
            print("오류: weasyprint 패키지가 필요합니다.", file=sys.stderr)
            print("설치: pip install helper-hwp[pdf]", file=sys.stderr)
        else:
            print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
        sys.exit(1)
