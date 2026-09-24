CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS customers (
 customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 full_name VARCHAR(200) NOT NULL,
 email VARCHAR(255),
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS accounts (
 account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 customer_id UUID NOT NULL REFERENCES customers(customer_id),
 account_type VARCHAR(30) NOT NULL,
 balance NUMERIC(20,2) NOT NULL DEFAULT 0,
 status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
);
CREATE TABLE IF NOT EXISTS merchants (
 merchant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 merchant_name VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS transactions (
 transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 from_account_id UUID NOT NULL REFERENCES accounts(account_id),
 to_account_id UUID REFERENCES accounts(account_id),
 merchant_id UUID REFERENCES merchants(merchant_id),
 transaction_type VARCHAR(30) NOT NULL,
 amount NUMERIC(20,2) NOT NULL,
 status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
 failure_reason VARCHAR(100),
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
