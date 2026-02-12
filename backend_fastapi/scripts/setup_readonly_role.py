"""Set up agent_readonly role with password and GRANT permissions.

Usage:
  python scripts/setup_readonly_role.py                  (use postgres default)
  python scripts/setup_readonly_role.py <postgres_password>
"""
import sys
import psycopg2

pg_password = sys.argv[1] if len(sys.argv) > 1 else "root"

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password=pg_password,
    dbname="photopolymer_formulation_db",
)
conn.autocommit = True
cur = conn.cursor()

# Check if role exists
cur.execute("SELECT 1 FROM pg_roles WHERE rolname = 'agent_readonly'")
exists = cur.fetchone()

if not exists:
    cur.execute("CREATE ROLE agent_readonly LOGIN PASSWORD 'agent_readonly_2026'")
    print("Role created with password")
else:
    cur.execute("ALTER ROLE agent_readonly WITH LOGIN PASSWORD 'agent_readonly_2026'")
    print("Role password updated")

# Grant permissions
cur.execute("GRANT CONNECT ON DATABASE photopolymer_formulation_db TO agent_readonly")
cur.execute("GRANT USAGE ON SCHEMA public TO agent_readonly")

tables = [
    "tbl_ProjectInfo",
    "tbl_FormulaComposition",
    "tbl_RawMaterials",
    "tbl_InorganicFillers",
    "tbl_TestResults_Ink",
    "tbl_TestResults_Coating",
    "tbl_TestResults_3DPrint",
    "tbl_TestResults_Composite",
]
for t in tables:
    try:
        cur.execute(f'GRANT SELECT ON TABLE "{t}" TO agent_readonly')
        print(f"  GRANT SELECT ON {t} - OK")
    except Exception as e:
        print(f"  GRANT SELECT ON {t} - SKIP ({e})")
        conn.rollback()
        conn.autocommit = True

cur.close()
conn.close()
print("Done!")
