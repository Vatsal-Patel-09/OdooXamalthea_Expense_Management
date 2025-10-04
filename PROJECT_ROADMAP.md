# 📊 Expense Management System - Project Roadmap

## 🏗️ Current Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                          │
│                    [Frontend - TBD]                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              FLASK BACKEND SERVER ✅                         │
│                  (Port 5000)                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │  API Routes                                        │    │
│  │  • /api/auth/*      - Authentication               │    │
│  │  • /api/expenses/*  - Expense Management           │    │
│  │  • /api/approvals/* - Approval Workflows           │    │
│  │  • /api/users/*     - User Management              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Business Logic (Coming in Step 2)                 │    │
│  │  • Authentication & Authorization                  │    │
│  │  • Expense Processing                              │    │
│  │  • Approval Rule Engine                            │    │
│  │  • OCR Integration                                 │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │ Supabase Client
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              SUPABASE (Database + Auth)                      │
│                    [Step 2]                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  PostgreSQL Tables                                 │    │
│  │  • users                                           │    │
│  │  • companies                                       │    │
│  │  • expenses                                        │    │
│  │  • categories                                      │    │
│  │  • approval_rules                                  │    │
│  │  • approvals                                       │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Storage                                           │    │
│  │  • Receipt images                                  │    │
│  │  • User uploads                                    │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## 📅 Development Phases

### ✅ Phase 1: Basic Flask Server Setup (COMPLETE)
- [x] Create backend directory structure
- [x] Set up Flask application
- [x] Configure CORS
- [x] Add health check endpoints
- [x] Install dependencies
- [x] Create environment configuration
- [x] Test server running

### 📍 Phase 2: Supabase Integration (NEXT)
- [ ] Create Supabase project
- [ ] Design database schema
- [ ] Create Supabase client module
- [ ] Set up authentication
- [ ] Test database connection

### 🔮 Phase 3: Authentication System
- [ ] Signup endpoint (Admin + Company creation)
- [ ] Login endpoint with JWT
- [ ] User role management
- [ ] Protected route middleware
- [ ] Password hashing and validation

### 🔮 Phase 4: User Management
- [ ] Create user endpoint (Admin only)
- [ ] List users endpoint
- [ ] Update user endpoint
- [ ] Assign manager to user
- [ ] Role-based permissions

### 🔮 Phase 5: Expense Management
- [ ] Create expense endpoint
- [ ] List expenses (filtered by role)
- [ ] Update expense endpoint
- [ ] Delete expense endpoint
- [ ] Upload receipt image
- [ ] Category management

### 🔮 Phase 6: Approval System
- [ ] Create approval rules
- [ ] Approval rule engine
- [ ] Submit expense for approval
- [ ] Approve/Reject endpoints
- [ ] Sequential vs parallel approval logic
- [ ] Percentage-based approval

### 🔮 Phase 7: Advanced Features
- [ ] OCR for receipt scanning
- [ ] Dashboard analytics
- [ ] Expense reports
- [ ] Email notifications
- [ ] Export to Excel/PDF

### 🔮 Phase 8: Frontend Development
- [ ] Choose frontend framework
- [ ] Authentication UI
- [ ] Expense creation UI
- [ ] Approval workflow UI
- [ ] Dashboard and reports
- [ ] Mobile responsive design

## 🎯 Key Features from PRD

### User Roles
```
┌─────────────────────────────────────────────┐
│ ADMIN                                       │
│ • Create company                            │
│ • Create users (Admin, Manager, Employee)  │
│ • Manage categories                         │
│ • Create approval rules                     │
│ • View all expenses                         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ MANAGER                                     │
│ • Create own expenses                       │
│ • Approve/Reject expenses                   │
│ • View team expenses                        │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ EMPLOYEE                                    │
│ • Create expenses                           │
│ • Upload receipts                           │
│ • View own expenses                         │
│ • Track approval status                     │
└─────────────────────────────────────────────┘
```

### Approval Workflow
```
Expense Created (Draft)
        ↓
Employee Submits
        ↓
Match Approval Rule
        ↓
    ┌───┴───┐
    ↓       ↓
Sequential  Parallel
Approval    Approval
    ↓           ↓
Manager(s)  All Managers
Approve     at Once
    ↓           ↓
    └───┬───┘
        ↓
Check % Threshold
        ↓
    ┌───┴───┐
    ↓       ↓
Approved  Rejected
```

### Database Schema Overview
```sql
-- Core Tables (Phase 2)
users (id, email, name, role, company_id, manager_id)
companies (id, name, currency, created_by)
categories (id, name, company_id)
expenses (id, user_id, category_id, amount, date, status, receipt_url)
approval_rules (id, company_id, category_id, min_amount, max_amount, approvers, is_sequential, approval_percentage)
approvals (id, expense_id, approver_id, status, comments, timestamp)
```

## 🔧 Technology Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT + Supabase Auth
- **File Storage**: Supabase Storage
- **OCR**: To be determined (Phase 7)

### Frontend (To be decided)
- React.js / Next.js / Vue.js
- Tailwind CSS / Material-UI
- State Management: Redux / Zustand

### DevOps (Future)
- Docker containerization
- CI/CD pipeline
- Deployment: Vercel / Railway / Heroku

## 📊 Success Metrics

- [ ] Basic Flask server running ✅
- [ ] Supabase connected
- [ ] Authentication working
- [ ] CRUD operations for expenses
- [ ] Approval workflow functional
- [ ] Frontend integrated
- [ ] OCR for receipts working
- [ ] Production deployment

## 🎉 Current Status

**Step 1 Complete!** ✅

Your Flask backend server is up and running at http://localhost:5000

Ready to move to Step 2: Supabase Integration? 🚀
