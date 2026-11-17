-- Pantrio / PantryPilot MySQL 8.0 Initial Database Schema
-- Baseline: docs/api-contract.md v1.1.0

CREATE DATABASE IF NOT EXISTS pantrio
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE pantrio;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('CUSTOMER', 'SHOPKEEPER', 'ADMIN') NOT NULL DEFAULT 'CUSTOMER',
    status ENUM('ACTIVE', 'SUSPENDED') NOT NULL DEFAULT 'ACTIVE',
    activity_metric VARCHAR(100) NOT NULL DEFAULT '0 orders placed',
    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Refresh Tokens Table
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_refresh_tokens_hash (token_hash),
    INDEX idx_refresh_tokens_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Customer Delivery Locations Table
CREATE TABLE IF NOT EXISTS customer_locations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL,
    lat DOUBLE NOT NULL DEFAULT 0.0,
    lng DOUBLE NOT NULL DEFAULT 0.0,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Pantry Items Table (OCC enabled)
CREATE TABLE IF NOT EXISTS pantry_items (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    quantity DOUBLE NOT NULL DEFAULT 1.0,
    unit VARCHAR(20) NOT NULL DEFAULT 'pcs',
    expiry_date VARCHAR(50) NOT NULL DEFAULT 'Expires in 7 days',
    min_threshold DOUBLE NOT NULL DEFAULT 1.0,
    notes TEXT,
    status ENUM('HEALTHY', 'LOW_STOCK', 'EXPIRING', 'EXPIRED') NOT NULL DEFAULT 'HEALTHY',
    version INT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_pantry_user (user_id),
    INDEX idx_pantry_category (category),
    INDEX idx_pantry_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Shopping Items Table (OCC enabled)
CREATE TABLE IF NOT EXISTS shopping_items (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    subtext VARCHAR(50) NOT NULL DEFAULT '',
    price DOUBLE NOT NULL DEFAULT 0.0,
    is_checked BOOLEAN NOT NULL DEFAULT FALSE,
    category VARCHAR(50) NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_shopping_user (user_id),
    INDEX idx_shopping_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Recipes Table
CREATE TABLE IF NOT EXISTS recipes (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    duration VARCHAR(30) NOT NULL,
    calories VARCHAR(30) NOT NULL,
    difficulty VARCHAR(30) NOT NULL,
    match_percentage INT NOT NULL DEFAULT 100,
    tags JSON NOT NULL,
    ingredients JSON NOT NULL,
    instructions JSON NOT NULL,
    image_url VARCHAR(255) NOT NULL DEFAULT '',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Stores Table (OCC enabled, No hard deletion)
CREATE TABLE IF NOT EXISTS stores (
    id VARCHAR(36) PRIMARY KEY,
    owner_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    owner_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    address VARCHAR(255) NOT NULL,
    lat DOUBLE NOT NULL DEFAULT 0.0,
    lng DOUBLE NOT NULL DEFAULT 0.0,
    delivery_time VARCHAR(30) NOT NULL DEFAULT '25-35 mins',
    rating VARCHAR(10) NOT NULL DEFAULT '4.8',
    orders_fulfilled INT NOT NULL DEFAULT 0,
    delivery_fee DOUBLE NOT NULL DEFAULT 25.0,
    delivery_radius VARCHAR(30) NOT NULL DEFAULT '5 km',
    operating_hours VARCHAR(50) NOT NULL DEFAULT '7:00 AM - 10:00 PM',
    is_open BOOLEAN NOT NULL DEFAULT TRUE,
    status ENUM('PENDING_APPROVAL', 'APPROVED', 'SUSPENDED') NOT NULL DEFAULT 'APPROVED',
    version INT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_stores_owner (owner_id),
    INDEX idx_stores_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Store Inventory Table (OCC enabled)
CREATE TABLE IF NOT EXISTS store_inventory (
    id VARCHAR(36) PRIMARY KEY,
    store_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    stock_qty DOUBLE NOT NULL DEFAULT 0.0,
    unit VARCHAR(20) NOT NULL DEFAULT 'kg',
    price DOUBLE NOT NULL DEFAULT 0.0,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    min_threshold DOUBLE NOT NULL DEFAULT 2.0,
    version INT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    INDEX idx_inventory_store (store_id),
    INDEX idx_inventory_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Store Orders Table (OCC enabled)
CREATE TABLE IF NOT EXISTS store_orders (
    id VARCHAR(36) PRIMARY KEY,
    store_id VARCHAR(36) NOT NULL,
    customer_id VARCHAR(36) NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(30) NOT NULL DEFAULT '',
    customer_address VARCHAR(255) NOT NULL,
    total DOUBLE NOT NULL DEFAULT 0.0,
    status ENUM('PENDING', 'PREPARING', 'READY_FOR_PICKUP', 'OUT_FOR_DELIVERY', 'DELIVERED', 'CANCELLED') NOT NULL DEFAULT 'PENDING',
    placed_at VARCHAR(50) NOT NULL,
    version INT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_orders_store (store_id),
    INDEX idx_orders_customer (customer_id),
    INDEX idx_orders_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Store Order Items Table
CREATE TABLE IF NOT EXISTS store_order_items (
    id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    quantity DOUBLE NOT NULL,
    unit VARCHAR(20) NOT NULL,
    price DOUBLE NOT NULL,
    FOREIGN KEY (order_id) REFERENCES store_orders(id) ON DELETE CASCADE,
    INDEX idx_order_items_order (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
