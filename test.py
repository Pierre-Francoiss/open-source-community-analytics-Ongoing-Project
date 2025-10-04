import psycopg2

# Paramètres de connexion
POSTGRES_USER = "community_user"
POSTGRES_PASSWORD = "Userpass"
POSTGRES_DB = "community_analytics"
POSTGRES_HOST = "localhost"   # ⚠️ pas "postgres"
POSTGRES_PORT = 5432

try:
    # Connexion
    print("🔌 Tentative de connexion à PostgreSQL...")
    conn = psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )
    print("✅ Connexion réussie !")

    # Test simple : récupérer la version du serveur
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print("🟢 Version PostgreSQL :", version[0])

    # Fermer proprement
    cur.close()
    conn.close()

except Exception as e:
    print("❌ Erreur capturée :", e)
    print("❌ Erreur brute (repr):", repr(e))
