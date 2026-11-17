# DefectVision AI — Local Development Frontend Container
# PURPOSE: Runs the Vite development server in local Docker Compose environments.
# NOTE: Cloud production deployment is decoupled: static frontend assets are built
# via 'npm run build' and served from Vercel Edge CDN (see docs/DEPLOYMENT_RUNBOOK.md).

FROM node:20-alpine

WORKDIR /app

# Copy dependency manifests
COPY package.json package-lock.json ./

# Deterministic lockfile-based dependency installation
RUN npm ci

# Copy frontend source code
COPY . .

# Expose standard Vite port
EXPOSE 5173

# Launch Vite development server binding to all network interfaces
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
