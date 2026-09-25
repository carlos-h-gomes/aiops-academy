-- Future D1 schema. Apply only through a reviewed Wrangler migration after deployment approval.
CREATE TABLE IF NOT EXISTS accounts (
  user_id TEXT PRIMARY KEY,
  handle TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  disabled_at TEXT
);

CREATE TABLE IF NOT EXISTS credential_verifiers (
  user_id TEXT PRIMARY KEY REFERENCES accounts(user_id),
  verifier TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recovery_codes (
  user_id TEXT NOT NULL REFERENCES accounts(user_id),
  code_hash TEXT NOT NULL,
  created_at TEXT NOT NULL,
  used_at TEXT,
  PRIMARY KEY (user_id, code_hash)
);

CREATE TABLE IF NOT EXISTS sessions (
  session_hash TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES accounts(user_id),
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  revoked_at TEXT
);

CREATE TABLE IF NOT EXISTS progress_snapshots (
  user_id TEXT PRIMARY KEY REFERENCES accounts(user_id),
  revision INTEGER NOT NULL DEFAULT 0,
  state_json TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS progress_operations (
  user_id TEXT NOT NULL REFERENCES accounts(user_id),
  operation_id TEXT NOT NULL,
  base_revision INTEGER NOT NULL,
  type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY (user_id, operation_id)
);

CREATE TABLE IF NOT EXISTS login_throttles (
  handle TEXT PRIMARY KEY,
  failures INTEGER NOT NULL DEFAULT 0,
  window_started_at TEXT NOT NULL,
  blocked_until TEXT
);

CREATE INDEX IF NOT EXISTS sessions_by_user_expiry ON sessions(user_id, expires_at);
CREATE INDEX IF NOT EXISTS recovery_codes_by_user ON recovery_codes(user_id, used_at);
CREATE INDEX IF NOT EXISTS progress_operations_by_user ON progress_operations(user_id, created_at);
