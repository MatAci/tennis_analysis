import time
import re
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from db_connection import DatabaseConnection

def parse_tennis_stat(stat_string):
    """Razbija '19/32 (59%)' na (19, 32, 59.0) ili '155' na (155, None, None)"""
    if not stat_string or stat_string == "-":
        return None, None, None
    
    # Traži format X/Y (Z%)
    match = re.search(r'(\d+)/(\d+)\s*\((\d+)%\)', stat_string)
    if match:
        return int(match.group(1)), int(match.group(2)), float(match.group(3))
    
    # Ako je samo jedan broj (npr. Aces ili Rating)
    only_digit = re.search(r'^\d+$', stat_string.strip())
    if only_digit:
        return int(only_digit.group(0)), None, None
        
    return None, None, None

def get_stats_player_names(driver):
    """
    Dohvaća imena igrača iz Stats (MatchStats) dijela hijerarhije.
    Prati putanju: content-wrapper -> MatchStats -> RGMatchStats -> StatsHeaderWrapper
    """
    try:
        # 1. Osnovna navigacija (zajednička do content-wrappera)
        body = driver.find_element(By.TAG_NAME, "body")
        container = body.find_element(By.CLASS_NAME, "container")
        wrapper = container.find_element(By.CLASS_NAME, "wrapper")
        atp_layout = wrapper.find_element(By.CLASS_NAME, "atp_layout")
        layout_container = atp_layout.find_element(By.CLASS_NAME, "atp_layout-container")
        stats_section = layout_container.find_element(By.CLASS_NAME, "stats-vs-stats--external")
        infosys_center = stats_section.find_element(By.ID, "InfosysMatchCenter")
        match_center = infosys_center.find_element(By.CLASS_NAME, "match-center")
        content_wrapper = match_center.find_element(By.CLASS_NAME, "content-wrapper")

        # 2. Ulazak u MatchStats i RGMatchStats
        match_stats = content_wrapper.find_element(By.ID, "MatchStats")
        rg_match_stats = match_stats.find_element(By.CLASS_NAME, "RGMatchStats")
        
        # 3. Dolazak do headera s igračima
        header_wrapper = rg_match_stats.find_element(By.CLASS_NAME, "StatsHeaderWrapper")
        header = header_wrapper.find_element(By.CLASS_NAME, "header")
        
        player_names = []
        
        # 4. Prolazimo kroz team1 i team2 (lijeva i desna strana)
        teams = ["team1", "team2"]
        for team in teams:
            team_div = header.find_element(By.CLASS_NAME, team)
            player_div = team_div.find_element(By.CLASS_NAME, "player")
            
            # Tražimo span s imenom i unutar njega 'a' tag
            name_span = player_div.find_element(By.CLASS_NAME, "name")
            anchor = name_span.find_element(By.CLASS_NAME, "player-details-anchor")
            
            # Izvlačimo tekst imena
            full_name = anchor.text.strip()
            
            # Čišćenje imena (ako je npr. "N. DJOKOVIC" -> "DJOKOVIC")
            if "." in full_name:
                parts = full_name.split(".")
                full_name = parts[-1].strip().upper()
            else:
                full_name = full_name.upper()
                
            player_names.append(full_name)

        return player_names # Vraća [PLAYER1, PLAYER2]
        
    except Exception as e:
        print("Greška u dohvaćanju imena igrača iz Stats headera:", e)
        return [None, None]

