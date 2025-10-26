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

if __name__ == "__main__":
    main()
