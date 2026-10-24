# 🍽️ foodieSense

Personalized food recommendation system built with Python, Streamlit, Pandas, Scikit-learn, and SQLite.

## Project Structure

```
foodieSense/
├── app.py                    # Entry point + page navigation
├── ui.py                     # Shared CSS / UI helpers
├── auth.py                   # Users + feedback database
├── recommender.py            # ML recommendation engine
├── views/
│   ├── login.py              # Login / Sign Up
│   ├── home.py               # Dashboard
│   ├── recommendations.py    # Preferences + dish cards + rating form
│   ├── my_feedback.py        # Rating history
│   └── my_model.py           # Train personal model
├── data/foods.csv
├── feedback.db               # SQLite (auto-created)
└── requirements.txt
```

## How It Works

1. User sets preferences (veg/non-veg, spice level, calories, category)
2. Recommender filters + ranks foods using cosine similarity + ratings
3. Results shown as cards with images, badges, and reason
4. User gives 👍/👎 feedback — saved to SQLite

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```
