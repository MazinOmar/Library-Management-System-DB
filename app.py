import tkinter as tk
from tkinter import ttk, messagebox

# importing backend functions
from bookSearch import search
from borrowers import add_borrower
from loans import checkout, check_in
from fines import get_borrower_fines, pay_fines, refresh_fines

# color scheme 
PRIMARY_COLOR = "#1a1a2e"
SECONDARY_COLOR = "#0f4c75"
ACCENT_COLOR = "#e94560"
BG_COLOR = "#16213e"
TEXT_COLOR = "#ffffff"
INPUT_BG = "#0f3460"
TEXT_BOX_BG = "#eaeaea"

# Main window
root = tk.Tk()
root.title("Library Management System")
root.geometry("1200x800")
root.configure(bg=BG_COLOR)

# Header
header_frame = tk.Frame(root, bg=PRIMARY_COLOR, height=80)
header_frame.pack(fill=tk.X)
header_frame.pack_propagate(False)

title = tk.Label(
    header_frame,
    text="📚 Library Management System",
    font=("Arial", 24, "bold"),
    bg=PRIMARY_COLOR,
    fg="white"
)
title.pack(pady=20)

# Main container with notebook (tabs)
main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

notebook = ttk.Notebook(main_frame)
notebook.pack(fill=tk.BOTH, expand=True)

# Style configuration
style = ttk.Style()
style.theme_use('clam')
style.configure('TNotebook', background=BG_COLOR, borderwidth=0)
style.configure('TNotebook.Tab', padding=[20, 10], font=('Arial', 10, 'bold'))
style.map('TNotebook.Tab', background=[('selected', SECONDARY_COLOR)], foreground=[('selected', 'white')])

# book search
search_frame = tk.Frame(notebook, bg=BG_COLOR)
notebook.add(search_frame, text="🔍 Book Search")

search_input_frame = tk.Frame(search_frame, bg=BG_COLOR)
search_input_frame.pack(pady=20, padx=20, fill=tk.X)

