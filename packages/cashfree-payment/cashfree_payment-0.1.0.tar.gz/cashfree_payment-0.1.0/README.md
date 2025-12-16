# Cashfree Payment

A Python library for Cashfree payment integration with access key management.

## Installation

```bash
pip install cashfree-payment
```

## Requirements

- Python 3.8+
- PostgreSQL database with Neon
- Environment variable: `NEON_DATABASE_URL`

## Quick Start

```python
from cashfree_payment import (
    create_owner,
    owner_login,
    generate_access_key,
    pay,
    list_keys
)

# Create an owner account
owner_id = create_owner('username', 'password')

# Login to get owner_id
owner_id = owner_login('username', 'password')

# Generate an access key (valid for 30 days)
access_key = generate_access_key(owner_id, valid_days=30)

# Make a payment
session_id = pay('your_upi_id@bank', access_key)

# List all your access keys
list_keys(owner_id)
```

## Features

### Owner Management
- `create_owner(username, password)` - Create a new owner account
- `owner_login(username, password)` - Login and get owner ID

### Access Key Management
- `generate_access_key(owner_id, valid_days=30, valid_hours=0)` - Generate a new access key
- `generate_access_key_custom(owner_id, valid_until_str)` - Generate key with custom expiry
- `list_keys(owner_id)` - List all access keys for an owner
- `ban_key(owner_id, access_key)` - Ban an access key
- `unban_key(owner_id, access_key)` - Unban an access key
- `delete_key(owner_id, access_key)` - Delete an access key
- `update_key_expiry(owner_id, access_key, new_valid_until_str)` - Update key expiry

### Payment
- `pay(upi_id, access_key)` - Make a payment using UPI ID

## Database Setup

Create the required tables in your PostgreSQL database:

```sql
CREATE TABLE owners (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE access_keys (
    id SERIAL PRIMARY KEY,
    key_value VARCHAR(255) UNIQUE NOT NULL,
    owner_id INTEGER REFERENCES owners(id),
    valid_until TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(255),
    payment_session_id VARCHAR(255),
    amount VARCHAR(50),
    upi_id VARCHAR(255),
    user_ip VARCHAR(50),
    request_count INTEGER DEFAULT 0
);

CREATE TABLE cookies (
    id SERIAL PRIMARY KEY,
    cookie TEXT NOT NULL
);
```

## Environment Variables

Set the following environment variable:

```bash
export NEON_DATABASE_URL="postgresql://user:password@host/database"
```

## License

MIT License
