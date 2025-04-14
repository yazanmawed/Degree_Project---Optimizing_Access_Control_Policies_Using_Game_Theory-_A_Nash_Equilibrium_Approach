import numpy as np
import nashpy as nash
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector


def run_game_theory_analysis():
    """Run game theory analysis and return the equilibria"""
    print("\n=== Game Theory Analysis ===\n")
    
    defender_payoffs = np.array([[1, 1],
                                 [-5, -3]])
    
    attacker_payoffs = np.array([[-2, 1],
                                 [3, 2]])
    
    game = nash.Game(defender_payoffs, attacker_payoffs)
    equilibria = list(game.support_enumeration())
    
    print("Nash Equilibria:")
    for eq in equilibria:
        defender_strategy, attacker_strategy = eq
        print(f"Defender: {defender_strategy}, Attacker: {attacker_strategy}")
    
    print("\nExpected Payoffs for Strategy Profiles:")
    for i, defender_strat in enumerate(["RBAC", "ABAC"]):
        for j, attacker_strat in enumerate(["Phishing", "Token Theft"]):
            print(f"If Defender plays {defender_strat} and Attacker plays {attacker_strat}:")
            print(f"  Defender payoff: {defender_payoffs[i, j]}")
            print(f"  Attacker payoff: {attacker_payoffs[i, j]}")
    
    return equilibria


class AccessControlModel(Model):
    """Mesa model for access control simulation"""
    def __init__(self, num_employees=50, num_attackers=10, initial_policy_mix=(0.5, 0.5)):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.num_employees = num_employees
        self.num_attackers = num_attackers
        self.policy_mix = initial_policy_mix
        self.breach_count = 0
        self.access_attempts = 0
        self.breach_rates_history = []
        self.moving_window = 10
        
        for i in range(self.num_attackers):
            attacker_id = i + self.num_employees
            attacker = AttackerAgent(attacker_id, self)
            self.schedule.add(attacker)
        
        defender_id = self.num_employees + self.num_attackers + 1
        self.defender = DefenderAgent(defender_id, self)
        self.schedule.add(self.defender)
        
        self.datacollector = DataCollector(
            model_reporters={
                "RBAC Policy": lambda m: m.policy_mix[0],
                "ABAC Policy": lambda m: m.policy_mix[1],
                "Breach Rate": lambda m: m.get_moving_breach_rate()
            }
        )

    def get_current_breach_rate(self):
        """Real-time breach rate"""
        if self.access_attempts == 0:
            return 0
          
        return self.breach_count / self.access_attempts

    def get_moving_breach_rate(self):
        """Moving average of breach rate calculation"""
        if len(self.breach_rates_history) == 0:
            return 0
          
        return np.mean(self.breach_rates_history[-self.moving_window:])

    def step(self):
        """Calculating the current rate and store it for later"""
        current_rate = self.get_current_breach_rate()
        self.breach_rates_history.append(current_rate)
        self.datacollector.collect(self)
        self.schedule.step()

class AttackerAgent(Agent):
    """Agent representing attackers"""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.attack_strategy = "phishing"
        
    def step(self):
        """Attack strat"""
        self.attack_strategy = np.random.choice(["phishing", "token_theft"], p=[0.5, 0.5])
        self.model.access_attempts += 1
        if self.execute_attack():
            self.model.breach_count += 1
            
    def execute_attack(self):
        rbac_weight = self.model.policy_mix[0]
        if self.attack_strategy == "phishing":
            success_rate = 0.3 * rbac_weight + 0.5 * (1 - rbac_weight)
          
        else:
            success_rate = 0.4 * rbac_weight + 0.6 * (1 - rbac_weight)
            
        return np.random.rand() < success_rate


class DefenderAgent(Agent):
    """Agent representing the system administrator as a defender"""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.K_s = 0.5
        self.K_u = 1.5
        self.target_breach_rate = 0.3
        self.target_abac_share = 0.4

    def step(self):
        breach_rate_ma = self.model.get_moving_breach_rate()
        rbac, abac = self.model.policy_mix
        error_security = breach_rate_ma - self.target_breach_rate
        error_usability = self.target_abac_share - abac
        delta_rbac = (self.K_s * error_security) - (self.K_u * error_usability)
        new_rbac = rbac + delta_rbac
        new_rbac = max(0.0, min(new_rbac, 1.0))
        new_abac = 1.0 - new_rbac
        self.model.policy_mix = (new_rbac, new_abac)


def run_simulation(steps=100):
    print("\n=== Agent-Based Simulation ===\n")
    model = AccessControlModel(num_employees=100, num_attackers=20, initial_policy_mix=(0.5, 0.5))
    print("Initial state:")
    print(f"  Number of employees: {model.num_employees}")
    print(f"  Number of attackers: {model.num_attackers}")
    print(f"  Initial policy mix (RBAC, ABAC): {model.policy_mix}")
    
    print("\nRunning simulation...")
    for i in range(steps):
        model.step()
        if i % 10 == 0:
            breach_ma = model.get_moving_breach_rate()
            print(f"Step {i}: Policy mix = {model.policy_mix}, Moving Average breach = {breach_ma:.4f}")
    
    results = model.datacollector.get_model_vars_dataframe()
    final_rbac, final_abac = model.policy_mix
    final_breach_rate = model.get_current_breach_rate()
    final_breach_ma = model.get_moving_breach_rate()
    
    print("\nFinal state:")
    print(f"  Final policy mix (RBAC, ABAC): ({final_rbac:.3f}, {final_abac:.3f})")
    print(f"  Total access attempts: {model.access_attempts}")
    print(f"  Total breaches: {model.breach_count}")
    print(f"  Final (instant) breach rate: {final_breach_rate:.4f}")
    print(f"  Final (moving average) breach rate: {final_breach_ma:.4f}")
    
    return results


def create_visualization(results, equilibria):
    print("\n=== Visualization ===\n")
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(results["RBAC Policy"], label="RBAC")
    plt.plot(results["ABAC Policy"], label="ABAC")
    plt.title("Policy Mix Evolution Over Time")
    plt.ylabel("Policy Mix")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.subplot(2, 1, 2)
    plt.plot(results["Breach Rate"], label="Moving Average Breach", color='red')
    plt.title("Security Breach Rate Over Time (Moving Average)")
    plt.xlabel("Simulation Steps")
    plt.ylabel("Breach Rate")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('access_control_simulation.png')
    print("Visualization saved to: access_control_simulation.png")
    
    final_policy_mix = (results["RBAC Policy"].iloc[-1], results["ABAC Policy"].iloc[-1])
    print(f"\nFinal policy mix from simulation: RBAC={final_policy_mix[0]:.2f}, ABAC={final_policy_mix[1]:.2f}")
    
    print("\nNash Equilibria from game theory analysis:")
    for i, eq in enumerate(equilibria):
        defender_strategy, attacker_strategy = eq
        print(f"Equilibrium {i+1}:")
        print(f"  Defender: {defender_strategy}")
        print(f"  Attacker: {attacker_strategy}")



if __name__ == "__main__":
    print("=== Access Control Policy Modeling ===")
    print("Combining Game Theory and Agent-Based Simulation\n")
    
    eq = run_game_theory_analysis()
    sim_results = run_simulation(steps=100)
    create_visualization(sim_results, eq)
    print("\n=== Analysis Complete ===")
