import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector


class PureABACModel(Model):
    """Mesa model for pure ABAC simulation."""
    def __init__(self, num_employees=50, num_attackers=10, attacker_strategy=None):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.num_employees = num_employees
        self.num_attackers = num_attackers
        self.policy = "ABAC"
        self.breach_count = 0
        self.access_attempts = 0
        self.breach_rates_history = []
        self.moving_window = 10

        self.attacker_strategy = attacker_strategy or [0.5, 0.5]

        for i in range(self.num_attackers):
            attacker_id = i + self.num_employees
            attacker = AttackerAgent(attacker_id, self, self.attacker_strategy)
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
    def __init__(self, unique_id, model, strategy_probs):
        super().__init__(unique_id, model)
        self.strategy_probs = strategy_probs
        self.attack_strategy = "phishing"

    def step(self):
        self.attack_strategy = np.random.choice(["phishing", "token_theft"], p=self.strategy_probs)
        self.model.access_attempts += 1

        if self.execute_attack():
            self.model.breach_count += 1

    def execute_attack(self):
        if self.attack_strategy == "phishing":
            success_rate = 0.42
        else:
            success_rate = 0.12
        return np.random.rand() < success_rate


class DefenderAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.target_breach_rate = 0.3


def run_simulation(steps=100, attacker_strategy=None):
    print("\n=== Agent-Based Simulation (Pure ABAC) ===\n")

    model = PureABACModel(
        num_employees=100,
        num_attackers=50,
        attacker_strategy=attacker_strategy
    )

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


def create_visualization(results):
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


if __name__ == "__main__":
    print("=== Pure ABAC Access Control Policy Modeling ===")
    attacker_strategy = [0.5, 0.5]
    sim_results = run_simulation(steps=100, attacker_strategy=attacker_strategy)
    create_visualization(sim_results)
    print("\n=== Analysis Complete ===")
