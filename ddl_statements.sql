-- Statements used to initialize the database.

-- First, drop the tables if they exist:
DROP TABLE IF EXISTS qr_change_history;
DROP TABLE IF EXISTS qr_access_history;
DROP TABLE IF EXISTS qr_codes;
DROP TABLE IF EXISTS users;

-- Create the tables:
CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	username VARCHAR(16) UNIQUE NOT NULL,
	password CHAR(64) NOT NULL,
	email VARCHAR(32) UNIQUE NOT NULL,
	is_admin BOOLEAN NOT NULL,
	is_premium BOOLEAN NOT NULL,
	qr_count INT NOT NULL,
	qr_changes INT NOT NULL
);


CREATE TABLE qr_codes (
	id SERIAL PRIMARY KEY,
	user_id INT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
	outgoing_link VARCHAR(256) NOT NULL
);

CREATE TABLE qr_change_history (
	qr_id INT NOT NULL,
	FOREIGN KEY (qr_id) REFERENCES qr_codes (id) ON DELETE CASCADE,
	change_time TIMESTAMP NOT NULL,
	from_link VARCHAR(256) NOT NULL,
	to_link VARCHAR(256) NOT NULL
);

CREATE TABLE qr_access_history (
	qr_id INT NOT NULL,
	FOREIGN KEY (qr_id) REFERENCES qr_codes (id) ON DELETE CASCADE,
	access_time TIMESTAMP NOT NULL,
	ip VARCHAR(46),
	country VARCHAR(256),
	city VARCHAR(256),
	agent VARCHAR(256),
	latitude REAL,
	longitude REAL
);