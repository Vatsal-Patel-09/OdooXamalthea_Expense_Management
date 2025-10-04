# 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                       │
│                      http://localhost:3000                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐      ┌──────────────────┐                  │
│  │   Pages         │      │  AuthContext     │                  │
│  │  - /signup      │◄────►│  - user state    │                  │
│  │  - /login       │      │  - token state   │                  │
│  │  - /dashboard   │      │  - login()       │                  │
│  └────────┬────────┘      │  - signup()      │                  │
│           │               │  - logout()      │                  │
│           │               └────────┬─────────┘                  │
│           │                        │                            │
│           └────────┬───────────────┘                            │
│                    │                                            │
│              ┌─────▼──────┐                                     │
│              │ API Client │                                     │
│              │ (axios)    │                                     │
│              │            │                                     │
│              │ - Add JWT  │                                     │
│              │ - Handle   │                                     │
│              │   errors   │                                     │
│              └─────┬──────┘                                     │
└────────────────────┼────────────────────────────────────────────┘
                     │ HTTP Requests
                     │ Authorization: Bearer <token>
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                    BACKEND (Flask)                               │
│                  http://localhost:5000                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐      ┌──────────────────┐                     │
│  │ Routes       │      │ Auth Utils       │                     │
│  │              │      │                  │                     │
│  │ /auth/signup │◄────►│ - hash_password  │                     │
│  │ /auth/login  │      │ - verify_pass    │                     │
│  │ /auth/me     │      │ - generate_token │                     │
│  │              │      │ - decode_token   │                     │
│  │ @token_req.. │      │ - @decorators    │                     │
│  └──────┬───────┘      └──────────────────┘                     │
│         │                                                        │
│         │              ┌──────────────────┐                     │
│         │              │ Database Config  │                     │
│         └─────────────►│                  │                     │
│                        │ - get_client()   │                     │
│                        │ - service_key    │                     │
│                        └────────┬─────────┘                     │
└─────────────────────────────────┼───────────────────────────────┘
                                  │
                                  │ Supabase Client
                                  │ (PostgreSQL)
┌─────────────────────────────────▼───────────────────────────────┐
│                      SUPABASE DATABASE                           │
│              https://qgrwcmavppzhplbhgwlp.supabase.co            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  companies  │  │    users    │  │  categories │             │
│  │             │  │             │  │             │             │
│  │  - id       │  │  - id       │  │  - id       │             │
│  │  - name     │  │  - email    │  │  - name     │             │
│  │  - currency │  │  - password │  │  - company  │             │
│  │  - created  │  │  - role     │  │             │             │
│  └─────────────┘  │  - company  │  └─────────────┘             │
│                   └─────────────┘                               │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  expenses   │  │ approvals   │  │ approval_   │             │
│  │             │  │             │  │ rules       │             │
│  │  - id       │  │  - id       │  │             │             │
│  │  - user_id  │  │  - expense  │  │  - id       │             │
│  │  - amount   │  │  - approver │  │  - company  │             │
│  │  - status   │  │  - status   │  │  - min_amt  │             │
│  │  - receipt  │  │  - comments │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Examples

### 1. Signup Flow
```
User fills form
    ↓
Frontend: signup({ email, password, name, company_name })
    ↓
API Client: POST /api/auth/signup with JSON body
    ↓
Backend: Validate input → Hash password → Create company
    ↓
Backend: Create admin user → Generate JWT token
    ↓
Backend: Return { success: true, token, user, company }
    ↓
Frontend: Store token + user in localStorage
    ↓
Frontend: Update AuthContext state
    ↓
Frontend: Redirect to /dashboard
```

### 2. Login Flow
```
User enters credentials
    ↓
Frontend: login(email, password)
    ↓
API Client: POST /api/auth/login
    ↓
Backend: Find user by email → Verify password hash
    ↓
Backend: Generate JWT token
    ↓
Backend: Return { success: true, token, user }
    ↓
Frontend: Store in localStorage + update state
    ↓
Frontend: Redirect to /dashboard
```

### 3. Protected API Call
```
User loads dashboard
    ↓
Frontend: api.expenses.list()
    ↓
Axios Interceptor: Add Authorization: Bearer <token>
    ↓
Backend: @token_required decorator validates JWT
    ↓
Backend: If valid → execute route → return data
    ↓
Backend: If invalid → return 401 Unauthorized
    ↓
Frontend Interceptor: On 401 → clear auth → redirect to /login
    ↓
Frontend: Display data or show login page
```

---

## 🔐 Security Layers

```
┌─────────────────────────────────────────────────┐
│ 1. Frontend Route Guard                         │
│    - Check isAuthenticated in AuthContext       │
│    - Redirect to /login if not authenticated    │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 2. JWT Token in Request Header                  │
│    - Axios interceptor adds token automatically │
│    - Format: Authorization: Bearer <token>      │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 3. Backend Token Validation                     │
│    - @token_required decorator                  │
│    - Decode JWT and verify signature            │
│    - Check expiration (24 hours)                │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│ 4. Database Query with Filters                  │
│    - Use current_user.company_id in queries     │
│    - Users only see their company's data        │
│    - Service role key bypasses RLS              │
└─────────────────────────────────────────────────┘
```

---

## 📦 Package Dependencies

### Frontend
- **next**: React framework
- **axios**: HTTP client
- **react**: UI library
- **tailwindcss**: Styling
- **shadcn/ui**: UI components
- **sonner**: Toast notifications

### Backend
- **Flask**: Web framework
- **supabase**: Database client (v2.21.1)
- **PyJWT**: JWT token handling
- **werkzeug**: Password hashing
- **python-dotenv**: Environment variables
- **flask-cors**: CORS support

---

## 🌐 Environment Configuration

### Frontend (`.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

### Backend (`.env`)
```bash
SUPABASE_URL=https://qgrwcmavppzhplbhgwlp.supabase.co
SUPABASE_KEY=eyJhbG... (anon key)
SUPABASE_SERVICE_KEY=eyJhbG... (service role key - used)
SECRET_KEY=dev-secret-key (JWT signing)
```

---

## 🎯 Integration Points

| Feature | Frontend | Backend | Status |
|---------|----------|---------|--------|
| Admin Signup | ✅ Form | ✅ POST /auth/signup | ✅ Working |
| User Login | ✅ Form | ✅ POST /auth/login | ✅ Working |
| Get Current User | ✅ Context | ✅ GET /auth/me | ✅ Working |
| JWT Storage | ✅ localStorage | ✅ Generate/Validate | ✅ Working |
| Protected Routes | ✅ AuthGuard | ✅ @token_required | ✅ Working |
| Error Handling | ✅ Interceptors | ✅ Status codes | ✅ Working |
| CORS | ✅ Config | ✅ Flask-CORS | ✅ Working |

---

## 🚀 Deployment Considerations

### Frontend (Vercel/Netlify)
```bash
# Build command
pnpm build

# Environment variables needed
NEXT_PUBLIC_API_URL=https://your-backend-url.com/api
```

### Backend (Heroku/Railway/Render)
```bash
# Start command
gunicorn app:app

# Environment variables needed
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
SECRET_KEY=...
PORT=5000
```

---

**Complete integration architecture documented!** 🎉
