import psycopg2

try:
    conn = psycopg2.connect(
        dbname="community_analytics",
        user="community_user",
        password="5342i",
        host="host.docker.internal",
        port=5432,
    )
    print("✅ Connected")
except Exception as e:
    print("❌ Erreur brute:", repr(e))
    print("❌ Erreur texte:", str(e).encode("utf-8", errors="replace"))
