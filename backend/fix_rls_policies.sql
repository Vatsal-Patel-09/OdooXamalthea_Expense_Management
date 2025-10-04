-- =====================================================
-- FIX RLS POLICIES - Disable for Custom JWT Auth
-- Since we're using custom JWT authentication in Flask,
-- we'll disable RLS and handle authorization in the backend
-- =====================================================

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view their own company" ON companies;
DROP POLICY IF EXISTS "Users can view users in their company" ON users;
DROP POLICY IF EXISTS "Users can view categories in their company" ON categories;
DROP POLICY IF EXISTS "Users can view expenses" ON expenses;
DROP POLICY IF EXISTS "Users can view approval rules in their company" ON approval_rules;
DROP POLICY IF EXISTS "Users can view relevant approvals" ON approvals;

-- Disable RLS on all tables (we'll handle authorization in Flask backend)
ALTER TABLE companies DISABLE ROW LEVEL SECURITY;
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE categories DISABLE ROW LEVEL SECURITY;
ALTER TABLE expenses DISABLE ROW LEVEL SECURITY;
ALTER TABLE approval_rules DISABLE ROW LEVEL SECURITY;
ALTER TABLE approval_rule_approvers DISABLE ROW LEVEL SECURITY;
ALTER TABLE approvals DISABLE ROW LEVEL SECURITY;

-- Verification query
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
