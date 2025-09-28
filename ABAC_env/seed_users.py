import sqlite3, random

conn = sqlite3.connect('loose_rule_company.db')
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS users")
c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        role TEXT NOT NULL,
        department TEXT NOT NULL,
        clearance INTEGER NOT NULL
    )
''')

user_distribution = {
    'Admin': 10,
    'Engineer': 40,
    'Staff': 59
}

staff_departments = ['Support', 'HR', 'Logistics']
engineer_department = 'Engineering'
admin_department = 'Administration'

def get_clearance(role):
    if role == 'Admin':
        return random.randint(4, 5)
    elif role == 'Engineer':
        return random.randint(3, 4)
    else:
        return random.randint(1, 3)

user_id = 1
for role, count in user_distribution.items():
    for _ in range(count):
        username = f"user{user_id:02d}"
        clearance = get_clearance(role)

        if role == 'Admin':
            department = admin_department
        elif role == 'Engineer':
            department = engineer_department
        else:
            department = random.choice(staff_departments)

        c.execute('''
            INSERT INTO users (username, role, department, clearance)
            VALUES (?, ?, ?, ?)
        ''', (username, role, department, clearance))
        
        user_id += 1

conn.commit()
conn.close()

print("109 users has been created: 10 Admins, 40 Engineers, 59 Staff")
