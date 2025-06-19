import sqlite3

def extract_unique_events(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Unique events from hitting_stats
    cur.execute("SELECT DISTINCT Event FROM hitting_stats")
    hitting_events = {row[0] for row in cur.fetchall()}

    # Unique events from pitching_stats
    cur.execute("SELECT DISTINCT Event FROM pitching_stats")
    pitching_events = {row[0] for row in cur.fetchall()}

    # Combine and sort
    all_events = sorted(hitting_events.union(pitching_events))

    conn.close()
    return all_events

# Run script
if __name__ == "__main__":
    db_path = "../data/mlb_stats.db"
    events = extract_unique_events(db_path)
    print("\n📋 Unique Events in the Database:")
    for e in events:
        print("-", e)
