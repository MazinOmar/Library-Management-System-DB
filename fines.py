from db import get_connection
from datetime import date, datetime

DAILY_FINE = 0.25  # $0.25 per day


def _parse_date(d):
    """Helper: parse 'YYYY-MM-DD' string to date, or None."""
    if d is None:
        return None
    d = d.strip()
    if d == "":
        return None
    return datetime.strptime(d, "%Y-%m-%d").date()


def refresh_fines():
    """
    Recalculate fines for all late loans according to the rules:

    - Late + returned: (Date_in - Due_date) * 0.25
    - Late + still out: (today - Due_date) * 0.25

    For each late loan:
      - If FINES row exists and Paid = 0: update Fine_amt.
      - If FINES row exists and Paid = 1: do nothing.
      - If no FINES row: insert a new one with Paid = 0.
    """
    conn = get_connection()
    cur = conn.cursor()

    today = date.today()

    # Get all loans to evaluate
    cur.execute("SELECT Loan_id, Due_date, Date_in FROM BOOK_LOANS")
    loans = cur.fetchall()

    for loan in loans:
        loan_id = loan["Loan_id"] if isinstance(loan, dict) or hasattr(loan, "keys") else loan[0]
        due_raw = loan["Due_date"] if isinstance(loan, dict) or hasattr(loan, "keys") else loan[1]
        in_raw = loan["Date_in"] if isinstance(loan, dict) or hasattr(loan, "keys") else loan[2]

        due_date = _parse_date(due_raw)
        date_in = _parse_date(in_raw)

        if due_date is None:
            continue

        # Compute days late
        if date_in is not None:
            days_late = (date_in - due_date).days
        else:
            days_late = (today - due_date).days

        if days_late <= 0:
            # Not late, skip (you could also choose to clear existing unpaid fines,
            # but the assignment does not require it).
            continue

        fine_amt = round(days_late * DAILY_FINE, 2)

        # Check if a FINES row already exists for this loan
        cur.execute("SELECT Fine_amt, Paid FROM FINES WHERE Loan_id = ?", (loan_id,))
        row = cur.fetchone()

        if row is None:
            # No existing fine row -> insert a new one
            cur.execute(
                "INSERT INTO FINES (Loan_id, Fine_amt, Paid) VALUES (?, ?, 0)",
                (loan_id, fine_amt)
            )
        else:
            existing_amt = row["Fine_amt"] if hasattr(row, "keys") else row[0]
            paid = row["Paid"] if hasattr(row, "keys") else row[1]

            # If already paid, do nothing
            if paid:
                continue

            # Unpaid fine: update amount if changed
            if float(existing_amt) != float(fine_amt):
                cur.execute(
                    "UPDATE FINES SET Fine_amt = ? WHERE Loan_id = ?",
                    (fine_amt, loan_id)
                )

    conn.commit()
    conn.close()
    return True


def get_borrower_fines(show_paid: bool = False):
    """
    Return list of (Card_id, Bname, total_fines) for borrowers.
    If show_paid == False, only include unpaid fines.
    """
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT 
            bl.Card_id,
            br.Bname,
            SUM(f.Fine_amt) AS total_fines
        FROM FINES f
        JOIN BOOK_LOANS bl ON f.Loan_id = bl.Loan_id
        JOIN BORROWER br   ON br.Card_id = bl.Card_id
        WHERE (? = 1 OR f.Paid = 0)
        GROUP BY bl.Card_id, br.Bname
        HAVING SUM(f.Fine_amt) > 0;
    """

    cur.execute(query, (1 if show_paid else 0,))
    rows = cur.fetchall()

    conn.close()
    return rows


def pay_fines(card_id: str):
    """
    Pay all unpaid fines for a borrower, if they have no books still out.

    - If borrower has any unpaid fines for books not yet returned -> reject.
    - Otherwise mark all those fines Paid = 1.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Check for unpaid fines on books still out
    check_query = """
        SELECT COUNT(*)
        FROM BOOK_LOANS bl
        JOIN FINES f ON f.Loan_id = bl.Loan_id
        WHERE bl.Card_id = ?
          AND bl.Date_in IS NULL
          AND f.Paid = 0;
    """
    cur.execute(check_query, (card_id,))
    still_out = cur.fetchone()[0]

    if still_out > 0:
        conn.close()
        return {
            "success": False,
            "error": "Cannot pay fines — borrower still has books out."
        }

    # Pay all unpaid fines for this borrower
    update_query = """
        UPDATE FINES
        SET Paid = 1
        WHERE Loan_id IN (
            SELECT Loan_id FROM BOOK_LOANS
            WHERE Card_id = ?
        ) AND Paid = 0;
    """
    cur.execute(update_query, (card_id,))
    conn.commit()
    affected = cur.rowcount

    conn.close()
    return {"success": True, "paid_rows": affected}


if __name__ == "__main__":
    # quick manual test of refresh + list
    refresh_fines()
    fines = get_borrower_fines(show_paid=False)
    for row in fines:
        card_id, name, total = row[0], row[1], row[2]
        print(card_id, name, total)
