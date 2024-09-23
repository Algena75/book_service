#!/bin/sh

until  alembic upgrade head 
do
    echo "Waiting for db to be ready..."
    sleep 2
done

# cd web/
uvicorn web.main:app --reload --host 0.0.0.0 --port 8000