-- =========================================================
-- init_db.sql
-- Database for Open Source Community Analytics
-- =========================================================

-- Table for GitHub projects
CREATE TABLE IF NOT EXISTS projects (
    project_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for contributors
CREATE TABLE IF NOT EXISTS contributors (
    contributor_id SERIAL PRIMARY KEY,
    login VARCHAR(100) NOT NULL,
    github_id BIGINT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for issues
CREATE TABLE IF NOT EXISTS issues (
    issue_id SERIAL PRIMARY KEY,
    project_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT,
    state VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

-- Table for pull requests
CREATE TABLE IF NOT EXISTS pull_requests (
    pr_id SERIAL PRIMARY KEY,
    project_id INT NOT NULL,
    contributor_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT,
    state VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    FOREIGN KEY (contributor_id) REFERENCES contributors(contributor_id) ON DELETE CASCADE
);