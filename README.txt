# NexaChain — Setup Guide
# =============================================
# Complete beginner's guide to run this project
# =============================================

## FOLDER STRUCTURE
nexachain/
├── app.py                  ← Python backend (Flask)
├── requirements.txt        ← Python packages to install
├── templates/
│   └── index.html          ← Main HTML page (all 3 pages)
└── static/
    ├── css/
    │   └── styles.css      ← All the styling
    └── js/
        └── main.js         ← All JavaScript + API calls


## STEP 1 — Install Python
  Download from: https://www.python.org/downloads/
  ✅ During install, CHECK "Add Python to PATH"
  Verify: open Terminal / Command Prompt → type:  python --version


## STEP 2 — Open Terminal in this folder
  Windows: Right-click the "nexachain" folder → "Open in Terminal"
  Mac/Linux: open Terminal, type:  cd path/to/nexachain


## STEP 3 — Install dependencies
  Run this command:
    pip install -r requirements.txt


## STEP 4 — Start the backend server
  Run:
    python app.py

  You should see:
    ==================================================
      NexaChain Backend  →  http://127.0.0.1:5000
    ==================================================


## STEP 5 — Open the app
  Open your browser and go to:
    http://127.0.0.1:5000

  The full NexaChain app will load! 🎉


## PAGES IN THE APP
  • Driver Dashboard  — Live map, tasks, status toggle
  • Customer Tracking — Search orders (try ORD-2847, ORD-2851, ORD-2863)
  • Admin Panel       — Table, charts, filters, CSV export


## API ENDPOINTS (what the backend provides)
  GET  /api/driver/stats          → driver stats
  GET  /api/driver/tasks          → task list
  POST /api/driver/status         → set on-duty/break/offline
  POST /api/driver/complete/<id>  → mark task done
  GET  /api/track/<order_id>      → track an order
  GET  /api/admin/stats           → admin stats
  GET  /api/admin/deliveries      → paginated delivery table
  GET  /api/admin/chart           → weekly chart data
  GET  /api/admin/alerts          → system alerts
  PATCH /api/admin/delivery/<id>  → update a delivery
  GET  /api/admin/export          → download CSV


## TROUBLESHOOTING
  "ModuleNotFoundError: flask"  → run:  pip install flask flask-cors
  Browser shows blank page      → make sure Flask is running (Step 4)
  Port in use error             → change port in app.py line: app.run(port=5001)
