# DefectVision AI — Frontend Application

[![Live on Vercel](https://img.shields.io/badge/Vercel-Live%20App-black?style=flat&logo=vercel)](https://defectvision-ai.vercel.app/)

The interactive frontend for **DefectVision AI** built with React 19, Vite, Tailwind CSS, Three.js / React Three Fiber, Lucide Icons, and Framer Motion.

## 🚀 Live URL
👉 [**https://defectvision-ai.vercel.app/**](https://defectvision-ai.vercel.app/)

## 🛠️ Development

```bash
# Install dependencies
npm install

# Start local development server (port 5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## ⚙️ Environment Variables

Create `.env.local` if connecting to a remote backend:
```env
VITE_API_URL=https://your-backend-api.onrender.com
```
When unset, all API requests leverage the local Vite proxy forwarding to `http://127.0.0.1:8000`.
