# Budget API

A FastAPI-based REST API for managing personal budgets and card transactions.

## Features

- User authentication and registration
- Credit/debit card management
- Transaction tracking (income and expenses)
- SQLite database for data persistence
- Modular architecture for easy scaling

## Requirements

- Python 3.7+
- FastAPI
- SQLAlchemy
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fastapi_budget_api
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the FastAPI server:
```bash
cd src
uvicorn main:app --reload
```

2. Access the API documentation at: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /api/v1/token` - Login and get access token
- `POST /api/v1/users/` - Register new user
- `GET /api/v1/users/me/` - Get current user info

### Cards
- `POST /api/v1/cards/` - Create new card
- `GET /api/v1/cards/` - List all user cards
- `GET /api/v1/cards/{card_id}` - Get specific card
- `DELETE /api/v1/cards/{card_id}` - Delete a card

### Transactions
- `POST /api/v1/cards/{card_id}/transactions/` - Create new transaction
- `GET /api/v1/cards/{card_id}/transactions/` - List card transactions
- `DELETE /api/v1/transactions/{transaction_id}` - Delete a transaction

## Security Note

For production deployment:
- Change the SECRET_KEY in security.py
- Configure proper CORS settings in main.py
- Use a production-grade database
- Set up proper environment variables for sensitive data