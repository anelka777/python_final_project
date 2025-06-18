import sqlite3
import os

def connect_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"Connection error: {e}")
        return None

def print_results(rows, headers):
    if not rows:
        print("No results found.")
        return

    print("\t".join(headers))
    print("-" * 60)
    for row in rows:
        print("\t".join(str(item) if item is not None else "" for item in row))

def search_by_player(conn, player_name):
    print(f"\n--- Hitting Stats for player '{player_name}' ---")
    query = """
        SELECT h.Year, h.Event, h.Player, h.Team, h.Value, e.Description
        FROM hitting_stats h
        LEFT JOIN events e ON h.Event = e.Event
        WHERE h.Player LIKE ?
        ORDER BY h.Year
    """
    try:
        cur = conn.cursor()
        cur.execute(query, (f"%{player_name}%",))
        rows = cur.fetchall()
        print_results(rows, ["Year", "Event", "Player", "Team", "Value", "Description"])
    except sqlite3.Error as e:
        print(f"Query error: {e}")

    print(f"\n--- Pitching Stats for player '{player_name}' ---")
    query = """
        SELECT p.Year, p.Event, p.Player, p.Team, p.Value, e.Description
        FROM pitching_stats p
        LEFT JOIN events e ON p.Event = e.Event
        WHERE p.Player LIKE ?
        ORDER BY p.Year
    """
    try:
        cur.execute(query, (f"%{player_name}%",))
        rows = cur.fetchall()
        print_results(rows, ["Year", "Event", "Player", "Team", "Value", "Description"])
    except sqlite3.Error as e:
        print(f"Query error: {e}")

def search_by_year(conn, year):
    print(f"\n--- Hitting Stats for year {year} ---")
    query = """
        SELECT h.Year, h.Event, h.Player, h.Team, h.Value, e.Description
        FROM hitting_stats h
        LEFT JOIN events e ON h.Event = e.Event
        WHERE h.Year = ?
        ORDER BY h.Player
    """
    try:
        cur = conn.cursor()
        cur.execute(query, (year,))
        rows = cur.fetchall()
        print_results(rows, ["Year", "Event", "Player", "Team", "Value", "Description"])
    except sqlite3.Error as e:
        print(f"Query error: {e}")

    print(f"\n--- Pitching Stats for year {year} ---")
    query = """
        SELECT p.Year, p.Event, p.Player, p.Team, p.Value, e.Description
        FROM pitching_stats p
        LEFT JOIN events e ON p.Event = e.Event
        WHERE p.Year = ?
        ORDER BY p.Player
    """
    try:
        cur.execute(query, (year,))
        rows = cur.fetchall()
        print_results(rows, ["Year", "Event", "Player", "Team", "Value", "Description"])
    except sqlite3.Error as e:
        print(f"Query error: {e}")

def search_by_event(conn, event):
    print(f"\n--- Hitting Stats for event '{event}' ---")
    query = """
        SELECT h.Year, h.Event, h.Player, h.Team, h.Value, e.Description
        FROM hitting_stats h
        LEFT JOIN events e ON h.Event = e.Event
        WHERE h.Event LIKE ?
        ORDER BY h.Year, h.Player
    """
    try:
        cur = conn.cursor()
        cur.execute(query, (f"%{event}%",))
        rows = cur.fetchall()
        print_results(rows, ["Year", "Event", "Player", "Team", "Value", "Description"])
    except sqlite3.Error as e:
        print(f"Query error: {e}")

    print(f"\n--- Pitching Stats for event '{event}' ---")
    query = """
        SELECT p.Year, p.Event, p.Player, p.Team, p.Value, e.Description
        FROM pitching_stats p
        LEFT JOIN events e ON p.Event = e.Event
        WHERE p.Event LIKE ?
        ORDER BY p.Year, p.Player
    """
    try:
        cur.execute(query, (f"%{event}%",))
        rows = cur.fetchall()
        print_results(rows, ["Year", "Event", "Player", "Team", "Value", "Description"])
    except sqlite3.Error as e:
        print(f"Query error: {e}")

def main():
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "mlb_stats.db")
    db_path = os.path.abspath(db_path)

    conn = connect_db(db_path)
    if not conn:
        return

    while True:
        print("\n📊 MLB Stats CLI Menu")
        print("1. Search by player name")
        print("2. Search by year")
        print("3. Search by event")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            name = input("Enter player name: ").strip()
            if name:
                search_by_player(conn, name)
            else:
                print("Player name cannot be empty.")
        elif choice == "2":
            year = input("Enter year (e.g., 2012): ").strip()
            if year.isdigit():
                search_by_year(conn, int(year))
            else:
                print("Invalid year.")
        elif choice == "3":
            event = input("Enter event (e.g., Home Runs, ERA): ").strip()
            if event:
                search_by_event(conn, event)
            else:
                print("Event cannot be empty.")
        elif choice == "0":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Try again.")

    conn.close()

if __name__ == "__main__":
    main()

