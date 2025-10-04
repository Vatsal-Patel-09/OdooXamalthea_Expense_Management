# 🔧 DATABASE MIGRATION INSTRUCTIONS

## Step 1: Add `paid_by` Field to Expenses Table

### **Run in Supabase SQL Editor:**

1. Go to your Supabase project: https://supabase.com/dashboard
2. Click on "SQL Editor" in the left sidebar
3. Click "New Query"
4. Copy and paste this SQL:

```sql
-- Add paid_by column to expenses table
ALTER TABLE expenses 
ADD COLUMN paid_by VARCHAR(20) 
CHECK (paid_by IN ('personal', 'company')) 
DEFAULT 'personal';

-- Add comment for documentation
COMMENT ON COLUMN expenses.paid_by IS 'Payment method: personal (employee paid) or company (company card)';
```

5. Click "Run" or press `Ctrl+Enter`
6. You should see: **Success. No rows returned**

### **Verify the Migration:**

Run this query to check if the column was added:

```sql
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_name = 'expenses' AND column_name = 'paid_by';
```

**Expected Result:**
```
column_name | data_type         | column_default | is_nullable
----------- | ----------------- | -------------- | -----------
paid_by     | character varying | 'personal'     | YES
```

### **Test the Constraint:**

Try inserting invalid data (should fail):

```sql
-- This should FAIL (invalid paid_by value)
INSERT INTO expenses (user_id, company_id, amount, expense_date, paid_by)
VALUES (
    'some-uuid',
    'some-uuid', 
    100.00,
    '2025-10-04',
    'invalid_value'  -- This should fail
);
```

**Expected Error:**
```
new row for relation "expenses" violates check constraint "expenses_paid_by_check"
```

✅ If you see this error, the constraint is working correctly!

---

## Step 2: Verify Database Schema

Run this query to see all expenses table columns:

```sql
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'expenses'
ORDER BY ordinal_position;
```

**Expected Columns:**
- id
- user_id
- company_id
- category_id
- amount
- currency
- expense_date
- description
- receipt_url
- **paid_by** ← Should be here now!
- status
- submitted_at
- created_at
- updated_at

---

## ✅ Migration Complete!

Once you see `paid_by` in the column list, the migration is complete and you're ready to use the new field in expense creation!

