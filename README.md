# 🎵 Music Recommender Simulation

## Project Summary

VibeMatcher 1.0 is a content-based music recommendation engine that matches songs to user preferences using weighted scoring. It includes 8 song attributes (genre, mood, energy, valence, danceability, acousticness, popularity, decade, detailed_mood), diversity penalties to avoid artist repetition, and multiple ranking modes (balanced, genre-first, energy-focus). The system uses a 20-song dataset and provides visual table outputs with detailed scoring explanations.

---

## How The System Works

Real-world music recommendation systems like Spotify and YouTube combine collaborative filtering (analyzing similar users' behavior) and content-based filtering (matching song attributes to preferences). They use rich data sources: listening history, skips, likes, playlists, explicit ratings, and song features extracted via audio analysis (tempo, mood, energy, genre tags).

Our VibeMatcher 1.0 focuses on content-based filtering with an expanded attribute set. It calculates weighted scores based on user preferences, applies diversity penalties, and supports multiple ranking modes for flexibility.

**Song Attributes Used:** genre, mood, energy, valence, danceability, acousticness, popularity, decade, detailed_mood

**User Preferences:** genre, mood, energy, likes_acoustic, prefers_popular, favorite_decade, favorite_detailed_mood

**Algorithm Recipe (Balanced Mode):**

- Genre match: +2.0 points
- Mood match: +1.0 point
- Energy similarity: 1 - |song_energy - user_energy| (0-1 scale)
- Acoustic preference: +0.5 if user likes acoustic and song >0.7 acousticness
- Popularity preference: +0.5 if user prefers popular and song >80 popularity
- Decade match: +0.5 if matches user's favorite decade
- Detailed mood match: +0.5 if matches user's favorite detailed mood
- Diversity penalty: -0.5 for each repeated artist in top recommendations
- Total score = sum of all applicable bonuses

**Mode Adjustments:**

- Genre-first: Doubles genre weight (+4.0)
- Energy-focus: Doubles energy similarity weight (0-2 scale)

**Data Flow:**

1. Load 20 songs from CSV with type conversions
2. For each song, calculate score based on user prefs and mode
3. Sort by score descending, apply diversity penalties
4. Return top K recommendations with explanations

**Potential Biases:** May over-prioritize genre in balanced mode; popularity bonuses could favor mainstream songs; diversity penalties help but may reduce optimal matches.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python src/main.py
   ```

### Run the Streamlit app

```bash
streamlit run src/streamlit_app.py
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

We tested the system with 3 diverse user profiles across all 3 ranking modes, demonstrating how different weighting affects recommendations.

### High-Energy Pop Fan Profile

Preferences: genre=pop, mood=happy, energy=0.8, prefers_popular=True, decade=2010s, detailed_mood=upbeat

**Balanced Mode Results:**

```
+-----------------+----------------+---------+---------------------------------------------------------------------------------------------------------------------------+
| Title           | Artist         |   Score | Reasons                                                                                                                   |
+=================+================+=========+===========================================================================================================================+
| Sunrise City    | Neon Echo      |    4.98 | genre match (+2.0), mood match (+1.0), energy similarity (0.98), popularity preference (+0.5), detailed mood match (+0.5) |
+-----------------+----------------+---------+---------------------------------------------------------------------------------------------------------------------------+
| Gym Hero        | Max Pulse      |    3.37 | genre match (+2.0), energy similarity (0.87), decade match (+0.5)                                                         |
+-----------------+----------------+---------+---------------------------------------------------------------------------------------------------------------------------+
| Rooftop Lights  | Indigo Parade  |    2.96 | mood match (+1.0), energy similarity (0.96), popularity preference (+0.5), decade match (+0.5)                            |
+-----------------+----------------+---------+---------------------------------------------------------------------------------------------------------------------------+
```

**Genre-First Mode:** Prioritizes pop songs like "Sunrise City" and "Gym Hero" with higher scores (6.98, 5.37)

**Energy-Focus Mode:** Emphasizes energy matching, boosting songs with similar energy levels

### Chill Lofi Listener Profile

Preferences: genre=lofi, mood=chill, energy=0.4, likes_acoustic=True, decade=2020s, detailed_mood=relaxed

**Balanced Mode Results:**

```
+---------------------+----------------+---------+-------------------------------------------------------------------------------------------------------------------------+
| Title               | Artist         |   Score | Reasons                                                                                                                 |
+=====================+================+=========+=========================================================================================================================+
| Midnight Coding     | LoRoom         |    4.98 | genre match (+2.0), mood match (+1.0), energy similarity (0.98), acoustic preference (+0.5), detailed mood match (+0.5) |
+---------------------+----------------+---------+-------------------------------------------------------------------------------------------------------------------------+
| Library Rain        | Paper Lanterns |    4.95 | genre match (+2.0), mood match (+1.0), energy similarity (0.95), acoustic preference (+0.5), decade match (+0.5)        |
+---------------------+----------------+---------+-------------------------------------------------------------------------------------------------------------------------+
| Focus Flow          | LoRoom         |    3.5  | genre match (+2.0), energy similarity (1.00), acoustic preference (+0.5), decade match (+0.5), diversity penalty (-0.5) |
+---------------------+----------------+---------+-------------------------------------------------------------------------------------------------------------------------+
```

Note the diversity penalty on "Focus Flow" (also by LoRoom) to avoid artist repetition.

### Intense Rock Lover Profile

Preferences: genre=rock, mood=intense, energy=0.9, decade=1990s, detailed_mood=aggressive

**Balanced Mode Results:**

```
+--------------+-------------+---------+------------------------------------------------------------------------------------------------------------------+
| Title        | Artist      |   Score | Reasons                                                                                                          |
+==============+=============+=========+==================================================================================================================+
| Storm Runner | Voltline    |    4.99 | genre match (+2.0), mood match (+1.0), energy similarity (0.99), decade match (+0.5), detailed mood match (+0.5) |
+--------------+-------------+---------+------------------------------------------------------------------------------------------------------------------+
| Thunder Clap | Rock Titans |    3.95 | genre match (+2.0), mood match (+1.0), energy similarity (0.95)                                                  |
+--------------+-------------+---------+------------------------------------------------------------------------------------------------------------------+
```

**Mode Comparison:** Genre-first mode boosts rock songs; energy-focus mode prioritizes high-energy tracks regardless of genre.

---

## Limitations and Risks

**Technical Limitations:**

- Small dataset (20 songs) limits discovery of diverse matches
- Simple matching rules miss complex musical relationships
- No collaborative filtering or user history consideration

**Bias Risks:**

- Popularity bonuses may reinforce mainstream music echo chambers
- Genre over-weighting can limit cross-genre discovery
- Decade preferences might exclude quality music from other eras
- Diversity penalties are simplistic and may reduce optimal recommendations

**Real-world Gaps:**

- Lacks user feedback loops for learning
- No consideration of listening context (time of day, activity)
- Missing audio features like key, instrumentation details
- No handling of user mood changes over time

**Ethical Considerations:**

- Could perpetuate cultural biases in music discovery
- Privacy concerns if expanded to real user data
- Potential for filter bubbles reducing musical exploration

---

## Future Improvements

- Integrate collaborative filtering with user similarity analysis
- Add more audio features (key, instrumentation, lyrics sentiment)
- Implement machine learning models for personalized scoring
- Add temporal context (time-of-day, weather, activity)
- Expand dataset and test with real user feedback
- Add explainability features showing why songs were not recommended

---

## Model Card

See [model_card.md](model_card.md) for detailed model documentation including dataset description, algorithm details, strengths, limitations, evaluation results, and ethical considerations.

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:

- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:

- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:

- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"
```
