import sqlite3

conn = sqlite3.connect('jobtrack.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM jobs")
total = cursor.fetchone()[0]
print(f"Total jobs: {total}")

cursor.execute("SELECT company, position FROM jobs LIMIT 5")
jobs = cursor.fetchall()
print("\nFirst 5 jobs:")
for job in jobs:
    print(f"  - {job[0]}: {job[1]}")

conn.close()
input("\nPress Enter to exit...")