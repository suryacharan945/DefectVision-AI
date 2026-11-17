# DefectVision AI — Frontend Container
# Multi-stage or dev container for Vite React application

FROM node:20-alpine

WORKDIR /app

# Copy dependency manifests
COPY package.json package-lock.json* ./

# Install frontend dependencies
RUN npm ci || npm install

# Copy frontend source code
COPY . .

# Expose standard Vite port
EXPOSE 5173

# Launch Vite development server binding to all network interfaces
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
