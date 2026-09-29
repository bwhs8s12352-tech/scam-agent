"""Claude API 호출 래퍼 (텍스트 + 스크린샷, JSON 파싱)."""
import os, re, json, base64
from anthropic import Anthropic

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
_client = None


def client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(timeout=25.0, max_retries=1)  # 키는 ANTHROPIC_API_KEY 환경변수, 응답 지연 방지용 타임아웃
    return _client


def ask(system: str, text: str, image: bytes | None = None,
        media_type: str = "image/png", max_tokens: int = 1000) -> str:
    content = []
    if image:
        content.append({"type": "image", "source": {
            "type": "base64", "media_type": media_type,
            "data": base64.b64encode(image).decode()}})
    content.append({"type": "text", "text": text})
    r = client().messages.create(model=MODEL, max_tokens=max_tokens, system=system,
                                 messages=[{"role": "user", "content": content}])
    return "".join(b.text for b in r.content if b.type == "text")


def ask_json(system: str, text: str, image: bytes | None = None, retries: int = 1) -> dict:
    for i in range(retries + 1):
        raw = ask(system, text, image)
        m = re.search(r"\{.*\}", re.sub(r"```json|```", "", raw), re.S)
        try:
            return json.loads(m.group(0))
        except Exception:
            if i == retries:
                raise
