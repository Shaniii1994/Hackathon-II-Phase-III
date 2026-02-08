-- Migration: Add security fields to User table for rate limiting and account lockout
-- Date: 2026-01-15
-- Description: Adds failed login tracking, account lockout, and last failed login timestamp
--              to support OWASP-compliant authentication security measures

-- Add failed_login_attempts column (default 0)
ALTER TABLE "user"
ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER NOT NULL DEFAULT 0;

-- Add locked_until column (nullable, NULL means not locked)
ALTER TABLE "user"
ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP NULL DEFAULT NULL;

-- Add last_failed_login column (nullable, NULL means no failed attempts)
ALTER TABLE "user"
ADD COLUMN IF NOT EXISTS last_failed_login TIMESTAMP NULL DEFAULT NULL;

-- Add index on locked_until for efficient lockout checks
CREATE INDEX IF NOT EXISTS idx_user_locked_until ON "user"(locked_until);

-- Add index on last_failed_login for rate limiting queries
CREATE INDEX IF NOT EXISTS idx_user_last_failed_login ON "user"(last_failed_login);

-- Verify migration
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'user'
AND column_name IN ('failed_login_attempts', 'locked_until', 'last_failed_login');