def get_all_stats_sections(driver):
    """
    Navigira kroz MatchStats i vraća listu sekcija: [service_section, return_section, points_section].
    Svaka sekcija je 'stat-section' element unutar svog 'topStatsWrapper'-a.
    """
    try:
        # 1. Standardna početna putanja do MatchStats
        body = driver.find_element(By.TAG_NAME, "body")
        container = body.find_element(By.CLASS_NAME, "container")
        wrapper = container.find_element(By.CLASS_NAME, "wrapper")
        atp_layout = wrapper.find_element(By.CLASS_NAME, "atp_layout")
        layout_container = atp_layout.find_element(By.CLASS_NAME, "atp_layout-container")
        stats_section_external = layout_container.find_element(By.CLASS_NAME, "stats-vs-stats--external")
        infosys_center = stats_section_external.find_element(By.ID, "InfosysMatchCenter")
        match_center = infosys_center.find_element(By.CLASS_NAME, "match-center")
        content_wrapper = match_center.find_element(By.CLASS_NAME, "content-wrapper")

        # 2. Ulazak u statistike
        match_stats = content_wrapper.find_element(By.ID, "MatchStats")
        rg_match_stats = match_stats.find_element(By.CLASS_NAME, "RGMatchStats")

        # --- DOHVAĆANJE STATISTIČKIH SEKCIJA ---
        # Dohvaćamo sve topStatsWrappere (Service, Return, Points)
        all_top_wrappers = rg_match_stats.find_elements(By.CLASS_NAME, "topStatsWrapper")
        
        # Lista u koju ćemo spremiti tri stat-section-a
        sections_list = []

        for wrapper in all_top_wrappers:
            try:
                # Iz svakog wrappera izvlačimo njegovu stat-section
                sec = wrapper.find_element(By.CLASS_NAME, "stat-section")
                sections_list.append(sec)
            except:
                continue

        # Vraća listu (npr. duljine 3)
        return sections_list

    except Exception as e:
        print(f"❌ Greška u navigaciji do statistika: {e}")
        return []

def parse_set_number(driver):
    """Izvlači 'Set 1' i vraća 1, ili 'Match Summary' i vraća 0."""
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        container = body.find_element(By.CLASS_NAME, "container")
        wrapper = container.find_element(By.CLASS_NAME, "wrapper")
        atp_layout = wrapper.find_element(By.CLASS_NAME, "atp_layout")
        layout_container = atp_layout.find_element(By.CLASS_NAME, "atp_layout-container")
        stats_section_external = layout_container.find_element(By.CLASS_NAME, "stats-vs-stats--external")
        infosys_center = stats_section_external.find_element(By.ID, "InfosysMatchCenter")
        match_center = infosys_center.find_element(By.CLASS_NAME, "match-center")
        content_wrapper = match_center.find_element(By.CLASS_NAME, "content-wrapper")

        match_stats = content_wrapper.find_element(By.ID, "MatchStats")
        rg_match_stats = match_stats.find_element(By.CLASS_NAME, "RGMatchStats")
        dd_label = rg_match_stats.find_element(By.CLASS_NAME, "dd-label")
        set_text = dd_label.get_attribute("innerText").strip()

        if "Set" in set_text:
            return int(re.search(r'\d+', set_text).group())
        return 0 # Match Summary ili Overall
    except:
        return 0

