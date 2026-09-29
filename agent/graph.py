"""LangGraph 상태 그래프:
  [START] -> analyze -> [END]                                        (1차: 판정, 이후 UI에서 상태 질문)
  [START] -> respond_{unsent|sent|malware} -> postprocess -> [END]   (2차: 대응+사후처리)
"""
from datetime import datetime
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from . import llm, rules, prompts
from .playbooks import PLAYBOOKS


class S(TypedDict, total=False):
    text: str
    image: bytes
    analysis: dict
    user_status: str      # 미송금 | 송금완료 | 악성앱
    details: dict         # 금액, 송금시각, 계좌 등 (UI 입력)
    guide: dict
    report: str
    family_msg: str


def analyze(s: S) -> S:
    h = rules.hints(s.get("text") or "")
    prompt = f"[입력]\n{s.get('text') or '(스크린샷만 입력)'}\n\n[규칙 힌트]\n" + ("\n".join(h) or "없음")
    a = llm.ask_json(prompts.ANALYZE_SYSTEM, prompt, s.get("image"))
    a["규칙힌트"] = h
    return {"analysis": a}


def route_start(s: S) -> str:
    if s.get("analysis") and s.get("user_status"):
        return {"미송금": "respond_unsent", "송금완료": "respond_sent",
                "악성앱": "respond_malware"}[s["user_status"]]
    return "analyze"


def _respond(status: str):
    def node(s: S) -> S:
        pb = PLAYBOOKS[status]
        try:
            intro = llm.ask(prompts.GUIDE_SYSTEM,
                            f"상황: {status}\n유형: {s['analysis'].get('유형')}", max_tokens=200)
        except Exception:
            intro = "놀라셨겠지만 침착하게 아래 순서대로만 하시면 됩니다."
        return {"guide": {"제목": pb["제목"], "안내": intro.strip(), "단계": pb["단계"]}}
    return node


def postprocess(s: S) -> S:
    a, d = s["analysis"], s.get("details") or {}
    f = a.get("사실", {})
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = f"""[보이스피싱·스미싱 피해 신고서 (초안)]
작성일시: {now}
피해 상태: {s['user_status']}
사기 유형: {a.get('유형')} (위험도: {a.get('위험도')})
접촉 수단: {f.get('수단','')}
사칭 대상: {f.get('사칭대상','')}
상대 전화번호: {f.get('전화번호','')}
접속 링크: {f.get('링크','')}
요구 내용: {f.get('요구사항','')}
피해 금액: {d.get('금액') or '(입력 필요)'}
송금 일시: {d.get('송금시각') or '(입력 필요)'}
송금 계좌(상대): {d.get('계좌') or f.get('계좌') or '(입력 필요)'}
피해 경위: {'; '.join(a.get('근거', []))}
※ 위 내용을 확인·수정한 뒤 경찰서/금융회사에 제출하세요."""
    try:
        fam = llm.ask(prompts.FAMILY_SYSTEM, f"사기 유형: {a.get('유형')}", max_tokens=300).strip()
    except Exception:
        fam = "최근 사기 문자가 많아요. 모르는 링크는 누르지 마시고, 돈 얘기가 나오면 꼭 저한테 먼저 전화하세요."
    return {"report": report, "family_msg": fam}


def build():
    g = StateGraph(S)
    g.add_node("analyze", analyze)
    for st, name in [("미송금", "respond_unsent"), ("송금완료", "respond_sent"), ("악성앱", "respond_malware")]:
        g.add_node(name, _respond(st))
        g.add_edge(name, "postprocess")
    g.add_node("postprocess", postprocess)
    g.add_conditional_edges(START, route_start)
    g.add_edge("analyze", END)
    g.add_edge("postprocess", END)
    return g.compile()
