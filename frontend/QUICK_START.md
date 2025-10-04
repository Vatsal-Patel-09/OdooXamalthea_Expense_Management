# Quick Start Guide - Frontend + Backend

## Prerequisites
- Backend is running on http://localhost:5000
- Node.js and pnpm installed

## Start Frontend

### Option 1: Using pnpm (Recommended)
```bash
pnpm install  # First time only
pnpm dev
```

### Option 2: Using npm
```bash
npm install   # First time only
npm run dev
```

### Option 3: Using yarn
```bash
yarn install  # First time only
yarn dev
```

## Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api

## Test Flow
1. Go to http://localhost:3000/signup
2. Create an admin account
3. You'll be redirected to dashboard
4. Try logging out and logging in again

## Environment Variables
Edit `.env.local` to change backend URL:
```
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

## Troubleshooting
- If port 3000 is in use, Next.js will ask to use port 3001
- Make sure backend is running first
- Clear browser localStorage if having auth issues
