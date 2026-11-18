import re
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "applications.db"
STATUSES = ["Received", "Documents Needed", "Submitted to Government", "Decision Issued"]
COUNTRIES = ["Schengen", "UAE", "Japan", "UK", "USA", "Singapore", "Thailand", "Australia"]
NAMES = ["Aarav", "Diya", "Rohan", "Isha", "Kabir", "Meera", "Arjun", "Sana", "Vihaan", "Ananya",
         "Rahul", "Priya", "Aditya", "Neha", "Karan", "Pooja", "Yash", "Riya", "Dev", "Tara",
         "Nikhil", "Kavya", "Sameer", "Zoya", "Manav", "Ira", "Harsh", "Naina", "Veer", "Anika"]


def seed():
    """Create 30 pretend applications. Same data every time."""
    rnd = random.Random(42)
    con = sqlite3.connect(DB_PATH)
    con.execute("DROP TABLE IF EXISTS applications")
    con.execute("""CREATE TABLE applications (
        application_id TEXT PRIMARY KEY, traveller_name TEXT, country TEXT,
        status TEXT, submitted_on TEXT, note TEXT)""")
    for i, name in enumerate(NAMES):
        status = rnd.choice(STATUSES)
        if status == "Documents Needed":
            note = "Bank statement for the last 6 months is unclear"
        elif status == "Decision Issued":
            note = rnd.choice(["Approved", "Refused"])
        else:
            note = ""
        when = (date(2026, 11, 1) - timedelta(days=rnd.randint(0, 20))).isoformat()
        con.execute("INSERT INTO applications VALUES (?,?,?,?,?,?)",
                    (f"VL-{100001 + i}", name, rnd.choice(COUNTRIES), status, when, note))
    con.commit()
    con.close()
    print("Seeded 30 applications (VL-100001 to VL-100030).")


def normalise_id(raw):
    """Turn 'vl 100007' or 'VL-100007' into 'VL-100007'. Returns None if it has no 6 digits."""
    digits = re.sub(r"\D", "", raw)
    return f"VL-{digits}" if len(digits) == 6 else None


def get_application(application_id):
    clean = normalise_id(application_id)
    if clean is None:
        return {"found": False, "reason": "That is not a valid reference. It should look like VL followed by six digits."}
    con = sqlite3.connect(DB_PATH)
    row = con.execute("SELECT application_id, country, status, submitted_on, note "
                      "FROM applications WHERE application_id = ?", (clean,)).fetchone()
    con.close()
    if row is None:
        return {"found": False, "reason": f"No application found with reference {clean}."}
    return {"found": True, "application_id": row[0], "country": row[1],
            "status": row[2], "submitted_on": row[3], "note": row[4]}


if __name__ == "__main__":
    seed()