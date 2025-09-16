#!/bin/bash
set -e 


if [ ! -d "./db_openai" ]; then
    echo "Database not found. Running ingestion script to create database"
    python database.py
else 
    echo "Database found. Skipping ingestion script"
fi


echo "Starting the FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 &

sleep 2

echo "Starting the Streamlit app..."
streamlit run streamlit.py --server.port 8501 --server.address 0.0.0.0
    