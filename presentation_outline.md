# VibeMatcher 5-7 Minute Presentation Outline

## 1. Problem And Original Prototype

- Original Module 3 project: rule-based music recommender.
- Limitation: users had to manually choose structured preferences.
- Final goal: make it behave more like an applied AI system with retrieval, reliability, and explanations.

## 2. Live Demo

- Run `streamlit run src/streamlit_app.py`.
- Demo input 1: `I need quiet focus music for coding homework in the rain.`
- Demo input 2: `Give me high energy songs for a gym workout.`
- Demo input 3: `I want soft calm music to relax before sleep.`
- Point out retrieved guides, planned preferences, confidence, warnings, and recommendation reasons.

## 3. Architecture

- User input goes to the intent retriever.
- Retriever searches `data/intent_guides.csv`.
- Preference planner merges context with user controls.
- Guardrails validate inputs and add warnings.
- Scorer ranks `data/songs.csv`.
- Evaluator reports confidence and reliability results.

## 4. Reliability And Guardrails

- Run `python src/evaluate_system.py`.
- Show `5/5` passing cases and average confidence `0.76`.
- Explain invalid energy clamping and unknown-query fallback.

## 5. Responsible AI Reflection

- Strength: transparent and reproducible.
- Limitation: small catalog and keyword-based retrieval.
- Misuse prevention: music suggestions only, not health or identity claims.
- AI collaboration: evaluation harness was helpful; using a larger model was unnecessary for this scope.

## 6. Portfolio Close

- This project shows retrieval, modular Python design, explainability, reliability testing, and responsible documentation.
