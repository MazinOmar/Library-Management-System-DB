README – Milestone 2

This project is Milestone 2 of our Library Management System.
For this milestone, we were responsible for building the backend logic and connecting it to a working database. 

We used SQLite for this milestone because it is easy to run, requires no setup, and works well with Python. Everything needed is included inside this folder.

1. Files Included

setup_db.py – creates the database and loads all the CSV data

normalize.py – cleans the raw CSV files and generates final CSVs

db.py – handles database connections

bookSearch.py – search functionality

borrowers.py – add borrower / lookup borrower

loans.py – checkout and check-in logic

fines.py – fine calculation and payments

book.csv

authors.csv

book_authors.csv

borrower.csv

library.db (auto-generated after running setup)

This README

2. How to Build the Database

To regenerate the database:

Make sure the terminal is inside this project folder.

Run:

python normalize.py


This creates the cleaned CSV files.

Then run:

python setup_db.py


This creates library.db and loads all the tables.

3. How to Test Each Part
Book Search:
python bookSearch.py


This lets you type a search term (ISBN, title, or author). It returns ISBN, title, authors, and whether the book is IN or OUT.

Borrower Management:
python borrowers.py


This file has logic for:

Adding a borrower

Checking if a borrower already exists

Generating card IDs


Loans:

Inside Python:

python


Then:

from loans import checkout, check_in


Checkout and check-in follow all the assignment rules (max 3 books, no unpaid fines, etc.).

Fines:
python -c "from fines import refresh_fines; refresh_fines()"


This recalculates all fines.

You can also get fines:

from fines import get_borrower_fines
print(get_borrower_fines())

4. What Is Completed for Milestone 2

Book search (substring and case-insensitive)

Borrower creation with validation

Auto-generated card IDs

Preventing duplicate borrowers by SSN

Loan checkout (including rules: max 3 books, no unpaid fines, book availability)

Loan check-in

Fine calculation for returned and unreturned books

Fine payment rules (no partial payments, cannot pay if book still out)

Fines grouped by borrower

Full working database with tables and CSV data loaded
