-- Populate initial test data
-- Doctor user
INSERT INTO Doctor (id, email, password, name, date_of_birth, specialization) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'doctor@gmail.com', '$2b$12$go2KM9jrMHs0D8KhQI/It.gS/yM6QZTYLIFdvYs86OmNvouoqDbAO', 'Dr. Test Doctor', '1980-01-01', 'Neurology');

-- Patient user
INSERT INTO Patient (id, email, password, name, date_of_birth, education_level, occupation, status) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'patient@gmail.com', '$2b$12$go2KM9jrMHs0D8KhQI/It.gS/yM6QZTYLIFdvYs86OmNvouoqDbAO', 'Test Patient', '1990-01-01', 'Bachelor Degree', 'Software Engineer', 'active');

-- Link patient to doctor
INSERT INTO PatientDoctor (patient_id, doctor_id) VALUES
('550e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000');