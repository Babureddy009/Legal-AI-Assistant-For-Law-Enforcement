-- Create FIR tables
CREATE TABLE IF NOT EXISTS fir_complainants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    nationality VARCHAR(50),
    occupation VARCHAR(100),
    address TEXT NOT NULL,
    contact VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fir_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fir_number VARCHAR(50) UNIQUE,
    police_station VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    fir_date DATE NOT NULL,
    complainant_id INT NOT NULL,
    info_type ENUM('Oral', 'Written') NOT NULL,
    place_of_occurrence TEXT NOT NULL,
    date_time_of_occurrence DATETIME NOT NULL,
    accused_details TEXT,
    property_details TEXT,
    property_value DECIMAL(15,2),
    complaint TEXT NOT NULL,
    sections_acts TEXT,
    status ENUM('Draft', 'Submitted', 'Under Review', 'Approved', 'Rejected') DEFAULT 'Draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (complainant_id) REFERENCES fir_complainants(id)
);

-- Create indexes for better query performance
CREATE INDEX idx_fir_number ON fir_reports(fir_number);
CREATE INDEX idx_police_station ON fir_reports(police_station);
CREATE INDEX idx_district ON fir_reports(district);
CREATE INDEX idx_fir_date ON fir_reports(fir_date);
CREATE INDEX idx_status ON fir_reports(status);

-- Create a view for easy FIR report retrieval
CREATE OR REPLACE VIEW fir_report_details AS
SELECT 
    fr.id,
    fr.fir_number,
    fr.police_station,
    fr.district,
    fr.fir_date,
    fr.info_type,
    fr.place_of_occurrence,
    fr.date_time_of_occurrence,
    fr.accused_details,
    fr.property_details,
    fr.property_value,
    fr.complaint,
    fr.sections_acts,
    fr.status,
    fr.created_at,
    fr.updated_at,
    fc.name as complainant_name,
    fc.parent_name as complainant_parent_name,
    fc.age as complainant_age,
    fc.gender as complainant_gender,
    fc.nationality as complainant_nationality,
    fc.occupation as complainant_occupation,
    fc.address as complainant_address,
    fc.contact as complainant_contact
FROM fir_reports fr
JOIN fir_complainants fc ON fr.complainant_id = fc.id;

-- Create IPC Sections table
CREATE TABLE IF NOT EXISTS ipc_sections (
    id INT PRIMARY KEY AUTO_INCREMENT,
    section_number VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    punishment TEXT,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_section (section_number)
);

-- Create index for faster searches
CREATE INDEX idx_ipc_section_number ON ipc_sections(section_number);
CREATE INDEX idx_ipc_category ON ipc_sections(category);
CREATE INDEX idx_ipc_active ON ipc_sections(is_active);

-- Insert some sample IPC sections
INSERT INTO ipc_sections (section_number, title, description, punishment, category) VALUES
('302', 'Murder', 'Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.', 'Death or imprisonment for life and fine', 'Offences Affecting Life'),
('307', 'Attempt to Murder', 'Whoever does any act with such intention or knowledge, and under such circumstances that, if he by that act caused death, he would be guilty of murder, shall be punished with imprisonment of either description for a term which may extend to ten years, and shall also be liable to fine.', 'Imprisonment up to 10 years and fine', 'Offences Affecting Life'),
('376', 'Rape', 'Whoever commits rape shall be punished with rigorous imprisonment of either description for a term which shall not be less than ten years, but which may extend to imprisonment for life, and shall also be liable to fine.', 'Rigorous imprisonment for 10 years to life and fine', 'Sexual Offences'),
('420', 'Cheating and Dishonestly Inducing Delivery of Property', 'Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, or anything which is signed or sealed, and which is capable of being converted into a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.', 'Imprisonment up to 7 years and fine', 'Offences Against Property'),
('498A', 'Cruelty by Husband or Relatives of Husband', 'Whoever, being the husband or the relative of the husband of a woman, subjects such woman to cruelty shall be punished with imprisonment for a term which may extend to three years and shall also be liable to fine.', 'Imprisonment up to 3 years and fine', 'Offences Relating to Marriage'); 