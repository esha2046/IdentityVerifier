-- database_schema.sql
-- PostgreSQL Database Schema for Cross-Platform Digital Identity Verifier

-- Drop existing tables if they exist
DROP TABLE IF EXISTS reputation_events CASCADE;
DROP TABLE IF EXISTS consistency_checks CASCADE;
DROP TABLE IF EXISTS platform_verifications CASCADE;
DROP TABLE IF EXISTS identity_anchors CASCADE;

-- Create identity_anchors table
CREATE TABLE identity_anchors (
    anchor_id SERIAL PRIMARY KEY,
    user_pub_key VARCHAR(500) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trust_score DECIMAL(5,2) DEFAULT 50.00 CHECK (trust_score >= 0 AND trust_score <= 100)
);

-- Create platform_verifications table
CREATE TABLE platform_verifications (
    verification_id SERIAL PRIMARY KEY,
    anchor_id INTEGER NOT NULL,
    platform_name VARCHAR(100) NOT NULL,
    profile_url VARCHAR(500),
    verification_token VARCHAR(500) NOT NULL,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (anchor_id) REFERENCES identity_anchors(anchor_id) ON DELETE CASCADE,
    UNIQUE(anchor_id, platform_name)
);

-- Create consistency_checks table
CREATE TABLE consistency_checks (
    check_id SERIAL PRIMARY KEY,
    identity_anchor VARCHAR(100),
    platform_a VARCHAR(100) NOT NULL,
    platform_b VARCHAR(100) NOT NULL,
    consistency_score DECIMAL(5,2) CHECK (consistency_score >= 0 AND consistency_score <= 100),
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create reputation_events table
CREATE TABLE reputation_events (
    event_id SERIAL PRIMARY KEY,
    anchor_id INTEGER NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    platform VARCHAR(100),
    time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score_impact DECIMAL(5,2) DEFAULT 0.00,
    FOREIGN KEY (anchor_id) REFERENCES identity_anchors(anchor_id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_platform_verifications_anchor ON platform_verifications(anchor_id);
CREATE INDEX idx_reputation_events_anchor ON reputation_events(anchor_id);
CREATE INDEX idx_reputation_events_timestamp ON reputation_events(time_stamp);
CREATE INDEX idx_consistency_checks_platforms ON consistency_checks(platform_a, platform_b);

-- Insert sample data
INSERT INTO identity_anchors (user_pub_key, trust_score) VALUES
('MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1x2y...', 75.50),
('MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8z9k...', 82.30),
('MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5m3p...', 68.00);

INSERT INTO platform_verifications (anchor_id, platform_name, profile_url, verification_token) VALUES
(1, 'Instagram', 'https://instagram.com/user1', 'tok_inst_abc123xyz'),
(1, 'LinkedIn', 'https://linkedin.com/in/user1', 'tok_link_def456uvw'),
(1, 'X', 'https://x.com/user1', 'tok_x_ghi789rst'),
(2, 'Instagram', 'https://instagram.com/user2', 'tok_inst_jkl012mno'),
(2, 'LinkedIn', 'https://linkedin.com/in/user2', 'tok_link_pqr345stu');

INSERT INTO reputation_events (anchor_id, event_type, platform, score_impact) VALUES
(1, 'successful_verification', 'Instagram', 5.00),
(1, 'successful_verification', 'LinkedIn', 5.00),
(1, 'suspicious_activity', 'X', -3.00),
(2, 'successful_verification', 'Instagram', 5.00),
(2, 'successful_verification', 'LinkedIn', 5.00);

INSERT INTO consistency_checks (identity_anchor, platform_a, platform_b, consistency_score) VALUES
('group_user1', 'Instagram', 'LinkedIn', 88.50),
('group_user1', 'Instagram', 'X', 75.20),
('group_user1', 'LinkedIn', 'X', 79.30),
('group_user2', 'Instagram', 'LinkedIn', 92.10);