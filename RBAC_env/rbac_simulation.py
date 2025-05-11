import sqlite3, random, rbac
from collections import defaultdict


def load_users():
    conn = sqlite3.connect('strict_rule_company.db')
    c = conn.cursor()
    c.execute("SELECT username, role FROM users")
    users = [{'username': row[0], 'role': row[1]} for row in c.fetchall()]
    conn.close()
    return users

rbac_policies = {
    'Admin': ['admin_page', 'engineering_page', 'general_page'],
    'Engineer': ['engineering_page', 'general_page'],
    'Staff': ['general_page']
}

def check_rbac_access(user, resource):
    allowed_resources = rbac_policies.get(user['role'], [])
    return resource in allowed_resources

def simulate_phishing(users, attempts=100):
    success_prob = {'Admin': 0.05, 'Engineer': 0.15, 'Staff': 0.25}
    compromised = []
    print("\n==== Phishing Attack Simulation (RBAC) ====")
    for i in range(1, attempts+1):
        user = random.choice(users)
        prob = success_prob.get(user['role'], 0.1)
        if random.random() < prob:
            compromised.append(user)
            result = "Success"
        else:
            result = "Failed"
        print(f"Attempt {i:3}: Target={user['username']} (Role={user['role']}) -> {result}")
    print(f"\nPhishing campaign resulted in {len(compromised)} compromised accounts")
    return compromised

def simulate_token_theft(users, attempts=100):
    theft_prob = {'Admin': 0.05, 'Engineer': 0.15, 'Staff': 0.25}
    compromised = []
    print("\n==== Token Theft Attack Simulation (RBAC) ====")
    for i in range(1, attempts+1):
        user = random.choice(users)
        prob = theft_prob.get(user['role'], 0.1)
        if random.random() < prob:
            compromised.append(user)
            result = "Captured"
        else:
            result = "Missed"
        print(f"Attempt {i:3}: User={user['username']} (Role={user['role']}) -> {result}")
    print(f"\nToken theft campaign resulted in {len(compromised)} compromised sessions")
    return compromised

def simulate_resource_access(compromised):
    resources = ['admin_page', 'engineering_page', 'general_page']
    successful = defaultdict(int)
    total = 0
    print("\n==== Unauthorized Access Attempts (RBAC) ====")
    for user in compromised:
        print(f"\nUsing compromised account: {user['username']} (Role={user['role']})")
        for res in resources:
            total += 1
            if check_rbac_access(user, res):
                successful[res] += 1
                result = "ACCESS GRANTED"
            else:
                result = "Access Denied"
            print(f"  Attempt to access {res}: {result}")
    return successful, total

def calculate_metrics(successful, total, compromised):
    print("\n==== RBAC Security Metrics ====")
    if not compromised:
        print("No accounts were compromised. RBAC effectiveness cannot be measured.")
        return
    total_successful = sum(successful.values())
    rate = (total_successful / total) * 100 if total > 0 else 0
    print(f"Total compromised accounts: {len(compromised)}")
    print(f"Total access attempts: {total}")
    print(f"Successful unauthorized access: {total_successful}")
    print(f"Overall unauthorized access rate: {rate:.2f}%")

    print("\nUnauthorized access by resource:")
    for resource, count in successful.items():
        resource_rate = (count / len(compromised)) * 100
        print(f"  {resource}: {count}/{len(compromised)} ({resource_rate:.2f}%)")

    effectiveness = 100 - rate
    print(f"\nRBAC effectiveness score: {effectiveness:.2f}%")

    return {
        'rbac_effectiveness': effectiveness,
        'unauthorized_access_rate': rate,
        'resource_access': successful
    }

def run_full_simulation(phishing_attempts=100, token_theft_attempts=100):
    users = load_users()

    phishing_comp = simulate_phishing(users, phishing_attempts)
    phishing_success_rate = (len(phishing_comp) / phishing_attempts) * 100 if phishing_attempts else 0
    phishing_metrics = None
    if phishing_comp:
        phishing_access, phishing_total = simulate_resource_access(phishing_comp)
        phishing_metrics = calculate_metrics(phishing_access, phishing_total, phishing_comp)

    token_comp = simulate_token_theft(users, token_theft_attempts)
    token_success_rate = (len(token_comp) / token_theft_attempts) * 100 if token_theft_attempts else 0
    token_metrics = None
    if token_comp:
        token_access, token_total = simulate_resource_access(token_comp)
        token_metrics = calculate_metrics(token_access, token_total, token_comp)

    print("\n=== FINAL SUCCESS RATES ===")
    print(f"Phishing attack success rate = {phishing_success_rate:.2f}%")
    print(f"Token theft attack success rate = {token_success_rate:.2f}%")

    return {
        'phishing': phishing_metrics,
        'token_theft': token_metrics,
        'phishing_success_rate': phishing_success_rate,
        'token_success_rate': token_success_rate
    }

if __name__ == "__main__":
    rbac.main()  
    print("=== RUNNING COMPREHENSIVE RBAC SECURITY ASSESSMENT ===")
    metrics = run_full_simulation(phishing_attempts=100, token_theft_attempts=100)
