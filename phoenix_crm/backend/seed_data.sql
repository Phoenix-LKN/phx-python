-- Seed script for Phoenix CRM database
-- Run this in your Supabase SQL Editor

-- First, let's make sure we have a test user
-- (Replace this ID with your actual authenticated user ID from Supabase Auth)
-- You can find your user ID by running: SELECT id, email FROM auth.users;

-- Insert sample leads
INSERT INTO leads (
    first_name,
    last_name,
    email,
    phone,
    company,
    title,
    source,
    status,
    priority,
    value,
    notes,
    assigned_to,
    created_at,
    updated_at
) VALUES
    -- Lead 1: High priority prospect
    (
        'Sarah',
        'Johnson',
        'sarah.johnson@techcorp.com',
        '+1-555-0101',
        'TechCorp Solutions',
        'VP of Engineering',
        'referral',
        'qualified',
        'high',
        150000.00,
        'Interested in enterprise package. Follow up next week.',
        (SELECT id FROM auth.users LIMIT 1),
        NOW(),
        NOW()
    ),
    
    -- Lead 2: New prospect
    (
        'Michael',
        'Chen',
        'mchen@innovateai.com',
        '+1-555-0102',
        'InnovateAI',
        'CTO',
        'website',
        'new',
        'medium',
        75000.00,
        'Downloaded whitepaper on AI solutions.',
        (SELECT id FROM auth.users LIMIT 1),
        NOW(),
        NOW()
    ),
    
    -- Lead 3: In negotiation
    (
        'Emily',
        'Rodriguez',
        'erodriguez@globalfinance.com',
        '+1-555-0103',
        'Global Finance Inc',
        'Director of IT',
        'linkedin',
        'negotiation',
        'high',
        200000.00,
        'Comparing our proposal with competitors. Decision by end of month.',
        (SELECT id FROM auth.users LIMIT 1),
        NOW(),
        NOW()
    ),
    
    -- Lead 4: Cold lead
    (
        'David',
        'Kim',
        'david.kim@startupxyz.io',
        '+1-555-0104',
        'StartupXYZ',
        'Founder & CEO',
        'cold_call',
        'contacted',
        'low',
        25000.00,
        'Initial contact made. Needs time to review proposal.',
        (SELECT id FROM auth.users LIMIT 1),
        NOW(),
        NOW()
    ),
    
    -- Lead 5: Won deal
    (
        'Jessica',
        'Martinez',
        'jmartinez@cloudservices.com',
        '+1-555-0105',
        'Cloud Services Pro',
        'Head of Operations',
        'referral',
        'won',
        'high',
        180000.00,
        'Contract signed! Implementation starts next quarter.',
        (SELECT id FROM auth.users LIMIT 1),
        NOW() - INTERVAL '7 days',
        NOW()
    ),
    
    -- Lead 6: Lost opportunity
    (
        'Robert',
        'Thompson',
        'rthompson@techventures.com',
        '+1-555-0106',
        'Tech Ventures LLC',
        'Managing Director',
        'conference',
        'lost',
        'medium',
        95000.00,
        'Went with competitor due to pricing.',
        (SELECT id FROM auth.users LIMIT 1),
        NOW() - INTERVAL '14 days',
        NOW()
    ),
    
    -- Lead 7: Active prospect
    (
        'Amanda',
        'Lee',
        'alee@healthtech.io',
        '+1-555-0107',
        'HealthTech Innovations',
        'Product Manager',
        'webinar',
        'qualified',
        'high',
        125000.00,
        'Very interested. Scheduled demo for next Tuesday.',
        (SELECT id FROM auth.users LIMIT 1),
        NOW(),
        NOW()
    ),
    
    -- Lead 8: Early stage
    (
        'Christopher',
        'Anderson',
        'canderson@retailpro.com',
        '+1-555-0108',
        'RetailPro Systems',
        'IT Manager',
        'website',
        'new',
        'medium',
        60000.00,
        'Filled out contact form. Awaiting initial call.',
        (SELECT id FROM auth.users LIMIT 1),
        NOW(),
        NOW()
    ),
    
    -- Lead 9: Follow-up needed
    (
        'Nicole',
        'White',
        'nwhite@eduplatform.com',
        '+1-555-0109',
        'EduPlatform Inc',
        'Chief Academic Officer',
        'linkedin',
        'contacted',
        'high',
        110000.00,
        'Needs approval from board. Follow up in 2 weeks.',
        (SELECT id FROM auth.users LIMIT 1),
        NOW(),
        NOW()
    ),
    
    -- Lead 10: Hot prospect
    (
        'James',
        'Wilson',
        'jwilson@manufacturing.com',
        '+1-555-0110',
        'Advanced Manufacturing Co',
        'VP of Technology',
        'referral',
        'proposal',
        'high',
        220000.00,
        'Proposal sent. Very positive signals. Expecting decision this week.',
        (SELECT id FROM auth.users LIMIT 1),
        NOW(),
        NOW()
    );

-- Verify the data was inserted
SELECT 
    first_name,
    last_name,
    email,
    company,
    status,
    priority,
    value
FROM leads
ORDER BY created_at DESC;

-- Get count by status
SELECT 
    status,
    COUNT(*) as count,
    SUM(value) as total_value
FROM leads
GROUP BY status
ORDER BY count DESC;
