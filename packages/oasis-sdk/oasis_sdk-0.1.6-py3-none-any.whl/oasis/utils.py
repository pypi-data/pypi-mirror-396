import os
import socket

def get_from_env(key: str, default: str = "") -> str:
    """
    환경 변수에서 값을 가져옵니다. 값이 없거나 비어 있으면 기본값을 반환합니다.
    """
    value = os.getenv(key)
    return value if value else default

def get_user_ip() -> str:
    """
    현재 사용자의 IP 주소를 반환합니다.
    로컬 환경에서는 가장 많이 사용되는 네트워크 인터페이스의 IP를 반환합니다.
    서버 환경에서는 X-Forwarded-For 등 별도 처리가 필요할 수 있습니다.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"