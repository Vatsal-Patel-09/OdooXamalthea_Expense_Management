# ✅ Testing Checklist

Complete testing guide before submission.

---

## 🚀 Pre-Test Setup

### 1. Start Backend Server
```bash
cd backend
# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Start server
python app.py
```
Expected output:
```
🚀 Starting Flask server on http://0.0.0.0:5000
📝 Environment: development
```

### 2. Start Frontend Server
```bash
cd frontend
npm run dev
```
Expected output:
```
▲ Next.js 15.5.4
- Local: http://localhost:3000
```

---

## 🧪 Test Scenarios

### ✅ 1. Authentication Tests

**Test 1.1: Admin Login**
- [ ] Navigate to http://localhost:3000
- [ ] Enter credentials: `admin@expense.com` / `admin123`
- [ ] Click Login
- [ ] ✅ Should redirect to dashboard
- [ ] ✅ Should see "Admin" badge in header

**Test 1.2: Manager Login**
- [ ] Logout
- [ ] Login with: `manager@expense.com` / `manager123`
- [ ] ✅ Should see "Manager" badge

**Test 1.3: Employee Login**
- [ ] Logout
- [ ] Login with: `employee@expense.com` / `employee123`
- [ ] ✅ Should see "Employee" badge

**Test 1.4: Invalid Login**
- [ ] Logout
- [ ] Try invalid credentials
- [ ] ✅ Should show error message

---

### ✅ 2. User Management Tests (Admin Only)

**Test 2.1: View Users**
- [ ] Login as admin
- [ ] Click "Users" in navigation
- [ ] ✅ Should see list of 3 users

**Test 2.2: Create New User**
- [ ] Click "Create User" button
- [ ] Fill form: name, email, password, role
- [ ] Click Submit
- [ ] ✅ User should appear in list
- [ ] ✅ Should show success message

**Test 2.3: Access Control**
- [ ] Login as employee
- [ ] Try to access http://localhost:3000/users directly
- [ ] ✅ Should redirect to dashboard or show error

---

### ✅ 3. Category Management Tests

**Test 3.1: View Categories**
- [ ] Login as admin
- [ ] Click "Categories"
- [ ] ✅ Should see predefined categories (Travel, Food, etc.)

**Test 3.2: Create Category**
- [ ] Click "Add Category"
- [ ] Enter name and description
- [ ] Click Save
- [ ] ✅ Category should appear in list

---

### ✅ 4. Expense Management Tests

**Test 4.1: Create Draft Expense (Employee)**
- [ ] Login as employee
- [ ] Click "Expenses" > "Create Expense"
- [ ] Fill form:
  - Amount: 150
  - Currency: USD
  - Category: Travel
  - Description: "Client meeting taxi"
  - Date: Today
  - Upload receipt (optional)
- [ ] Click "Save as Draft"
- [ ] ✅ Should see expense in list with status "Draft"

**Test 4.2: Edit Draft Expense**
- [ ] Click on draft expense
- [ ] Modify amount to 175
- [ ] Click "Update"
- [ ] ✅ Changes should be saved

**Test 4.3: Delete Draft Expense**
- [ ] Create another draft expense
- [ ] Click delete button
- [ ] Confirm deletion
- [ ] ✅ Expense should be removed

**Test 4.4: View Expense Statistics**
- [ ] Go to Expenses page
- [ ] Check statistics cards at top
- [ ] ✅ Should show: Total, Pending, Approved, Rejected

---

### ✅ 5. Approval Rule Tests (Admin Only)

**Test 5.1: View Approval Rules**
- [ ] Login as admin
- [ ] Navigate to Approval Rules page
- [ ] ✅ Should see existing rules (if any)

**Test 5.2: Create Approval Rule**
- [ ] Click "Create Rule"
- [ ] Fill form:
  - Name: "Manager Approval"
  - Description: "All expenses need manager approval"
  - Min Amount: 0
  - Max Amount: 10000
  - Currency: USD
  - Priority: 1
  - Is Sequential: No
  - Approval Percentage: 100
  - Select Approver: Manager
- [ ] Click Create
- [ ] ✅ Rule should appear in list

**Test 5.3: Edit Approval Rule**
- [ ] Click edit on a rule
- [ ] Change max amount to 5000
- [ ] Click Update
- [ ] ✅ Changes should be saved

**Test 5.4: Delete Approval Rule**
- [ ] Create a test rule
- [ ] Click delete
- [ ] Confirm
- [ ] ✅ Rule should be removed

---

### ✅ 6. Approval Workflow Tests (CRITICAL)

**Test 6.1: Submit Expense for Approval**
- [ ] Login as employee
- [ ] Create a new expense:
  - Amount: 250 USD
  - Category: Travel
  - Description: "Airport transfer"
- [ ] Click "Submit for Approval"
- [ ] ✅ Status should change to "Pending Approval"
- [ ] ✅ Should NOT be able to edit anymore

