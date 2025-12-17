# 사용자 가이드

helper_hwp 라이브러리 사용 방법을 안내합니다.

## 목차

- [시작하기](#시작하기)
- [기본 사용법](#기본-사용법)
- [고급 기능](#고급-기능)
- [API 레퍼런스](#api-레퍼런스)
- [예제](#예제)
- [문제 해결](#문제-해결)

## 시작하기

### 설치

```bash
pip install helper-hwp
```

### 첫 번째 프로그램

```python
from helper_hwp import hwp_to_txt

# HWP 파일에서 텍스트 추출
text = hwp_to_txt('example.hwp')
print(text)
```

## 기본 사용법

### 1. 텍스트 추출

HWP 파일에서 순수 텍스트만 추출합니다.

```python
from helper_hwp import hwp_to_txt

text = hwp_to_txt('document.hwp')
print(text)
```

**출력 예시:**
```
안녕하세요
이것은 HWP 문서입니다
텍스트가 추출됩니다
```

### 2. 마크다운 변환

HWP 파일을 마크다운 형식으로 변환합니다. 헤더, 볼드, 표 등이 변환됩니다.

```python
from helper_hwp import hwp_to_markdown

markdown = hwp_to_markdown('document.hwp')
print(markdown)

# 파일로 저장
with open('output.md', 'w', encoding='utf-8') as f:
    f.write(markdown)
```

**출력 예시:**
```markdown
# 제목

## 부제목

본문 텍스트입니다.

**굵은 글씨**

| 열1 | 열2 | 열3 |
| --- | --- | --- |
| A | B | C |
| D | E | F |
```

### 3. HWP 문서 열기

문서 객체를 사용하여 더 세밀한 제어가 가능합니다.

```python
from helper_hwp import open_hwp

# Context manager 사용 (권장)
with open_hwp('document.hwp') as doc:
    print(f"버전: {doc.version}")
    print(f"섹션 수: {len(doc.sections)}")
    print(f"압축 여부: {doc.compressed}")
```

## 고급 기능

### 문단 단위 순회

```python
from helper_hwp import open_hwp, ElementType

with open_hwp('document.hwp') as doc:
    for element_type, element in doc.iter_tags():
        if element_type == ElementType.PARAGRAPH:
            print(f"문단: {element.text}")

            # 글자 모양 정보
            if element.char_shape:
                print(f"  폰트 크기: {element.char_shape.font_size}")
                print(f"  굵기: {element.char_shape.bold}")
                print(f"  이탤릭: {element.char_shape.italic}")
```

### 표 추출

```python
from helper_hwp import open_hwp, ElementType

with open_hwp('document.hwp') as doc:
    for element_type, element in doc.iter_tags():
        if element_type == ElementType.TABLE:
            print(f"표 {element.table_index}")
            print(f"  크기: {element.rows}행 x {element.cols}열")
            print(f"  셀 수: {element.cell_count}")
```

### 페이지 단위 처리

```python
from helper_hwp import open_hwp

with open_hwp('document.hwp') as doc:
    for page in doc.pages:
        print(f"\n=== 페이지 {page.page_number} ===")
        for paragraph in page.paragraphs:
            if paragraph.text:
                print(paragraph.text)
```

### 특정 요소 타입 검색

```python
from helper_hwp import open_hwp, ElementType

with open_hwp('document.hwp') as doc:
    # 모든 문단 가져오기
    paragraphs = doc.get_elements_by_type(ElementType.PARAGRAPH)
    print(f"총 {len(paragraphs)}개의 문단")

    # 모든 표 가져오기
    tables = doc.get_elements_by_type(ElementType.TABLE)
    print(f"총 {len(tables)}개의 표")

    # 페이지 구분자 찾기
    page_breaks = doc.get_elements_by_type(ElementType.PAGE_BREAK)
    print(f"총 {len(page_breaks)}개의 페이지 구분")
```

### 순회 모드

문서를 순회하는 두 가지 모드가 있습니다:

#### SEQUENTIAL 모드 (기본)

문서 출현 순서대로 빠르게 순회합니다.

```python
from helper_hwp import open_hwp, IterMode

with open_hwp('document.hwp', IterMode.SEQUENTIAL) as doc:
    for element_type, element in doc.iter_tags():
        print(element_type, element)
```

#### STRUCTURED 모드

계층 구조를 유지하며 상세하게 순회합니다.

```python
from helper_hwp import open_hwp, IterMode

with open_hwp('document.hwp', IterMode.STRUCTURED) as doc:
    for element_type, element in doc.iter_tags():
        print(element_type, element)
```

### 유틸리티 함수

HWP 단위를 다른 단위로 변환합니다.

```python
from helper_hwp import hwpunit_to_cm, hwpunit_to_inch, hwpunit_to_px

hwpunit = 1000

# HWPUNIT → cm
cm = hwpunit_to_cm(hwpunit)
print(f"{hwpunit} HWPUNIT = {cm} cm")

# HWPUNIT → inch
inch = hwpunit_to_inch(hwpunit)
print(f"{hwpunit} HWPUNIT = {inch} inch")

# HWPUNIT → px (기본 DPI: 96)
px = hwpunit_to_px(hwpunit)
print(f"{hwpunit} HWPUNIT = {px} px")

# 커스텀 DPI
px_300 = hwpunit_to_px(hwpunit, dpi=300)
print(f"{hwpunit} HWPUNIT = {px_300} px (300 DPI)")
```

## API 레퍼런스

### 메인 함수

#### `open_hwp(file_path, iter_mode=IterMode.SEQUENTIAL)`

HWP 파일을 열어 `HwpDocument` 객체를 반환합니다.

**매개변수:**
- `file_path` (str): HWP 파일 경로
- `iter_mode` (IterMode): 순회 모드 (SEQUENTIAL 또는 STRUCTURED)

**반환:**
- `HwpDocument`: HWP 문서 객체

**예제:**
```python
with open_hwp('document.hwp') as doc:
    print(doc.version)
```

#### `hwp_to_txt(hwp_path)`

HWP 파일에서 텍스트를 추출합니다.

**매개변수:**
- `hwp_path` (str): HWP 파일 경로

**반환:**
- `str`: 추출된 텍스트

**예제:**
```python
text = hwp_to_txt('document.hwp')
```

#### `hwp_to_markdown(hwp_path)`

HWP 파일을 마크다운으로 변환합니다.

**매개변수:**
- `hwp_path` (str): HWP 파일 경로

**반환:**
- `str`: 마크다운 텍스트

**예제:**
```python
markdown = hwp_to_markdown('document.hwp')
```

### HwpDocument 클래스

#### 속성

- `version`: 문서 버전
- `compressed`: 압축 여부
- `encrypted`: 암호화 여부
- `sections`: 섹션 리스트
- `pages`: 페이지 리스트

#### 메서드

##### `iter_tags(mode=None)`

문서 요소를 순회하는 제너레이터입니다.

**매개변수:**
- `mode` (IterMode, optional): 순회 모드

**반환:**
- Generator[(ElementType, element)]: 요소 타입과 요소의 튜플

**예제:**
```python
for element_type, element in doc.iter_tags():
    if element_type == ElementType.PARAGRAPH:
        print(element.text)
```

##### `get_elements_by_type(element_type)`

특정 타입의 요소를 검색합니다.

**매개변수:**
- `element_type` (ElementType): 검색할 요소 타입

**반환:**
- `List`: 검색된 요소 리스트

**예제:**
```python
paragraphs = doc.get_elements_by_type(ElementType.PARAGRAPH)
tables = doc.get_elements_by_type(ElementType.TABLE)
```

##### `to_text()`

전체 텍스트를 추출합니다.

**반환:**
- `str`: 추출된 텍스트

### ElementType (요소 타입)

- `PARAGRAPH`: 문단
- `TABLE`: 표
- `PAGE_BREAK`: 페이지 구분
- `PICTURE`: 그림
- `EQUATION`: 수식
- `FOOTNOTE`: 각주
- `ENDNOTE`: 미주
- `HEADER`: 머리글
- `FOOTER`: 바닥글
- `SECTION`: 섹션

### 파싱된 요소

#### ParsedParagraph

문단 정보를 담은 객체입니다.

**속성:**
- `text` (str): 문단 텍스트
- `paragraph` (Paragraph): 원본 문단 객체
- `char_shape` (CharShapeInfo): 글자 모양 정보
- `char_shapes` (List): 위치별 글자 모양 정보

#### ParsedTable

표 정보를 담은 객체입니다.

**속성:**
- `table_index` (int): 표 인덱스
- `rows` (int): 행 수
- `cols` (int): 열 수
- `cell_count` (int): 셀 개수
- `cell_para_counts` (List[int]): 셀별 문단 수
- `cell_widths` (List[int]): 셀 너비
- `cell_heights` (List[int]): 셀 높이
- `cell_colspans` (List[int]): 셀 병합 (가로)
- `cell_rowspans` (List[int]): 셀 병합 (세로)

#### ParsedPage

페이지 정보를 담은 객체입니다.

**속성:**
- `page_number` (int): 페이지 번호
- `paragraphs` (List[ParsedParagraph]): 문단 리스트

## 예제

### 예제 1: HWP → TXT 변환

```python
from helper_hwp import hwp_to_txt
from pathlib import Path

hwp_file = 'example.hwp'
txt_file = 'output.txt'

# 텍스트 추출
text = hwp_to_txt(hwp_file)

# 파일로 저장
Path(txt_file).write_text(text, encoding='utf-8')

print(f"변환 완료: {txt_file}")
```

### 예제 2: HWP → Markdown 변환

```python
from helper_hwp import hwp_to_markdown
from pathlib import Path

hwp_file = 'example.hwp'
md_file = 'output.md'

# 마크다운 변환
markdown = hwp_to_markdown(hwp_file)

# 파일로 저장
Path(md_file).write_text(markdown, encoding='utf-8')

print(f"변환 완료: {md_file}")
```

### 예제 3: 표 데이터 추출

```python
from helper_hwp import open_hwp, ElementType

with open_hwp('document.hwp') as doc:
    tables = doc.get_elements_by_type(ElementType.TABLE)

    for table in tables:
        print(f"\n표 {table.table_index}")
        print(f"크기: {table.rows}행 x {table.cols}열")

        if table.cell_para_counts:
            print("셀별 문단 수:", table.cell_para_counts)
```

### 예제 4: 문서 정보 추출

```python
from helper_hwp import open_hwp

with open_hwp('document.hwp') as doc:
    print("=== 문서 정보 ===")
    print(f"버전: {doc.version}")
    print(f"압축: {doc.compressed}")
    print(f"암호화: {doc.encrypted}")
    print(f"섹션 수: {len(doc.sections)}")

    # 문단 개수
    paragraphs = doc.get_elements_by_type('paragraph')
    print(f"문단 수: {len(paragraphs)}")

    # 표 개수
    tables = doc.get_elements_by_type('table')
    print(f"표 수: {len(tables)}")

    # 페이지 수
    print(f"페이지 수: {len(doc.pages)}")
```

### 예제 5: JSON으로 변환

```python
from helper_hwp import open_hwp, ElementType
import json

with open_hwp('document.hwp') as doc:
    data = {
        'version': str(doc.version),
        'compressed': doc.compressed,
        'encrypted': doc.encrypted,
        'paragraphs': [],
        'tables': []
    }

    for element_type, element in doc.iter_tags():
        if element_type == ElementType.PARAGRAPH:
            para_data = {
                'text': element.text,
                'font_size': element.char_shape.font_size if element.char_shape else None,
                'bold': element.char_shape.bold if element.char_shape else None
            }
            data['paragraphs'].append(para_data)

        elif element_type == ElementType.TABLE:
            table_data = {
                'index': element.table_index,
                'rows': element.rows,
                'cols': element.cols
            }
            data['tables'].append(table_data)

    # JSON 저장
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

### 예제 6: 대용량 파일 처리

```python
from helper_hwp import open_hwp, ElementType

# 제너레이터 사용으로 메모리 효율적 처리
with open_hwp('large_document.hwp') as doc:
    paragraph_count = 0

    for element_type, element in doc.iter_tags():
        if element_type == ElementType.PARAGRAPH:
            paragraph_count += 1

            # 필요한 문단만 처리
            if '중요' in element.text:
                print(f"[{paragraph_count}] {element.text}")
```

## 문제 해결

### Q1: 파일을 찾을 수 없습니다

```python
FileNotFoundError: [Errno 2] No such file or directory: 'example.hwp'
```

**해결:** 파일 경로를 확인하세요. 절대 경로 또는 상대 경로를 올바르게 지정했는지 확인합니다.

```python
from pathlib import Path

hwp_file = Path('example.hwp')
if hwp_file.exists():
    text = hwp_to_txt(str(hwp_file))
else:
    print(f"파일을 찾을 수 없습니다: {hwp_file}")
```

### Q2: 암호화된 파일은 지원하나요?

현재 버전에서는 암호화된 HWP 파일의 복호화를 지원하지 않습니다. 한글에서 암호화를 해제한 후 사용하세요.

```python
from helper_hwp import open_hwp

with open_hwp('document.hwp') as doc:
    if doc.encrypted:
        print("이 파일은 암호화되어 있습니다. 한글에서 암호화를 해제해 주세요.")
```

### Q3: 표가 제대로 추출되지 않습니다

표 추출은 HWP 파일의 구조에 따라 달라질 수 있습니다. `cell_para_counts`를 확인하여 셀 구조를 파악할 수 있습니다.

```python
from helper_hwp import open_hwp, ElementType

with open_hwp('document.hwp') as doc:
    for element_type, element in doc.iter_tags():
        if element_type == ElementType.TABLE:
            print(f"표 {element.table_index}")
            print(f"행/열: {element.rows} x {element.cols}")
            print(f"셀 문단 수: {element.cell_para_counts}")
```

### Q4: 특정 문자가 깨집니다

인코딩 문제일 수 있습니다. 파일 저장 시 UTF-8 인코딩을 사용하세요.

```python
text = hwp_to_txt('document.hwp')
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(text)
```

### Q5: HWP 5.0 미만 버전은 지원하나요?

현재 helper_hwp는 HWP 5.x (CFB 기반) 파일만 지원합니다. HWP 3.0 이하 버전은 다른 형식을 사용하므로 지원하지 않습니다.

```python
from helper_hwp import open_hwp

with open_hwp('document.hwp') as doc:
    print(f"문서 버전: {doc.version}")
    # 5.x 버전인지 확인
```

## 추가 리소스

- [GitHub 저장소](https://github.com/c0z0c-helper/helper_hwp)
- [개발자 문서](https://github.com/c0z0c-helper/helper_hwp/blob/master/DEVELOPER.md)
- [예제 코드](https://github.com/c0z0c-helper/helper_hwp/blob/master/examples/)

## 라이센스

이 프로젝트는 Apache License 2.0 하에 배포됩니다.

출처: [https://github.com/c0z0c-helper/helper_hwp](https://github.com/c0z0c-helper/helper_hwp)

