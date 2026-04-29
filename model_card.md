# Model Card: VibeMatcher 2.0

## Model Name

VibeMatcher 2.0 - Offline Retrieval-Augmented Music Recommender

## Intended Use

VibeMatcher recommends songs from a small local catalog based on a user's listening goal and optional structured preferences. It is intended for education, portfolio demonstration, and lightweight music discovery simulation.

It should not be used as a production music recommender, a mental health tool, or a system for making claims about a user's identity, personality, health, culture, or background.

## Base Project

This project extends my Module 3 **Music Recommender Simulation**. The original project used weighted content-based scoring to recommend songs from a CSV catalog. VibeMatcher 2.0 adds retrieval, guarded preference planning, context-aware reranking, confidence scoring, logging, tests, and an evaluation harness.

## System Type

This is not a large language model and does not call an external AI API. It is an applied AI workflow made from modular Python components:

- Local retrieval over `data/intent_guides.csv`.
- Rule-based planning that converts retrieved context into recommendation preferences.
- Content-based scoring over `data/songs.csv`.
- Guardrail and confidence logic.
- Specialized response formatting using synthetic few-shot examples in `data/response_styles.csv`.
- Automated reliability evaluation.

## Data

The song catalog contains 20 synthetic or classroom-scale songs with fields for title, artist, genre, mood, energy, tempo, valence, danceability, acousticness, popularity, decade, and detailed mood.

The retrieval knowledge base contains six listening-intent guides:

- Deep Focus Coding
- Workout Push
- Social Party
- Calm Reset
- Nostalgia Trip
- Road Trip

Each guide includes keywords, preferred genres, moods, target energy, detailed moods, decade hints, rationale, and a guardrail note.

## How It Works

1. Tokenize the user's listening goal.
2. Retrieve matching intent guides by keyword overlap.
3. Plan final preferences from retrieved guidance and optional user controls.
4. Validate inputs with guardrails.
5. Score every song by genre, mood, energy similarity, acousticness, popularity, decade, and detailed mood.
6. Add context-fit bonuses from retrieved guides.
7. Apply an artist diversity penalty.
8. Estimate confidence from top score strength, retrieval quality, and artist diversity.
9. Generate a constrained evidence-backed response that includes best match, retrieved evidence, confidence, and reliability notes.

## Strengths

- Runs locally without API keys or model downloads.
- Produces transparent explanations for every recommendation.
- Shows observable intermediate steps instead of hiding the decision process.
- Handles invalid energy values and unsupported categories safely.
- Includes repeatable tests and a reliability harness.
- Demonstrates specialized response behavior and measures how it differs from a baseline answer.

## Limitations And Biases

- The catalog is very small, so recommendations may repeat genres or artists.
- The retrieval system depends on exact-ish keyword overlap and can miss synonyms.
- The guide set reflects the designer's assumptions about listening contexts.
- Popularity scoring can favor mainstream-style songs.
- English-only keywords limit accessibility.
- It does not use real listening history, collaborative filtering, lyrics, or audio embeddings.

Bias may appear when a listening guide maps a context too narrowly, such as assuming focus music should be lofi or calm music should be acoustic. The system reduces some harm by showing the retrieved guide and allowing the user to lock structured preferences, but it does not eliminate representational bias.

## Misuse Risks And Preventations

Potential misuse:

- Treating music suggestions as mental health or productivity advice.
- Inferring sensitive attributes from music taste.
- Presenting the small catalog as culturally complete.

Mitigations:

- Safety warnings for mental-health-related phrasing.
- Sensitive-attribute warning for protected-trait language.
- Transparent explanations and confidence scores.
- Documentation that states the system is a classroom-scale recommender.

## Evaluation

The reliability harness runs five predefined cases:

```text
Passed: 5/5
Average confidence: 0.76
RAG impact: 3/3 passed; top recommendation changed 3/3
Specialization comparison: 3/3 passed; average evidence marker delta 7.0
```

Covered behaviors:

- Focus query retrieves calm study music.
- Workout query favors high-energy songs.
- Calm query favors acoustic low-energy songs.
- Invalid energy is clamped and warned.
- Unknown query returns a safe fallback rather than crashing.

What surprised me: the retrieval layer made the system much more useful even without a large model. A user can accidentally leave the sidebar on "pop" and "happy," but the text goal "coding focus" still steers the output toward lofi and ambient music.

## Human Evaluation

I inspected the CLI outputs for three end-to-end examples: focus coding, workout push, and calm reset. The top recommendations matched the intended listening context and the explanations exposed why each song ranked highly.

Remaining risk: the tests validate a few important behaviors, not every possible query. A larger deployment would need more test prompts, broader human review, and user feedback loops.

## Specialization Behavior

The system includes a lightweight specialization layer instead of fine-tuning a large model. `data/response_styles.csv` stores synthetic few-shot examples and tone rules for an evidence-backed music-advisor response. The response generator uses workflow evidence to produce a constrained answer with:

- best match
- retrieved guide
- ranking evidence
- confidence
- reliability note

`python src/compare_specialization.py` compares this specialized output to a minimal baseline response. In the current run, all three cases passed, with an average evidence-marker delta of `7.0` and average word-count delta of `78.7`.

## AI Collaboration Reflection

A helpful AI collaboration moment was the suggestion to add a reliability harness with predefined inputs and pass/fail criteria. That made the project stronger than a demo-only recommender because the system now proves basic behavior automatically.

A flawed AI suggestion was to consider using an external model or API for language understanding. That would have added setup friction, cost, and reliability risk. For this assignment, a small offline retrieval system is easier to run, explain, and evaluate.

## Future Improvements

- Expand the song catalog and retrieval guides.
- Add synonym handling or a small local embedding model if downloads are allowed.
- Add user feedback controls for "more like this" and "less like this."
- Track false positives and false negatives from more evaluation prompts.
- Add fairness checks for genre and decade distribution.
- Export evaluation results as JSON for easier portfolio reporting.
