import streamlit as st
from agent.graph import build

st.set_page_config(page_title="보이스피싱·스미싱 대응 에이전트", page_icon="🛡️", layout="centered")
st.title("🛡️ 보이스피싱·스미싱 대응 에이전트")

@st.cache_resource
def graph():
    return build()

ss = st.session_state
ss.setdefault("analysis", None); ss.setdefault("result", None)

text = st.text_area("의심되는 문자·통화 내용을 붙여넣으세요", height=140)
img = st.file_uploader("또는 스크린샷 업로드", type=["png", "jpg", "jpeg"])

if st.button("분석하기", type="primary") and (text or img):
    with st.spinner("분석 중..."):
        out = graph().invoke({"text": text, "image": img.getvalue() if img else None})
    ss.analysis, ss.result, ss.text = out["analysis"], None, text

a = ss.analysis
if a:
    color = {"높음": "🔴", "중간": "🟠", "낮음": "🟢"}.get(a["위험도"], "⚪")
    st.subheader(f"{color} 위험도 {a['위험도']} · {a['유형']}")
    for r in a["근거"]:
        st.write("• " + r)

    if a["위험도"] != "낮음":
        st.divider()
        st.markdown("### 지금 상황이 어떤가요?")
        status = st.radio("", ["미송금", "송금완료", "악성앱"], horizontal=True,
                          captions=["아직 아무것도 안 했어요", "돈을 보냈어요", "링크 누르고 앱이 깔렸어요"])
        with st.expander("신고서에 넣을 정보 (선택)"):
            d = {"금액": st.text_input("피해 금액"), "송금시각": st.text_input("송금 일시"),
                 "계좌": st.text_input("상대 계좌번호")}
        if st.button("대응 방법 보기"):
            with st.spinner("정리 중..."):
                ss.result = graph().invoke({"text": ss.text, "analysis": a,
                                            "user_status": status, "details": d})

r = ss.result
if r:
    g = r["guide"]
    st.error(g["제목"]); st.write(g["안내"])
    for i, s in enumerate(g["단계"], 1):
        st.checkbox(f"{i}. {s}", key=f"step{i}")
    st.markdown("### 📄 신고서 초안")
    st.text_area("", r["report"], height=320)
    st.markdown("### 👨‍👩‍👧 가족 알림 문구")
    st.code(r["family_msg"], language=None)
