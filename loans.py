import sqlite3
from db import get_connection
from datetime import datetime, timedelta

# checkout a book
def checkout(isbn, card_id):
    conn = get_connection()
    cur = conn.cursor()

    # check if book is already out
    cur.execute("""
        SELECT 1 FROM BOOK_LOANS
        WHERE Isbn = ? AND Date_in IS NULL
    """, (isbn,))
    row = cur.fetchone()

    if row:
        conn.close()
        return {"success": False, "message": "Book is already checked out"}

    # create loan
    date_out = datetime.now().date()
    due = date_out + timedelta(days=14)

    cur.execute("""
        INSERT INTO BOOK_LOANS (Isbn, Card_id, Date_out, Due_date)
        VALUES (?, ?, ?, ?)
    """, (isbn, card_id, date_out, due))

    conn.commit()
    loan_id = cur.lastrowid
    conn.close()

    return {"success": True, "loan_id": loan_id}


# check a book in
def check_in(isbn, card_id):
    conn = get_connection()
    cur = conn.cursor()

    # find active loan
    cur.execute("""
        SELECT Loan_id
        FROM BOOK_LOANS
        WHERE Isbn = ? AND Card_id = ? AND Date_in IS NULL
    """, (isbn, card_id))

    row = cur.fetchone()
    if not row:
        conn.close()
        return {"success": False, "message": "No active loan for this book/card"}

    loan_id = row[0]
    today = datetime.now().date()

    cur.execute("""
        UPDATE BOOK_LOANS
        SET Date_in = ?
        WHERE Loan_id = ?
    """, (today, loan_id))

    conn.commit()
    conn.close()

    return {"success": True, "loan_id": loan_id}
