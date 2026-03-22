from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def normalize_dash(text):
    if not text:
        return ""
    return text.replace('‑', '-').replace('–', '-').replace('—', '-').replace(' ', ' ').strip()

def parse_score(score_str):
    score_str = normalize_dash(score_str)
    parts = score_str.split('-')
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return "", ""

def is_empty_row(row):
    tds = row.find_elements(By.TAG_NAME, "td")
    for td in tds:
        text = td.get_attribute('innerHTML').strip()
        if text != "" and text != "&nbsp;":
            return False
    return True

def extract_gemovi(match_suffix):
    url = "https://www.tennisabstract.com/charting/" + match_suffix

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).text

    player_x, player_y = title.split('vs')
    player_x = player_x.split(':')[-1].strip()
    player_y = player_y.strip()

    print("Igraju:", player_x, "vs", player_y)

    set_score = {player_x: 0, player_y: 0}
    gem_score = {player_x: 0, player_y: 0}
    tie_break = False
    last_line = False

    wait.until(EC.element_to_be_clickable((By.ID, "pointlog"))).click()
    time.sleep(1)

    rows = driver.find_element(By.ID, "forecast").find_elements(By.TAG_NAME, "tr")
    rows = [row for row in rows if not is_empty_row(row)]

    for i in range(len(rows) - 1):
        tds_now = rows[i].find_elements(By.TAG_NAME, "td")
        tds_next = rows[i + 1].find_elements(By.TAG_NAME, "td")

        if len(tds_now) < 4 or len(tds_next) < 4:
            continue

        server_now = normalize_dash(tds_now[0].text)
        game_score_now = normalize_dash(tds_now[2].text)
        point_score_now = normalize_dash(tds_now[3].text)
        game_score_next = normalize_dash(tds_next[2].text)

        gs_now = parse_score(game_score_now)
        gs_next = parse_score(game_score_next)

        if i == len(rows) - 2:
            last_line = True

        # Provjera početka tie-breaka
        if gem_score[player_x] == 6 and gem_score[player_y] == 6 and not tie_break:
            tie_break = True

        # Regularan završetak gema (izvan tie-breaka)
        if gs_now != gs_next and not tie_break:
            point1, point2 = parse_score(point_score_now)
            gem_winner = None
            status = "unknown"

            if point1 in ['AD', '40'] and point2 not in ['AD']:
                gem_winner = server_now
                gem_score[server_now] += 1
                status = "hold"
            elif point2 in ['AD', '40'] and point1 not in ['AD']:
                opponent = player_y if server_now == player_x else player_x
                gem_winner = opponent
                gem_score[opponent] += 1
                status = "break"
            else:
                continue

            print(f"Set score {set_score}, Gem score {gem_score} - Server: {server_now}, Osvojio: {gem_winner}, Status: {status}")

            # Provjera završetka seta
            g1 = gem_score[player_x]
            g2 = gem_score[player_y]
            if (g1 == 6 and g2 <= 4) or (g2 == 6 and g1 <= 4) or (g1 == 7 and g2 <= 5) or (g2 == 7 and g1 <= 5):
                if g1 > g2:
                    set_score[player_x] += 1
                else:
                    set_score[player_y] += 1
                    
                print(f" ")
                print(f"Set završen. Rezultat u setovima: {set_score}")
                print(f" ")
                gem_score[player_x] = 0
                gem_score[player_y] = 0

        # Tie-break završetak
        if tie_break:
            tds_bef = rows[i - 1].find_elements(By.TAG_NAME, "td")
            server_bef = normalize_dash(tds_bef[0].text)
            point_score_bef = normalize_dash(tds_bef[3].text)

            if game_score_now == "0-0":
                tie_break = False
                point1, point2 = parse_score(point_score_bef)
                gem_winner = None
                status = "tie-break"

                if point1.isdigit() and point2.isdigit():
                    point1 = int(point1)
                    point2 = int(point2)
                    if point1 > point2:
                        gem_winner = server_bef
                    else:
                        gem_winner = player_y if server_bef == player_x else player_x
                else:
                    continue

                gem_score[gem_winner] += 1
                print(f"Set score {set_score}, Gem score {gem_score}, Status: {status}")
                set_score[gem_winner] += 1
                print(f" ")
                print(f"Set završen. Rezultat u setovima: {set_score}")
                print(f" ")
                gem_score[player_x] = 0
                gem_score[player_y] = 0

        if last_line:
            point1, point2 = parse_score(point_score_now)
            gem_winner = None
            status = "unknown"

            if point1 in ['AD', '40'] and point2 not in ['AD']:
                gem_winner = server_now
                gem_score[gem_winner] += 1
                status = "hold"
                print(f"Set score {set_score}, Gem score {gem_score} - Server: {server_now}, Osvojio: {gem_winner}, Status: {status}")
                set_score[gem_winner] += 1
                print(f" ")
                print(f"Set završen. Rezultat u setovima: {set_score}")
                
            elif point2 in ['AD', '40'] and point1 not in ['AD']:
                opponent = player_y if server_now == player_x else player_x
                gem_winner = opponent
                status = "break"
                gem_score[gem_winner] += 1
                print(f"Set score {set_score}, Gem score {gem_score} - Server: {server_now}, Osvojio: {gem_winner}, Status: {status}")
                set_score[gem_winner] += 1
                print(f" ")
                print(f"Set završen. Rezultat u setovima: {set_score}")
            elif point1 > point2:
                gem_winner = server_now
                gem_score[gem_winner] += 1
                status = "tie-break"
                print(f"Set score {set_score}, Gem score {gem_score}, Status: {status}")
                set_score[gem_winner] += 1
                print(f" ")
                print(f"Set završen. Rezultat u setovima: {set_score}")
            elif point2 > point1:
                opponent = player_y if server_now == player_x else player_x
                gem_winner = opponent
                gem_score[gem_winner] += 1
                status = "tie-break"
                print(f"Set score {set_score}, Gem score {gem_score}, Status: {status}")
                set_score[gem_winner] += 1
                print(f" ")
                print(f"Set završen. Rezultat u setovima: {set_score}")
                


    driver.quit()

# Primjer poziva:
extract_gemovi("20250628-M-Mallorca-F-Tallon_Griekspoor-Corentin_Moutet.html")

# TENNIS ABSTRACT SCRAPE