# Utilisez une image de base Python
FROM python:3.9

# Installez FastAPI, Uvicorn et autres dépendances
RUN pip install fastapi uvicorn psycopg2-binary sqlalchemy

# Copiez votre fichier source
COPY ./main.py /main.py

# Commande pour exécuter l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
