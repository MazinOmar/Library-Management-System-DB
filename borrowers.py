import mysql.connector
from mysql.connector import Error
import re


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",          
    "database": "library_db"
}




def get_connection():
    """
    Create and return a new MySQL connection.
    """
    return mysql.connector.connect(**DB_CONFIG)



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
    
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT MAX(Card_id) FROM BORROWER")
        row = cur.fetchone()[0]

        if row is None:
            return "ID000001"

        try:
            num = int(row[2:])  # Remove "ID"
        except Exception:
            num = 0

        num += 1
        new_id = "ID" + str(num).zfill(6)
        return new_id

    finally:
        if conn is not None and conn.is_connected():
            conn.close()









def add_borrower(name, ssn, address, phone=None):
    
    """
    Adds a new borrower to the BORROWER table.

    Table structure (from your dump):
        BORROWER(
            Card_id  VARCHAR(10) PRIMARY KEY,
            Ssn      CHAR(9) UNIQUE NOT NULL,
            Bname    VARCHAR(255) NOT NULL,
            Address  VARCHAR(255) NOT NULL,
            Phone    VARCHAR(20) NOT NULL
        )
    """
    name = clean(name)
    
    ssn = normalize_ssn(ssn)
    
    address = clean(address)
    
    phone = clean(phone)


    if name == "" or ssn == "" or address == "":
        
        return {
            "success": False,
            "message": "Name, SSN, and Address are required."
        }

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

       
        cur.execute("SELECT Card_id FROM BORROWER WHERE Ssn = %s", (ssn,))
        row = cur.fetchone()

        if row is not None:
            
            return {
                "success": False,
                "message": "A borrower with this SSN already exists.",
                "card_id": row[0]
            }

  
        card_id = make_card_id()


        insert_sql = """
            INSERT INTO BORROWER (Card_id, Bname, Address, Phone, Ssn)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(insert_sql, (card_id, name, address, phone, ssn))
        conn.commit()

        return {
            
            "success": True,
            
            "message": "Borrower added successfully.",
            
            "card_id": card_id
        }

    except Error as e:
       
        return {
            
            "success": False,
            
            
            
            
            "message": f"Database error: {e}"
        }

    finally:
        if conn is not None and conn.is_connected():
            conn.close()












def get_borrower_by_card(card_id):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT Card_id, Bname, Address, Phone, Ssn FROM BORROWER WHERE Card_id = %s", (card_id,))
        row = cur.fetchone()

        if row is None:
            return None

        return {
            "Card_id": row[0],
            "Bname": row[1],
            "Address": row[2],
            "Phone": row[3],
            "Ssn": row[4]
        }

    finally:
        if conn is not None and conn.is_connected():
            conn.close()



def get_borrower_by_ssn(ssn):
    
    ssn = normalize_ssn(ssn)
    conn = None
    try:
        
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT Card_id, Bname, Address, Phone, Ssn FROM BORROWER WHERE Ssn = %s", (ssn,))
        row = cur.fetchone()

        if row is None:
            return None

        return {
            
            "Card_id": row[0],
            
            "Bname": row[1],
            
            "Address": row[2],
            
            "Phone": row[3],
            
            "Ssn": row[4]
        }

    finally:
        if conn is not None and conn.is_connected():
            conn.close()



if __name__ == "__main__":
    result = add_borrower(
        name="John Smith",
        ssn="123-45-6789",
        address="123 Main St",
        phone="555-111-222"
    )
    print(result)

