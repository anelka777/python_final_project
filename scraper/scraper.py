from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import os

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
    # chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)

def parse_player_review(driver, url, target_year):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
    results = []

    for tbody in driver.find_elements(By.TAG_NAME, "tbody"):
        header_tds = tbody.find_elements(By.CSS_SELECTOR, "td.header[colspan='5']")
        if not header_tds:
            continue
        h2s = header_tds[0].find_elements(By.TAG_NAME, "h2")
        if not h2s:
            continue
        h2_text = h2s[0].text.strip()
        if str(target_year) in h2_text and "American League Player Review" in h2_text:
            for row in tbody.find_elements(By.TAG_NAME, "tr"):
                if row.find_elements(By.CSS_SELECTOR, "td.banner, td.headerBlue, td.header"):
                    continue
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 4:
                    category = cells[0].text.strip()
                    player = cells[1].text.strip()
                    team = cells[2].text.strip()
                    value = cells[3].text.strip()
                    if category and player and team and value:
                        results.append([target_year, category, player, team, value])
            break
    return results

def parse_pitcher_review(driver, url, target_year):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
    results = []

    for tbody in driver.find_elements(By.TAG_NAME, "tbody"):
        header_tds = tbody.find_elements(By.CSS_SELECTOR, "td.header[colspan='5']")
        if not header_tds:
            continue
        h2s = header_tds[0].find_elements(By.TAG_NAME, "h2")
        if not h2s:
            continue
        h2_text = h2s[0].text.strip()
        if str(target_year) in h2_text and "American League Pitcher Review" in h2_text:
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            current_category = None
            current_value = None
            for row in rows:
                if row.find_elements(By.CSS_SELECTOR, "td.banner, td.headerBlue, td.header"):
                    continue
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    continue
                try:
                    if cells[0].get_attribute("class").startswith("datacolBlue"):
                        current_category = cells[0].text.strip()
                        player = cells[1].text.strip()
                        team = cells[2].text.strip()
                        current_value = cells[3].text.strip()
                    else:
                        player = cells[0].text.strip()
                        team = cells[1].text.strip()
                    results.append([target_year, current_category, player, team, current_value])
                except Exception as e:
                    print(f"Row parsing error: {e}")
            break
    return results

def main():
    os.makedirs("../data", exist_ok=True)
    base_url = "https://www.baseball-almanac.com/yearly/yr{year}a.shtml"
    all_player_data = []
    all_pitcher_data = []

    driver = create_driver()

    for year in range(1901, 2025):
        url = base_url.format(year=year)
        print(f"\nParsing year {year}...")
        try:
            player_data = parse_player_review(driver, url, year)
            if player_data:
                print(f"  ✅ Player stats found for {year}: {len(player_data)} rows")
                all_player_data.extend(player_data)
            else:
                print(f"  ⚠️ No player data for {year}")

            pitcher_data = parse_pitcher_review(driver, url, year)
            if pitcher_data:
                print(f"  ✅ Pitcher stats found for {year}: {len(pitcher_data)} rows")
                all_pitcher_data.extend(pitcher_data)
            else:
                print(f"  ⚠️ No pitcher data for {year}")
        except Exception as e:
            print(f"  ❌ Error processing {year}: {e}")
        time.sleep(2)

    driver.quit()

    with open("../data/american_league_stats_1901_2024.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Year", "Event", "Player", "Team", "Value"])
        writer.writerows(all_player_data)

    with open("../data/american_league_pitcher_stats_1901_2024.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Year", "Event", "Player", "Team", "Value"])
        writer.writerows(all_pitcher_data)

    print("\n✅ All data saved successfully!")

if __name__ == "__main__":
    main()
