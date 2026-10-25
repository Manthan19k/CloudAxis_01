# CloudAxis Backend Setup

## Prerequisites
- Python 3.13+
- PostgreSQL 15+

## Setup
1. Create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```
4. Run migrations:
   ```bash
   alembic upgrade head
   ```
5. Run the server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
