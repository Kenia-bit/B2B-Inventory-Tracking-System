# B2B Inventory Tracking System

A full-stack web application built to help agricultural B2B operations track crop yields, manage farmer profiles, enforce relational data constraints, and view real-time stock metrics.

## Project Overview

* Backend Framework: Python 3, Flask, Flask-SQLAlchemy, Flask-Login
* Database: PostgreSQL (Production on Render) / SQLite (Local Development)
* Frontend Technologies: HTML5, CSS3, JavaScript (Fetch API)
* Deployment Platform: Render Web Service connected to Render PostgreSQL

## System Features

* Authentication System: Secure registration, login, and session management using password hashing.
* Farmer Management: Create, view, update, and delete farmer profiles.
* Relational Data Integrity Constraints: Protect data by automatically blocking the deletion of any farmer who currently has active inventory or harvest records attached to their profile.
* Harvest Logging: Logs crop yield metrics including crop type, weight or quantity, and collection date linked to specific farmer accounts.
* Real-Time Dashboard: Live summary calculations of available inventory and agricultural stock metrics.

## Step-by-Step Local Setup Instructions

To run this project locally, follow these steps in order: 
1.  Clone the repository by running `git clone https://github.com/kenia-bit/b2b_inventory_tracking_system.git` and enter the directory with `cd b2b_inventory_tracking_system`. 
2. Create and activate a virtual environment by running `python3 -m venv venv` followed by `source venv/bin/activate` 
on Linux/macOS (or `python -m venv venv` followed by `venv\Scripts\activate` on Windows). 
3. Install all required dependencies by running `pip install -r requirements.txt`. 
4. Create a `.env` file in your root folder containing `FLASK_APP=app.py`, `FLASK_ENV=development`, `SECRET_KEY=supersecretkey123`, and `DATABASE_URL=sqlite:///app.db`. 
5. Initialize the local database tables by running `python3 -c "from app import app, db; app.app_context().push(); db.create_all()"`. 
6. Start the local server by running `flask run` and open your web browser to `http://127.0.0.1:5000`.

## Production Deployment Setup (Render)
This project is configured for automated web deployment on Render using a PostgreSQL database instance. The build command is set to `pip install -r requirements.txt`, the start command is set to `gunicorn app:app`, and environment variables `SECRET_KEY` and `DATABASE_URL` are securely linked directly through the Render environment dashboard.

## License
This project is open-source and developed for academic assessment purposes.

## URL for the System
https://b2b-inventory-tracking-system.onrender.com/
