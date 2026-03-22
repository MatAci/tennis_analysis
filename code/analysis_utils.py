# analysis_utils.py
from collections import defaultdict
import sqlite3
import configparser

def analyze_state_and_straight_sets(analysis, return_games_rows=False):
    """
    analysis: dict rezultat iz analyze_favorites_status()
    return_games_rows: ako True vraća i sve retke iz games (list of tuples)
    Vraća dict sa:
      - state1_count: broj mečeva sa state==1 (iz analysis)
      - opp_2_0_count: broj mečeva gdje je oponent osvojio setove 1 i 2
      - opp_2_0_matches: lista match_id-ova koji su 2:0 za oponenta
      - games_rows: (opcionalno) svi retci iz games
    """
    # 1) broj state=1 IZ analysis (točno i konzistentno)
    state1_count = sum(1 for d in analysis.values() if d.get("state") == 1)

    # 2) broj mečeva gdje je oponent osvojio 2:0 (koristimo set_winner iz analysis)
    opp_2_0_count = 0
    opp_2_0_matches = []
    for match_id, d in analysis.items():
        sw = d.get("set_winner", {})      # očekujemo nešto poput {1: "OPPONENT", 2: "OPPONENT", ...}
        opponent = d.get("opponent")      # u analysis su opponent/favorite normalizirani
        if sw.get(1) == opponent and sw.get(2) == opponent:
            opp_2_0_count += 1
            opp_2_0_matches.append(match_id)

    # 3) opcionalno: izvuci sve iz games (ako ti treba raw dump)
    games_rows = None
    if return_games_rows:
        config = configparser.ConfigParser()
        config.read("config.ini")
        DB_FILE = config.get("database", "db_file")
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("""
            SELECT match_id, set_number, game_number, player_name, score1, score2
            FROM games
            ORDER BY match_id, set_number, game_number
        """)
        games_rows = cur.fetchall()
        conn.close()

    return {
        "state1_count": state1_count,
        "opp_2_0_count": opp_2_0_count,
        "opp_2_0_matches": opp_2_0_matches,
        "games_rows": games_rows
    }

