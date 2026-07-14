from abc import ABC
from typing import Optional


class Part(ABC):
    """모든 부품이 공유하는 선택 메시지/리포트 라벨 동작(템플릿 메서드)."""

    label: str
    unit_label: str  # 예: "엔진을", "제동장치를", "조향장치를"

    def selection_message(self) -> str:
        return f"{self.label.upper()} {self.unit_label} 선택하셨습니다."

    def run_label(self) -> Optional[str]:
        return self.label
