-- Seed Data for E-Commerce MVP Testing
-- This data supports the evaluation_questions.json testing

-- Insert Sample Users
INSERT INTO users (id, email, name, verified, loyalty_tier, loyalty_points) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'john@example.com', 'John Doe', TRUE, 'silver', 750),
    ('550e8400-e29b-41d4-a716-446655440002', 'sarah@example.com', 'Sarah Smith', TRUE, 'gold', 2500),
    ('550e8400-e29b-41d4-a716-446655440003', 'mike@example.com', 'Mike Johnson', TRUE, 'bronze', 300),
    ('550e8400-e29b-41d4-a716-446655440004', 'lisa@example.com', 'Lisa Brown', TRUE, 'silver', 1200),
    ('550e8400-e29b-41d4-a716-446655440005', 'david@example.com', 'David Wilson', TRUE, 'bronze', 200),
    ('550e8400-e29b-41d4-a716-446655440006', 'emily@example.com', 'Emily Davis', TRUE, 'platinum', 6000),
    ('550e8400-e29b-41d4-a716-446655440007', 'james@example.com', 'James Miller', TRUE, 'gold', 3000),
    ('550e8400-e29b-41d4-a716-446655440008', 'jane@example.com', 'Jane Anderson', TRUE, 'silver', 1500),
    ('550e8400-e29b-41d4-a716-446655440009', 'bob@example.com', 'Bob Taylor', TRUE, 'bronze', 100),
    ('550e8400-e29b-41d4-a716-446655440010', 'alice@example.com', 'Alice Martinez', TRUE, 'gold', 2800),
    ('550e8400-e29b-41d4-a716-446655440011', 'charlie@example.com', 'Charlie Garcia', TRUE, 'silver', 900),
    ('550e8400-e29b-41d4-a716-446655440012', 'test@example.com', 'Test User', TRUE, 'bronze', 500),
    ('550e8400-e29b-41d4-a716-446655440013', 'ahmedyaqoobbusiness@gmail.com', 'Ahmed Yaqoob', TRUE, 'gold', 3500)
ON CONFLICT (email) DO NOTHING;

