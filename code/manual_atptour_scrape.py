import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import configparser
from db_connection import DatabaseConnection  # Import nove klase za konekciju

def get_player_names(driver):
    """
    Dohvati imena igrača iz graph_area hijerarhije.
    Vraća listu [player1_name, player2_name], samo prezimena ako je format 'A. BCDEF'.
    """
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        container = body.find_element(By.CLASS_NAME, "container")
        wrapper = container.find_element(By.CLASS_NAME, "wrapper")
        atp_layout = wrapper.find_element(By.CLASS_NAME, "atp_layout")
        layout_container = atp_layout.find_element(By.CLASS_NAME, "atp_layout-container")
        stats_section = layout_container.find_element(By.CLASS_NAME, "stats-vs-stats--external")
        infosys_center = stats_section.find_element(By.ID, "InfosysMatchCenter")
        match_center = infosys_center.find_element(By.CLASS_NAME, "match-center")
        content_wrapper = match_center.find_element(By.CLASS_NAME, "content-wrapper")
        matchbeats = content_wrapper.find_element(By.ID, "MatchBeats")
        matchbeats_wrapper = matchbeats.find_element(By.CLASS_NAME, "matchbeats-wrapper")
        graph_area = matchbeats_wrapper.find_element(By.CLASS_NAME, "graph-area")
        player_panel_wrapper = graph_area.find_element(By.CLASS_NAME, "player-panel-wrapper")
        player_name_block = player_panel_wrapper.find_element(By.CLASS_NAME, "player-name-block")
        name_block_wrappers = player_name_block.find_elements(By.CLASS_NAME, "name-block-wrapper")

        player_names = []

        for wrapper_el in name_block_wrappers:
            name_ret_containers = wrapper_el.find_elements(By.CLASS_NAME, "name-ret-container")
            for container_el in name_ret_containers:
                shot_label_wrapper = container_el.find_element(By.CLASS_NAME, "name-shot-label-wrapper")
                name_wrapper = shot_label_wrapper.find_element(By.CLASS_NAME, "name-wrapper")
                link = name_wrapper.find_element(By.TAG_NAME, "a")
                span = link.find_element(By.CSS_SELECTOR, "span.popover-wrapper")
                full_name = span.text.strip()
                
                # Ako je format "A. Prezime", uzmi samo prezime
                if "." in full_name:
                    parts = full_name.split(".")
                    
                    full_name = parts[1].strip().upper()  # samo prezime, velika slova
                
                player_names.append(full_name)

        return player_names[:2]  # prvih dvoje igrača
    except Exception as e:
        print("Greška u dohvaćanju imena igrača:", e)
        return [None, None]

