from db import get_connection
import re

def clean(x):
    if x is None:
        return ""
    return x.strip()

def normalize_ssn(ssn):
    """
    Remove all non-digit characters from the SSN string.
    Example: '123-45-6789' -> '123456789'
    """
    ssn = clean(ssn)
    return re.sub(r"\D", "", ssn)  # keep only digits

def make_card_id():
    """
    Generate the next Card_id in the format ID000001, ID000002, ...
    based on the current max Card_id in BORROWER.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT MAX(Card_id) FROM BORROWER")
        row = cur.fetchone()
        max_id = row[0] if row else None

        if max_id is None:
            return "ID000001"

        try:
            num = int(max_id[2:])  # remove "ID"
        except Exception:
            num = 0

        num += 1
        new_id = "ID" + str(num).zfill(6)
        return new_id

    finally:
        if conn is not None:
            conn.close()

def add_borrower(name, ssn, address, phone=None):
    """
    Adds a new borrower to the BORROWER table.

    BORROWER(
        Card_id  TEXT PRIMARY KEY,
        Ssn      TEXT UNIQUE NOT NULL,
        Bname    TEXT NOT NULL,
        Address  TEXT NOT NULL,
        Phone    TEXT NOT NULL
    )
    """
    name = clean(name)
    ssn = normalize_ssn(ssn)
    address = clean(address)
    phone = clean(phone)

    # Required fields
    if name == "" or ssn == "" or address == "":
        return {
            "success": False,
            "message": "Name, SSN, and Address are required."
        }

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Check if a borrower with this SSN already exists
        cur.execute("SELECT Card_id FROM BORROWER WHERE Ssn = ?", (ssn,))
        row = cur.fetchone()

        if row is not None:
            return {
                "success": False,
                "message": "A borrower with this SSN already exists.",
                "card_id": row[0]
            }

        # Generate new card ID
        card_id = make_card_id()

        # Insert new borrower
        insert_sql = """
            INSERT INTO BORROWER (Card_id, Bname, Address, Phone, Ssn)
            VALUES (?, ?, ?, ?, ?)
        """
        cur.execute(insert_sql, (card_id, name, address, phone, ssn))
        conn.commit()

        return {
            "success": True,
            "message": "Borrower added successfully.",
            "card_id": card_id
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Database error: {e}"
        }

    finally:
        if conn is not None:
            conn.close()

def get_borrower_by_card(card_id):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT Card_id, Bname, Address, Phone, Ssn FROM BORROWER WHERE Card_id = ?",
            (card_id,)
        )
        row = cur.fetchone()

        if row is None:
            return None

        # row is a sqlite3.Row (dict-like) because of row_factory
        return {
            "Card_id": row["Card_id"],
            "Bname": row["Bname"],
            "Address": row["Address"],
            "Phone": row["Phone"],
            "Ssn": row["Ssn"]
        }

    finally:
        if conn is not None:
            conn.close()

def get_borrower_by_ssn(ssn):
    ssn = normalize_ssn(ssn)
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT Card_id, Bname, Address, Phone, Ssn FROM BORROWER WHERE Ssn = ?",
            (ssn,)
        )
        row = cur.fetchone()

        if row is None:
            return None

        return {
            "Card_id": row["Card_id"],
            "Bname": row["Bname"],
            "Address": row["Address"],
            "Phone": row["Phone"],
            "Ssn": row["Ssn"]
        }

    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    result = add_borrower(
        name="John Smith",
        ssn="123-45-6789",
        address="123 Main St",
        phone="555-111-222"
    )
    print(result)
