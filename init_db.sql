-- Initialize PostgreSQL database with pgvector extension
-- This script runs when the container starts for the first time

-- Create the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the whatsapp_bot database if it doesn't exist
-- Note: This might already be created by POSTGRES_DB env var
SELECT 'CREATE DATABASE whatsapp_bot'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'whatsapp_bot')\gexec

-- Connect to whatsapp_bot database and enable vector extension there too
\c whatsapp_bot
CREATE EXTENSION IF NOT EXISTS vector;