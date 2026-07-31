from abc import ABC, abstractmethod
from typing import Optional


class SNSPoster(ABC):
    """모든 SNS 플랫폼 클라이언트가 구현해야 하는 공통 인터페이스.

    새로운 플랫폼(Instagram 등)을 추가할 때는 이 클래스를 상속받아
    post() 메서드만 구현하면 job.py 쪽 로직은 수정할 필요가 없다.
    """

    name: str = "base"
    MAX_LENGTH: Optional[int] = None

    @abstractmethod
    def post(self, text: str) -> bool:
        """텍스트를 게시하고 성공 여부를 bool로 반환한다. 실패 시 예외를 던지지 않고 False를 반환하거나
        호출부에서 예외를 잡아 로깅할 수 있도록 한다."""
        raise NotImplementedError
