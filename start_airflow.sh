#!/bin/bash
set -e

# Initialise la base Airflow si pas encore faite
airflow db init

# Crée ou met à jour l'utilisateur admin
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com || true

# Démarre Airflow en mode standalone
exec airflow standalone
