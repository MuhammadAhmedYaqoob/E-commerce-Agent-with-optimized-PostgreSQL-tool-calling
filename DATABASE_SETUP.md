# Database Setup Instructions

## Quick Setup for Local PostgreSQL

### Step 1: Initialize Database

```bash
python database/init_database.py
```

This will:
- Create `ecommerce_db` database
- Create all tables
- Insert seed data

### Step 2: Configure .env

```env
USE_SUPABASE=False
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=5432
LOCAL_DB_NAME=ecommerce_db
LOCAL_DB_USER=postgres
LOCAL_DB_PASSWORD=datalens
```

### Step 3: Test Connection

The system will automatically connect when you run it. Check logs for:
```
[INFO] Connected to local PostgreSQL: ecommerce_db
```

## Database Schema

### Tables Created

1. **users** - 12 sample users
2. **products** - 10 products (men's/women's clothing)
3. **product_variants** - 18 variants (sizes/colors)
4. **orders** - 9 sample orders
5. **order_items** - 10 order items
6. **payments** - 8 payment records
7. **graph_cache** - For MiniRAG optimization
8. Plus: addresses, returns, carts, reviews

### Sample Data

- **Users**: Emails matching evaluation_questions.json
- **Orders**: ORD-12345, ORD-67890, ORD-11111, etc.
- **Products**: Men's and women's clothing items

## Switching to Supabase

1. Set `USE_SUPABASE=True` in `.env`
2. Add Supabase credentials
3. Run `schema.sql` in Supabase SQL Editor
4. (Optional) Run `seed_data.sql` for test data

## Verification

Test the connection:
```python
from src.tools.database_tool import DatabaseTool

db = DatabaseTool()
user = db.get_user_by_email("john@example.com")
print(user)  # Should return user data
```

## Support

- Schema: `database/schema.sql`
- Seed Data: `database/seed_data.sql`
- Initialization: `database/init_database.py`
- Tool: `src/tools/database_tool.py`

