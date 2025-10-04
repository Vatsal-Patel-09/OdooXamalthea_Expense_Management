# ✅ Frontend-Backend Integration Checklist

## 📋 Pre-Test Checklist

### Backend
- [ ] Flask server running on port 5000
- [ ] Virtual environment activated
- [ ] All dependencies installed (supabase 2.21.1)
- [ ] `.env` file configured with Supabase credentials
- [ ] Database tables created in Supabase
- [ ] Can access http://localhost:5000/api/health

### Frontend
- [ ] Node.js installed
- [ ] pnpm/npm/yarn installed
- [ ] Dependencies installed (`pnpm install`)
- [ ] `.env.local` file created with API URL
- [ ] Can run `pnpm dev` without errors

---

## 🧪 Testing Checklist

### 1. Signup Flow ✅
- [ ] Navigate to http://localhost:3000/signup
- [ ] Fill in all required fields:
  - [ ] Company Name: "Test Company"
  - [ ] Your Name: "Test Admin"
  - [ ] Email: "admin@test.com"
  - [ ] Password: "SecurePass123" (meets requirements)
- [ ] Click "Create account" button
- [ ] **Expected:** Loading state shows
- [ ] **Expected:** Success toast appears
- [ ] **Expected:** Redirects to /dashboard
- [ ] **Expected:** User info displayed in header
- [ ] **Verify in Supabase:**
  - [ ] New company in `companies` table
  - [ ] New user in `users` table with `role='admin'`
  - [ ] User's `company_id` matches company `id`

### 2. Login Flow ✅
- [ ] Click "Logout" from dashboard
- [ ] Navigate to http://localhost:3000/login
- [ ] Enter credentials from signup
- [ ] Click "Sign in" button
- [ ] **Expected:** Loading state shows
- [ ] **Expected:** Success toast appears
- [ ] **Expected:** Redirects to /dashboard
- [ ] **Expected:** User info displayed correctly

### 3. Token Persistence ✅
- [ ] Login successfully
- [ ] Open DevTools → Application → Local Storage
- [ ] **Verify:** `token` key exists with JWT value
- [ ] **Verify:** `user` key exists with JSON user object
- [ ] Refresh the page (F5)
- [ ] **Expected:** Still logged in (no redirect to login)
- [ ] **Expected:** User info still displayed

### 4. Protected Routes ✅
- [ ] Clear localStorage (DevTools → Application → Clear all)
- [ ] Try to access http://localhost:3000/dashboard
- [ ] **Expected:** Redirects to /login
- [ ] **Expected:** Dashboard does not show

### 5. Logout Flow ✅
- [ ] Login successfully
- [ ] Click "Logout" button
- [ ] **Expected:** Redirects to /login
- [ ] Check localStorage
- [ ] **Verify:** `token` and `user` keys removed
- [ ] Try to access /dashboard
- [ ] **Expected:** Redirects to /login

### 6. Error Handling ✅
- [ ] Go to /login
- [ ] Enter wrong password
- [ ] **Expected:** Error toast shows "Invalid email or password"
- [ ] **Expected:** Does not redirect
- [ ] Enter invalid email format
- [ ] **Expected:** HTML5 validation prevents submit
- [ ] Stop backend server
- [ ] Try to login
- [ ] **Expected:** Error toast shows network error
- [ ] Restart backend
- [ ] Login works again

### 7. Password Validation ✅
- [ ] Go to /signup
- [ ] Enter password: "test"
- [ ] **Expected:** Too short message
- [ ] Enter password: "testtest"
- [ ] **Expected:** No uppercase message (backend validates)
- [ ] Enter password: "TestTest"
- [ ] **Expected:** No number message (backend validates)
- [ ] Enter password: "TestTest1"
- [ ] **Expected:** Passes validation ✅

### 8. Duplicate Email Check ✅
- [ ] Go to /signup
- [ ] Use same email from previous signup
- [ ] Fill all fields
- [ ] Click "Create account"
- [ ] **Expected:** Error toast shows "User with this email already exists"
- [ ] **Expected:** Status code 409 (Conflict)

### 9. JWT Token Expiration ⏰
- [ ] Login successfully
- [ ] Copy JWT token from localStorage
- [ ] Go to https://jwt.io
- [ ] Paste token
- [ ] **Verify:** Payload contains:
  - [ ] `user_id`
  - [ ] `email`
  - [ ] `role`
  - [ ] `company_id`
  - [ ] `exp` (expiration - 24 hours from now)
  - [ ] `iat` (issued at)

