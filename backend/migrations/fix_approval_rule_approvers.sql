-- ============================================
-- Migration: Rename columns in approval_rule_approvers
-- Date: October 4, 2025
-- ============================================

-- Rename approval_rule_id to rule_id (if it exists)
DO $$ 
BEGIN
    ALTER TABLE approval_rule_approvers RENAME COLUMN approval_rule_id TO rule_id;
EXCEPTION WHEN undefined_column THEN
    NULL;
END $$;

-- Rename approver_id to approver_user_id (if it exists)
DO $$ 
BEGIN
    ALTER TABLE approval_rule_approvers RENAME COLUMN approver_id TO approver_user_id;
EXCEPTION WHEN undefined_column THEN
    NULL;
END $$;

-- Rename sequence_order to order_index (if it exists)
DO $$ 
BEGIN
    ALTER TABLE approval_rule_approvers RENAME COLUMN sequence_order TO order_index;
EXCEPTION WHEN undefined_column THEN
    NULL;
END $$;

-- Drop old constraints if they exist
DO $$ 
BEGIN
    ALTER TABLE approval_rule_approvers DROP CONSTRAINT IF EXISTS approval_rule_approvers_approval_rule_id_fkey;
EXCEPTION WHEN undefined_object THEN
    NULL;
END $$;

DO $$ 
BEGIN
    ALTER TABLE approval_rule_approvers DROP CONSTRAINT IF EXISTS approval_rule_approvers_approver_id_fkey;
EXCEPTION WHEN undefined_object THEN
    NULL;
END $$;

-- Add new foreign key constraints
DO $$ 
BEGIN
    ALTER TABLE approval_rule_approvers DROP CONSTRAINT IF EXISTS approval_rule_approvers_rule_id_fkey;
EXCEPTION WHEN undefined_object THEN
    NULL;
END $$;

ALTER TABLE approval_rule_approvers 
ADD CONSTRAINT approval_rule_approvers_rule_id_fkey 
FOREIGN KEY (rule_id) REFERENCES approval_rules(id) ON DELETE CASCADE;

DO $$ 
BEGIN
    ALTER TABLE approval_rule_approvers DROP CONSTRAINT IF EXISTS approval_rule_approvers_approver_user_id_fkey;
EXCEPTION WHEN undefined_object THEN
    NULL;
END $$;

ALTER TABLE approval_rule_approvers 
ADD CONSTRAINT approval_rule_approvers_approver_user_id_fkey 
FOREIGN KEY (approver_user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Add comments
COMMENT ON COLUMN approval_rule_approvers.rule_id IS 'Foreign key to approval_rules table';
COMMENT ON COLUMN approval_rule_approvers.approver_user_id IS 'User ID of the approver (manager or admin)';
COMMENT ON COLUMN approval_rule_approvers.order_index IS 'Order index for sequential approval (0-based)';

-- Verify the changes
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'approval_rule_approvers' 
ORDER BY ordinal_position;
