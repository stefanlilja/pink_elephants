-- Database: elephant

-- DROP DATABASE IF EXISTS elephant;

CREATE DATABASE elephant
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Swedish_Sweden.1252'
    LC_CTYPE = 'Swedish_Sweden.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-- Dimension table, time
CREATE TABLE time(
	time_stamp TIMESTAMP PRIMARY KEY,
	year INT,
	month INT,
	day INT,
	hour INT,
	minute INT
);

-- Fact table
CREATE TABLE location_ping(
	loc_id SERIAL PRIMARY KEY,
	latitude NUMERIC(7, 5),
	longitude NUMERIC(7, 5),
	time_stamp TIMESTAMP REFERENCES time(time_stamp),
	temperature NUMERIC(3, 1),
	tag_id TEXT
);