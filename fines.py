import mysql.connector
from datetime import datetime

# conneciton
def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Mansi",   
        database="library_db"
    )

# refresh fines
def refresh_fines():
    db = get_connection()
    cursor = db.cursor()

    cursor.callproc("refresh_fines")
    db.commit()

    cursor.close()
    db.close()
    return True

# get fines
def get_borrower_fines(show_paid=False):
    db = get_connection()
    cursor = db.cursor()

    query = """
        SELECT 
            b.Card_id,
            br.bname,
            SUM(f.fine_amt) AS total_fines
        FROM fines f
        JOIN book_loans b ON f.loan_id = b.loan_id
        JOIN borrower br ON br.card_id = b.card_id
        WHERE (%s = TRUE OR f.paid = 0)
        GROUP BY b.Card_id, br.bname
        HAVING SUM(f.fine_amt) > 0;
    """

    cursor.execute(query, (show_paid,))
    rows = cursor.fetchall()

    cursor.close()
    db.close()
    return rows

# pay fines
def pay_fines(card_id):
    db = get_connection()
    cursor = db.cursor()

    #  no unpaid books still out
    check_query = """
        SELECT COUNT(*)
        FROM book_loans bl
        JOIN fines f ON f.loan_id = bl.loan_id
        WHERE bl.card_id = %s
          AND bl.date_in IS NULL
          AND f.paid = 0;
    """
    cursor.execute(check_query, (card_id,))
    still_out = cursor.fetchone()[0]

    if still_out > 0:
        cursor.close()
        db.close()
        return {"success": False, "error": "Cannot pay fines — borrower still has books out."}

    # pay fines
    update_query = """
        UPDATE fines f
        JOIN book_loans bl ON f.loan_id = bl.loan_id
        SET f.paid = 1
        WHERE bl.card_id = %s AND f.paid = 0;
    """

    cursor.execute(update_query, (card_id,))
    db.commit()
    affected = cursor.rowcount

    cursor.close()
    db.close()

    return {"success": True, "paid_rows": affected}
