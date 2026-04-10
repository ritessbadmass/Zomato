# Zomato AI - Deployment Guide

This guide covers deploying Zomato AI with **Railway** (backend) and **Vercel** (frontend).

---

## Architecture

```
User → Vercel (React SPA) → Railway (FastAPI) → Groq API
                              ↓
                       HuggingFace Dataset
```

---

## Prerequisites

- GitHub account
- [Railway](https://railway.app) account (free tier available)
- [Vercel](https://vercel.com) account (free tier)
- Groq API key

---

## Step 1: Deploy Backend to Railway

### Option A: Deploy via Railway Dashboard (Recommended)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Setup Railway deployment"
   git push origin main
   ```

2. **Create New Project on Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Service**
   - Railway will auto-detect the `railway.json` configuration
   - The build command will install dependencies from `backend/requirements.txt`
   - The start command will launch the FastAPI server

4. **Set Environment Variables**
   - Go to your service → Variables tab
   - Add new variable:
     - Name: `GROQ_API_KEY`
     - Value: your Groq API key

5. **Generate Domain**
   - Go to Settings tab
   - Click "Generate Domain"
   - Copy your backend URL (e.g., `https://zomato-ai-backend.up.railway.app`)

6. **Verify Deployment**
   - Visit `https://your-backend-url.railway.app/api/health`
   - Should return: `{"status": "ok", "message": "Zomato AI backend running"}`

### Option B: Deploy via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up

# Set environment variable
railway variables set GROQ_API_KEY=your_key_here
```

---

## Step 2: Deploy Frontend to Vercel

### Step 2a: Update API URL

Edit [`frontend/.env.production`](frontend/.env.production):

```
VITE_API_BASE_URL=https://your-railway-backend-url.railway.app
```

Replace with your actual Railway backend URL.

### Step 2b: Deploy

#### Option A: Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Click "Deploy"

#### Option B: Vercel CLI

```bash
cd frontend

# Install Vercel CLI if not already installed
npm install -g vercel

# Deploy
vercel --prod
```

---

## Environment Variables Reference

| Variable | Location | Required | Description |
|----------|----------|----------|-------------|
| `GROQ_API_KEY` | Railway | Yes | Groq API key for LLM recommendations |
| `VITE_API_BASE_URL` | Vercel | Yes | URL of Railway backend |

---

## Verification

After deployment:

1. **Test Backend**: Visit `https://your-backend.railway.app/api/filters`
2. **Test Frontend**: Visit your Vercel URL
3. **End-to-End**: Search for restaurants on the frontend

---

## Troubleshooting

### Backend Issues (Railway)

**Build fails**
- Check that `backend/requirements.txt` exists and has all dependencies
- Verify Python version compatibility (3.10+)

**App crashes on start**
- Check Railway logs for errors
- Verify `GROQ_API_KEY` is set correctly
- Ensure `PORT` environment variable is used (Railway sets this automatically)

**CORS errors**
- Backend CORS is already configured to allow all origins in `main.py`
- If issues persist, check that `allow_origins=["*"]` is set

### Frontend Issues (Vercel)

**API calls failing**
- Verify `VITE_API_BASE_URL` is set correctly in `.env.production`
- Ensure no trailing slash in the URL
- Check browser console for CORS errors

**Build fails**
- Ensure `vercel.json` is present in `frontend/` directory
- Check that `dist` folder is created during build

---

## Local Development

### Run Backend Locally
```bash
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Run Frontend Locally
```bash
cd frontend
npm install
npm run dev
```

The frontend will proxy API calls to `localhost:8000` via Vite's dev server proxy.

---

## Updating Deployments

### Update Backend
```bash
git add .
git commit -m "Update backend"
git push origin main
```
Railway will auto-deploy on push.

### Update Frontend
```bash
git add .
git commit -m "Update frontend"
git push origin main
```
Vercel will auto-deploy on push.

---

## Custom Domain (Optional)

### Railway Backend
1. Go to Railway dashboard → Settings
2. Click "Custom Domain"
3. Follow DNS configuration instructions

### Vercel Frontend
1. Go to Vercel dashboard → Domains
2. Add your domain
3. Follow DNS configuration instructions
