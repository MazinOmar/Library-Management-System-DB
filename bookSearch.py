from db import get_connection

def search(query):
    conn = get_connection()
    cur = conn.cursor()

    # Prepare the wildcard once
    wildcard = f"%{query.lower()}%"

    search_sql = """
    SELECT
        b.Isbn,
        b.Title,
        GROUP_CONCAT(a.Name, ', ') AS Authors,
        CASE 
            WHEN EXISTS (
                SELECT 1
                FROM BOOK_LOANS bl
                WHERE bl.Isbn = b.Isbn AND bl.Date_in IS NULL
            ) THEN 'OUT'
            ELSE 'IN'
        END AS Availability
    FROM BOOK b
    JOIN BOOK_AUTHORS ba ON b.Isbn = ba.Isbn
    JOIN AUTHORS a ON ba.Author_id = a.Author_id
    WHERE
           LOWER(b.Isbn)  LIKE ?
        OR LOWER(b.Title) LIKE ?
        OR LOWER(a.Name)  LIKE ?
    GROUP BY b.Isbn, b.Title
    ORDER BY b.Title;
    """

    cur.execute(search_sql, (wildcard, wildcard, wildcard))
    results = cur.fetchall()

    conn.close()
    return results


# Simple CLI test
if __name__ == "__main__":
    q = input("Search for: ")
    rows = search(q)

    print("\n--- Results ---")
    for r in rows:
        print(f"ISBN: {r['Isbn']}")
        print(f"Title: {r['Title']}")
        print(f"Authors: {r['Authors']}")
        print(f"Status: {r['Availability']}")
        print("-------------------------")
