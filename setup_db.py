# setup_db.py
import sqlite3
import csv

DB_PATH = "library.db"

schema_sql = """
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS FINES;
DROP TABLE IF EXISTS BOOK_LOANS;
DROP TABLE IF EXISTS BOOK_AUTHORS;
DROP TABLE IF EXISTS AUTHORS;
DROP TABLE IF EXISTS BORROWER;
DROP TABLE IF EXISTS BOOK;

-- BOOK table (from book.csv: Isbn, Title)
CREATE TABLE BOOK (
    Isbn  TEXT PRIMARY KEY,
    Title TEXT NOT NULL
);

-- AUTHORS table (from authors.csv: Author_id, Name)
CREATE TABLE AUTHORS (
    Author_id INTEGER PRIMARY KEY,
    Name      TEXT NOT NULL
);

-- BOOK_AUTHORS (from book_authors.csv: Author_id, Isbn)
CREATE TABLE BOOK_AUTHORS (
    Author_id INTEGER NOT NULL,
    Isbn      TEXT    NOT NULL,
    PRIMARY KEY (Author_id, Isbn),
    FOREIGN KEY (Author_id) REFERENCES AUTHORS(Author_id),
    FOREIGN KEY (Isbn)      REFERENCES BOOK(Isbn)
);

-- BORROWER table (from borrower.csv: Card_id, Ssn, Bname, Address, Phone)
CREATE TABLE BORROWER (
    Card_id TEXT PRIMARY KEY,
    Ssn     TEXT NOT NULL UNIQUE,
    Bname   TEXT NOT NULL,
    Address TEXT NOT NULL,
    Phone   TEXT NOT NULL
);

-- BOOK_LOANS (start empty)
CREATE TABLE BOOK_LOANS (
    Loan_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    Isbn     TEXT NOT NULL,
    Card_id  TEXT NOT NULL,
    Date_out TEXT NOT NULL,   -- store dates as 'YYYY-MM-DD'
    Due_date TEXT NOT NULL,
    Date_in  TEXT,
    FOREIGN KEY (Isbn)   REFERENCES BOOK(Isbn),
    FOREIGN KEY (Card_id) REFERENCES BORROWER(Card_id)
);

-- FINES (Loan_id as PK and FK)
CREATE TABLE FINES (
    Loan_id  INTEGER PRIMARY KEY,
    Fine_amt NUMERIC(10,2) NOT NULL,
    Paid     INTEGER       NOT NULL DEFAULT 0,
    FOREIGN KEY (Loan_id) REFERENCES BOOK_LOANS(Loan_id)
);

PRAGMA foreign_keys = ON;
"""

def run_sql(cur, sql):
    cur.executescript(sql)

def load_csv(cur, table, columns, filename):
    print(f"Loading {filename} into {table}...")
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        placeholders = ",".join(["?"] * len(columns))
        col_list = ",".join(columns)
        for row in reader:
            if not row or all(v.strip() == "" for v in row):
                continue
            cur.execute(
                f"INSERT OR IGNORE INTO {table} ({col_list}) VALUES ({placeholders})",
                row
            )

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Creating schema in library.db ...")
    run_sql(cur, schema_sql)

    # Adjust filenames here if yours are named differently
    load_csv(cur, "BOOK",         ["Isbn", "Title"],                         "book.csv")
    load_csv(cur, "AUTHORS",      ["Author_id", "Name"],                     "authors.csv")
    load_csv(cur, "BOOK_AUTHORS", ["Author_id", "Isbn"],                     "book_authors.csv")
    load_csv(cur, "BORROWER",     ["Card_id", "Ssn", "Bname", "Address", "Phone"], "borrower.csv")

    conn.commit()
    conn.close()
    print("Done. SQLite database created as library.db")

if __name__ == "__main__":
    main()
