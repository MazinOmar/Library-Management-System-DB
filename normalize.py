# normalize_borrowers.py

import pandas as pd
import re

IN_FILE  = "borrowers.csv"   # raw file
OUT_FILE = "borrower.csv"    # normalized output

def clean_name(first, last):
    full = f"{(first or '').strip()} {(last or '').strip()}".strip()
    full = full.title()
    return full

def clean_phone(p):
    if pd.isna(p): return None
    digits = re.sub(r"\D", "", str(p))
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:]}"
    return p  # leave as-is if not 10 digits

def clean_ssn(s):
    if pd.isna(s): return None
    digits = re.sub(r"\D", "", str(s))
    if len(digits) == 9:
        return f"{digits[0:3]}-{digits[3:5]}-{digits[5:]}"
    return s  # leave if already formatted 

def normalize_books():
  df_books = pd.read_csv('books.csv', sep='\t')

  # Book
  df_book = df_books[['ISBN10', 'Title']].copy()
  df_book.rename(columns={'ISBN10': 'Isbn', 'Title': 'Title'}, inplace=True)

  # Authors
  author_dict = {} # Seen authors
  author_rows = [] # Cols: Author_id, Name
  book_author_rows = [] # Cols: Author_id, Isbn
  author_id = 1 # Index

  for _, row in df_books.iterrows():
    isbn = str(row['ISBN10'])
    authors = [a.title() for a in str(row['Author']).split(',')]

    for a in authors:
      if a not in author_dict:
        author_dict[a] = author_id
        author_rows.append({'Author_id': author_id, 'Name': a})
        author_id += 1

      book_author_rows.append({'Author_id': author_dict[a], 'Isbn': isbn})

  # Create CSVs
  df_authors = pd.DataFrame(author_rows)
  df_book_authors = pd.DataFrame(book_author_rows)

  df_book.to_csv('book.csv', index=False)
  df_authors.to_csv('authors.csv', index=False)
  df_book_authors.to_csv('book_authors.csv', index=False)

def main():
    df = pd.read_csv(IN_FILE, dtype=str)  # keep leading zeros

    # Build Bname and Address
    df["Bname"]  = [clean_name(f, l) for f, l in zip(df.get("first_name"), df.get("last_name"))]
    df["Ssn"]    = df["ssn"].apply(clean_ssn)
    df["Phone"]  = df["phone"].apply(clean_phone)

    # combination
    def combine_addr(row):
        parts = [row.get("address"), row.get("city"), row.get("state")]
        parts = [p.strip() for p in parts if isinstance(p, str) and p.strip()]
        return ", ".join(parts) if parts else None
    df["Address"] = df.apply(combine_addr, axis=1)

    # Choose Card_id:
    # If the file already has an ID column, reuse it. Otherwise generate sequential IDs.
    if "ID0000id" in df.columns:
        df["Card_id"] = df["ID0000id"].astype(str).str.strip()
    elif "Card_id" in df.columns:
        df["Card_id"] = df["Card_id"].astype(str).str.strip()
    else:
        # Generate like 10000001, 10000002, ...
        start = 10000001
        df["Card_id"] = [str(start + i) for i in range(len(df))]

    # Drop exact dupes (same SSN means same person) – keep first
    if "Ssn" in df.columns:
        df = df.drop_duplicates(subset=["Ssn"], keep="first")

    # Final column order per schema
    out = df[["Card_id", "Ssn", "Bname", "Address", "Phone"]]

    #out = out.sort_values(by="Card_id")

    # Write CSV with no index
    out.to_csv(OUT_FILE, index=False)

    #  report
    print(f"Rows written: {len(out)}")
    print(f"Saved: {OUT_FILE}")

    normalize_books()

if __name__ == "__main__":
    main()
