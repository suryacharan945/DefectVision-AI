# DefectVision AI — Production Deployment Guide

## 1. System Requirements

### Hardware
- **CPU:** Quad-core Intel Core i5 / AMD Ryzen 5 or higher (AVX2 support recommended for FAISS).
- **RAM:** Minimum 8 GB (16 GB recommended for resident caching of all 15 models).
- **GPU:** Optional. PyTorch runs efficiently on CPU with batch latencies under 50 ms.
- **Disk:** 5 GB free disk space for memory bank artifacts and checkpoints.

### Software
- **Operating System:** Linux (Ubuntu 20.04+), Windows 10/11, or macOS.
- **Python:** Version 3.10 to 3.12.
- **Node.js:** Version 18+ and npm 9+.

---

## 2. Installation & Quick Start

### Step 1: Environment Setup
```bash
# Clone the repository
git clone https://github.com/suryacharan945/DefectVision-AI.git
cd DefectVision-AI

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Launch Backend Server
```bash
cd DefectVisionAI
python -m uvicorn app:app --host 0.0.0.0 --port 8001
```
*Wait ~20 seconds for the resident PatchCore models and category classifier to load into memory.*

### Step 3: Launch Frontend Application
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 3. Production Deployment with Systemd / Docker

### Systemd Service Configuration (`/etc/systemd/system/defectvision-api.service`)
```ini
[Unit]
Description=DefectVision AI FastAPI Server
After=network.target

[Service]
Type=simple
User=defectvision
WorkingDirectory=/opt/DefectVision-AI/DefectVisionAI
ExecStart=/opt/DefectVision-AI/.venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8001 --workers 1
Restart=always
RestartSec=5
Environment=KMP_DUPLICATE_LIB_OK=TRUE

[Install]
WantedBy=multi-user.target
```

### Frontend Production Build & Nginx Serving
```bash
cd frontend
npm run build
# Copy dist directory to web root
cp -r dist/* /var/www/defectvision/
```

### Nginx Reverse Proxy Configuration
```nginx
server {
    listen 80;
    server_name defectvision.local;

    root /var/www/defectvision;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 60s;
        client_max_body_size 50M;
    }
}
```