-- Insert Sample Products (Men's Clothing)
INSERT INTO products (id, name, description, category, subcategory, price, compare_at_price, sku, status) VALUES
    ('660e8400-e29b-41d4-a716-446655440001', 'Mens Classic Blue Shirt', 'Premium cotton shirt in classic blue', 'Mens Clothing', 'Shirts', 49.99, 59.99, 'MENS-SHIRT-BLUE-001', 'active'),
    ('660e8400-e29b-41d4-a716-446655440002', 'Mens White Dress Shirt', 'Formal white dress shirt', 'Mens Clothing', 'Shirts', 59.99, 69.99, 'MENS-SHIRT-WHITE-001', 'active'),
    ('660e8400-e29b-41d4-a716-446655440003', 'Mens Blue Jeans', 'Classic fit blue denim jeans', 'Mens Clothing', 'Jeans', 79.99, 89.99, 'MENS-JEANS-BLUE-001', 'active'),
    ('660e8400-e29b-41d4-a716-446655440004', 'Mens Black T-Shirt', 'Comfortable cotton t-shirt', 'Mens Clothing', 'T-Shirts', 29.99, 39.99, 'MENS-TSHIRT-BLACK-001', 'active'),
    ('660e8400-e29b-41d4-a716-446655440005', 'Mens Navy Jacket', 'Stylish navy blue jacket', 'Mens Clothing', 'Jackets', 129.99, 149.99, 'MENS-JACKET-NAVY-001', 'active')
ON CONFLICT DO NOTHING;

-- Insert Sample Products (Women's Clothing)
INSERT INTO products (id, name, description, category, subcategory, price, compare_at_price, sku, status) VALUES
    ('660e8400-e29b-41d4-a716-446655440006', 'Womens Summer Dress', 'Beautiful summer dress in floral pattern', 'Womens Clothing', 'Dresses', 69.99, 89.99, 'WOMENS-DRESS-SUMMER-001', 'active'),
    ('660e8400-e29b-41d4-a716-446655440007', 'Womens Black Dress', 'Elegant black dress for formal occasions', 'Womens Clothing', 'Dresses', 89.99, 119.99, 'WOMENS-DRESS-BLACK-001', 'active'),
    ('660e8400-e29b-41d4-a716-446655440008', 'Womens Blue Jeans', 'Slim fit blue jeans', 'Womens Clothing', 'Jeans', 79.99, 99.99, 'WOMENS-JEANS-BLUE-001', 'active'),
    ('660e8400-e29b-41d4-a716-446655440009', 'Womens White Top', 'Casual white blouse', 'Womens Clothing', 'Tops', 39.99, 49.99, 'WOMENS-TOP-WHITE-001', 'active'),
    ('660e8400-e29b-41d4-a716-446655440010', 'Womens Red Skirt', 'Stylish red A-line skirt', 'Womens Clothing', 'Skirts', 49.99, 59.99, 'WOMENS-SKIRT-RED-001', 'active')
ON CONFLICT DO NOTHING;

-- Insert Product Variants
INSERT INTO product_variants (id, product_id, size, color, sku, price, stock_quantity) VALUES
    -- Men's Blue Shirt
    ('770e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440001', 'S', 'Blue', 'MENS-SHIRT-BLUE-S', 49.99, 10),
    ('770e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440001', 'M', 'Blue', 'MENS-SHIRT-BLUE-M', 49.99, 15),
    ('770e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440001', 'L', 'Blue', 'MENS-SHIRT-BLUE-L', 49.99, 8),
    ('770e8400-e29b-41d4-a716-446655440004', '660e8400-e29b-41d4-a716-446655440001', 'XL', 'Blue', 'MENS-SHIRT-BLUE-XL', 49.99, 5),
    -- Men's White Shirt
    ('770e8400-e29b-41d4-a716-446655440005', '660e8400-e29b-41d4-a716-446655440002', 'M', 'White', 'MENS-SHIRT-WHITE-M', 59.99, 12),
    ('770e8400-e29b-41d4-a716-446655440006', '660e8400-e29b-41d4-a716-446655440002', 'L', 'White', 'MENS-SHIRT-WHITE-L', 59.99, 10),
    -- Men's Jeans
    ('770e8400-e29b-41d4-a716-446655440007', '660e8400-e29b-41d4-a716-446655440003', '30', 'Blue', 'MENS-JEANS-30', 79.99, 20),
    ('770e8400-e29b-41d4-a716-446655440008', '660e8400-e29b-41d4-a716-446655440003', '32', 'Blue', 'MENS-JEANS-32', 79.99, 25),
    ('770e8400-e29b-41d4-a716-446655440009', '660e8400-e29b-41d4-a716-446655440003', '34', 'Blue', 'MENS-JEANS-34', 79.99, 18),
    -- Women's Summer Dress
    ('770e8400-e29b-41d4-a716-446655440010', '660e8400-e29b-41d4-a716-446655440006', 'S', 'Floral', 'WOMENS-DRESS-SUMMER-S', 69.99, 8),
    ('770e8400-e29b-41d4-a716-446655440011', '660e8400-e29b-41d4-a716-446655440006', 'M', 'Floral', 'WOMENS-DRESS-SUMMER-M', 69.99, 12),
    ('770e8400-e29b-41d4-a716-446655440012', '660e8400-e29b-41d4-a716-446655440006', 'L', 'Floral', 'WOMENS-DRESS-SUMMER-L', 69.99, 10),
    -- Women's Black Dress
    ('770e8400-e29b-41d4-a716-446655440013', '660e8400-e29b-41d4-a716-446655440007', '4', 'Black', 'WOMENS-DRESS-BLACK-4', 89.99, 6),
    ('770e8400-e29b-41d4-a716-446655440014', '660e8400-e29b-41d4-a716-446655440007', '6', 'Black', 'WOMENS-DRESS-BLACK-6', 89.99, 8),
    ('770e8400-e29b-41d4-a716-446655440015', '660e8400-e29b-41d4-a716-446655440007', '8', 'Black', 'WOMENS-DRESS-BLACK-8', 89.99, 10),
    -- Women's Jeans
    ('770e8400-e29b-41d4-a716-446655440016', '660e8400-e29b-41d4-a716-446655440008', '6', 'Blue', 'WOMENS-JEANS-6', 79.99, 15),
    ('770e8400-e29b-41d4-a716-446655440017', '660e8400-e29b-41d4-a716-446655440008', '8', 'Blue', 'WOMENS-JEANS-8', 79.99, 20),
    ('770e8400-e29b-41d4-a716-446655440018', '660e8400-e29b-41d4-a716-446655440008', '10', 'Blue', 'WOMENS-JEANS-10', 79.99, 18)
ON CONFLICT DO NOTHING;

-- Insert Sample Orders
INSERT INTO orders (id, user_id, order_number, status, payment_status, payment_method, subtotal, tax, shipping_cost, total_amount, tracking_number, carrier, estimated_delivery) VALUES
    ('880e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'ORD-12345', 'shipped', 'captured', 'Credit Card', 49.99, 4.00, 5.99, 59.98, 'TRACK123456789', 'FedEx', CURRENT_DATE + INTERVAL '3 days'),
    ('880e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', 'ORD-67890', 'delivered', 'captured', 'PayPal', 89.99, 7.20, 0.00, 97.19, 'TRACK987654321', 'UPS', CURRENT_DATE - INTERVAL '2 days'),
    ('880e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440003', 'ORD-11111', 'processing', 'authorized', 'Credit Card', 79.99, 6.40, 0.00, 86.39, NULL, NULL, NULL),
    ('880e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440004', 'ORD-22222', 'pending', 'pending', 'Credit Card', 129.99, 10.40, 12.99, 153.38, NULL, NULL, NULL),
    ('880e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440006', 'ORD-33333', 'shipped', 'captured', 'Apple Pay', 69.99, 5.60, 0.00, 75.59, 'TRACK555666777', 'USPS', CURRENT_DATE + INTERVAL '5 days'),
    ('880e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440007', 'ORD-44444', 'delivered', 'captured', 'Credit Card', 159.98, 12.80, 0.00, 172.78, 'TRACK111222333', 'FedEx', CURRENT_DATE - INTERVAL '5 days'),
    ('880e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440008', 'ORD-55555', 'processing', 'authorized', 'Google Pay', 39.99, 3.20, 5.99, 49.18, NULL, NULL, NULL),
    ('880e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440009', 'ORD-66666', 'shipped', 'captured', 'Credit Card', 49.99, 4.00, 0.00, 53.99, 'TRACK444555666', 'DHL', CURRENT_DATE + INTERVAL '2 days'),
    ('880e8400-e29b-41d4-a716-446655440009', '550e8400-e29b-41d4-a716-446655440010', 'ORD-77777', 'delivered', 'captured', 'PayPal', 79.99, 6.40, 0.00, 86.39, 'TRACK777888999', 'UPS', CURRENT_DATE - INTERVAL '1 day'),
    ('880e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440013', 'ORD-88888', 'shipped', 'captured', 'Credit Card', 149.99, 12.00, 10.99, 172.98, 'TRACK999888777', 'FedEx', CURRENT_DATE + INTERVAL '2 days'),
    ('880e8400-e29b-41d4-a716-446655440011', '550e8400-e29b-41d4-a716-446655440013', 'ORD-99999', 'delivered', 'captured', 'PayPal', 89.99, 7.20, 0.00, 97.19, 'TRACK111222333', 'UPS', CURRENT_DATE - INTERVAL '3 days')
ON CONFLICT DO NOTHING;

-- Insert Order Items
INSERT INTO order_items (id, order_id, product_id, variant_id, product_name, variant_description, quantity, unit_price, total_price) VALUES
    ('990e8400-e29b-41d4-a716-446655440001', '880e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440003', 'Mens Classic Blue Shirt', 'Size: L, Color: Blue', 1, 49.99, 49.99),
    ('990e8400-e29b-41d4-a716-446655440002', '880e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440007', '770e8400-e29b-41d4-a716-446655440013', 'Womens Black Dress', 'Size: 4, Color: Black', 1, 89.99, 89.99),
    ('990e8400-e29b-41d4-a716-446655440003', '880e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440003', '770e8400-e29b-41d4-a716-446655440008', 'Mens Blue Jeans', 'Size: 32, Color: Blue', 1, 79.99, 79.99),
    ('990e8400-e29b-41d4-a716-446655440004', '880e8400-e29b-41d4-a716-446655440004', '660e8400-e29b-41d4-a716-446655440005', NULL, 'Mens Navy Jacket', 'One Size', 1, 129.99, 129.99),
    ('990e8400-e29b-41d4-a716-446655440005', '880e8400-e29b-41d4-a716-446655440005', '660e8400-e29b-41d4-a716-446655440006', '770e8400-e29b-41d4-a716-446655440011', 'Womens Summer Dress', 'Size: M, Color: Floral', 1, 69.99, 69.99),
    ('990e8400-e29b-41d4-a716-446655440006', '880e8400-e29b-41d4-a716-446655440006', '660e8400-e29b-41d4-a716-446655440001', '770e8400-e29b-41d4-a716-446655440002', 'Mens Classic Blue Shirt', 'Size: M, Color: Blue', 2, 49.99, 99.98),
    ('990e8400-e29b-41d4-a716-446655440007', '880e8400-e29b-41d4-a716-446655440006', '660e8400-e29b-41d4-a716-446655440003', '770e8400-e29b-41d4-a716-446655440007', 'Mens Blue Jeans', 'Size: 30, Color: Blue', 1, 79.99, 79.99),
    ('990e8400-e29b-41d4-a716-446655440008', '880e8400-e29b-41d4-a716-446655440007', '660e8400-e29b-41d4-a716-446655440009', NULL, 'Womens White Top', 'One Size', 1, 39.99, 39.99),
    ('990e8400-e29b-41d4-a716-446655440009', '880e8400-e29b-41d4-a716-446655440008', '660e8400-e29b-41d4-a716-446655440008', '770e8400-e29b-41d4-a716-446655440017', 'Womens Blue Jeans', 'Size: 8, Color: Blue', 1, 79.99, 79.99),
    ('990e8400-e29b-41d4-a716-446655440010', '880e8400-e29b-41d4-a716-446655440009', '660e8400-e29b-41d4-a716-446655440003', '770e8400-e29b-41d4-a716-446655440009', 'Mens Blue Jeans', 'Size: 34, Color: Blue', 1, 79.99, 79.99),
    ('990e8400-e29b-41d4-a716-446655440011', '880e8400-e29b-41d4-a716-446655440010', '660e8400-e29b-41d4-a716-446655440005', NULL, 'Mens Navy Jacket', 'One Size', 1, 129.99, 129.99),
    ('990e8400-e29b-41d4-a716-446655440012', '880e8400-e29b-41d4-a716-446655440010', '660e8400-e29b-41d4-a716-446655440004', NULL, 'Mens Black T-Shirt', 'One Size', 1, 29.99, 29.99),
    ('990e8400-e29b-41d4-a716-446655440013', '880e8400-e29b-41d4-a716-446655440011', '660e8400-e29b-41d4-a716-446655440006', '770e8400-e29b-41d4-a716-446655440010', 'Womens Summer Dress', 'Size: S, Color: Floral', 1, 69.99, 69.99)
ON CONFLICT DO NOTHING;

-- Insert Sample Payments
INSERT INTO payments (id, order_id, transaction_id, payment_method, amount, status) VALUES
    ('aa0e8400-e29b-41d4-a716-446655440001', '880e8400-e29b-41d4-a716-446655440001', 'TXN-123456789', 'Credit Card', 59.98, 'captured'),
    ('aa0e8400-e29b-41d4-a716-446655440002', '880e8400-e29b-41d4-a716-446655440002', 'TXN-987654321', 'PayPal', 97.19, 'captured'),
    ('aa0e8400-e29b-41d4-a716-446655440003', '880e8400-e29b-41d4-a716-446655440003', 'TXN-111222333', 'Credit Card', 86.39, 'authorized'),
    ('aa0e8400-e29b-41d4-a716-446655440004', '880e8400-e29b-41d4-a716-446655440005', 'TXN-444555666', 'Apple Pay', 75.59, 'captured'),
    ('aa0e8400-e29b-41d4-a716-446655440005', '880e8400-e29b-41d4-a716-446655440006', 'TXN-777888999', 'Credit Card', 172.78, 'captured'),
    ('aa0e8400-e29b-41d4-a716-446655440006', '880e8400-e29b-41d4-a716-446655440007', 'TXN-101112131', 'Google Pay', 49.18, 'authorized'),
    ('aa0e8400-e29b-41d4-a716-446655440007', '880e8400-e29b-41d4-a716-446655440008', 'TXN-141516171', 'Credit Card', 53.99, 'captured'),
    ('aa0e8400-e29b-41d4-a716-446655440008', '880e8400-e29b-41d4-a716-446655440009', 'TXN-181920212', 'PayPal', 86.39, 'captured')
ON CONFLICT DO NOTHING;

