import sqlite3

# Connect to your database
conn = sqlite3.connect('jobtrack.db')
cursor = conn.cursor()

# 1. Count total jobs
cursor.execute("SELECT COUNT(*) FROM jobs")
total = cursor.fetchone()[0]
print(f"Total jobs: {total}")

# 2. Find all wishlist jobs
cursor.execute("SELECT company, position FROM jobs WHERE status = 'wishlist'")
wishlist_jobs = cursor.fetchall()
print(f"\nWishlist jobs: {len(wishlist_jobs)}")
for job in wishlist_jobs:
    print(f"  - {job[0]}: {job[1]}")

# 3. Find high-paying jobs (over $150k)
cursor.execute("SELECT company, position, salary_min FROM jobs WHERE salary_min > 150000")
high_paying = cursor.fetchall()
print(f"\nHigh paying jobs (>$150k): {len(high_paying)}")
for job in high_paying:
    print(f"  - {job[0]}: {job[1]} (${job[2]:,})")

# 4. Count jobs by status
cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
by_status = cursor.fetchall()
print("\nJobs by status:")
for status, count in by_status:
    print(f"  - {status}: {count}")

# 5. Find most recent jobs (last 7 days)
cursor.execute("""
    SELECT company, position, date_added 
    FROM jobs 
    WHERE date_added >= date('now', '-7 days')
    ORDER BY date_added DESC
""")
recent = cursor.fetchall()
print(f"\nRecent jobs (last 7 days): {len(recent)}")
for job in recent:
    print(f"  - {job[0]}: {job[1]} (added {job[2]})")

# 6. Average salary by status
cursor.execute("""
    SELECT status, 
           AVG(salary_min) as avg_min, 
           AVG(salary_max) as avg_max
    FROM jobs 
    WHERE salary_min IS NOT NULL
    GROUP BY status
""")
avg_salaries = cursor.fetchall()
print("\nAverage salary by status:")
for status, avg_min, avg_max in avg_salaries:
    print(f"  - {status}: ${avg_min:,.0f} - ${avg_max:,.0f}")

# CHALLENGE 1: Find all Google or Meta jobs
print("\n=== CHALLENGE 1: Google or Meta jobs ===")
cursor.execute("SELECT company, position, salary_min FROM jobs WHERE company IN ('Google', 'Meta')")
tech_giants = cursor.fetchall()
print(f"Found {len(tech_giants)} jobs:")
for job in tech_giants:
    print(f"  - {job[0]}: {job[1]} (${job[2]:,})")

# CHALLENGE 2: Jobs with salary range over $50k
print("\n=== CHALLENGE 2: Jobs with wide salary range (>$50k) ===")
cursor.execute("""
    SELECT company, position, salary_min, salary_max, 
           (salary_max - salary_min) as range
    FROM jobs
    WHERE (salary_max - salary_min) > 50000
    ORDER BY range DESC
""")
wide_range = cursor.fetchall()
print(f"Found {len(wide_range)} jobs:")
for job in wide_range:
    print(f"  - {job[0]}: {job[1]} (${job[2]:,} - ${job[3]:,}, range: ${job[4]:,})")

# CHALLENGE 3: Which company has the most jobs?
print("\n=== CHALLENGE 3: Company with most jobs ===")
cursor.execute("""
    SELECT company, COUNT(*) as count
    FROM jobs
    GROUP BY company
    ORDER BY count DESC
    LIMIT 3
""")
top_companies = cursor.fetchall()
print("Top 3 companies:")
for company, count in top_companies:
    print(f"  - {company}: {count} jobs")

# NEW FEATURE: Jobs added this month
print("\n=== Jobs added this month ===")
cursor.execute("""
    SELECT company, position, date_added
    FROM jobs
    WHERE strftime('%Y-%m', date_added) = strftime('%Y-%m', 'now')
    ORDER BY date_added DESC
""")
this_month = cursor.fetchall()
print(f"Found {len(this_month)} jobs this month:")
for job in this_month:
    print(f"  - {job[0]}: {job[1]} (added {job[2]})")

# NEW FEATURE: Jobs by company
print("\n=== Jobs by company ===")
cursor.execute("""
    SELECT company, COUNT(*) as count
    FROM jobs
    GROUP BY company
    ORDER BY count DESC
""")
company_jobs = cursor.fetchall()
print(f"Found {len(company_jobs)} companies:")
for job in company_jobs:
    print(f"  - {job[0]}: {job[1]} jobs")

conn.close()
print("\n✓ Done!")