-- =====================================================
-- FIX: Add paid_by field to expenses table
-- Date: October 4, 2025
-- =====================================================

-- Add paid_by column to expenses table
ALTER TABLE expenses 
ADD COLUMN paid_by VARCHAR(20) 
CHECK (paid_by IN ('personal', 'company')) 
DEFAULT 'personal';

-- Add comment for documentation
COMMENT ON COLUMN expenses.paid_by IS 'Payment method: personal (employee paid) or company (company card)';