def match_final_winner(match_id):
    config = configparser.ConfigParser()
    config.read("config.ini")
    DB_FILE = config.get("database", "db_file")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT player1_name, player2_name, result_player1, result_player2
        FROM matches
        WHERE match_id = ?
    """, (match_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None

    p1, p2, res1, res2 = row
    return normalize_name(p1), normalize_name(p2), int(res1), int(res2)


def normalize_name(name):
    if not name:
        return None
    translit_table = str.maketrans({
        "Š": "S", "š": "s",
        "Č": "C", "č": "c",
        "Ć": "C", "ć": "c",
        "Ž": "Z", "ž": "z",
        "Đ": "DZ", "đ": "dz"
    })
    norm = name.translate(translit_table).upper()
    return norm[:7]  # uvijek samo prvih 7 znakova

def compare_player_name(player_name, player1, player2):
    if not player_name:
        return player_name
    pn_cmp = normalize_name(player_name)
    p1_cmp = normalize_name(player1)
    p2_cmp = normalize_name(player2)
    if pn_cmp == p1_cmp:
        return p1_cmp
    elif pn_cmp == p2_cmp:
        return p2_cmp
    else:
        return pn_cmp

def analyze_favorites_status():
    config = configparser.ConfigParser()
    config.read("config.ini")
    DB_FILE = config.get("database", "db_file")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        SELECT m.match_id, m.player1_name, m.player2_name, m.odds_player1, m.odds_player2, 
               g.set_number, g.game_number, g.player_name, g.result_type, g.score1, g.score2
        FROM matches m
        JOIN games g ON m.match_id = g.match_id
        ORDER BY m.match_id, g.set_number, g.game_number
    """)

    rows = cur.fetchall()
    matches_dict = defaultdict(list)
    for r in rows:
        match_id = r[0]
        matches_dict[match_id].append(r)

    results = {}

    for match_id, games in matches_dict.items():
        _, p1_full, p2_full, kv1, kv2, _, _, _, _, _, _ = games[0]

        player1 = normalize_name(p1_full)
        player2 = normalize_name(p2_full)

        try:
            kv1 = float(kv1)
            kv2 = float(kv2)
        except:
            kv1 = kv2 = 1.0

        # ispravno: favorit je onaj s manjom kvotom
        if kv1 < kv2:
            favorite, opponent = player1, player2
        else:
            favorite, opponent = player2, player1

        favorite_breaks = 0
        opponent_breaks = 0
        status = 0
        state = 0
        prev_set = 1
        set_winner = {}

        flag_break_opponent = {}
        flag_break_favorite = {}

        last_game_in_set = defaultdict(dict)

        for g in games:
            set_num = g[5]
            game_num = g[6]
            player = compare_player_name(g[7], player1, player2)
            result = g[8].upper()
            score1 = int(g[9])
            score2 = int(g[10])

            if set_num != prev_set:
                favorite_breaks = 0
                opponent_breaks = 0
                prev_set = set_num

            if result == "BREAKS":
                if player == favorite:
                    favorite_breaks += 1
                    if favorite_breaks > opponent_breaks:
                        flag_break_favorite[set_num] = True
                else:
                    opponent_breaks += 1
                    if opponent_breaks > favorite_breaks:
                        flag_break_opponent[set_num] = True

            last_game_in_set[set_num] = {
                "player": player,
                "score1": score1,
                "score2": score2,
                "fav_breaks": favorite_breaks,
                "opp_breaks": opponent_breaks,
                "result": result,
                "game_num": game_num
            }

        for set_num, last_game in last_game_in_set.items():
            set_winner[set_num] = last_game["player"]

            if set_num == 1:
                if flag_break_opponent.get(1, False):
                    status = 1
                if set_winner[1] == opponent:
                    status = 2

            if set_num == 2:
                if set_winner.get(1) == favorite:
                    if flag_break_opponent.get(2, False):
                        status = 3
                    if set_winner[2] == opponent:
                        status = 5
                else:
                    if flag_break_opponent.get(2, False):
                        status = 4

            if set_num == 3:
                if set_winner.get(1) == favorite and set_winner.get(2) == opponent:
                    if flag_break_opponent.get(3, False):
                        status = 6

        if set_winner.get(1) == opponent and set_winner.get(2) == favorite:
            state = 1

        results[match_id] = {
            "status": status,
            "favorite": favorite,
            "opponent": opponent,
            "set_winner": set_winner,
            "state": state,
            "odds_by_player": {
                player1: kv1,
                player2: kv2
            }
        }

    conn.close()
    return results

def _format_odds_for(player, odds_map):
    if player in odds_map:
        return f"{odds_map[player]:.3f}"
    return "N/A"

def build_results_map():
    analysis = analyze_favorites_status()
    results_map = {}

    for match_id, data in analysis.items():
        mf = match_final_winner(match_id)
        if mf is None:
            p1, p2, res1, res2 = None, None, 0, 0
        else:
            p1, p2, res1, res2 = mf

        fav = data["favorite"]
        opp = data["opponent"]
        odds_map = data.get("odds_by_player", {})

        fav_odds_str = _format_odds_for(fav, odds_map)
        opp_odds_str = _format_odds_for(opp, odds_map)

        # rezultat u formatu favorit – oponent
        fav_res = res1 if fav == p1 else res2
        opp_res = res2 if opp == p2 else res1
        pobjednik = fav if fav_res > opp_res else opp

        match_data = {
            "status": data["status"],
            "favorite": fav,
            "fav_odds": fav_odds_str,
            "opponent": opp,
            "opp_odds": opp_odds_str,
            "pobjednik": pobjednik,
            "rezultat": f"{fav_res}-{opp_res}"
        }

        if data["state"] != 0:
            match_data["state"] = data["state"]

        results_map[match_id] = match_data

    summary = analyze_state_and_straight_sets(analysis, return_games_rows=False)

    return results_map, summary