def scrape_matchbeats():
    options = webdriver.ChromeOptions()
    options.debugger_address = "127.0.0.1:9222"  # koristi već otvoreni Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    driver.switch_to.window(driver.current_window_handle)
    wait.until(EC.presence_of_element_located((By.ID, "MatchBeats")))
    time.sleep(2)

    '''
    # === SQLite DB ===
    config = configparser.ConfigParser()
    config.read("config.ini")  # ili path do tvoje .ini datoteke
    DB_FILE = config.get("database", "db_file")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    '''

    config = configparser.ConfigParser()
    config.read("config.ini")  # Učitavanje konfiguracije
    schema = config.get("postgresql", "schema")  # Dohvati shemu iz config.ini

    db = DatabaseConnection()  # Inicijaliziraj konekciju na bazu
    conn = db.connect()

    try:

        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {schema};")
            cur.execute(f"SELECT nextval('match_id_seq')")  
            match_id = cur.fetchone()[0]

        body = driver.find_element(By.TAG_NAME, "body")
        container = body.find_element(By.CLASS_NAME, "container")
        wrapper = container.find_element(By.CLASS_NAME, "wrapper")
        atp_layout = wrapper.find_element(By.CLASS_NAME, "atp_layout")
        layout_container = atp_layout.find_element(By.CLASS_NAME, "atp_layout-container")
        stats_section = layout_container.find_element(By.CLASS_NAME, "stats-vs-stats--external")
        infosys_center = stats_section.find_element(By.ID, "InfosysMatchCenter")
        match_center = infosys_center.find_element(By.CLASS_NAME, "match-center")
        content_wrapper = match_center.find_element(By.CLASS_NAME, "content-wrapper")
        matchbeats = content_wrapper.find_element(By.ID, "MatchBeats")
        matchbeats_wrapper = matchbeats.find_element(By.CLASS_NAME, "matchbeats-wrapper")
        graph_area = matchbeats_wrapper.find_element(By.CLASS_NAME, "graph-area")
        svg_panel = graph_area.find_element(By.CLASS_NAME, "svg-panel")
        draggable_wrapper = svg_panel.find_element(By.CLASS_NAME, "draggableContainerWrapper")
        drag_container = draggable_wrapper.find_element(By.ID, "dragMe")
        set_container = drag_container.find_element(By.CLASS_NAME, "set-container")

        set_wrappers = set_container.find_elements(By.CLASS_NAME, "set-wrapper")

        # === Dohvati imena igrača pomoću nove funkcije ===
        player1_name, player2_name = get_player_names(driver)
        print("Player 1:", player1_name)
        print("Player 2:", player2_name)

        # napravi match_id od prvih 7 slova oba imena
        if player1_name and player2_name:
            match_name = f"{player1_name[:7]}_{player2_name[:7]}"
        else:
            match_name = None

        '''
        # === Spremi meč i uzmi match_id ===
        cur.execute("INSERT INTO matches (player1_name, player2_name) VALUES (?, ?)", (player1_name, player2_name))
        match_id = cur.lastrowid

        '''

        # === Prođi kroz setove i gemove ===
        all_games = []
        valid_match = True

        for set_index, set_div in enumerate(set_wrappers, start=1):
            print(f"\nSet {set_index}")
            game_blocks = set_div.find_elements(By.CLASS_NAME, "game-block")

            set_games = []

            for game_index, game_block in enumerate(game_blocks, start=1):
                try:
                    game_card = game_block.find_element(By.CLASS_NAME, "game-card-wrapper")

                    player_name = game_card.find_element(By.CLASS_NAME, "name").text
                    result_type = game_card.find_element(By.CLASS_NAME, "result").text
                    score1 = game_card.find_element(By.CLASS_NAME, "box1").text
                    score2 = game_card.find_element(By.CLASS_NAME, "box2").text
                    duration = game_card.find_element(By.CLASS_NAME, "duration").text

                    print(f"    Gem {game_index}: {player_name} - {result_type} ({score1}-{score2}) - {duration}")

                    set_games.append((match_id, match_name, set_index, game_index, player_name, result_type, int(score1), int(score2), duration))

                except Exception as e:
                    print(f"  Gem {game_index}: [Greška] {e}")
                    valid_match = False
                    break

            # === VALIDACIJA SETA (SAMO JEDNOM!) ===
            if set_games:
                # Ispravno dohvaćanje score1 i score2
                last_score1 = set_games[-1][6]  # Ovo je score1
                last_score2 = set_games[-1][7]  # Ovo je score2

                # Pretvori u integer ako već nije
                try:
                    last_score1 = int(last_score1)
                    last_score2 = int(last_score2)
                except ValueError as e:
                    print(f"  ❌ Greška u pretvorbi rezultata u broj: {e}")
                    valid_match = False
                    break

                expected_games = last_score1 + last_score2
                actual_games = len(set_games)

                print(f"  → Očekivano: {expected_games}, stvarno: {actual_games}")

                # Provjera: broj gemova i netko mora imati 6 ili 7
                if expected_games != actual_games:
                    print(f"  ❌ Krivi broj gemova")
                    valid_match = False
                elif last_score1 not in (6, 7) and last_score2 not in (6, 7):
                    print(f"  ❌ Set nije završen — nitko nema 6 ili 7 gemova")
                    valid_match = False

            # dodaj set u globalnu listu SAMO ako je validan
            if valid_match:
                all_games.extend(set_games)

        # === FINALNA ODLUKA ===
        if valid_match:
            try:
                with conn.cursor() as cur:
                    cur.executemany("""
                        INSERT INTO match_scores(match_id, match_name, set_number, game_number, player_name, result_type, score1, score2, duration)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, all_games)

                conn.commit()
                print("\n✅ MATCH spremljen")

            except Exception as e:
                print(f"\n❌ Greška pri insertu: {e}")
                conn.rollback()
        else:
            print("\n❌ MATCH NIJE VALIDAN — ništa nije spremljeno")
            conn.rollback()

    except Exception as e:
        print("❌ Došlo je do greške u hijerarhiji:", e)

    finally:
        db.close()  # Zatvori konekciju na bazu
        driver.quit()


scrape_matchbeats()