**Test 6.2: View Pending Approvals (Manager)**
- [ ] Login as manager
- [ ] Click "Approvals" in navigation
- [ ] ✅ Should see the submitted expense
- [ ] ✅ Should show "Pending" status

**Test 6.3: Approve Expense**
- [ ] Click "Approve" button
- [ ] Add comment: "Approved"
- [ ] Click Confirm
- [ ] ✅ Expense should move to "Approved" tab
- [ ] ✅ Should show success message

**Test 6.4: Reject Expense**
- [ ] Login as employee
- [ ] Create another expense (150 USD)
- [ ] Submit for approval
- [ ] Login as manager
- [ ] Go to Approvals
- [ ] Click "Reject" button
- [ ] Add comment: "Need more details"
- [ ] Click Confirm
- [ ] ✅ Expense should move to "Rejected" tab

**Test 6.5: Verify Employee View**
- [ ] Login as employee
- [ ] Go to Expenses page
- [ ] ✅ Should see approved expense with "Approved" status
- [ ] ✅ Should see rejected expense with "Rejected" status

---

### ✅ 7. Currency & Country Tests

**Test 7.1: Multi-Currency Expense**
- [ ] Login as employee
- [ ] Create expense with currency: EUR
- [ ] Amount: 100 EUR
- [ ] Submit
- [ ] ✅ Should accept EUR currency

**Test 7.2: View Countries**
- [ ] Go to Settings (if available)
- [ ] ✅ Should see list of countries with flags

---

### ✅ 8. File Upload Tests

**Test 8.1: Upload Receipt**
- [ ] Create new expense
- [ ] Click "Upload Receipt"
- [ ] Select image file (< 5MB)
- [ ] ✅ Should show preview
- [ ] Save expense
- [ ] ✅ Receipt should be visible in expense details

**Test 8.2: File Size Validation**
- [ ] Try uploading file > 5MB
- [ ] ✅ Should show error message

**Test 8.3: File Type Validation**
- [ ] Try uploading .exe or .zip file
- [ ] ✅ Should show error message (images only)

---

### ✅ 9. Search & Filter Tests

**Test 9.1: Filter by Status**
- [ ] Go to Expenses page
- [ ] Select filter: "Approved"
- [ ] ✅ Should show only approved expenses

**Test 9.2: Filter by Category**
- [ ] Select category filter: "Travel"
- [ ] ✅ Should show only travel expenses

**Test 9.3: Date Range Filter**
- [ ] Select date range (last 7 days)
- [ ] ✅ Should show expenses within range

---

### ✅ 10. Edge Cases

**Test 10.1: Concurrent Approvals**
- [ ] Submit 3 expenses from employee
- [ ] Login as manager
- [ ] Approve all 3 quickly
- [ ] ✅ All should be approved without errors

**Test 10.2: Session Expiry**
- [ ] Login and wait for JWT to expire (if configured)
- [ ] Try to make an action
- [ ] ✅ Should redirect to login

**Test 10.3: Network Error Handling**
- [ ] Stop backend server
- [ ] Try to create expense
- [ ] ✅ Should show appropriate error message

---

## 📊 Expected Results Summary

| Test Category | Total Tests | Priority |
|--------------|-------------|----------|
| Authentication | 4 | 🔴 Critical |
| User Management | 3 | 🟡 High |
| Categories | 2 | 🟢 Medium |
| Expenses | 4 | 🔴 Critical |
| Approval Rules | 4 | 🟡 High |
| Approval Workflow | 5 | 🔴 Critical |
| Currency | 2 | 🟢 Medium |
| File Upload | 3 | 🟡 High |
| Search & Filter | 3 | 🟢 Medium |
| Edge Cases | 3 | 🟡 High |
| **TOTAL** | **33** | - |

---

## 🐛 Bug Reporting Template

If you find any issues during testing:

```markdown
### Bug: [Short Description]

**Severity:** Critical / High / Medium / Low
**Test Case:** [Test number]
**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happened]

**Screenshots:**
[If applicable]

**Console Errors:**
[Browser console or backend logs]
```

---

## ✅ Final Checklist

Before marking as complete:

- [ ] All Critical tests passing
- [ ] All High priority tests passing
- [ ] No console errors in browser
- [ ] No 500 errors in backend
- [ ] All features working as documented
- [ ] File uploads working
- [ ] Approval workflow working end-to-end
- [ ] Multi-user scenarios tested
- [ ] Data persistence verified (refresh page)
- [ ] Logout and re-login works correctly

---

## 🎯 Success Criteria

✅ **Project is submission-ready if:**
1. All Critical tests pass (Authentication, Expenses, Approval Workflow)
2. 90%+ of total tests pass
3. No blocking bugs
4. Core workflow works: Create → Submit → Approve/Reject → View

---

**Good luck with testing! 🚀**
