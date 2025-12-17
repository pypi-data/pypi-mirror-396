# Multi-Source Join Example

This example demonstrates joining data from three different sources:

1. **JSONL file** (`products.jsonl`) - Product data
2. **CSV file** (`categories.csv`) - Category data
3. **Free API** (JSONPlaceholder) - User and post data

## What This Example Shows

- ✅ Reading from JSONL files
- ✅ Reading from CSV files
- ✅ Fetching data from free APIs (no API key needed)
- ✅ Joining all three sources together
- ✅ Real-world cross-system data integration

## Free API Used

**JSONPlaceholder** - https://jsonplaceholder.typicode.com

A free fake REST API for testing and prototyping. No API key required!

Endpoints used:

- `/users` - User data (name, email, city, company)
- `/posts` - Post data (title, body, linked to users)

## Setup

1. **Install dependencies:**

   ```bash
   pip install requests
   ```

2. **Run the example:**
   ```bash
   python example_multi_source_join.py
   ```

The script will:

- Automatically create sample `products.jsonl` and `categories.csv` files
- Fetch data from JSONPlaceholder API
- Join all sources together
- Display results

## Example Queries

### Query 1: Join JSONL + CSV

```sql
SELECT
    p.product_id,
    p.name as product_name,
    p.price,
    c.category_name
FROM products p
JOIN categories c ON p.category_id = c.category_id
```

### Query 2: Join JSONL + API

```sql
SELECT
    p.name as product_name,
    u.user_name,
    u.user_email
FROM products p
JOIN users u ON p.user_id = u.user_id
```

### Query 3: Join ALL THREE sources

```sql
SELECT
    p.name as product_name,
    c.category_name,
    u.user_name,
    u.user_email
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN users u ON p.user_id = u.user_id
```

## Data Structure

### products.jsonl (JSONL file)

```json
{"product_id": 1, "name": "Laptop", "price": 999.99, "user_id": 1, "category_id": 1}
{"product_id": 2, "name": "Mouse", "price": 29.99, "user_id": 2, "category_id": 2}
```

### categories.csv (CSV file)

```csv
category_id,category_name,description
1,Electronics,Electronic devices
2,Accessories,Computer accessories
```

### users (API - JSONPlaceholder)

```json
{
  "id": 1,
  "name": "Leanne Graham",
  "email": "Sincere@april.biz",
  "address": { "city": "Gwenborough" },
  "company": { "name": "Romaguera-Crona" }
}
```

## Output Example

```
Product: Laptop          | Price: $ 999.99 | Category: Electronics
Product: Monitor         | Price: $ 299.99 | Category: Electronics
Product: Headphones      | Price: $ 149.99 | Category: Audio
Product: Keyboard        | Price: $  79.99 | Category: Accessories
```

## Customization

You can easily modify this example to:

- Use your own JSONL/CSV files
- Use different APIs (just change the API source function)
- Add more data sources
- Join with databases (see other examples)

## Other Free APIs You Can Use

- **REST Countries**: https://restcountries.com (country data)
- **Random User**: https://randomuser.me/api (random user data)
- **JSONPlaceholder**: https://jsonplaceholder.typicode.com (users, posts, comments)
- **OpenWeatherMap**: https://openweathermap.org (weather - needs free API key)
- **GitHub API**: https://api.github.com (public repos - no auth needed for public data)

## Notes

- The example creates sample data files automatically
- API calls are made on-the-fly (no caching)
- All joins happen in memory (streaming)
- No database required!
