# 📋 Step 2: Supabase Setup Instructions

## ✅ What We've Done So Far:

1. ✅ Configured `.env` file with your Supabase credentials
2. ✅ Created database schema SQL file (`database_schema.sql`)
3. ✅ Created Supabase client module (`config/database.py`)
4. ✅ Added database test endpoint to Flask app

---

## 🎯 Next: Execute Database Schema

You need to run the SQL schema in your Supabase project to create all the tables.

### **Option 1: Using Supabase Dashboard (EASIEST)** ✨

1. **Go to your Supabase project:**
   - Visit: https://supabase.com/dashboard
   - Open your project: `qgrwcmavppzhplbhgwlp`

2. **Open SQL Editor:**
   - Click on **SQL Editor** in the left sidebar
   - Click **New Query**

3. **Copy and paste the schema:**
   - Open the file: `backend/database_schema.sql`
   - Copy ALL the content
   - Paste it into the SQL Editor

4. **Run the query:**
   - Click **Run** button (or press Ctrl+Enter)
   - Wait for completion (should take ~5 seconds)

5. **Verify tables created:**
   - Click on **Table Editor** in the left sidebar
   - You should see these tables:
     - ✅ companies
     - ✅ users
     - ✅ categories
     - ✅ expenses
     - ✅ approval_rules
     - ✅ approval_rule_approvers
     - ✅ approvals

---

### **Option 2: Using psql (Command Line)**

If you prefer command line:

```bash
psql "postgresql://postgres:FAKeGocgkKFUJFBQ@db.qgrwcmavppzhplbhgwlp.supabase.co:5432/postgres" -f backend/database_schema.sql
```

---

## 🧪 Test the Connection

After creating the tables:

1. **Make sure Flask server is running:**
   ```powershell
   cd backend
   .\venv\Scripts\python.exe app.py
   ```

2. **Test the database connection:**
   - Open browser: http://localhost:5000/api/database/test
   
   **Expected response:**
   ```json
   {
     "success": true,
     "message": "Successfully connected to Supabase",
     "url": "https://qgrwcmavppzhplbhgwlp.supabase.co"
   }
   ```

---

## 📊 Database Schema Overview

Here's what we created:

### **Tables:**

1. **companies** - Company information
   - id, name, currency, created_by, timestamps

2. **users** - User accounts with roles
   - id, email, password_hash, name, role (admin/manager/employee)
   - company_id, manager_id, is_active, timestamps

3. **categories** - Expense categories
   - id, name, description, company_id, is_active, timestamps

4. **expenses** - Main expense records
   - id, user_id, company_id, category_id, amount, currency
   - expense_date, description, receipt_url
   - status (draft/submitted/approved/rejected), timestamps

5. **approval_rules** - Approval workflow rules
   - id, company_id, category_id, name, description
   - min_amount, max_amount, is_sequential, approval_percentage
   - is_active, timestamps

6. **approval_rule_approvers** - Approvers for rules
   - id, approval_rule_id, approver_id, sequence_order
   - is_required, timestamp

7. **approvals** - Approval tracking
   - id, expense_id, approver_id, approval_rule_id
   - status (pending/approved/rejected), comments
   - responded_at, timestamps

### **Features:**
- ✅ UUID primary keys
- ✅ Foreign key relationships
- ✅ Indexes for performance
- ✅ Auto-updating timestamps
- ✅ Row Level Security (RLS) policies
- ✅ Check constraints for data validation

---

## ✅ Checklist

Complete these steps:

- [ ] Open Supabase Dashboard
- [ ] Navigate to SQL Editor
- [ ] Copy `database_schema.sql` content
- [ ] Paste and run in SQL Editor
- [ ] Verify tables created in Table Editor
- [ ] Start Flask server
- [ ] Test database connection: http://localhost:5000/api/database/test
- [ ] Confirm "success": true

---

## 🎉 Once Complete

Let me know when you've:
1. ✅ Run the SQL schema
2. ✅ Verified tables are created
3. ✅ Tested the database connection endpoint

Then we'll move to **Mini-Step 3: Build Authentication Endpoints** 🚀

---

## 🆘 Troubleshooting

### If SQL fails:
- Make sure you copied the ENTIRE schema file
- Check if tables already exist (you may need to drop them first)
- Verify you're connected to the correct database

### If connection test fails:
- Check `.env` file has correct credentials
- Make sure Flask server is running
- Verify Supabase project is active

Let me know if you need help! 😊
