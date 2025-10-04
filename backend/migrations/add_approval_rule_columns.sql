-- ============================================
-- Migration: Add currency_code and priority to approval_rules
-- Date: October 4, 2025
-- ============================================

-- Add currency_code column
ALTER TABLE approval_rules 
ADD COLUMN IF NOT EXISTS currency_code VARCHAR(3) DEFAULT 'USD';

-- Add priority column
ALTER TABLE approval_rules 
ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 1;

-- Add check constraint for priority (must be between 1 and 10)
-- Drop constraint first if it exists (ignore error if it doesn't exist)
DO $$ 
BEGIN
    ALTER TABLE approval_rules DROP CONSTRAINT IF EXISTS approval_rules_priority_check;
EXCEPTION WHEN undefined_object THEN
    NULL;
END $$;

-- Add the constraint
ALTER TABLE approval_rules 
ADD CONSTRAINT approval_rules_priority_check 
CHECK (priority >= 1 AND priority <= 10);

-- Add foreign key for currency_code (optional - only if you want to enforce valid currencies)
-- Uncomment the lines below if you want strict validation
-- DO $$ 
-- BEGIN
--     ALTER TABLE approval_rules DROP CONSTRAINT IF EXISTS approval_rules_currency_code_fkey;
-- EXCEPTION WHEN undefined_object THEN
--     NULL;
-- END $$;
-- ALTER TABLE approval_rules 
-- ADD CONSTRAINT approval_rules_currency_code_fkey 
-- FOREIGN KEY (currency_code) REFERENCES currencies(code);

-- Add helpful comments
COMMENT ON COLUMN approval_rules.currency_code IS 'Currency code for amount comparison (e.g., USD, EUR)';
COMMENT ON COLUMN approval_rules.priority IS 'Rule priority (1=highest, 10=lowest)';

-- Verify the changes
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'approval_rules' 
AND column_name IN ('currency_code', 'priority');
