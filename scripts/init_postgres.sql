-- Initialize PostgreSQL database

-- Parts table
CREATE TABLE IF NOT EXISTS parts (
    id SERIAL PRIMARY KEY,
    part_number VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    oem BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    vin VARCHAR(17) UNIQUE,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    trim VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Specifications table
CREATE TABLE IF NOT EXISTS specifications (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(id),
    spec_type VARCHAR(50) NOT NULL,
    spec_key VARCHAR(100) NOT NULL,
    spec_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Part compatibility table
CREATE TABLE IF NOT EXISTS part_compatibility (
    id SERIAL PRIMARY KEY,
    part_id INTEGER REFERENCES parts(id),
    vehicle_id INTEGER REFERENCES vehicles(id),
    compatible BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Paint codes table
CREATE TABLE IF NOT EXISTS paint_codes (
    id SERIAL PRIMARY KEY,
    manufacturer VARCHAR(50) NOT NULL,
    paint_code VARCHAR(50) NOT NULL,
    color_name VARCHAR(100) NOT NULL,
    year_start INTEGER,
    year_end INTEGER,
    formula TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fault codes table
CREATE TABLE IF NOT EXISTS fault_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    system VARCHAR(50),
    description TEXT NOT NULL,
    severity VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_parts_category ON parts(category);
CREATE INDEX IF NOT EXISTS idx_vehicles_make_model_year ON vehicles(make, model, year);
CREATE INDEX IF NOT EXISTS idx_paint_codes_manufacturer ON paint_codes(manufacturer);
CREATE INDEX IF NOT EXISTS idx_fault_codes_system ON fault_codes(system);

-- Sample data (optional)
-- INSERT INTO parts (part_number, name, description, category, oem) VALUES
-- ('BRK001', 'Front Brake Pad Set', 'Ceramic brake pads', 'Brakes', false);
