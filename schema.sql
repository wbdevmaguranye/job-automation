CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    url VARCHAR(255),
    description TEXT,
    date_posted DATE,
    location VARCHAR(255),
    benefits TEXT,
    schedule VARCHAR(255),
    application_questions TEXT
);

-- Insert sample data for testing
INSERT INTO jobs (title, company, url, description, date_posted, location, benefits, schedule, application_questions)
VALUES
('Senior DevOps Engineer', 'CommIT', 'https://example.com', 
 'The company develops and operates a cutting-edge, cloud-based core banking platform tailored for the financial sector. Expertise in Jenkins, Kubernetes, AWS, and Terraform required.', 
 NOW(), 'London', 
 'Flexible working hours, Healthcare benefits', 'Full-time', 'Are you comfortable working remotely?'),
('Frontend Developer', 'TechCorp', 'https://example2.com', 
 'Join our team to build modern web applications using Vue.js and Tailwind CSS. Experience with REST APIs is required.', 
 NOW(), 'Manchester', 
 'Competitive salary, Stock options', 'Part-time', 'Do you have experience with Vue.js?');