### 10. CORS Verification ✅
- [ ] Open browser DevTools → Network tab
- [ ] Login or signup
- [ ] Check the POST request
- [ ] **Verify:** No CORS errors in console
- [ ] **Verify:** Response has proper headers
- [ ] **Verify:** Request completed successfully

---

## 🔍 Backend Verification

### Check Database
- [ ] Open Supabase Dashboard
- [ ] Go to Table Editor
- [ ] Check `companies` table:
  - [ ] Has test company
  - [ ] `currency` is 'USD'
  - [ ] `created_by` matches admin user id
- [ ] Check `users` table:
  - [ ] Has admin user
  - [ ] `email` is correct
  - [ ] `password_hash` starts with "scrypt:"
  - [ ] `role` is 'admin'
  - [ ] `is_active` is true
  - [ ] `company_id` matches company

### Check Backend Logs
```bash
# You should see:
127.0.0.1 - - [timestamp] "POST /api/auth/signup HTTP/1.1" 201
127.0.0.1 - - [timestamp] "POST /api/auth/login HTTP/1.1" 200
127.0.0.1 - - [timestamp] "GET /api/auth/me HTTP/1.1" 200
```

---

## 🐛 Troubleshooting Checklist

### Backend Not Starting
- [ ] Check if port 5000 is already in use
- [ ] Verify virtual environment is activated
- [ ] Check `.env` file exists and has correct values
- [ ] Run `pip list` to verify packages installed
- [ ] Check for Python errors in terminal

### Frontend Not Starting
- [ ] Check if port 3000 is already in use
- [ ] Run `pnpm install` to ensure dependencies
- [ ] Check `.env.local` exists
- [ ] Clear `.next` folder and rebuild
- [ ] Check for TypeScript errors

### Login Fails
- [ ] Backend is running (check http://localhost:5000/api/health)
- [ ] Correct credentials being used
- [ ] Check browser Network tab for actual error
- [ ] Check backend terminal for errors
- [ ] Verify user exists in Supabase

### Redirect Not Working
- [ ] Check AuthContext is wrapping the app (layout.tsx)
- [ ] Verify localStorage has token
- [ ] Check browser console for errors
- [ ] Verify token is valid (not expired)
- [ ] Check if isAuthenticated returns true

### Token Not Attaching
- [ ] Check axios interceptor in api.ts
- [ ] Verify localStorage has token
- [ ] Check browser Network tab → Request Headers
- [ ] Should see: `Authorization: Bearer <token>`

### CORS Errors
- [ ] Backend CORS is enabled (check app.py)
- [ ] Frontend URL matches allowed origins
- [ ] Check browser console for specific CORS error
- [ ] Try accessing API directly (Postman/curl)

---

## ✨ Success Criteria

### All Green ✅
- [ ] Can signup new admin
- [ ] Can login with created user
- [ ] Dashboard shows user info
- [ ] Logout clears auth
- [ ] Protected routes redirect when not logged in
- [ ] Token persists across page refreshes
- [ ] Error messages display correctly
- [ ] No console errors
- [ ] No CORS errors
- [ ] Backend logs show successful requests

### Ready for Production 🚀
- [ ] All tests pass ✅
- [ ] No TypeScript errors
- [ ] No runtime errors
- [ ] Proper error handling
- [ ] Loading states working
- [ ] Toast notifications working
- [ ] Responsive design working
- [ ] Database entries correct

---

## 📊 Test Results Template

```
Date: _______________
Tester: _______________

┌─────────────────────────────────┬────────┬───────────┐
│ Test Case                       │ Status │ Notes     │
├─────────────────────────────────┼────────┼───────────┤
│ 1. Signup Flow                  │ ✅/❌  │           │
│ 2. Login Flow                   │ ✅/❌  │           │
│ 3. Token Persistence            │ ✅/❌  │           │
│ 4. Protected Routes             │ ✅/❌  │           │
│ 5. Logout Flow                  │ ✅/❌  │           │
│ 6. Error Handling               │ ✅/❌  │           │
│ 7. Password Validation          │ ✅/❌  │           │
│ 8. Duplicate Email Check        │ ✅/❌  │           │
│ 9. JWT Token Expiration         │ ✅/❌  │           │
│ 10. CORS Verification           │ ✅/❌  │           │
└─────────────────────────────────┴────────┴───────────┘

Overall Status: ✅ PASS / ❌ FAIL
```

---

**Happy Testing! 🎉**
