import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import configparser

def normalize_name(name):
    """
    Zamijeni hrvatske znakove u engleski ASCII ekvivalent i stavi velika slova.
    Š->S, Č->C, Ć->C, Ž->Z, Đ->DZ
    """
    if not name:
        return None

    translit_table = str.maketrans({
        "Š": "S", "š": "s",
        "Č": "C", "č": "c",
        "Ć": "C", "ć": "c",
        "Ž": "Z", "ž": "z",
        "Đ": "DZ", "đ": "dz"
    })

    return name.translate(translit_table).upper()

def adjust_odds(odds1, odds2, target_margin=0.02):
    # --- Pretvorba string -> float (sa zarezom u točku)
    try:
        odds1 = float(str(odds1).replace(",", "."))
        odds2 = float(str(odds2).replace(",", "."))
    except Exception as e:
        raise ValueError(f"Greška u pretvorbi kvota: {e}")
    
    # 1. Izračunaj trenutnu marginu
    current_margin = (1 / odds1 + 1 / odds2) - 1

    # 2. Izračunaj "fair" vjerojatnosti (bez margine)
    p1 = 1 / odds1
    p2 = 1 / odds2
    total_p = p1 + p2
    fair_p1 = p1 / total_p
    fair_p2 = p2 / total_p

    # 3. Dodaj ciljanu marginu (npr. 1%) ravnomjerno
    adj_p1 = fair_p1 * (1 + target_margin)
    adj_p2 = fair_p2 * (1 + target_margin)

    # 4. Normalizacija (da margina bude točno 1%)
    scale = (1 + target_margin) / (adj_p1 + adj_p2)
    adj_p1 *= scale
    adj_p2 *= scale

    # 5. Pretvori natrag u kvote
    new_odds1 = round(1 / adj_p1, 3)
    new_odds2 = round(1 / adj_p2, 3)

    return new_odds1, new_odds2, round(current_margin * 100, 2)

# === funkcija za spremanje u bazu ===
def save_match_to_db(match_id, player1, player2, rezultat1, rezultat2, kvota1, kvota2):
    config = configparser.ConfigParser()
    config.read("config.ini")  # ili path do tvoje .ini datoteke
    DB_FILE = config.get("database", "db_file")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO matches (match_id, player1_name, player2_name, result_player1, result_player2, odds_player1, odds_player2)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (match_id, player1, player2, rezultat1, rezultat2, kvota1, kvota2))

    conn.commit()
    conn.close()


def scrape_match_data():
    options = webdriver.ChromeOptions()
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--user-data-dir=/tmp/selenium")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    driver.switch_to.window(driver.current_window_handle)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(1)

    try:
        body = driver.find_element(By.TAG_NAME, "body")
        container = body.find_element(By.CLASS_NAME, "container")
        container_content = container.find_element(By.CLASS_NAME, "container__content")
        container_main = container_content.find_element(By.CLASS_NAME, "container__main")
        container_main_inner = container_main.find_element(By.CLASS_NAME, "container__mainInner")
        live_table_wrapper = container_main_inner.find_element(By.CLASS_NAME, "container__liveTableWrapper")
        live_table = live_table_wrapper.find_element(By.CLASS_NAME, "container__livetable")
        detail_inner = live_table.find_element(By.CLASS_NAME, "container__detailInner")

        # === Imena igrača ===
        duel_container = detail_inner.find_element(By.CLASS_NAME, "duelParticipant__container")
        duel = duel_container.find_element(By.CLASS_NAME, "duelParticipant")

        home_wrapper = duel.find_element(By.CSS_SELECTOR, ".duelParticipant__home .participant__participantNameWrapper a.participant__participantName")
        away_wrapper = duel.find_element(By.CSS_SELECTOR, ".duelParticipant__away .participant__participantNameWrapper a.participant__participantName")

        player1_full = home_wrapper.text.strip() if home_wrapper else None
        player2_full = away_wrapper.text.strip() if away_wrapper else None

        player1 = player1_full.split()[0].upper() if player1_full else None
        player2 = player2_full.split()[0].upper() if player2_full else None

        

        print("Home player name:", player1)
        print("Away player name:", player2)

        # === Rezultat ===
        score_element = duel.find_element(By.CLASS_NAME, "duelParticipant__score")
        match_info = score_element.find_element(By.CLASS_NAME, "detailScore__matchInfo")
        wrapper_score = match_info.find_element(By.CLASS_NAME, "detailScore__wrapper")
        spans = wrapper_score.find_elements(By.TAG_NAME, "span")

        rezultat1 = spans[0].text if len(spans) > 0 else None
        rezultat2 = spans[2].text if len(spans) > 2 else None

        print("Rezultat 1:", rezultat1)
        print("Rezultat 2:", rezultat2)

        # === Kvote ===
        outer_tab = detail_inner.find_element(By.CSS_SELECTOR, 'div[data-analytics-context="tab-match-summary"]')
        inner_tab = outer_tab.find_element(By.CSS_SELECTOR, 'div[data-analytics-context="tab-match-summary"]')
        section = inner_tab.find_element(By.CSS_SELECTOR, "section.loadable__section.complete")
        loadable_divs = section.find_elements(By.CSS_SELECTOR, "div.loadable.complete")
        second_loadable_div = loadable_divs[1]  # drugi po redu

        section_div = second_loadable_div.find_element(By.CSS_SELECTOR, "div.section.section--nmb")
        prematch_div = section_div.find_element(By.CSS_SELECTOR, ":scope > div.section.section__prematchOdds")
        last_div = prematch_div.find_element(By.CLASS_NAME, "odds")

        all_odds_info_divs = last_div.find_elements(By.CLASS_NAME, "wcl-oddsInfo_CqWpN")

        kvota1, kvota2 = None, None
        if len(all_odds_info_divs) >= 2:
            span1 = all_odds_info_divs[0].find_element(By.CSS_SELECTOR, "span.wcl-oddsValue_3e8Cq")
            span2 = all_odds_info_divs[1].find_element(By.CSS_SELECTOR, "span.wcl-oddsValue_3e8Cq")
            kvota1 = span1.text if span1 else None
            kvota2 = span2.text if span2 else None

        print("Kvota 1:", kvota1)
        print("Kvota 2:", kvota2)

        kvota1, kvota2, margin = adjust_odds(kvota1, kvota2)
        print(f"Adjusted Odds: Kvota 1: {kvota1}, Kvota 2: {kvota2}, Margin: {margin}%")

        # === Match ID ===
        player1_norm = normalize_name(player1.split()[0]) if player1_full else None
        player2_norm = normalize_name(player2.split()[0]) if player2_full else None

        match_id = f"{player1_norm[:7]}_{player2_norm[:7]}".replace(" ", "_")
        print("Match ID:", match_id)

        # === Spremi u bazu ===
        save_match_to_db(match_id, player1, player2, rezultat1, rezultat2, kvota1, kvota2)

    except Exception as e:
        print("Greška u dohvaćanju podataka:", e)

    finally:
        driver.quit()


scrape_match_data()
