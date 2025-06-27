-- Create the database
CREATE DATABASE IF NOT EXISTS legal_ai;
USE legal_ai;

-- IPC Sections table
CREATE TABLE IF NOT EXISTS ipc_sections (
    id INT PRIMARY KEY AUTO_INCREMENT,
    section_number VARCHAR(10) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    punishment TEXT NOT NULL,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Crimes table
CREATE TABLE IF NOT EXISTS crimes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity ENUM('minor', 'major', 'heinous') NOT NULL,
    category ENUM('violent', 'property', 'financial', 'cyber', 'sexual', 'drug', 'other') NOT NULL,
    bailable BOOLEAN NOT NULL,
    cognizable BOOLEAN NOT NULL,
    compoundable BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Crime-IPC Section mapping
CREATE TABLE IF NOT EXISTS crime_ipc_mapping (
    id INT PRIMARY KEY AUTO_INCREMENT,
    crime_id INT NOT NULL,
    ipc_section_id INT NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (crime_id) REFERENCES crimes(id),
    FOREIGN KEY (ipc_section_id) REFERENCES ipc_sections(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User queries and responses (for improving the model)
CREATE TABLE IF NOT EXISTS user_interactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_query TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_section_number ON ipc_sections(section_number);
CREATE INDEX idx_ipc_category ON ipc_sections(category);
CREATE INDEX idx_ipc_active ON ipc_sections(is_active);
CREATE INDEX idx_crime_name ON crimes(name);
CREATE INDEX idx_crime_category ON crimes(category);
CREATE INDEX idx_crime_severity ON crimes(severity);
CREATE INDEX idx_user_query ON user_interactions(user_query(100)); 