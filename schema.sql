-- ── Users ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    user_id       SERIAL PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email    ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);


-- ── Identity Anchors ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS identity_anchors (
    anchor_id             SERIAL PRIMARY KEY,
    user_id               INTEGER REFERENCES users(user_id),
    user_pub_key          VARCHAR(255) NOT NULL,
    public_key_b64        TEXT,
    private_key_encrypted TEXT,
    trust_score           NUMERIC(5,2) DEFAULT 50.0,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anchors_user_id ON identity_anchors(user_id);


-- ── Platform Verifications ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS platform_verifications (
    verification_id    SERIAL PRIMARY KEY,
    anchor_id          INTEGER NOT NULL REFERENCES identity_anchors(anchor_id),
    platform_name      VARCHAR(50) NOT NULL,
    profile_url        VARCHAR(500) NOT NULL,
    verification_token VARCHAR(255),
    signature          TEXT,
    signed_at          TIMESTAMP,
    verified_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_verifications_anchor_id ON platform_verifications(anchor_id);


-- ── OAuth Verifications ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS oauth_verifications (
    id                 SERIAL PRIMARY KEY,
    user_id            INTEGER NOT NULL REFERENCES users(user_id),
    anchor_id          INTEGER REFERENCES identity_anchors(anchor_id),
    platform           VARCHAR(50) NOT NULL,
    platform_user_id   VARCHAR(255) NOT NULL,
    platform_username  VARCHAR(255),
    profile_url        VARCHAR(500),
    encrypted_token    TEXT NOT NULL,
    signature          TEXT,
    signed_at          TIMESTAMP,
    connected_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, platform_user_id)
);

CREATE INDEX IF NOT EXISTS idx_oauth_user_id  ON oauth_verifications(user_id);
CREATE INDEX IF NOT EXISTS idx_oauth_platform ON oauth_verifications(platform);


-- ── Consistency Checks ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS consistency_checks (
    check_id           SERIAL PRIMARY KEY,
    user_group         VARCHAR(255),
    platform_a         VARCHAR(50) NOT NULL,
    platform_b         VARCHAR(50) NOT NULL,
    consistency_score  NUMERIC(5,2),
    breakdown          JSONB,
    algorithm          VARCHAR(100),
    checked_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ── Reputation Events ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reputation_events (
    event_id    SERIAL PRIMARY KEY,
    anchor_id   INTEGER NOT NULL REFERENCES identity_anchors(anchor_id),
    event_type  VARCHAR(100) NOT NULL,
    platform    VARCHAR(50),
    time_stamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_anchor_id ON reputation_events(anchor_id);