from datetime import date, timedelta
from sqlalchemy import text
from db import session

# Checkout books
def checkout(isbn: str, borrower_id: str):

  # Check if borrower exists
  borrower = session.execute(
    text("SELECT * FROM Borrower WHERE Card_id = :cid"),
    {"cid": borrower_id}
  ).fetchone()

  if borrower is None:
    return {"success": False, "message": "Borrower not found"}

  # Unpaid fines (Coalesce returns 0 not null)
  unpaid = session.execute(
    text("""
      SELECT COALESCE(SUM(F.Fine_amt), 0) AS unpaid_fines
      FROM Fines F
      JOIN Book_Loans BL ON F.Loan_id = BL.Loan_id
      WHERE BL.Card_id = :cid AND F.Paid = 0
    """),
    {"cid": borrower_id}
  ).scalar()

  if unpaid > 0:
    return {"success": False, "message": "Borrower has unpaid fines"}

  # Active loans
  active = session.execute(
    text("""
      SELECT COUNT(*) 
      FROM Book_Loans
      WHERE Card_id = :cid AND Date_in IS NULL
    """),
    {"cid": borrower_id}
  ).scalar()

  if active >= 3:
    return {"success": False, "message": "Borrower has 3 active loans"}

  # Check if book is checked out
  loaned = session.execute(
    text("""
      SELECT * 
      FROM Book_Loans
      WHERE Isbn = :isbn AND Date_in IS NULL
    """),
    {"isbn": isbn}
  ).fetchone()

  if loaned:
    return {"success": False, "message": "Book is already checked out"}

  # Insert loan
  session.execute(
    text("""
      INSERT INTO Book_Loans (Isbn, Card_id, Date_out, Due_date, Date_in)
      VALUES (:isbn, :cid, :dout, :ddue, NULL)
    """),
    {
      "isbn": isbn,
      "cid": borrower_id,
      "dout": date.today(),
      "ddue": date.today() + timedelta(days=14)
    }
  )
  session.commit()

  return {"success": True, "message": "Book has been checked out"}

# Search for loans
def search_loans(isbn=None, card_id=None, name=None):

  sql = """
    SELECT 
      BL.Loan_id,
      BL.Isbn,
      BL.Card_id,
      BL.Date_out,
      BL.Due_date
    FROM Book_Loans BL
    JOIN Borrower B ON BL.Card_id = B.Card_id
    WHERE BL.Date_in IS NULL
  """

  # Search options
  params = {}

  if isbn:
    sql += " AND BL.Isbn = :isbn"
    params["isbn"] = isbn

  if card_id:
    sql += " AND BL.Card_id = :cid"
    params["cid"] = card_id

  if name:
    sql += " AND B.Bname LIKE :name"
    params["name"] = f"%{name}%"

  rows = session.execute(text(sql), params).fetchall()

  return [
    {
      "loan_id": r.Loan_id,
      "isbn": r.Isbn,
      "borrower": r.Card_id,
      "date_out": str(r.Date_out),
      "due_date": str(r.Due_date)
    }
    for r in rows
  ]

# Check in books
def checkin(loan_ids):
  if not loan_ids or not isinstance(loan_ids, list):
    return {"success": False, "message": "loan_ids must be a list"}

  if len(loan_ids) > 3:
    return {"success": False, "message": "A maximum of 3 check-ins allowed"}

  checked_in = 0

  for loan_id in loan_ids:
    res = session.execute(
      text("""
        UPDATE Book_Loans
        SET Date_in = :today
        WHERE Loan_id = :lid AND Date_in IS NULL
      """),
      {"today": date.today(), "lid": loan_id}
    )

    checked_in += res.rowcount

  session.commit()

  return {
      "success": True,
      "message": f"Checked in {checked_in} book(s)"
  }
