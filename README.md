https://predictive-maintenance-i05f.onrender.com

A complete end-to-end predictive maintenance web application built using Flask, Machine Learning, HTML/CSS/JS, and deployed
🚀 Features
🔐 Authentication

User Signup

User Login

Password encryption using bcrypt

NavGuard using localStorage token

🤖 Machine Learning

Random Forest model (rf_zfail.joblib)

Predicts whether a machine will Fail / Normal based on input features

📊 Dashboard

Prediction input form

Real-time statistics

Clean UI with HTML & JavaScript

🧱 Backend (Flask)

REST API endpoints under /auth and /api

CORS enabled

JSON-based communication

Modular structure with:

backend/app.py

backend/routes/auth.py

backend/services/user_service.py

📁 Project Structure
Predictive_Maintenance/
│   app.py 
│   requirements.txt
│
└─── backend/
     │   app.py
     │
     ├─── routes/
     │      auth.py
     │
     ├─── services/
     │      user_service.py
     │
     └─── static/
            auth.html
            dashboard.html
            stats_table.json
            rf_zfail.joblib

🛠️ Installation (Localhost)
1️⃣ Clone the project
git clone https://github.com/varshiniml7/predictive-maintenance.git
cd predictive-maintenance

2️⃣ Install dependencies

Make sure requirements.txt is in root:

pip install -r requirements.txt

3️⃣ Run the backend
python backend/app.py

App will start at:

http://127.0.0.1:5000

4️⃣ Open the frontend

Open:

backend/static/auth.html
Or access directly:

http://127.0.0.1:5000/

🌐 Render Deployment
Required settings:
Root Directory
<empty>

Build Command
pip install -r requirements.txt

Start Command
gunicorn backend.app:app


Make sure to add:

pymysql


to requirements.txt if using MySQL.

🧪 API Endpoints
🔐 AUTH
Method	Endpoint	Description
POST	/auth/signup	Create user
POST	/auth/login	Authenticate user
🤖 ML Prediction
Method	Endpoint	Description
POST	/api/predict	Get machine failure result
📦 Tech Stack
Backend

Python

Flask

Flask-CORS

Flask-Mail

PyMySQL

bcrypt

gunicorn

Machine Learning

scikit-learn

numpy

pandas

joblib

Frontend

HTML

CSS

JavaScript

🧑‍💻 Author

Varshini ML
Predictive Maintenance – AIML Project
