# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatcher 1.0**

---

## 2. Intended Use

Generates personalized music recommendations based on user preferences for genre, mood, and energy level. Designed for classroom exploration of how recommendation algorithms work, not for real-world production use.

---

## 3. How the Model Works

The model uses content-based filtering. It scores songs by matching user preferences: +2.0 points for genre match, +1.0 for mood match, and energy similarity (1 - absolute difference in energy levels). Total score determines ranking.

---

## 4. Data

20 songs from diverse genres (pop, lofi, rock, electronic, folk, reggae, hip hop, world, classical, jazz) and moods (happy, chill, intense, etc.). Energy ranges from 0.28 to 0.95. Dataset expanded from 10 to 20 songs for variety.

---

## 5. Strengths

Works well for users with specific preferences, providing reasonable matches and clear explanations of why songs were recommended.

---

## 6. Limitations and Bias

Over-prioritizes genre matches, potentially creating filter bubbles by favoring songs from the same genre even if mood/energy don't match perfectly. Dataset is small and may not represent all musical tastes, especially niche genres.

---

## 7. Evaluation

Tested with three profiles: High-Energy Pop, Chill Lofi, Intense Rock. Results generally matched expectations, with top songs having high scores for matching preferences.

---

## 8. Future Work

Add more features like danceability and acousticness to scoring. Implement diversity penalties to avoid recommending too many songs from the same artist/genre. Explore collaborative filtering.

---

## Personal Reflection

Biggest learning: Understanding the difference between scoring individual items and ranking a list. AI tools helped generate code quickly, but I double-checked the math logic. Surprised that simple weighted rules can produce recommendations that feel intuitive. Next, I'd add user feedback loops to refine preferences over time.

Where does your system seem to work well

Prompts:

- User types for which it gives reasonable results
- Any patterns you think your scoring captures correctly
- Cases where the recommendations matched your intuition

---

## 6. Limitations and Bias

Where the system struggles or behaves unfairly.

Prompts:

- Features it does not consider
- Genres or moods that are underrepresented
- Cases where the system overfits to one preference
- Ways the scoring might unintentionally favor some users

---

## 7. Evaluation

How you checked whether the recommender behaved as expected.

Prompts:

- Which user profiles you tested
- What you looked for in the recommendations
- What surprised you
- Any simple tests or comparisons you ran

No need for numeric metrics unless you created some.

---

## 8. Future Work

Ideas for how you would improve the model next.

Prompts:

- Additional features or preferences
- Better ways to explain recommendations
- Improving diversity among the top results
- Handling more complex user tastes

---

## 9. Personal Reflection

A few sentences about your experience.

Prompts:

- What you learned about recommender systems
- Something unexpected or interesting you discovered
- How this changed the way you think about music recommendation apps
