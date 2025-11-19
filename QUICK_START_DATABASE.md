# Quick Start - Database Setup

## 🚀 Fast Setup (3 Steps)

### Step 1: Initialize Database

```bash
python database/init_database.py
```

This creates:
- Database: `ecommerce_db`
- All tables (13 tables)
- Seed data (12 users, 10 products, 9 orders)

### Step 2: Configure .env

Create `.env` file with:

```env
USE_SUPABASE=False
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=5432
LOCAL_DB_NAME=ecommerce_db
LOCAL_DB_USER=postgres
LOCAL_DB_PASSWORD=datalens

OPENAI_API_KEY=your_key_here
```

### Step 3: Test

```bash
python -c "from src.tools.database_tool import DatabaseTool; db = DatabaseTool(); print(db.get_user_by_email('john@example.com'))"
```

Should return user data!

## 📊 What Gets Created

### Tables
- users (12 sample users)
- products (10 clothing items)
- product_variants (18 size/color combinations)
- orders (9 sample orders)
- order_items (10 items)
- payments (8 transactions)
- graph_cache (for MiniRAG)
- Plus: addresses, returns, carts, reviews

### Sample Data Matches Evaluation Questions

**Users** (emails from evaluation_questions.json):
- john@example.com
- sarah@example.com
- mike@example.com
- lisa@example.com
- david@example.com
- emily@example.com
- james@example.com
- jane@example.com
- bob@example.com
- alice@example.com
- charlie@example.com
- test@example.com

**Orders** (order numbers from evaluation questions):
- ORD-12345
- ORD-67890
- ORD-11111
- ORD-22222
- ORD-33333
- ORD-44444
- ORD-55555
- ORD-66666
- ORD-77777

## ✅ Verification

Check database:
```sql
-- Connect to PostgreSQL
psql -U postgres -d ecommerce_db

-- Check tables
\dt

-- Check users
SELECT email, name FROM users LIMIT 5;

-- Check orders
SELECT order_number, status FROM orders LIMIT 5;
```

## 🔄 Switch to Supabase Later

When ready:
1. Set `USE_SUPABASE=True` in `.env`
2. Add Supabase credentials
3. Run `schema.sql` in Supabase SQL Editor
4. System automatically switches!

## 🎯 Ready for Testing

Once database is set up:
1. Add OpenAI API key to `.env`
2. Build graph: `python -m src.main --build-graph`
3. Test agent: `streamlit run streamlit_app.py`
4. Run evaluation: `python run_evaluation.py`

---

**That's it!** Your database is ready for testing the agent with evaluation questions.

