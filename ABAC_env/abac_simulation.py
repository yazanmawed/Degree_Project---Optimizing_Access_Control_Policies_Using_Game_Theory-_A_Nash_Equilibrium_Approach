import sqlite3, random, abac
from collections import defaultdict

def load_users():
    """Load all users from the database with their full attributes."""
    conn = sqlite3.connect('loose_rule_company.db')
    c = conn.cursor()
    c.execute("SELECT username, role, department, clearance FROM users")
    users = []
    for row in c.fetchall():
        users.append({
            'username': row[0],
            'role': row[1],
            'department': row[2],
            'clearance': row[3]
        })
    conn.close()
    return users

def simulate_phishing(users, attempts=100):
    success_prob = {'Admin': 0.11, 'Engineer': 0.11, 'Staff': 0.61}
    compromised_accounts = []

    print("\n==== Phishing Attack Simulation ====")
    for i in range(1, attempts + 1):
        user = random.choice(users)
        username = user['username']
        role = user['role']
        prob = success_prob.get(role, 0.3)
        if random.random() < prob:
            compromised_accounts.append(user)
            result = "Success"
        else:
            result = "Failed"
        print(f"Attempt {i:3}: Target={username} (Role={role}) -> {result}")

    print(f"\nPhishing campaign resulted in {len(compromised_accounts)} compromised accounts")
    return compromised_accounts

def simulate_token_theft(users, attempts=100):
    theft_prob = {'Admin': 0.05, 'Engineer': 0.05, 'Staff': 0.15}
    compromised_accounts = []

    print("\n==== Token Theft Attack Simulation ====")
    for i in range(1, attempts + 1):
        user = random.choice(users)
        username = user['username']
        role = user['role']
        prob = theft_prob.get(role, 0.2)
        if random.random() < prob:
            compromised_accounts.append(user)
            result = "Captured"
        else:
            result = "Missed"
        print(f"Attempt {i:3}: User={username} (Role={role}) -> {result}")

    print(f"\nToken theft campaign resulted in {len(compromised_accounts)} compromised sessions")
    return compromised_accounts

def simulate_resource_access(compromised_accounts):
    resources = ['admin_page', 'engineering_page', 'general_page']
    successful_access = defaultdict(int)
    total_attempts = 0

    print("\n==== Unauthorized Access Attempts ====")
    for user in compromised_accounts:
        print(f"\nUsing compromised account: {user['username']} (Role={user['role']}, Dept={user['department']})")
        for resource in resources:
            total_attempts += 1
            access_granted = abac.check_access(user, resource)
            if access_granted:
                successful_access[resource] += 1
                result = "ACCESS GRANTED"
            else:
                result = "Access Denied"
            print(f"  Attempt to access {resource}: {result}")

    return successful_access, total_attempts

def calculate_metrics(successful_access, total_attempts, compromised_accounts):
    print("\n==== ABAC Security Metrics ====")
    if not compromised_accounts:
        print("No accounts were compromised. ABAC effectiveness cannot be measured.")
        return

    total_successful = sum(successful_access.values())
    overall_rate = (total_successful / total_attempts) * 100 if total_attempts > 0 else 0

    print(f"Total compromised accounts: {len(compromised_accounts)}")
    print(f"Total access attempts: {total_attempts}")
    print(f"Successful unauthorized access: {total_successful}")
    print(f"Overall unauthorized access rate: {overall_rate:.2f}%")

    print("\nUnauthorized access by resource:")
    for resource, count in successful_access.items():
        resource_rate = (count / len(compromised_accounts)) * 100
        print(f"  {resource}: {count}/{len(compromised_accounts)} ({resource_rate:.2f}%)")

    abac_effectiveness = 100 - overall_rate
    print(f"\nABAC effectiveness score: {abac_effectiveness:.2f}%")

    return {
        'abac_effectiveness': abac_effectiveness,
        'unauthorized_access_rate': overall_rate,
        'resource_access': successful_access
    }

def run_full_simulation(phishing_attempts=100, token_theft_attempts=100):
    users = load_users()

    phishing_compromised = simulate_phishing(users, phishing_attempts)
    phishing_success_rate = (len(phishing_compromised) / phishing_attempts) * 100 if phishing_attempts else 0

    if phishing_compromised:
        print("\n--- Testing ABAC against phished accounts ---")
        phishing_access, phishing_total_attempts = simulate_resource_access(phishing_compromised)
        phishing_metrics = calculate_metrics(phishing_access, phishing_total_attempts, phishing_compromised)
    else:
        phishing_metrics = None

    token_compromised = simulate_token_theft(users, token_theft_attempts)
    token_success_rate = (len(token_compromised) / token_theft_attempts) * 100 if token_theft_attempts else 0

    if token_compromised:
        print("\n--- Testing ABAC against token theft ---")
        token_access, token_total_attempts = simulate_resource_access(token_compromised)
        token_metrics = calculate_metrics(token_access, token_total_attempts, token_compromised)
    else:
        token_metrics = None

    return {
        'phishing': phishing_metrics,
        'token_theft': token_metrics,
        'phishing_success_rate': phishing_success_rate,
        'token_success_rate': token_success_rate
    }

if __name__ == "__main__":
    print("=== RUNNING COMPREHENSIVE ABAC SECURITY ASSESSMENT ===")
    metrics = run_full_simulation(phishing_attempts=100, token_theft_attempts=100)

    print("\n=== FINAL COMPARISON ===")
    if metrics['phishing'] and metrics['token_theft']:
        print(f"ABAC Effectiveness against phishing: {metrics['phishing']['abac_effectiveness']:.2f}%")
        print(f"ABAC Effectiveness against token theft: {metrics['token_theft']['abac_effectiveness']:.2f}%")
    else:
        print("Could not complete full comparison due to no compromised accounts in one or both attack vectors.")

    print("\n=== FINAL SUCCESS RATES ===")
    print(f"Phishing attack success rate = {metrics['phishing_success_rate']:.2f}%")
    print(f"Token theft attack success rate = {metrics['token_success_rate']:.2f}%")
