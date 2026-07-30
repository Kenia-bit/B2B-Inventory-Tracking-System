CREATE TABLE farmers (
    farmer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(100),
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE harvest (
    harvest_id SERIAL PRIMARY KEY,
    farmer_id INT REFERENCES farmers(farmer_id) ON DELETE CASCADE,
    crop_type VARCHAR(100) NOT NULL,
    quantity_kg NUMERIC (10, 2) NOT NULL,
    harvest_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Available'
);

CREATE TABLE buyers (
    buyer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    location VARCHAR(255)
);
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    buyer_id INT REFERENCES buyers(buyer_id) ON DELETE CASCADE,
    harvest_id INT REFERENCES harvest(harvest_id) ON DELETE CASCADE,
    quantity_ordered NUMERIC (10, 2) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Pending'
);