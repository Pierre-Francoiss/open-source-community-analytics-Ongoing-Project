-- =========================================================
-- init_db.sql
-- Database for Open Source Community Analytics
-- =========================================================

-- droping previous database if exists

DROP TABLE IF EXISTS pull_requests_clean CASCADE;
DROP TABLE IF EXISTS issues_clean CASCADE;
DROP TABLE IF EXISTS contributors_clean CASCADE;
DROP TABLE IF EXISTS projects_clean CASCADE;

DROP TABLE IF EXISTS pull_requests_raw CASCADE;
DROP TABLE IF EXISTS issues_raw CASCADE;
DROP TABLE IF EXISTS contributors_raw CASCADE;
DROP TABLE IF EXISTS projects_raw CASCADE;


-- Tables for Raw data

-- Table for projects
CREATE TABLE IF NOT EXISTS projects_raw (
    project_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for contributors
CREATE TABLE IF NOT EXISTS contributors_raw (
    contributor_id SERIAL PRIMARY KEY,
    login VARCHAR(100) NOT NULL,
    github_id BIGINT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for issues
CREATE TABLE IF NOT EXISTS issues_raw (
    issue_id SERIAL PRIMARY KEY,
    project_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT,
    state VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects_raw(project_id) ON DELETE CASCADE
);

-- Table for pull requests
CREATE TABLE IF NOT EXISTS pull_requests_raw (
    pr_id SERIAL PRIMARY KEY,
    project_id INT NOT NULL,
    contributor_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT,
    state VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects_raw(project_id) ON DELETE CASCADE,
    FOREIGN KEY (contributor_id) REFERENCES contributors_raw(contributor_id) ON DELETE CASCADE
);

-- Tables for clean data (after processing)

-- Table for cleaned projects
CREATE TABLE IF NOT EXISTS projects_clean (
    project_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    name_clean VARCHAR(255), -- normalized (e.g., lowercase, trimmed)
    activity_level VARCHAR(50), -- e.g., "active", "stale", "archived"
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    transformed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for cleaned contributors
CREATE TABLE IF NOT EXISTS contributors_clean (
    contributor_id SERIAL PRIMARY KEY,
    login VARCHAR(100) NOT NULL,
    github_id BIGINT UNIQUE NOT NULL,
    login_clean VARCHAR(100), -- normalized login (lowercase)
    activity_score NUMERIC(5,2), -- calculated engagement metric
    created_at TIMESTAMP,
    transformed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for cleaned issues
CREATE TABLE IF NOT EXISTS issues_clean (
    issue_id SERIAL PRIMARY KEY,
    project_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT,
    state VARCHAR(50) NOT NULL,
    title_clean VARCHAR(255),
    word_count INT, -- number of words in the issue body
    is_closed BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    transformed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects_clean(project_id) ON DELETE CASCADE
);

-- Table for cleaned pull requests
CREATE TABLE IF NOT EXISTS pull_requests_clean (
    pr_id SERIAL PRIMARY KEY,
    project_id INT NOT NULL,
    contributor_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT,
    state VARCHAR(50) NOT NULL,
    title_clean VARCHAR(255),
    is_merged BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    transformed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects_clean(project_id) ON DELETE CASCADE,
    FOREIGN KEY (contributor_id) REFERENCES contributors_clean(contributor_id) ON DELETE CASCADE
);