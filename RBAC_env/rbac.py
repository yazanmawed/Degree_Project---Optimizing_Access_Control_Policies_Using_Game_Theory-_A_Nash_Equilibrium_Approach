import sqlite3, random

def main():
    conn = sqlite3.connect('strict_rule_company.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT,
        role TEXT,
        department TEXT,
        clearance INTEGER
    )
    ''')

    roles_distribution = {
        'Admin': 5,
        'Engineer': 15,
        'Staff': 30
    }

    departments = ['Management', 'Engineering', 'Support']
    sample_users = []
    user_index = 0

    for role, count in roles_distribution.items():
        for _ in range(count):
            username = f"user{user_index:02d}"
            dept = 'Engineering' if role == 'Engineer' else random.choice(departments)
            clearance = {'Admin': 5, 'Engineer': 3, 'Staff': 1}[role]
            sample_users.append((username, role, dept, clearance))
            user_index += 1

    c.executemany('INSERT INTO users VALUES (?, ?, ?, ?)', sample_users)
    conn.commit()
    conn.close()
    print("Users table created and populated with exact role distribution.")

if __name__ == "__main__":
    main()

