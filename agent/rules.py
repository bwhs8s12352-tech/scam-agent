"""LLM 판정 전에 붙이는 규칙 기반 힌트 (정확도 보강 + 근거 제시용)."""
import re

SHORTENERS = ["bit.ly", "me2.do", "url.kr", "han.gl", "vo.la", "t.ly", "goo.gl", "tinyurl.com", "naver.me"]
KEYWORDS = {
    "기관사칭": ["검찰", "경찰", "금융감독원", "금감원", "수사", "범죄 연루", "안전계좌", "계좌 동결"],
    "대출빙자": ["저금리", "대환", "대출 승인", "선입금", "보증료", "정부지원 대출"],
    "택배스미싱": ["택배", "배송", "주소 불일치", "미배송", "반송"],
    "가족사칭": ["엄마", "아빠", "폰 고장", "액정", "급하게 돈", "상품권"],
    "원격/앱설치": ["원격", "앱 설치", "apk", "보안 앱", "팀뷰어", "인증 앱"],
}


def hints(text: str) -> list[str]:
    out = []
    for u in re.findall(r"https?://[^\s]+", text):
        if any(s in u for s in SHORTENERS):
            out.append(f"단축URL 발견: {u}")
        if u.lower().endswith(".apk"):
            out.append(f"APK 링크: {u}")
    for kind, words in KEYWORDS.items():
        found = [w for w in words if w.lower() in text.lower()]
        if found:
            out.append(f"[{kind}] 관련 키워드: {', '.join(found)}")
    return out
