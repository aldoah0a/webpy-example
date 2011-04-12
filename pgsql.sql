DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS account_info;
DROP TABLE IF EXISTS sessions;

CREATE TABLE accounts (
  "id"       SERIAL PRIMARY KEY,
  "username" text NOT NULL,
  "password" text NOT NULL,
  UNIQUE (username)
);

CREATE TABLE account_info (
  "id"         SERIAL PRIMARY KEY,
  "username"   text NOT NULL,
  "key"        text NOT NULL,
  "value"      text
);

CREATE TABLE sessions (
  "session_id" CHARACTER(40) PRIMARY KEY,
  "atime" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "data" TEXT
);

INSERT INTO accounts VALUES ( DEFAULT, 'admin', '$5$rounds=36026$SWgKLja6xCHvUHXW$iYpPGY7mRl.ppt9Lg./8SDbggMuOfmKXKK.8nXL9KuD' );
INSERT INTO account_info VALUES ( DEFAULT, 'admin', 'role', 'administrator' );
INSERT INTO account_info VALUES ( DEFAULT, 'admin', 'last_login', CURRENT_TIMESTAMP );
INSERT INTO account_info VALUES ( DEFAULT, 'admin', 'last_ip', '127.0.0.1' );
INSERT INTO account_info VALUES ( DEFAULT, 'admin', 'consumer_key', 'rGgkUYhqjNEtwZdhnnLZoBkXkdKCPJmI' );
INSERT INTO account_info VALUES ( DEFAULT, 'admin', 'consumer_secret', 'OSdTYJAeQJLLOHlOdmatRvEdBcuxuKGD' );