def save_to_database(conn, schema, match_url, p1_name, p2_name, all_sections, set_num):
    """
    Dinamički sprema podatke za oba igrača prolazeći kroz sve sekcije.
    Sada koristi točna imena kolona iz baze!
    """
    # Mapiranje: "single" za jedan broj, "full" za tuple od 3 kolone (won/in, total/facing, pct)
    tables_config = {
        0: { # SERVICE STATS
            "table": "match_service_stats",
            "columns": [
                ("single", "serve_rating"),
                ("single", "aces"),
                ("single", "double_faults"),
                ("full", ("first_serve_in", "first_serve_total", "first_serve_pct")),
                ("full", ("first_serve_points_won", "first_serve_points_total", "first_serve_points_pct")),
                ("full", ("second_serve_points_won", "second_serve_points_total", "second_serve_points_pct")),
                ("full", ("break_points_saved", "break_points_facing", "break_points_saved_pct")),
                ("single", "service_games_played")
            ]
        },
        1: { # RETURN STATS
            "table": "match_return_stats",
            "columns": [
                ("single", "return_rating"),
                ("full", ("first_return_won", "first_return_total", "first_return_pct")),
                ("full", ("second_return_won", "second_return_total", "second_return_pct")),
                ("full", ("bp_converted", "bp_opportunities", "bp_converted_pct")),
                ("single", "return_games_played")
            ]
        },
        2: { # POINT STATS
            "table": "match_point_stats",
            "columns": [
                ("full", ("net_points_won", "net_points_total", "net_points_pct")),
                ("single", "winners"),
                ("single", "unforced_errors"),
                ("full", ("service_points_won", "service_points_total", "service_points_pct")),
                ("full", ("return_points_won", "return_points_total", "return_points_pct")),
                ("full", ("total_points_won", "total_points_total", "total_points_pct"))
            ]
        }
    }

    with conn.cursor() as cur:
        cur.execute(f"SET search_path TO {schema};")
        
        for sec_idx, section in enumerate(all_sections):
            if sec_idx not in tables_config:
                continue
            
            config = tables_config[sec_idx]
            tiles = section.find_elements(By.CLASS_NAME, "statTileWrapper")
            
            extracted_rows = []
            for tile in tiles:
                try:
                    v1 = tile.find_element(By.CSS_SELECTOR, "div[class*='player1'][class*='label']").get_attribute("textContent").strip()
                    v2 = tile.find_element(By.CSS_SELECTOR, "div[class*='player2'][class*='label']").get_attribute("textContent").strip()
                    extracted_rows.append((v1, v2))
                except Exception:
                    continue

            for p_idx, p_name in enumerate([p1_name, p2_name]):
                insert_dict = {
                    "match_url": match_url,
                    "player_name": p_name,
                    "set_number": set_num
                }

                # Uparivanje
                for row_idx, (col_type, col_names) in enumerate(config["columns"]):
                    if row_idx >= len(extracted_rows):
                        break
                    
                    val_str = extracted_rows[row_idx][p_idx]
                    won, total, pct = parse_tennis_stat(val_str)

                    if col_type == "full":
                        col_w, col_t, col_p = col_names
                        insert_dict[col_w] = won
                        insert_dict[col_t] = total
                        insert_dict[col_p] = pct
                    else:
                        insert_dict[col_names] = won

                columns = list(insert_dict.keys())
                values = list(insert_dict.values())
                
                query = f"""
                    INSERT INTO {config['table']} ({', '.join(columns)}) 
                    VALUES ({', '.join(['%s'] * len(values))})
                """
                
                print(f"\n🚀 Pripremam upis u tablicu: {config['table']} (Igrač: {p_name})")
                
                try:
                    cur.execute(query, values)
                    print(f"   ✅ Uspješno izvršeno!")
                except Exception as db_err:
                    print(f"   ❌ Greška pri upisu u bazu: {db_err}")
                    # ROLLBACK VRLO BITAN - ako jedan upis padne, otključava bazu za sljedeći!
                    conn.rollback() 

        # Ako je sve prošlo ok, zapiši u bazu trajno
        conn.commit()
        print("\n🏁 Commit u bazu je završen.")

def scrape_stats():
    # === Inicijalizacija Drivera ===
    options = webdriver.ChromeOptions()
    options.debugger_address = "127.0.0.1:9222"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    driver.switch_to.window(driver.current_window_handle)
    wait.until(EC.presence_of_element_located((By.ID, "MatchStats")))
    time.sleep(2)

    # === DOHVAĆANJE URL-a ===
    match_url = driver.current_url

    # === Konfiguracija i Baza ===
    config = configparser.ConfigParser()
    config.read("config.ini")
    schema = config.get("postgresql", "schema")

    db = DatabaseConnection()
    conn = db.connect()

    try:
        with conn.cursor() as cur:
            cur.execute(f"SET search_path TO {schema};")

        # === Dohvaćanje elemenata i imena ===
        #set_wrappers = get_set_wrappers(driver)
        player1_name, player2_name = get_stats_player_names(driver)
        print("Player 1:", player1_name)
        print("Player 2:", player2_name)

        all_sections = get_all_stats_sections(driver)

        for section in all_sections:
            tiles = section.find_elements(By.CLASS_NAME, "statTileWrapper")

            for tile in tiles:
                              
                p1_val = tile.find_element(By.CSS_SELECTOR, "div[class*='player1'][class*='label']").get_attribute("textContent").strip()
                p2_val = tile.find_element(By.CSS_SELECTOR, "div[class*='player2'][class*='label']").get_attribute("textContent").strip()

                print(f"{p1_val} vs {p2_val} ")
            
            print("---")

        if all_sections:
            save_to_database(conn, schema, match_url, player1_name, player2_name, all_sections, parse_set_number(driver))
        else:
            print("⚠️ Nisu pronađene statističke sekcije.")

    
    

    except Exception as e:
        print("❌ Došlo je do greške u hijerarhiji:", e)
    finally:
        db.close()
        driver.quit()

if __name__ == "__main__":
    scrape_stats()