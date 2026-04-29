# Project 4 Rubric Checklist

This checklist maps each grading condition to concrete evidence in the repository.

## Required Features: 21/21

| Rubric item | Evidence |
| --- | --- |
| Clear identification of base project | `README.md` section "Original Project"; `model_card.md` section "Base Project" |
| Original scope described accurately | README explains the Module 3 rule-based music recommender and its original limits |
| Substantial new AI feature | Offline RAG workflow in `src/recommender.py`; custom guide data in `data/intent_guides.csv` |
| New feature integrated, not isolated | `run_recommendation_workflow()` is used by `src/main.py`, `src/streamlit_app.py`, tests, and evaluation scripts |
| Feature changes behavior | `python src/compare_rag_impact.py` shows top recommendation changed in 3/3 cases |
| Architecture diagram | `assets/system_architecture.svg`, embedded in README |
| Diagram shows data flow | Diagram shows UI/CLI -> retriever -> planner/guardrails -> scorer -> evaluator/output |
| Diagram matches implementation | Components match `src/recommender.py`, `src/streamlit_app.py`, `src/evaluate_system.py`, and CSV data files |
| End-to-end demo | `python src/main.py` runs three complete example workflows |
| UI demo | `streamlit run src/streamlit_app.py` runs the interactive system |
| 2-3 consistent examples | README includes focus, workout, and calm-reset examples |
| Reliability/guardrail component | Input validation, confidence scoring, warnings, logs, and `src/evaluate_system.py` |
| Reliability mechanism improves behavior | Invalid energy is clamped; unknown query falls back safely; low confidence can warn |
| Guardrail/evaluator examples | `python src/evaluate_system.py` prints pass/fail results and warnings |
| README goals and features | README sections "What The System Does" and "Design Decisions" |
| README setup | README section "Setup Instructions" |
| README sample I/O | README section "Sample Interactions" |
| AI collaboration reflection | README "Reflection"; `model_card.md` "AI Collaboration Reflection" |
| Helpful and flawed AI suggestion | Both are explicitly named in README and model card |
| Limitations and future improvements | README "Reflection"; `model_card.md` "Limitations And Biases" and "Future Improvements" |

## Stretch Features: +8/8

| Stretch item | Evidence |
| --- | --- |
| +2 RAG enhancement | Custom retrieval guide index in `data/intent_guides.csv`; `python src/compare_rag_impact.py` demonstrates top recommendation changes in 3/3 cases |
| +2 Agentic workflow enhancement | `run_recommendation_workflow()` returns observable `plan_steps`; CLI and Streamlit display parse, retrieval, planning, scoring, and confidence steps |
| +2 Fine-tuning or specialization behavior | Synthetic few-shot style data in `data/response_styles.csv`; specialized response generator in `src/recommender.py`; `python src/compare_specialization.py` shows measurable baseline-vs-specialized deltas |
| +2 Test harness/evaluation script | `src/evaluate_system.py` runs predefined cases and prints pass/fail plus confidence summary |

## Verification Commands

```bash
.venv/bin/python -m pytest -q
.venv/bin/python src/evaluate_system.py
.venv/bin/python src/compare_rag_impact.py
.venv/bin/python src/compare_specialization.py
```

Current verified results:

```text
pytest: 6 passed
evaluation harness: 5/5 passed, average confidence 0.76
RAG impact: 3/3 passed, top recommendation changed 3/3
specialization comparison: 3/3 passed, average evidence marker delta 7.0
```
