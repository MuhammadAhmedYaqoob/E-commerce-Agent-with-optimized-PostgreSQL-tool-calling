# Database Setup Guide

## Overview

This directory contains the database schema and initialization scripts for the e-commerce MVP system. The system supports both **Supabase** and **Local PostgreSQL**.

## Quick Start

### Option 1: Local PostgreSQL (Recommended for Testing)

1. **Ensure PostgreSQL is running** on your local machine

2. **Initialize the database**:
   ```bash
   python database/init_database.py
   ```

   This will:
   - Create the `ecommerce_db` database
   - Create all required tables
   - Insert seed data for testing

3. **Configure .env file**:
   ```env
   USE_SUPABASE=False
   LOCAL_DB_HOST=localhost
   LOCAL_DB_PORT=5432
   LOCAL_DB_NAME=ecommerce_db
   LOCAL_DB_USER=postgres
   LOCAL_DB_PASSWORD=datalens
   ```

### Option 2: Supabase (Cloud)

1. **Set up Supabase project** at https://supabase.com

2. **Run schema in Supabase SQL Editor**:
   - Copy contents of `database/schema.sql`
   - Run in Supabase SQL Editor
   - (Optional) Run `database/seed_data.sql` for test data

3. **Configure .env file**:
   ```env
   USE_SUPABASE=True
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   ```

## Database Schema

### Core Tables

1. **users** - Customer accounts
2. **addresses** - Shipping and billing addresses
3. **products** - Product catalog
4. **product_variants** - Size and color variants
5. **orders** - Order information
6. **order_items** - Items in each order
7. **payments** - Payment transactions
8. **returns** - Return requests
9. **return_items** - Items being returned
10. **graph_cache** - MiniRAG graph entity cache
11. **carts** - Shopping carts
12. **cart_items** - Items in cart
13. **reviews** - Product reviews

### Key Features

- **UUID primary keys** for all tables
- **Foreign key constraints** for data integrity
- **Indexes** for performance optimization
- **JSONB fields** for flexible data storage
- **Automatic timestamps** (created_at, updated_at)
- **Triggers** for updated_at maintenance

## Seed Data

The `seed_data.sql` file includes:

- **12 sample users** (matching evaluation_questions.json emails)
- **10 sample products** (men's and women's clothing)
- **18 product variants** (sizes and colors)
- **9 sample orders** (various statuses)
- **10 order items**
- **8 payment records**

This seed data supports testing with the 100 evaluation questions.

## Testing with Evaluation Questions

The seed data includes orders that match the evaluation questions:

- `ORD-12345` - Shipped order
- `ORD-67890` - Delivered order
- `ORD-11111` - Processing order
- `ORD-22222` - Pending order
- `ORD-33333` - Shipped order
- `ORD-44444` - Delivered order
- `ORD-55555` - Processing order
- `ORD-66666` - Shipped order
- `ORD-77777` - Delivered order

Users match the emails in evaluation questions:
- `john@example.com`
- `sarah@example.com`
- `mike@example.com`
- `lisa@example.com`
- `david@example.com`
- `emily@example.com`
- `james@example.com`
- `jane@example.com`
- `bob@example.com`
- `alice@example.com`
- `charlie@example.com`
- `test@example.com`

## Switching Between Supabase and Local PostgreSQL

Simply change the `USE_SUPABASE` flag in `.env`:

```env
# Use Local PostgreSQL
USE_SUPABASE=False

# Use Supabase
USE_SUPABASE=True
```

The system automatically uses the correct database based on this flag.

## Database Connection

The `DatabaseTool` class (`src/tools/database_tool.py`) handles:
- Automatic connection based on configuration
- Same interface for both databases
- Optimized queries for both backends
- Graceful fallback to mock mode if connection fails

## Troubleshooting

### Local PostgreSQL Connection Issues

1. **Check PostgreSQL is running**:
   ```bash
   # Windows
   services.msc  # Look for PostgreSQL service
   
   # Or check if port 5432 is listening
   ```

2. **Verify credentials**:
   - Default user: `postgres`
   - Password: `datalens` (as you specified)

3. **Check database exists**:
   ```sql
   \l  -- List databases in psql
   ```

4. **Reinitialize if needed**:
   ```bash
   python database/init_database.py
   ```

### Supabase Connection Issues

1. **Verify credentials** in `.env`
2. **Check Supabase project** is active
3. **Verify schema** is created in Supabase

## Schema Compatibility

The schema is designed to work with both:
- **Supabase** (PostgreSQL with additional features)
- **Local PostgreSQL** (standard PostgreSQL)

Both use the same SQL schema, ensuring compatibility.

## Next Steps

1. Run `python database/init_database.py` to set up local database
2. Configure `.env` with `USE_SUPABASE=False`
3. Test the system with evaluation questions
4. Switch to Supabase when ready for production

