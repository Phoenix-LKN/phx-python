-- Replace 'YOUR_USER_ID_HERE' with your actual user ID from auth.users

INSERT INTO leads (first_name, last_name, email, phone, company, status, priority, value, assigned_to)
VALUES
    ('John', 'Doe', 'john@example.com', '555-0001', 'Acme Corp', 'new', 'high', 50000, 'b1ee73bd-9356-456c-ad44-95bc5861fcd2'),
    ('Jane', 'Smith', 'jane@example.com', '555-0002', 'Tech Solutions', 'qualified', 'medium', 75000, 'b1ee73bd-9356-456c-ad44-95bc5861fcd2'),
    ('Bob', 'Johnson', 'bob@example.com', '555-0003', 'Global Inc', 'proposal', 'high', 100000, 'b1ee73bd-9356-456c-ad44-95bc5861fcd2'),
    ('Alice', 'Williams', 'alice@example.com', '555-0004', 'StartUp LLC', 'contacted', 'low', 25000, 'b1ee73bd-9356-456c-ad44-95bc5861fcd2'),
    ('Charlie', 'Brown', 'charlie@example.com', '555-0005', 'Enterprise Co', 'won', 'high', 150000, 'b1ee73bd-9356-456c-ad44-95bc5861fcd2');
