CREATE DATABASE stock;
CREATE USER stockuser WITH PASSWORD 'stock';
GRANT ALL PRIVILEGES ON DATABASE stock TO stockuser;