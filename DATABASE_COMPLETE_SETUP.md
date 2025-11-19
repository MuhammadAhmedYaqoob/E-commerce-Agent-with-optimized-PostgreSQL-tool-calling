# Complete Database Setup Guide

## ✅ What Was Created

### 1. Database Schema (`database/schema.sql`)

**13 Tables for MVP E-Commerce:**

1. **users** - Customer accounts with loyalty program
2. **addresses** - Shipping and billing addresses
3. **products** - Product catalog (men's/women's clothing)
4. **product_variants** - Size and color variants
5. **orders** - Order management
6. **order_items** - Items in each order
7. **payments** - Payment transactions
8. **returns** - Return requests
9. **return_items** - Items being returned
10. **graph_cache** - MiniRAG optimization cache
11. **carts** - Shopping carts
12. **cart_items** - Cart items
13. **reviews** - Product reviews

**Features:**
- UUID primary keys
- Foreign key constraints
- Performance indexes
- JSONB for flexible data
- Auto-updating timestamps
- Triggers for data integrity

### 2. Seed Data (`database/seed_data.sql`)

**Test Data Matching Evaluation Questions:**

- **12 Users**: Emails from evaluation_questions.json
  - john@example.com, sarah@example.com, mike@example.com, etc.
  
- **10 Products**: Men's and women's clothing
  - Men's shirts, jeans, jackets
  - Women's dresses, tops, jeans, skirts
  
- **18 Variants**: Size and color combinations
  - Men's: S, M, L, XL, sizes 28-40
  - Women's: XS, S, M, L, XL, sizes 0-18
  
- **9 Orders**: Various statuses
  - ORD-12345, ORD-67890, ORD-11111, ORD-22222, etc.
  - Statuses: pending, processing, shipped, delivered
  
- **10 Order Items**: Product details
- **8 Payments**: Transaction records

### 3. Database Initialization (`database/init_database.py`)

**Automated Setup Script:**
- Creates database if not exists
- Runs schema.sql
- Runs seed_data.sql
- Error handling and verification

### 4. Unified Database Tool (`src/tools/database_tool.py`)

**Supports Both Supabase and Local PostgreSQL:**

- Same interface for both
- Automatic switching based on `USE_SUPABASE` flag
- Optimized queries for both backends
- Graceful fallback to mock mode

**Methods:**
- `get_user_by_email()` - Get user data
- `get_user_orders()` - Get user's orders
- `get_order_by_id()` - Get order details
- `search_orders_by_status()` - Search orders
- `cache_graph_entity()` - Cache for MiniRAG
- `get_cached_entity()` - Retrieve cached data
- `create_user()` - Create new user
- `update_order_status()` - Update order

### 5. Configuration Updates

**Updated `src/config.py`:**
- `USE_SUPABASE` flag (True/False)
- Local PostgreSQL configuration
- Supabase configuration
- Automatic selection

**Updated `.env.example`:**
- Database selection flag
- Local PostgreSQL settings
- Supabase settings (optional)

## 🚀 Quick Setup

### Step 1: Initialize Database

```bash
python database/init_database.py
```

**Expected Output:**
```
[INFO] Creating database 'ecommerce_db'...
[INFO] Database 'ecommerce_db' created successfully
[INFO] Running schema...
[INFO] Executed schema.sql
[INFO] Running seed data...
[INFO] Executed seed_data.sql
[INFO] Database initialization complete!
✅ Database ready for use!
```

### Step 2: Configure .env

Create `.env` file:

```env
# Database Selection
USE_SUPABASE=False

# Local PostgreSQL (used when USE_SUPABASE=False)
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=5432
LOCAL_DB_NAME=ecommerce_db
LOCAL_DB_USER=postgres
LOCAL_DB_PASSWORD=datalens

# OpenAI (add your key)
OPENAI_API_KEY=your_key_here

# Gmail (optional)
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

### Step 3: Test Connection

```python
from src.tools.database_tool import DatabaseTool

db = DatabaseTool()
user = db.get_user_by_email("john@example.com")
print(user)  # Should show user data
```

## 📊 Database Schema Details

### Users Table
- id (UUID)
- email (unique)
- name
- loyalty_tier (bronze/silver/gold/platinum)
- loyalty_points
- verified

### Orders Table
- id (UUID)
- order_number (unique, e.g., ORD-12345)
- user_id
- status (pending/processing/shipped/delivered/cancelled/returned/refunded)
- payment_status
- total_amount
- tracking_number
- carrier
- estimated_delivery

### Products Table
- id (UUID)
- name
- category (Men's Clothing, Women's Clothing)
- subcategory (Shirts, Dresses, Jeans, etc.)
- price
- status (active/inactive/out_of_stock)

### Product Variants Table
- id (UUID)
- product_id
- size (S, M, L, XL, or numeric sizes)
- color
- stock_quantity
- price

## 🔄 Switching Between Databases

### Use Local PostgreSQL
```env
USE_SUPABASE=False
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=5432
LOCAL_DB_NAME=ecommerce_db
LOCAL_DB_USER=postgres
LOCAL_DB_PASSWORD=datalens
```

### Use Supabase
```env
USE_SUPABASE=True
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_key
SUPABASE_SERVICE_KEY=your_service_key
```

**No code changes needed!** The system automatically uses the correct database.

## ✅ Verification

### Check Database
```sql
-- Connect
psql -U postgres -d ecommerce_db

-- Check tables
\dt

-- Check users
SELECT email, name, loyalty_tier FROM users;

-- Check orders
SELECT order_number, status, total_amount FROM orders;

-- Check products
SELECT name, category, price FROM products;
```

### Test with Python
```python
from src.tools.database_tool import DatabaseTool

db = DatabaseTool()

# Test user lookup
user = db.get_user_by_email("john@example.com")
print(f"User: {user['name']}, Email: {user['email']}")

# Test order lookup
order = db.get_order_by_id("ORD-12345")
print(f"Order: {order['order_number']}, Status: {order['status']}")

# Test user orders
orders = db.get_user_orders(user['id'], limit=5)
print(f"User has {len(orders)} orders")
```

## 🎯 Testing with Evaluation Questions

The seed data is designed to support all evaluation questions:

**State/Memory Tests:**
- Users exist: john@example.com, sarah@example.com, etc.
- Orders exist: ORD-12345, ORD-67890, etc.

**Tool Calling Tests:**
- Order queries work: `get_order("ORD-12345")`
- User queries work: `get_user_by_email("john@example.com")`
- Status searches work: `search_orders_by_status("shipped")`

**Complex Queries:**
- Multi-step queries supported
- Order history available
- User verification ready

## 🔧 Troubleshooting

### Connection Failed

1. **Check PostgreSQL is running**:
   ```bash
   # Windows: Check Services
   services.msc
   # Look for "postgresql-x64-XX" service
   ```

2. **Verify credentials**:
   - User: `postgres`
   - Password: `datalens`
   - Port: `5432`

3. **Test connection manually**:
   ```bash
   psql -U postgres -h localhost -p 5432
   # Enter password: datalens
   ```

### Database Not Found

Run initialization again:
```bash
python database/init_database.py
```

### Import Errors

Install dependencies:
```bash
pip install psycopg2-binary
```

## 📋 Next Steps

1. ✅ Database initialized
2. ✅ Seed data loaded
3. ⏳ Add OpenAI API key to `.env`
4. ⏳ Build graph: `python -m src.main --build-graph`
5. ⏳ Test agent: `streamlit run streamlit_app.py`
6. ⏳ Run evaluation: `python run_evaluation.py`

---

**Database is ready!** All tables created, seed data loaded, and system configured for local PostgreSQL.

