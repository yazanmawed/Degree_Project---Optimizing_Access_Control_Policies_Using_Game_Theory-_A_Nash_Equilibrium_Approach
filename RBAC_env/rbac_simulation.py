import random
import sqlite3
from collections import defaultdict
import rbac

DB_PATH = rbac.DB_PATH

PHISH_ATTEMPTS  = 100
TOKEN_ATTEMPTS  = 100
DETECTION_PROB  = 0.40 

def load_users():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT username, role, compromised FROM users")
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "username":   row[0],
            "role":       row[1],
            "compromised": bool(row[2]),  
            "breached":   False,
        }
        for row in rows
    ]

RBAC_POLICIES = {
    "Admin":    ["admin_page", "engineering_page", "general_page"],
    "Engineer": ["engineering_page"],
    "Staff":    ["general_page"],
}

def flag_in_database(username):
    """Set compromised = 1 in SQLite so future sessions are blocked."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET compromised = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def check_rbac_access(user, resource, detection_prob=DETECTION_PROB) -> bool:
    """
    Enforce RBAC *and* run inline detection.
    Return True *only* if the request is ultimately allowed.
    """
    if user["compromised"]:
        return False

    allowed = resource in RBAC_POLICIES.get(user["role"], [])

    if random.random() < detection_prob:
        print("  !! DETECTED – account disabled")
        user["compromised"] = True
        flag_in_database(user["username"])
        return False

    return allowed

def compromise_accounts(users, attempts, odds, label):
    """Generic helper for phishing & token theft."""
    compromised = []
    print(f"\n=== {label} ===")
    for i in range(1, attempts + 1):
        victim = random.choice(users)
        if random.random() < odds[victim["role"]]:
            victim["breached"] = True
            compromised.append(victim)
            outcome = "Success"
        else:
            outcome = "Failed"
        print(f"[{i:03}] {victim['username']} ({victim['role']}) → {outcome}")
    print(f"{len(compromised)} accounts now in attacker hands.")
    return compromised

def simulate_phishing(users, attempts=PHISH_ATTEMPTS):
    success_prob = {'Admin': 0.11, 'Engineer': 0.11, 'Staff': 0.61}
    return compromise_accounts(users, attempts, success_prob, "Phishing Campaign")

def simulate_token_theft(users, attempts=TOKEN_ATTEMPTS):
    theft_prob   = {'Admin': 0.05, 'Engineer': 0.05, 'Staff': 0.15}
    return compromise_accounts(users, attempts, theft_prob, "Token-Theft Campaign")

def simulate_resource_access(breached_accounts, detection_prob=DETECTION_PROB):
    resources  = ["admin_page", "engineering_page", "general_page"]
    successes  = defaultdict(int)
    total_reqs = 0

    if not breached_accounts:
        return successes, total_reqs

    print("\n=== Malicious Resource Requests ===")
    for user in breached_accounts:
        if user["compromised"]:
            continue

        print(f"\n> Attacker uses {user['username']} ({user['role']})")
        for res in resources:
            if user["compromised"]:
                break

            total_reqs += 1
            allowed = check_rbac_access(user, res, detection_prob)

            result = "ACCESS GRANTED" if allowed else "Access Denied"
            print(f"  {res:17}: {result}")

            if allowed:
                successes[res] += 1

            if user["compromised"]:
                break

    return successes, total_reqs

def print_metrics(successes, total, compromised_list, banner):
    print(f"\n=== Metrics after {banner} ===")
    if total == 0:
        print("No breached accounts → nothing to measure.")
        return

    success_count = sum(successes.values())
    rate          = (success_count / total) * 100
    effectiveness = 100 - rate

    print(f"Breached accounts        : {len(compromised_list)}")
    print(f"Total malicious requests : {total}")
    print(f"Successful unauthorised  : {success_count}")
    print(f"Unauthorised rate        : {rate:.2f}%")
    print(f"RBAC effectiveness       : {effectiveness:.2f}%")
    for res, n in successes.items():
        print(f"  – {res}: {n}")

def run_full_simulation():
    users = load_users()

    phish_breach = simulate_phishing(users)
    phish_success, phish_total = simulate_resource_access(phish_breach)
    print_metrics(phish_success, phish_total, phish_breach, "Phishing")

    token_breach = simulate_token_theft(users)
    token_success, token_total = simulate_resource_access(token_breach)
    print_metrics(token_success, token_total, token_breach, "Token Theft")
    
    print("\n=== FINAL SUCCESS RATES ===")
    if phish_total > 0:
        phish_rate = (sum(phish_success.values()) / phish_total) * 100
        print(f"Phishing attack success rate = {phish_rate:.2f}%")
    else:
        print("Phishing attack success rate = N/A (no data)")

    if token_total > 0:
        token_rate = (sum(token_success.values()) / token_total) * 100
        print(f"Token theft attack success rate = {token_rate:.2f}%")
    else:
        print("Token theft attack success rate = N/A (no data)")

if __name__ == "__main__":
    rbac.main()
    print("\n=== RUNNING RBAC SIM WITH INLINE DETECTION ===")
    run_full_simulation()
