"""
RecordStream 클래스

HWP 5.0 파일 형식의 레코드 스트림 처리.
- 데이터 레코드: 문서 정보, 본문, 바이너리 데이터 등을 tag_id로 식별
- 계층 구조: 스택을 통해 레벨별 레코드 그룹화 지원

참고: 한글문서파일형식_5.0_revision1.3.txt, Section 4 (데이터 레코드)
"""

from typing import BinaryIO, List, Tuple

from .models import Record


class RecordStream:
    """레코드 계층 구조 순회용 스트림.

    HWP 파일의 binary stream에서 순차적으로 레코드를 읽고,
    tag_id 기반 필터링 및 계층별 스택 관리를 수행.

    Attributes:
        stream: HWP 파일의 binary I/O 스트림
        stack: (level, records) 튜플의 리스트. 계층 구조 순회 시 사용
    """

    def __init__(self, stream: BinaryIO):
        """RecordStream 초기화.

        Args:
            stream: 레코드를 읽을 binary I/O 스트림
        """
        self.stream = stream
        self.stack: List[Tuple[int, List[Record]]] = []

    def read_all_records(self) -> List[Record]:
        """스트림의 모든 레코드 읽기.

        Record.read_from_stream()이 None을 반환할 때까지 반복 읽음.
        스트림 끝 도달 시 읽기 종료.

        Returns:
            읽은 모든 Record 객체의 리스트
        """
        records = []
        while True:
            record = Record.read_from_stream(self.stream)
            if record is None:
                break
            records.append(record)
        return records

    def read_records_by_tag(self, tag_id: int) -> List[Record]:
        """특정 tag_id를 가진 레코드만 필터링.

        HWP 스펙의 tag_id (예: HWPTAG_PARA_HEADER, HWPTAG_SHAPE_COMPONENT_PICTURE)
        에 따라 레코드를 분류할 때 사용.

        Args:
            tag_id: 필터링 대상 tag_id

        Returns:
            tag_id가 일치하는 Record 객체의 리스트
        """
        all_records = self.read_all_records()
        return [r for r in all_records if r.tag_id == tag_id]
