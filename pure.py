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
    print("\n=== Game Theory Analysis (Pure ABAC) ===\n")
    
    defender_payoffs = [[-6, 4]]
    attacker_payoffs = [[3, -2]]
    game = nash.Game(defender_payoffs, attacker_payoffs)
    equilibria = list(game.support_enumeration())

    print("Nash Equilibria:")
    for eq in equilibria:
        defender_strategy, attacker_strategy = eq
        print(f"Defender: {defender_strategy}, Attacker: {attacker_strategy}")
    
    return equilibria


class PureABACModel(Model):
    """Mesa model for pure ABAC simulation."""
    def __init__(self, num_employees=50, num_attackers=10, defender_strategy=None, attacker_strategy=None):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.num_employees = num_employees
        self.num_attackers = num_attackers
        self.policy = "ABAC"
        self.breach_count = 0
        self.access_attempts = 0
        self.breach_rates_history = []
        self.moving_window = 10
        self.defender_strategy = [1.0, 0.0]
        if attacker_strategy is not None:
            self.attacker_strategy = attacker_strategy
        else:
            self.attacker_strategy = [0.5, 0.5]

        for i in range(self.num_attackers):
            attacker_id = i + self.num_employees
            attacker = AttackerAgent(attacker_id, self)
            self.schedule.add(attacker)

        defender_id = self.num_employees + self.num_attackers + 1
        self.defender = DefenderAgent(defender_id, self)
        self.schedule.add(self.defender)

        self.datacollector = DataCollector(
            model_reporters={
                "Policy": lambda m: m.policy,
                "Breach Rate": lambda m: m.get_moving_breach_rate()
            }
        )

    def get_current_breach_rate(self):
        if self.access_attempts == 0:
            return 0
        return self.breach_count / self.access_attempts

    def get_moving_breach_rate(self):
        if len(self.breach_rates_history) == 0:
            return 0
        return np.mean(self.breach_rates_history[-self.moving_window:])

    def step(self):
        current_rate = self.get_current_breach_rate()
        self.breach_rates_history.append(current_rate)
        self.datacollector.collect(self)
        self.schedule.step()


class AttackerAgent(Agent):
    """Agent representing attackers."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        strategy = self.model.attacker_strategy
        attack_type = np.random.choice(["phishing", "token_theft"], p=strategy)
        self.model.access_attempts += 1
        if self.execute_attack(attack_type):
            self.model.breach_count += 1

    def execute_attack(self, attack_type):
        success_rate = 0.7 if attack_type == "phishing" else 0.6
        return np.random.rand() < success_rate


class DefenderAgent(Agent):
    """Agent representing the system administrator (defender)."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.target_breach_rate = 0.3

    def step(self):
        breach_rate_ma = self.model.get_moving_breach_rate()
        if breach_rate_ma > self.target_breach_rate:
            pass
        else:
            pass


def run_simulation(steps=100, defender_strategy=None, attacker_strategy=None):
    print("\n=== Agent-Based Simulation (Pure ABAC) ===\n")

    model = PureABACModel(num_employees=100, num_attackers=20,
                          defender_strategy=defender_strategy,
                          attacker_strategy=attacker_strategy)

    print("Initial state:")
    print(f"  Number of employees: {model.num_employees}")
    print(f"  Number of attackers: {model.num_attackers}")
    print(f"  Policy: {model.policy}")

    print("\nRunning simulation...")
    for i in range(steps):
        model.step()
        if i % 10 == 0:
            breach_ma = model.get_moving_breach_rate()
            print(f"Step {i}: Policy = {model.policy}, Moving Average breach = {breach_ma:.4f}")

    results = model.datacollector.get_model_vars_dataframe()
    final_breach_rate = model.get_current_breach_rate()
    final_breach_ma = model.get_moving_breach_rate()

    print("\nFinal state:")
    print(f"  Policy: {model.policy}")
    print(f"  Total access attempts: {model.access_attempts}")
    print(f"  Total breaches: {model.breach_count}")
    print(f"  Final (instant) breach rate: {final_breach_rate:.4f}")
    print(f"  Final (moving average) breach rate: {final_breach_ma:.4f}")
    return results


def create_visualization(results, equilibria):
    print("\n=== Visualization (Pure ABAC) ===\n")
    plt.figure(figsize=(12, 8))
    plt.plot(results["Breach Rate"], label="Moving Average Breach", color='green')
    plt.title("Security Breach Rate Over Time (Pure ABAC)")
    plt.xlabel("Simulation Steps")
    plt.ylabel("Breach Rate")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig('pure_abac_simulation.png')
    print("Visualization saved to: pure_abac_simulation.png")

    print("\nNash Equilibria from game theory analysis:")
    for i, eq in enumerate(equilibria):
        defender_strategy, attacker_strategy = eq
        print(f"Equilibrium {i+1}:")
        print(f"  Defender: {defender_strategy}")
        print(f"  Attacker: {attacker_strategy}")


if __name__ == "__main__":
    print("=== Pure ABAC Access Control Policy Modeling ===")
    print("Combining Game Theory and Agent-Based Simulation\n")

    equilibria = run_game_theory_analysis()
    defender_strat, attacker_strat = equilibria[0]

    sim_results = run_simulation(steps=100,
                                 defender_strategy=defender_strat,
                                 attacker_strategy=attacker_strat)

    create_visualization(sim_results, equilibria)
    print("\n=== Analysis Complete ===")
