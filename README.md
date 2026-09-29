# 보이스피싱·스미싱 실시간 대응 에이전트

## 실행
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # Windows: set ANTHROPIC_API_KEY=...
streamlit run app.py
python -m eval.run_eval                  # 정확도·오탐률·응답시간 측정
```

## 구조 (계획서 흐름과 1:1)
| 계획서 단계 | 코드 |
|---|---|
| 입력 분석 → 위험도 판정 | `agent/graph.py: analyze` + `prompts.py` + `rules.py` |
| 상태 확인 | `app.py` 라디오 버튼 (미송금/송금완료/악성앱) |
| 상황별 대응 | `graph.py: respond_*` + `playbooks.py` (고정 절차) |
| 사후 처리 | `graph.py: postprocess` (신고서 초안, 가족 알림 문구) |
| 정확도·오탐률 측정 | `eval/run_eval.py` |

## 일정별 할 일
- 9/29: 위 코드 실행 확인, `analyze` JSON 출력 안정화
- 9/30~10/1: 플레이북 검증(금감원·경찰청 안내와 대조), 분기 테스트
- 10/2: 신고서 항목 다듬기
- 10/3: 모바일 화면 확인 (폰으로 Streamlit 접속)
- 10/4: `eval/testset.csv`를 사기/정상 각 50건 이상으로 확장 후 측정, 오답으로 프롬프트 개선, RAG는 선택
- 10/5: 배포 (Streamlit Community Cloud 또는 AWS/GCP), 시연 리허설
- 10/6: 최종 점검·제출

## 주의
- `playbooks.py`의 전화번호·절차는 발표 전 공식 사이트로 재확인
- 테스트셋은 직접 작성한 합성 데이터임을 발표 때 밝히기 (정상 문자를 충분히 넣어야 오탐률이 의미 있음)
