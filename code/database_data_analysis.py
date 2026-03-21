from analysis_utils import build_results_map
from betting_simulation import simulate_total_profit_grid

'''
if __name__ == "__main__":
    results_map, summary = build_results_map()


    for match_id, data in results_map.items():
      print(match_id, "->", data)

    print("\nBroj mečeva sa state=1 (iz analysis):", summary["state1_count"])
    print("Broj mečeva gdje je oponent osvojio 2:0:", summary["opp_2_0_count"])
    print("Matchovi 2:0 za oponenta:", summary["opp_2_0_matches"])

'''

if __name__ == "__main__":
    results_map, summary = build_results_map()

    status_sims = simulate_total_profit_grid(results_map, n_points=30)

    # ispis ukupnog profita po statusu
    for status, data in status_sims.items():
        print(f"\n=== Status {status} ===")
        for kv, prof in zip(data["grid"], data["profit"]):
            print(f"kvota={kv:.2f}, profit={prof:.2f}")

