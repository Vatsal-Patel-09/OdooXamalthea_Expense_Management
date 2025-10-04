# Expense Management Backend - Flask API

This is the backend server for the Expense Management System built with Flask and Supabase.

## 🚀 Quick Start

### Step 1: Setup Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

1. Copy `.env.example` to `.env`
2. Fill in your configuration values:
   - `SECRET_KEY`: Your Flask secret key
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
   - `SUPABASE_SERVICE_KEY`: Your Supabase service role key

### Step 4: Run the Server

```powershell
python app.py
```

The server will start at `http://localhost:5000`

## 📁 Project Structure

```
backend/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## 🔧 Next Steps

- [ ] Set up Supabase integration
- [ ] Create authentication endpoints
- [ ] Implement expense management APIs
- [ ] Add approval workflow logic
- [ ] Integrate OCR for receipt scanning

## 📝 API Endpoints (Coming Soon)

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

### Expenses
- `GET /api/expenses` - List expenses
- `POST /api/expenses` - Create expense
- `GET /api/expenses/:id` - Get expense details
- `PUT /api/expenses/:id` - Update expense
- `DELETE /api/expenses/:id` - Delete expense

### Approvals
- `GET /api/approvals` - List pending approvals
- `POST /api/approvals/:id/approve` - Approve expense
- `POST /api/approvals/:id/reject` - Reject expense

## 🛠️ Development

Make sure to keep your virtual environment activated while developing:

```powershell
.\venv\Scripts\Activate.ps1
```

To deactivate:

```powershell
deactivate
```
