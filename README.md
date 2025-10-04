# 💼 Expense Management System

A comprehensive expense management system with approval workflows, built with Flask, Next.js, and Supabase.

## ✨ Features

### Core Functionality
- **User Authentication** - Secure JWT-based authentication with role-based access control
- **Expense Management** - Create, view, edit, and submit expenses
- **Receipt Upload** - Upload and attach receipt images to expenses
- **Multi-Currency Support** - Handle expenses in multiple currencies (USD, EUR, GBP, INR, etc.)
- **Category Management** - Organize expenses by customizable categories
- **Real-time Currency Conversion** - Automatic currency conversion using live exchange rates

### Approval Workflow
- **Configurable Approval Rules** - Set up rules based on amount, currency, and category
- **Priority-based Rule Matching** - Intelligent rule matching with priority levels
- **Sequential & Parallel Approvals** - Support for both approval types
- **Manager Dashboard** - Dedicated interface for approvers to review expenses
- **Approval History** - Complete audit trail of all approval actions
- **Auto-approval** - Automatic approval for expenses without matching rules

### User Roles
- **Admin** - Full system access, manage users, categories, and approval rules
- **Manager** - Approve/reject expenses, manage team expenses
- **Employee** - Create and submit expenses, view own expenses

---

## 🛠️ Tech Stack

### Backend
- **Flask 3.1.2** - Python web framework
- **Supabase** - PostgreSQL database and authentication
- **JWT** - JSON Web Tokens for authentication
- **Flask-CORS** - Cross-origin resource sharing
- **Python Decimal** - Precise monetary calculations

### Frontend
- **Next.js 15.5.4** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Re-usable component library
- **React Hook Form** - Form validation and management

### Infrastructure
- **Supabase Storage** - File storage for receipts
- **PostgreSQL** - Relational database
- **Vercel** (optional) - Frontend deployment
- **Railway/Heroku** (optional) - Backend deployment

---

## 📋 Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm/pnpm
- **Supabase Account** (free tier works)
- **Git**

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/OdooXamalthea_Expense_Management.git
cd OdooXamalthea_Expense_Management
```

### 2. Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Run the database migrations in Supabase SQL Editor:
   - `backend/migrations/add_approval_rule_columns.sql`
   - `backend/migrations/fix_approval_rule_approvers.sql`
3. Set up Supabase Storage bucket named `receipts` (public access)
4. Get your API credentials from Settings > API

For detailed setup instructions, see [docs/SUPABASE_SETUP.md](docs/SUPABASE_SETUP.md)

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\\venv\\Scripts\\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your Supabase credentials
```

**Backend .env variables:**
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SECRET_KEY=your_secret_key_for_jwt
EXCHANGE_RATE_API_KEY=your_api_key (optional)
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Create .env.local file
cp .env.example .env.local

# Edit .env.local with your backend URL
```

**Frontend .env.local variables:**
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

---

## 🏃 Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
# Server runs on http://localhost:5000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# or
pnpm dev
# App runs on http://localhost:3000
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Health Check**: http://localhost:5000/api/health

### Default Users

After running database setup, you'll have these default users:

| Email | Password | Role |
|-------|----------|------|
| admin@company.com | admin123 | Admin |
| manager@company.com | manager123 | Manager |
| employee@company.com | employee123 | Employee |

---

## 📁 Project Structure

```
OdooXamalthea_Expense_Management/
├── backend/
│   ├── config/              # Database and configuration
│   ├── routes/              # API endpoints
│   │   ├── auth.py          # Authentication
│   │   ├── users.py         # User management
│   │   ├── categories.py    # Category management
│   │   ├── expenses.py      # Expense CRUD
│   │   ├── approval_rules.py # Approval rule configuration
│   │   └── approvals.py     # Approval workflow
│   ├── utils/               # Utility functions
│   │   ├── auth.py          # JWT and decorators
│   │   ├── currency.py      # Currency conversion
│   │   └── approval_workflow.py # Workflow logic
│   ├── migrations/          # Database migrations
│   ├── app.py              # Flask application entry point
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js App Router
│   │   │   ├── (dashboard)/ # Dashboard layout group
│   │   │   │   ├── expenses/ # Expense pages
│   │   │   │   └── approvals/ # Approval pages
│   │   │   ├── login/      # Login page
│   │   │   └── signup/     # Signup page
│   │   ├── components/     # Reusable components
│   │   ├── contexts/       # React contexts (Auth)
│   │   └── lib/            # Utilities
│   └── package.json        # Node dependencies
│
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md     # System architecture
│   └── SUPABASE_SETUP.md   # Database setup guide
│
├── README.md               # This file
├── .gitignore             # Git ignore rules
└── prd.pdf                # Product Requirements Document
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints

#### POST /auth/signup
Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe",
  "role": "employee"
}
```

#### POST /auth/login
Authenticate user and get JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "success": true,
  "token": "jwt_token_here",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "employee"
  }
}
```

### Expense Endpoints

All expense endpoints require `Authorization: Bearer <token>` header.

#### GET /expenses
List user's expenses (employees see own, managers/admins see all).

#### POST /expenses
Create new expense.

#### GET /expenses/:id
Get single expense details.

#### PUT /expenses/:id
Update expense (draft status only).

#### DELETE /expenses/:id
Delete expense (draft status only).

#### POST /expenses/:id/submit
Submit expense for approval.

### Approval Endpoints

#### GET /approvals
List approvals for the current manager/admin.

#### POST /approvals/:id/approve
Approve an expense.

#### POST /approvals/:id/reject
Reject an expense.

#### GET /approvals/stats
Get approval statistics.

For complete API documentation, see [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

---

## 🧪 Testing

### Manual Testing Workflow

1. **Login as Employee** (`employee@company.com`)
2. **Create Expense** with amount $150
3. **Submit for Approval**
4. **Verify Status** = "Pending Approval"
5. **Login as Manager** (`manager@company.com`)
6. **Go to Approvals Dashboard**
7. **Approve/Reject** the expense
8. **Verify Status Change**

---

## 🐛 Troubleshooting

### Backend Issues

**Issue:** Module not found errors
```bash
# Ensure virtual environment is activated
pip install -r requirements.txt
```

**Issue:** Database connection errors
- Verify Supabase credentials in `.env`
- Check if database migrations are applied

### Frontend Issues

**Issue:** API connection refused
- Ensure backend is running on port 5000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`

**Issue:** CORS errors
- Backend CORS is configured for `localhost:3000`
- Check Flask CORS configuration in `app.py`

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

## 🙏 Acknowledgments

- **Odoo X Amalthea Hackathon** - For the project requirements
- **Supabase** - For the excellent backend infrastructure
- **shadcn/ui** - For beautiful UI components
- **Next.js Team** - For the amazing framework

---

**Made with ❤️ for Odoo X Amalthea Hackathon**
