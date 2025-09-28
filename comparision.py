import matplotlib.pyplot as plt
from hybrid import run_simulation as run_hybrid_sim
from pure_abac import run_simulation as run_abac_sim
from pure_rbac import run_simulation as run_rbac_sim

def benchmark(steps=100, attacker_strategy=[0.5, 0.5], graph_path="combined_breach_rate_comparison.png"):
    if not graph_path:
        raise ValueError("Output graph path must be provided.")

    print("\nRunning Hybrid Simulation...")
    hybrid_results, _ = run_hybrid_sim(steps=steps)

    print("\nRunning Pure ABAC Simulation...")
    abac_results = run_abac_sim(steps=steps, attacker_strategy=attacker_strategy)

    print("\nRunning Pure RBAC Simulation...")
    rbac_results = run_rbac_sim(steps=steps, attacker_strategy=attacker_strategy)

    plt.figure(figsize=(12, 8))
    plt.plot(hybrid_results["Breach Rate"], label="Hybrid", color='red')
    plt.plot(abac_results["Breach Rate"], label="ABAC", color='green')
    plt.plot(rbac_results["Breach Rate"], label="RBAC", color='blue')

    plt.title("Breach Rate Comparison: RBAC vs ABAC vs Hybrid")
    plt.xlabel("Simulation Steps")
    plt.ylabel("Moving Average Breach Rate")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()

    plt.savefig(graph_path)
    print(f"\nCombined visualization saved to: {graph_path}")
  
if __name__ == "__main__":
    run_steps = 100
    attacker_strategies = [0.5, 0.5]
    file_name = "combined_breach_rate_comparison.png"
    benchmark(run_steps, attacker_strategies, file_name)
