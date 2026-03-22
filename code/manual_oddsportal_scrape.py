import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_tournament_info(driver):
    """
    Izvlači naziv turnira i podlogu iz H1 naslova.
    """
    try:
        # Čekamo do 5 sekundi da se H1 pojavi
        wait = WebDriverWait(driver, 5)
        h1_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sport-country-tournament h1")))
        full_text = h1_element.get_attribute("innerText").strip()
        clean_name = full_text.split(" Results")[0].strip()
        return clean_name
    except Exception:
        return "Nepoznat Turnir"

def scrape_tournament_data(driver):
    results = []
    
    try:
        # Pronalazimo sve redove utakmica
        rows = driver.find_elements(By.CSS_SELECTOR, "[data-testid='game-row']")
        
        for index, row in enumerate(rows):
            is_debug = (index == 0)
            current_date = "N/A"

            try:
                # --- PUTANJA DO DATUMA ---
                # XPath koji ide na dedu (event-row) i traži njegovog brata (secondary-header)
                xpath_date = "./parent::div/parent::div/preceding-sibling::div[@data-testid='secondary-header'][1]//div[@data-testid='date-header']/div"
                
                date_elements = row.find_elements(By.XPATH, xpath_date)
                
                if date_elements:
                    current_date = date_elements[0].get_attribute("textContent").strip()
                else:
                    # Fallback: Tražimo bilo koji prethodni header u dokumentu
                    xpath_fallback = "./preceding::div[@data-testid='secondary-header'][1]//div[@data-testid='date-header']/div"
                    fallback_elements = row.find_elements(By.XPATH, xpath_fallback)
                    if fallback_elements:
                        current_date = fallback_elements[0].get_attribute("textContent").strip()

                # --- PODACI O IGRAČIMA ---
                name_elements = row.find_elements(By.CLASS_NAME, "participant-name")
                if len(name_elements) < 2: 
                    continue
                
                # Čistimo imena od brojeva setova na kraju (npr. "Fucsovics M.2" -> "Fucsovics M.")
                p1 = re.sub(r'\d+$', '', name_elements[0].get_attribute("textContent")).strip()
                p2 = re.sub(r'\d+$', '', name_elements[1].get_attribute("textContent")).strip()

                # --- REZULTAT ---
                participants_div = row.find_element(By.CSS_SELECTOR, "[data-testid='event-participants']")
                score_match = re.search(r'(\d[\s]*[–\-:][\s]*\d)', participants_div.get_attribute("textContent"))
                score = score_match.group(1).replace(" ", "") if score_match else "-"

                # --- KVOTE ---
                odds_elements = row.find_elements(By.CSS_SELECTOR, "div.flex.items-center.justify-center.font-bold")
                clean_odds = [o.text.strip() for o in odds_elements if re.match(r'^\d+\.\d+$', o.text.strip())]
                o1 = clean_odds[0] if len(clean_odds) > 0 else "-"
                o2 = clean_odds[1] if len(clean_odds) > 1 else "-"

                # Filtriranje: Dodajemo samo ako postoje kvote (eliminacija duplikata bez kvota)
                if o1 != "-" or o2 != "-":
                    results.append({
                        "date": current_date,
                        "p1": p1,
                        "p2": p2,
                        "score": score,
                        "o1": o1,
                        "o2": o2
                    })
            except Exception:
                continue
                
        return results
    except Exception as e:
        print(f"❌ Greška pri scrapingu: {e}")
        return []

def run_test():
    options = webdriver.ChromeOptions()
    options.debugger_address = "127.0.0.1:9222"
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # 1. Prikupljanje zaglavlja turnira
        tournament = get_tournament_info(driver)
        surface_match = re.search(r'\((.*?)\)', tournament)
        surface = surface_match.group(1) if surface_match else "N/A"

        print("\n" + "="*125)
        print(f"🔍 POKREĆEM SCRAPE PODATAKA...")
        print("="*125)
        print(f"🏆 TURNIR: {tournament}")
        print(f"📍 PODLOGA: {surface}")
        print("-" * 125)
        print(f"📡 Prikupljam listu svih mečeva (filtriram duplikate)...")
        
        # 2. Glavni scrape
        match_list = scrape_tournament_data(driver)
        
        print(f"✅ USPJEH! Pronađeno unikatnih mečeva: {len(match_list)}")
        print("-" * 125)
        
        # 3. Formatirani ispis tablice
        print(f"{'#':<4} {'DATUM / FAZA':<25} {'IGRAČ 1':<25} {'IGRAČ 2':<25} {'REZ':<8} {'K1':<7} {'K2':<7}")
        print("-" * 125)

        for i, m in enumerate(match_list, 1):
            # Skraćujemo "Qualification" u ispisu radi preglednosti
            display_date = m['date'].replace("Qualification - ", "Quali: ")
            
            print(f"[{i:02d}] {display_date:<25} {m['p1']:<25} vs  {m['p2']:<25} | {m['score']:^6} | {m['o1']:<6} | {m['o2']:<6}")

        print("="*125)
        print(f"🏁 ZAVRŠENO. Ukupno obrađeno: {len(match_list)} mečeva.")
        print("="*125)

    except Exception as e:
        print(f"❌ Kritična greška: {e}")

if __name__ == "__main__":
    run_test()