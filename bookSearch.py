import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="insert_password_here",
        database="library_db"
    )

def search(query):
    db = get_connection()
    cursor = db.cursor()

    # Main search SQL adjusted for your real table names
    search_sql = """
    SELECT
        b.ISBN,
        b.title,
        GROUP_CONCAT(a.name SEPARATOR ', ') AS authors,
        CASE 
            WHEN EXISTS (
                SELECT 1
                FROM book_loans bl
                WHERE bl.ISBN = b.ISBN AND bl.date_in IS NULL
            ) THEN 'OUT'
            ELSE 'IN'
        END AS availability
    FROM book b
    JOIN book_authors ba ON b.ISBN = ba.ISBN
    JOIN authors a ON ba.author_id = a.author_id
    WHERE
           LOWER(b.ISBN) LIKE CONCAT('%', LOWER(%s), '%')
        OR LOWER(b.title) LIKE CONCAT('%', LOWER(%s), '%')
        OR LOWER(a.name) LIKE CONCAT('%', LOWER(%s), '%')
    GROUP BY b.ISBN, b.title
    ORDER BY b.title;
    """

    cursor.execute(search_sql, (query, query, query))
    results = cursor.fetchall()

    cursor.close()
    db.close()

    return results


# CLI test
if __name__ == "__main__":
    q = input("Search for: ")
    rows = search(q)

    print("\n--- Results ---")
    for r in rows:
        print(f"ISBN: {r[0]}")
        print(f"Title: {r[1]}")
        print(f"Authors: {r[2]}")
        print(f"Status: {r[3]}")
        print("-------------------------")
