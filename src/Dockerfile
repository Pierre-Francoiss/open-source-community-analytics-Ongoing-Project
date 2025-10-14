# Image Python légère
FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le script ETL, l'app streamlit et le fichier requirements
COPY app_streamlit.py /app/
COPY etl_github.py /app/
COPY requirements.txt /app/

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Commande par défaut
CMD ["python", "etl_github.py"]
