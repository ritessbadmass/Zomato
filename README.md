# Zomato AI - Smart Restaurant Recommendations

An AI-powered restaurant discovery platform that helps users find the perfect dining spot based on their preferences.

## Product Overview

**Zomato AI** combines a curated restaurant dataset with Groq's LLM to deliver personalized restaurant recommendations with intelligent explanations.

### Key Features

| Feature | Description |
|---------|-------------|
| **Smart Filtering** | Location, budget, cuisine, and rating-based filtering |
| **AI-Powered Rankings** | LLM ranks restaurants and explains why each matches your preferences |
| **Budget Tags** | Visual budget selection (Rs. 500 to 3000+) for 2 people |
| **Interactive Dropdowns** | Clean, clickable dropdowns for location and cuisine |
| **Real-time Results** | Instant recommendations with detailed explanations |

## Tech Stack

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Vercel        │────▶│    Railway      │────▶│   Groq API      │
│  (React App)    │     │  (FastAPI)      │     │   (LLM)         │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  HuggingFace    │
                        │  (Dataset)      │
                        └─────────────────┘
```

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | React + Vite + Tailwind | User interface |
| **Backend** | FastAPI (Python) | API server |
| **AI Engine** | Groq (llama-3.3-70b) | Restaurant ranking & explanations |
| **Data** | HuggingFace Dataset | Restaurant catalog |
| **Deployment** | Railway + Vercel | Hosting |

## Project Structure

```
zomato-ai/
├── backend/                 # FastAPI backend (Railway)
│   ├── main.py             # API endpoints
│   ├── data_loader.py      # Dataset loading & filtering
│   ├── recommender.py      # Groq LLM integration
│   ├── models.py           # Pydantic models
│   └── requirements.txt    # Python dependencies
│
├── frontend/                # React frontend (Vercel)
│   ├── src/
│   │   ├── App.jsx         # Main app component
│   │   ├── api.js          # API client
│   │   └── components/     # React components
│   │       ├── SearchForm.jsx
│   │       ├── RestaurantCard.jsx
│   │       └── LoadingSpinner.jsx
│   ├── .env.production     # Production API URL
│   └── package.json
│
├── data/                    # Data storage
│   └── processed/
│
├── railway.json            # Railway deployment config
├── requirements.txt        # Root requirements for Railway
├── runtime.txt             # Python version
├── Procfile               # Railway start command
└── DEPLOY.md              # Deployment guide
```

## User Flow

1. **Input Preferences**
   - Select location from dropdown
   - Choose budget tag (Rs. 500 - 3000+)
   - Pick cuisine from dropdown
   - Set minimum rating
   - Add optional preferences

2. **AI Processing**
   - Backend filters restaurants by criteria
   - Groq LLM ranks top matches
   - AI generates personalized explanations

3. **Results Display**
   - Top 5 ranked restaurants
   - Each with: name, location, cuisines, cost, rating
   - AI explanation for each recommendation
   - Summary of overall recommendations

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/filters` | Get locations & cuisines |
| POST | `/api/recommendations` | Get AI recommendations |

## Deployment

- **Backend**: Railway (auto-deploys from GitHub)
- **Frontend**: Vercel (auto-deploys from GitHub)

See [DEPLOY.md](DEPLOY.md) for detailed instructions.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for LLM |

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

Built with AI · Restaurant data from Zomato
