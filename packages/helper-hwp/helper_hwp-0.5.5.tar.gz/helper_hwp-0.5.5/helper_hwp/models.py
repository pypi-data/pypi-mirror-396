"""
HWP 파일 기본 데이터 모델
한글문서파일형식_5.0_revision1.3 참고
"""

import struct
from dataclasses import dataclass
from typing import BinaryIO, Optional

from .constants import HeaderConstants, RecordBitMask


@dataclass
class Version:
    """HWP 버전 정보 (예: 5.1.2.3)"""
    major: int
    minor: int
    micro: int
    build: int

    @classmethod
    def from_u32(cls, value: int):
        """
        u32 값으로부터 버전 생성 (각 8비트씩)
        - value: DWORD 형식의 버전 정보 (0xMMnnPPrr)
          - MM: 문서 형식의 구조가 완전히 바뀌는 경우
          - nn: 큰 구조는 동일하나, 큰 변화가 있는 경우
          - PP: 구조는 동일하나, Record가 추가된 경우
          - rr: Record에 정보가 추가된 경우
        """
        major = (value >> 24) & 0xFF
        minor = (value >> 16) & 0xFF
        micro = (value >> 8) & 0xFF
        build = value & 0xFF
        return cls(major, minor, micro, build)

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.micro}.{self.build}"

@dataclass
class Flags:
    """HWP 파일 플래그 (18비트)"""
    compressed: bool  # 압축 여부
    encrypted: bool  # 암호화 여부
    distributed: bool  # 배포용 문서 (ViewText 사용)
    has_script: bool  # 스크립트 포함
    drm: bool  # DRM 보호
    has_xml_template_storage: bool  # XML 템플릿
    has_vcs: bool  # 버전 관리 시스템
    has_electronic_signature: bool  # 전자 서명
    certificate_encrypted: bool  # 인증서 암호화
    has_signature_spare: bool  # 서명 예비
    has_certificate_drm: bool  # 인증서 DRM
    has_ccl: bool  # CCL 라이선스

    @classmethod
    def from_u32(cls, value: int):
        """
        u32 값으로부터 플래그 생성
        - value: DWORD 형식의 플래그 정보
          - bit 0: 압축 여부
          - bit 1: 암호화 여부
          - bit 2: 배포용 문서 여부
          - bit 3: 스크립트 포함 여부
          - bit 4: DRM 보호 여부
          - bit 5: XML 템플릿 존재 여부
          - bit 6: 버전 관리 시스템 존재 여부
          - bit 7: 전자 서명 포함 여부
          - bit 8: 인증서 암호화 여부
          - bit 9: 서명 예비 여부
          - bit 10: 인증서 DRM 여부
          - bit 11: CCL 라이선스 여부
        """
        return cls(
            compressed=(value & 0x1) != 0,
            encrypted=(value & 0x2) != 0,
            distributed=(value & 0x4) != 0,
            has_script=(value & 0x8) != 0,
            drm=(value & 0x10) != 0,
            has_xml_template_storage=(value & 0x20) != 0,
            has_vcs=(value & 0x40) != 0,
            has_electronic_signature=(value & 0x80) != 0,
            certificate_encrypted=(value & 0x100) != 0,
            has_signature_spare=(value & 0x200) != 0,
            has_certificate_drm=(value & 0x400) != 0,
            has_ccl=(value & 0x800) != 0,
        )

@dataclass
class Header:
    """HWP 파일 헤더 (256 bytes)"""
    signature: bytes  # "HWP Document File" + 버전 정보
    version: Version
    flags: Flags

    @classmethod
    def from_stream(cls, stream: BinaryIO):
        """
        CFB 스트림으로부터 헤더 파싱
        - stream: BinaryIO 스트림
        """
        data = stream.read(HeaderConstants.TOTAL_SIZE)
        if len(data) < HeaderConstants.TOTAL_SIZE:
            raise ValueError("Invalid header size")

        # 서명 확인 (32 bytes)
        signature = data[0:HeaderConstants.SIGNATURE_SIZE]
        if not signature.startswith(b"HWP Document File"):
            raise ValueError("Invalid HWP signature")

        # 버전 (offset 0x20, 4 bytes)
        version_value = struct.unpack('<I', data[HeaderConstants.VERSION_OFFSET:HeaderConstants.FLAGS_OFFSET])[0]
        version = Version.from_u32(version_value)

        # 플래그 (offset 0x24, 4 bytes)
        flags_value = struct.unpack('<I', data[HeaderConstants.FLAGS_OFFSET:HeaderConstants.FLAGS_END])[0]
        flags = Flags.from_u32(flags_value)

        return cls(signature=signature, version=version, flags=flags)

@dataclass
class Record:
    """HWP 레코드"""
    tag_id: int  # 10비트
    level: int  # 10비트
    size: int  # 12비트 또는 32비트
    data: bytes

    @classmethod
    def read_from_stream(cls, stream: BinaryIO) -> Optional['Record']:
        """
        스트림에서 레코드 읽기
        - stream: BinaryIO 스트림
        """
        header_bytes = stream.read(4)
        if len(header_bytes) < 4:
            return None

        header = struct.unpack('<I', header_bytes)[0]

        # 비트 언패킹: tag_id(10) | level(10) | size(12)
        tag_id = header & RecordBitMask.TAG_ID_MASK
        level = (header >> RecordBitMask.LEVEL_SHIFT) & RecordBitMask.LEVEL_MASK
        size = (header >> RecordBitMask.SIZE_SHIFT) & RecordBitMask.SIZE_MASK

        # size가 0xFFF이면 다음 4바이트가 실제 크기
        if size == RecordBitMask.SIZE_EXTENDED:
            size_bytes = stream.read(4)
            size = struct.unpack('<I', size_bytes)[0]

        # 데이터 읽기
        data = stream.read(size)
        if len(data) < size:
            raise ValueError(f"Unexpected end of stream (expected {size} bytes, got {len(data)})")

        return cls(tag_id=tag_id, level=level, size=size, data=data)