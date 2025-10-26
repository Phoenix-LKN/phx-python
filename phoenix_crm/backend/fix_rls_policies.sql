-- Fix RLS policies to prevent infinite recursion

-- === USERS TABLE ===
-- Drop ALL existing policies
DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'users') 
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(r.policyname) || ' ON users';
    END LOOP;
END $$;

-- Disable and re-enable RLS
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create simple, non-recursive policies
CREATE POLICY "authenticated_users_select_all"
ON users FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "users_update_own"
ON users FOR UPDATE
TO authenticated
USING (auth.uid() = id);

CREATE POLICY "users_insert_own"
ON users FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = id);

-- === LEADS TABLE ===
-- Drop ALL existing policies
DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'leads') 
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(r.policyname) || ' ON leads';
    END LOOP;
END $$;

-- Disable and re-enable RLS
ALTER TABLE leads DISABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;

-- Create simple policies
CREATE POLICY "authenticated_leads_all"
ON leads FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);

-- === WORKSHEETS TABLE ===
-- Drop ALL existing policies
DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'worksheets') 
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS ' || quote_ident(r.policyname) || ' ON worksheets';
    END LOOP;
END $$;

-- Disable and re-enable RLS
ALTER TABLE worksheets DISABLE ROW LEVEL SECURITY;
ALTER TABLE worksheets ENABLE ROW LEVEL SECURITY;

-- Create simple policies
CREATE POLICY "authenticated_worksheets_all"
ON worksheets FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);

-- Verify policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename IN ('users', 'leads', 'worksheets')
ORDER BY tablename, policyname;
