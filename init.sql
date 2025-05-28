-- Create scroll_logs table
CREATE TABLE IF NOT EXISTS scroll_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action TEXT NOT NULL,
    user_id TEXT NOT NULL,
    data JSONB,
    metadata JSONB
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_scroll_logs_timestamp ON scroll_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_scroll_logs_user_id ON scroll_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_scroll_logs_action ON scroll_logs(action);

-- Create scroll_analytics table
CREATE TABLE IF NOT EXISTS scroll_analytics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC,
    dimensions JSONB,
    metadata JSONB
);

-- Create indexes for analytics
CREATE INDEX IF NOT EXISTS idx_scroll_analytics_timestamp ON scroll_analytics(timestamp);
CREATE INDEX IF NOT EXISTS idx_scroll_analytics_metric_name ON scroll_analytics(metric_name);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    metadata JSONB
);

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    metadata JSONB
);

-- Create indexes for sessions
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token); 