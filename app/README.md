
# Noise & Code — Self-Generating Blog Engine

**Noise & Code** is a belief-based, science-rooted blog platform that transforms your ideas into positive blog posts using AI.

## 🌱 Features

- Simple blog form
- GPT-powered belief reframing (positive-only blogs)
- Auto-published to homepage
- Trending system based on views
- Flask + SQLite backend

## 🚀 Live Deployment

### One-Click Deploy on Render (Backend)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Run Locally

```bash
git clone https://github.com/yourusername/noise-and-code.git
cd app
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
python app.py
```

Then open `http://localhost:5000`.

---

## ✍️ Blog Generation Philosophy

- Every idea has potential when backed by logic or science.
- All blog posts are reframed into positive beliefs to support self-worth.
- Science helps refine, not erase, unconventional ideas.

## 📁 Structure

- `app.py` — Main backend
- `templates/` — HTML templates
- `database.db` — SQLite storage (auto-created)
- `render.yaml` — For one-click deployment to Render

---

## 🔐 Environment Variables

| Variable         | Purpose             |
|------------------|---------------------|
| `OPENAI_API_KEY` | Used to generate blogs via ChatGPT |

---

## 👥 Created For

Thinkers, builders, dreamers, healers. Anyone with an idea that deserves to live.

