"""사기 판정 정확도 / 유형 분류 정확도 / 오탐률 / 응답시간 측정
사용: py -m eval.run_eval eval/testset_100.csv"""
import sys, time, pandas as pd
from agent.graph import build

path = sys.argv[1] if len(sys.argv) > 1 else "eval/testset.csv"
df = pd.read_csv(path)
g, rows = build(), []
print(f"{len(df)}건 측정 시작 (건당 2~5초, 진행 상황이 아래에 표시됩니다)", flush=True)
for i, r in df.iterrows():
    t0 = time.time()
    try:
        a = g.invoke({"text": r["text"]})["analysis"]
        rows.append({"pred_scam": a["위험도"] != "낮음", "pred_type": a["유형"], "sec": time.time() - t0})
    except Exception as e:
        print(f"  ! {i+1}번 오류: {e}", flush=True)
        rows.append({"pred_scam": None, "pred_type": "오류", "sec": time.time() - t0})
    print(f"[{i+1}/{len(df)}] {r['label']:6} -> {rows[-1]['pred_type']} ({rows[-1]['sec']:.1f}s)", flush=True)

res = pd.concat([df, pd.DataFrame(rows)], axis=1)
res["is_scam"] = res["label"] == "scam"
ok = res[res["pred_scam"].notna()].copy()
ok["pred_scam"] = ok["pred_scam"].astype(bool)

acc = (ok["pred_scam"] == ok["is_scam"]).mean()
sc = ok[ok["is_scam"]]
type_acc = (sc["pred_type"] == sc["type"]).mean()
fpr = ok[~ok["is_scam"]]["pred_scam"].mean()
print()
print(f"판정 정확도 {acc:.1%} (목표 90%↑) | 유형 분류 {type_acc:.1%} (목표 80%↑) | "
      f"오탐률 {fpr:.1%} (목표 10%↓) | 평균 {res.sec.mean():.1f}s, 최대 {res.sec.max():.1f}s (목표 10s↓)")
if len(ok) < len(res):
    print(f"※ 오류로 제외된 건수: {len(res) - len(ok)}")
res.to_csv("eval/result.csv", index=False, encoding="utf-8-sig")
print("\n[판정 오답]")
print(ok[ok["pred_scam"] != ok["is_scam"]][["text", "label", "pred_type"]].to_string())
print("\n[유형 오분류]")
print(sc[sc["pred_type"] != sc["type"]][["text", "type", "pred_type"]].to_string())
