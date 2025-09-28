import sqlite3
import random

DB_PATH = "strict_rule_company.db"

def main() -> None:
    """Create the users table (with a 'compromised' flag) and fill it with
    a deterministic distribution of Admin, Engineer, and Staff accounts."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username     TEXT PRIMARY KEY,
            role         TEXT,
            department   TEXT,
            clearance    INTEGER,
            compromised  INTEGER DEFAULT 0
        )
        """
    )

    role_counts = {"Admin": 10, "Engineer": 40, "Staff": 59}
    staff_departments = ["Support", "HR", "Logistics"]

    sample_rows = []
    uid = 1
    for role, count in role_counts.items():
        for _ in range(count):
            username = f"user{uid:02d}"
            uid += 1

            if role == "Admin":
                department = "Administration"
                clearance  = 5
            elif role == "Engineer":
                department = "Engineering"
                clearance  = 3
            else:
                department = random.choice(staff_departments)
                clearance  = 1

            sample_rows.append(
                (username, role, department, clearance, 0)
            )

    cur.executemany(
        "INSERT OR REPLACE INTO users VALUES (?,?,?,?,?)",
        sample_rows,
    )
    conn.commit()
    conn.close()
    print("Database initialised and populated.")

if __name__ == "__main__":
    main()
