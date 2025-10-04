-- =====================================================
-- EXPENSE MANAGEMENT SYSTEM - DATABASE SCHEMA
-- Supabase PostgreSQL Database
-- Created: October 4, 2025
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLE: companies
-- Stores company information
-- =====================================================
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- TABLE: users
-- Stores user accounts with role-based access
-- Roles: admin, manager, employee
-- =====================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'manager', 'employee')),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    manager_id UUID REFERENCES users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- TABLE: categories
-- Expense categories per company
-- =====================================================
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name, company_id)
);

-- =====================================================
-- TABLE: expenses
-- Main expense records
-- Status: draft, submitted, approved, rejected
-- =====================================================
CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(10) DEFAULT 'USD',
    expense_date DATE NOT NULL,
    description TEXT,
    receipt_url TEXT,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
    submitted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- TABLE: approval_rules
-- Defines approval workflow rules per category
-- =====================================================
CREATE TABLE approval_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    min_amount DECIMAL(12, 2) DEFAULT 0,
    max_amount DECIMAL(12, 2),
    is_sequential BOOLEAN DEFAULT FALSE,
    approval_percentage INTEGER DEFAULT 100 CHECK (approval_percentage > 0 AND approval_percentage <= 100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- TABLE: approval_rule_approvers
-- Links approvers to approval rules (many-to-many)
-- =====================================================
CREATE TABLE approval_rule_approvers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    approval_rule_id UUID REFERENCES approval_rules(id) ON DELETE CASCADE,
    approver_id UUID REFERENCES users(id) ON DELETE CASCADE,
    sequence_order INTEGER DEFAULT 1,
    is_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(approval_rule_id, approver_id)
);

-- =====================================================
-- TABLE: approvals
-- Tracks approval requests and responses
-- Status: pending, approved, rejected
-- =====================================================
CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    expense_id UUID REFERENCES expenses(id) ON DELETE CASCADE,
    approver_id UUID REFERENCES users(id) ON DELETE CASCADE,
    approval_rule_id UUID REFERENCES approval_rules(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    comments TEXT,
    responded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- INDEXES for better query performance
-- =====================================================
CREATE INDEX idx_users_company ON users(company_id);
CREATE INDEX idx_users_manager ON users(manager_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_categories_company ON categories(company_id);
CREATE INDEX idx_expenses_user ON expenses(user_id);
CREATE INDEX idx_expenses_company ON expenses(company_id);
CREATE INDEX idx_expenses_category ON expenses(category_id);
CREATE INDEX idx_expenses_status ON expenses(status);
CREATE INDEX idx_expenses_date ON expenses(expense_date);
CREATE INDEX idx_approval_rules_company ON approval_rules(company_id);
CREATE INDEX idx_approval_rules_category ON approval_rules(category_id);
CREATE INDEX idx_approvals_expense ON approvals(expense_id);
CREATE INDEX idx_approvals_approver ON approvals(approver_id);
CREATE INDEX idx_approvals_status ON approvals(status);

-- =====================================================
-- TRIGGERS for updated_at timestamps
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_expenses_updated_at BEFORE UPDATE ON expenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_approval_rules_updated_at BEFORE UPDATE ON approval_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_approvals_updated_at BEFORE UPDATE ON approvals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- Enable RLS for all tables
-- =====================================================
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE approval_rule_approvers ENABLE ROW LEVEL SECURITY;
ALTER TABLE approvals ENABLE ROW LEVEL SECURITY;

-- Companies: Users can only see their own company
CREATE POLICY "Users can view their own company"
    ON companies FOR SELECT
    USING (id IN (SELECT company_id FROM users WHERE id = auth.uid()));

-- Users: Can view users in their company
CREATE POLICY "Users can view users in their company"
    ON users FOR SELECT
    USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

-- Categories: Can view categories in their company
CREATE POLICY "Users can view categories in their company"
    ON categories FOR SELECT
    USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

-- Expenses: Users can view their own expenses or expenses in their company (managers/admins)
CREATE POLICY "Users can view expenses"
    ON expenses FOR SELECT
    USING (
        user_id = auth.uid() OR
        company_id IN (SELECT company_id FROM users WHERE id = auth.uid())
    );

-- Approval Rules: Can view rules in their company
CREATE POLICY "Users can view approval rules in their company"
    ON approval_rules FOR SELECT
    USING (company_id IN (SELECT company_id FROM users WHERE id = auth.uid()));

-- Approvals: Users can view approvals for their expenses or approvals assigned to them
CREATE POLICY "Users can view relevant approvals"
    ON approvals FOR SELECT
    USING (
        approver_id = auth.uid() OR
        expense_id IN (SELECT id FROM expenses WHERE user_id = auth.uid())
    );

-- =====================================================
-- SAMPLE DATA (Optional - for testing)
-- =====================================================
-- Note: This will be populated through the API endpoints