tk.Label(
    search_input_frame,
    text="Search Books:",
    font=("Arial", 12, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
).pack(anchor=tk.W, pady=5)

search_entry_frame = tk.Frame(search_input_frame, bg=BG_COLOR)
search_entry_frame.pack(fill=tk.X)

search_entry = tk.Entry(search_entry_frame, width=60, font=("Arial", 11), bg=INPUT_BG, fg="white", insertbackground="white")
search_entry.pack(side=tk.LEFT, ipady=5, fill=tk.X, expand=True)

def run_search():
    search_results_box.delete("1.0", tk.END)
    query = search_entry.get()
    if not query:
        messagebox.showwarning("Input Required", "Please enter a search query.")
        return
    
    try:
        results = search(query)
        
        if not results:
            search_results_box.insert(tk.END, "No results found.")
            return
        
        for r in results[:50]:
            search_results_box.insert(tk.END, f"📖 ISBN: {r['Isbn']}\n", "isbn")
            search_results_box.insert(tk.END, f"   Title: {r['Title']}\n", "title")
            search_results_box.insert(tk.END, f"   Authors: {r['authors']}\n")
            search_results_box.insert(tk.END, f"   Status: {r['availability']}\n", "status")
            search_results_box.insert(tk.END, "─" * 80 + "\n\n")
    except Exception as e:
        search_results_box.insert(tk.END, f"Error: {str(e)}")

search_btn = tk.Button(
    search_entry_frame,
    text="Search",
    command=run_search,
    bg=SECONDARY_COLOR,
    fg="white",
    font=("Arial", 10, "bold"),
    padx=20,
    cursor="hand2",
    relief=tk.FLAT
)
search_btn.pack(side=tk.LEFT, padx=10)

search_results_box = tk.Text(search_frame, height=25, width=100, font=("Consolas", 10), wrap=tk.WORD, bg=TEXT_BOX_BG, fg="#1a1a1a", relief=tk.SOLID, borderwidth=2)
search_results_box.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
search_results_box.tag_config("isbn", foreground=SECONDARY_COLOR, font=("Consolas", 10, "bold"))
search_results_box.tag_config("title", font=("Consolas", 10, "bold"))
search_results_box.tag_config("status", foreground="#27ae60")

# scrollbar
search_scroll = tk.Scrollbar(search_results_box)
search_scroll.pack(side=tk.RIGHT, fill=tk.Y)
search_results_box.config(yscrollcommand=search_scroll.set)
search_scroll.config(command=search_results_box.yview)

#  borrowers 
borrower_frame = tk.Frame(notebook, bg=BG_COLOR)
notebook.add(borrower_frame, text="👤 Borrowers")

borrower_input_frame = tk.Frame(borrower_frame, bg=BG_COLOR)
borrower_input_frame.pack(pady=30, padx=40)

tk.Label(
    borrower_input_frame,
    text="Add New Borrower",
    font=("Arial", 16, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
).grid(row=0, column=0, columnspan=2, pady=20)

fields = [("Name:", "name"), ("SSN:", "ssn"), ("Address:", "address"), ("Phone:", "phone")]
entries = {}

for i, (label, key) in enumerate(fields, start=1):
    tk.Label(
        borrower_input_frame,
        text=label,
        font=("Arial", 11),
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        anchor=tk.W
    ).grid(row=i, column=0, sticky=tk.W, pady=10, padx=5)
    
    entry = tk.Entry(borrower_input_frame, width=40, font=("Arial", 11), bg=INPUT_BG, fg="white", insertbackground="white")
    entry.grid(row=i, column=1, pady=10, padx=5, ipady=5)
    entries[key] = entry

borrower_result_box = tk.Text(borrower_frame, height=10, width=80, font=("Arial", 10), bg=TEXT_BOX_BG, fg="#1a1a1a", relief=tk.SOLID, borderwidth=2)
borrower_result_box.pack(pady=10, padx=40)

def create_borrower():
    borrower_result_box.delete("1.0", tk.END)
    try:
        result = add_borrower(
            entries["name"].get(),
            entries["ssn"].get(),
            entries["address"].get(),
            entries["phone"].get()
        )
        borrower_result_box.insert(tk.END, str(result))
    except Exception as e:
        borrower_result_box.insert(tk.END, f"Error: {str(e)}")

tk.Button(
    borrower_input_frame,
    text="Add Borrower",
    command=create_borrower,
    bg="#27ae60",
    fg="black",
    font=("Arial", 11, "bold"),
    padx=30,
    pady=5,
    cursor="hand2",
    relief=tk.FLAT
).grid(row=len(fields)+1, column=0, columnspan=2, pady=20)

#  loans
loans_frame = tk.Frame(notebook, bg=BG_COLOR)
notebook.add(loans_frame, text="📋 Loans")

# checkout section
checkout_section = tk.LabelFrame(
    loans_frame,
    text="Checkout Book",
    font=("Arial", 12, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR,
    padx=20,
    pady=20
)
checkout_section.pack(pady=20, padx=40, fill=tk.X)

tk.Label(checkout_section, text="ISBN:", font=("Arial", 10), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky=tk.W, pady=5)
isbn_checkout = tk.Entry(checkout_section, width=40, font=("Arial", 10), bg=INPUT_BG, fg="white", insertbackground="white")
isbn_checkout.grid(row=0, column=1, pady=5, ipady=3)

tk.Label(checkout_section, text="Card ID:", font=("Arial", 10), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=1, column=0, sticky=tk.W, pady=5)
card_checkout = tk.Entry(checkout_section, width=40, font=("Arial", 10), bg=INPUT_BG, fg="white", insertbackground="white")
card_checkout.grid(row=1, column=1, pady=5, ipady=3)

checkout_result = tk.Text(loans_frame, height=5, width=80, font=("Arial", 10), bg=TEXT_BOX_BG, fg="#1a1a1a", relief=tk.SOLID, borderwidth=2)
checkout_result.pack(padx=40)

def run_checkout():
    checkout_result.delete("1.0", tk.END)
    try:
        result = checkout(isbn_checkout.get(), card_checkout.get())
        checkout_result.insert(tk.END, str(result))
    except Exception as e:
        checkout_result.insert(tk.END, f"Error: {str(e)}")

tk.Button(
    checkout_section,
    text="Checkout",
    command=run_checkout,
    bg=SECONDARY_COLOR,
    fg="black",
    font=("Arial", 10, "bold"),
    padx=20,
    cursor="hand2",
    relief=tk.FLAT
).grid(row=2, column=0, columnspan=2, pady=15)

# Check-in section
checkin_section = tk.LabelFrame(
    loans_frame,
    text="Check In Book",
    font=("Arial", 12, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR,
    padx=20,
    pady=20
)
checkin_section.pack(pady=20, padx=40, fill=tk.X)

tk.Label(checkin_section, text="ISBN:", font=("Arial", 10), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky=tk.W, pady=5)
isbn_checkin = tk.Entry(checkin_section, width=40, font=("Arial", 10), bg=INPUT_BG, fg="white", insertbackground="white")
isbn_checkin.grid(row=0, column=1, pady=5, ipady=3)

tk.Label(checkin_section, text="Card ID:", font=("Arial", 10), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=1, column=0, sticky=tk.W, pady=5)
card_checkin = tk.Entry(checkin_section, width=40, font=("Arial", 10), bg=INPUT_BG, fg="white", insertbackground="white")
card_checkin.grid(row=1, column=1, pady=5, ipady=3)

checkin_result = tk.Text(loans_frame, height=5, width=80, font=("Arial", 10), bg=TEXT_BOX_BG, fg="#1a1a1a", relief=tk.SOLID, borderwidth=2)
checkin_result.pack(padx=40)

def run_checkin():
    checkin_result.delete("1.0", tk.END)
    try:
        result = check_in(isbn_checkin.get(), card_checkin.get())
        checkin_result.insert(tk.END, str(result))
    except Exception as e:
        checkin_result.insert(tk.END, f"Error: {str(e)}")

tk.Button(
    checkin_section,
    text="Check In",
    command=run_checkin,
    bg="#27ae60",
    fg="black",
    font=("Arial", 10, "bold"),
    padx=20,
    cursor="hand2",
    relief=tk.FLAT
).grid(row=2, column=0, columnspan=2, pady=15)

#  fines
fines_frame = tk.Frame(notebook, bg=BG_COLOR)
notebook.add(fines_frame, text="💰 Fines")

fines_btn_frame = tk.Frame(fines_frame, bg=BG_COLOR)
fines_btn_frame.pack(pady=20)

fines_results_box = tk.Text(fines_frame, height=20, width=80, font=("Consolas", 10), bg=TEXT_BOX_BG, fg="#1a1a1a", relief=tk.SOLID, borderwidth=2)
fines_results_box.pack(pady=10, padx=40, fill=tk.BOTH, expand=True)

def show_fines():
    fines_results_box.delete("1.0", tk.END)
    try:
        refresh_fines()
        fines = get_borrower_fines()
        
        if not fines:
            fines_results_box.insert(tk.END, "No fines found.")
            return
        
        for f in fines:
            fines_results_box.insert(tk.END, f"💳 Card ID: {f[0]}\n", "card")
            fines_results_box.insert(tk.END, f"   Name: {f[1]}\n")
            fines_results_box.insert(tk.END, f"   Total Fines: ${f[2]:.2f}\n", "amount")
            fines_results_box.insert(tk.END, "─" * 60 + "\n\n")
    except Exception as e:
        fines_results_box.insert(tk.END, f"Error: {str(e)}")

fines_results_box.tag_config("card", foreground=SECONDARY_COLOR, font=("Consolas", 10, "bold"))
fines_results_box.tag_config("amount", foreground=ACCENT_COLOR, font=("Consolas", 10, "bold"))

tk.Button(
    fines_btn_frame,
    text="Show All Fines",
    command=show_fines,
    bg=SECONDARY_COLOR,
    fg="black",
    font=("Arial", 11, "bold"),
    padx=20,
    pady=8,
    cursor="hand2",
    relief=tk.FLAT
).pack(side=tk.LEFT, padx=10)

# pay fines section
pay_frame = tk.Frame(fines_frame, bg=BG_COLOR)
pay_frame.pack(pady=10)

tk.Label(pay_frame, text="Card ID:", font=("Arial", 10), bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT, padx=5)
card_fines = tk.Entry(pay_frame, width=20, font=("Arial", 10), bg=INPUT_BG, fg="white", insertbackground="white")
card_fines.pack(side=tk.LEFT, padx=5, ipady=3)

def run_pay_fines():
    try:
        result = pay_fines(card_fines.get())
        messagebox.showinfo("Payment Result", str(result))
        show_fines()  # Refresh the fines display
    except Exception as e:
        messagebox.showerror("Error", str(e))

tk.Button(
    pay_frame,
    text="Pay Fines",
    command=run_pay_fines,
    bg="#27ae60",
    fg="black",
    font=("Arial", 10, "bold"),
    padx=20,
    cursor="hand2",
    relief=tk.FLAT
).pack(side=tk.LEFT, padx=10)

# star
root.mainloop()
