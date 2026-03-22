import numpy as np

# status -> (povećanje kvote, tolerancija)
STATUS_RULES = {
    0: None,
    1: (0.4, 0.2),
    2: (1.2, 0.3),
    3: (0.0, 0.2),
    4: (3.7, 0.4),
    5: (0.1, 0.2),
    6: (2.5, 0.4),
}

def simulate_total_profit_grid(results_map, n_points=20):
    # priprema dict za ukupne gridove po statusu
    status_grids = {}

    for status in STATUS_RULES:
        if STATUS_RULES[status] is None:
            continue
        base_inc, tol = STATUS_RULES[status]
        status_grids[status] = {
            "grid": None,
            "profit": None
        }

    # prolazak kroz sve mečeve
    for match_id, data in results_map.items():
        status = data["status"]
        fav_odds = float(data["fav_odds"])
        winner = data["pobjednik"]
        fav = data["favorite"]

        if status not in STATUS_RULES or STATUS_RULES[status] is None:
            continue

        base_inc, tol = STATUS_RULES[status]
        new_base = fav_odds + base_inc
        low = max(1.01, new_base - tol)
        high = new_base + tol
        grid = np.linspace(low, high, n_points)

        profits = np.array([((odd * 1.0 - 1.0) if winner == fav else -1.0) for odd in grid])

        # inicijalizacija ili zbrajanje
        if status_grids[status]["profit"] is None:
            status_grids[status]["profit"] = profits
            status_grids[status]["grid"] = grid
        else:
            status_grids[status]["profit"] += profits

    return status_grids



