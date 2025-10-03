import psycopg2

try:
    conn = psycopg2.connect(
        dbname="community_analytics",
        user="community_user",
        password="Userpass",
        host="localhost",
        port=5432
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print("✅ Connexion réussie :", cur.fetchone())
    conn.close()
except Exception as e:
    print("❌ Erreur de connexion :", repr(e))
