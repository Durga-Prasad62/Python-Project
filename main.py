import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime, timedelta
import os, csv, logging
os.makedirs("logs", exist_ok=True)
os.makedirs("backups", exist_ok=True)

logging.basicConfig(
    filename="logs/library_logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def save_backup(filename, data, headers):
    path = os.path.join("backups", filename)
    new = not os.path.exists(path)

    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(headers)
        w.writerow(data)

    logging.info(f"Backup[{filename}] → {data}")

# DB CONNECTION
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Prasadmajji1234",
        database="LIBRARY_DB" 
    )


#BOOKS 
def refresh_book_table():
    for r in book_table.get_children():
        book_table.delete(r)
    db = connect_db()
    c = db.cursor()
    c.execute("SELECT * FROM books")
    for row in c.fetchall():
        book_table.insert("", "end", values=row)
    db.close()

def insert_book(data):
    try:
        db = connect_db()
        c = db.cursor()
        c.execute("INSERT INTO books VALUES(%s,%s,%s,%s,%s,%s,%s)", data)
        db.commit()
        db.close()
        messagebox.showinfo("Success","Book Added")
        refresh_book_table()
    except Exception as e:
        messagebox.showerror("Error",str(e))

def update_book(data):
    try:
        db = connect_db()
        c = db.cursor()
        c.execute(
            "UPDATE books SET title=%s,author=%s,category=%s,publisher=%s,price=%s,qty=%s WHERE book_id=%s",
            (*data, book_id_entry.get())
        )
        db.commit()
        db.close()
        messagebox.showinfo("Updated","Book Updated")
        refresh_book_table()
    except Exception as e:
        messagebox.showerror("Error",str(e))

def delete_book():
    if not book_id_entry.get():
        return
    db = connect_db()
    c = db.cursor()
    c.execute("DELETE FROM books WHERE book_id=%s",(book_id_entry.get(),))
    db.commit()
    db.close()
    messagebox.showinfo("Deleted","Book Deleted")
    clear_book_form()
    refresh_book_table()

def book_row_click(e):
    row = book_table.focus()
    d = book_table.item(row)["values"]
    if d:
        clear_book_form()
        for i, v in enumerate(d):
            entries[i].insert(0,v)

def clear_book_form():
    for e in entries:
        e.delete(0,tk.END)

# MEMBERS
def refresh_member_table():
    for r in member_table.get_children():
        member_table.delete(r)
    db = connect_db()
    c = db.cursor()
    c.execute("SELECT * FROM members")
    for row in c.fetchall():
        member_table.insert("", "end", values=row)
    db.close()

def add_member(data):
    try:
        db = connect_db()
        c = db.cursor()
        c.execute("INSERT INTO members VALUES(%s,%s,%s,%s,%s)", data)
        db.commit()
        db.close()
        messagebox.showinfo("Success","Member Added")
        refresh_member_table()
    except Exception as e:
        messagebox.showerror("Error",str(e))

def update_member(data):
    try:
        db = connect_db()
        c = db.cursor()
        c.execute(
            "UPDATE members SET name=%s,email=%s,phone=%s,address=%s WHERE member_id=%s",
            (*data, member_id_entry.get())
        )
        db.commit()
        db.close()
        messagebox.showinfo("Updated","Member Updated")
        refresh_member_table()
    except Exception as e:
        messagebox.showerror("Error",str(e))

def delete_member():
    if not member_id_entry.get():
        return
    db = connect_db()
    c = db.cursor()
    c.execute("DELETE FROM members WHERE member_id=%s",(member_id_entry.get(),))
    db.commit()
    db.close()
    messagebox.showinfo("Deleted","Member Deleted")
    clear_member_form()
    refresh_member_table()

def member_row_click(e):
    row = member_table.focus()
    d = member_table.item(row)["values"]
    if d:
        clear_member_form()
        for i, v in enumerate(d):
            m_entries[i].insert(0,v)

def clear_member_form():
    for e in m_entries:
        e.delete(0,tk.END)

#TRANSACTIONS 
def refresh_issue_table():
    for r in issue_table.get_children():
        issue_table.delete(r)
    db = connect_db()
    c = db.cursor()
    c.execute("SELECT * FROM transactions")
    for row in c.fetchall():
        issue_table.insert("", "end", values=row)
    db.close()

def issue_book():
    book = book_trans_entry.get()
    mem = member_trans_entry.get()
    trans = transaction_entry.get()

    if not (book and mem and trans):
        messagebox.showwarning("Missing","Fill all fields")
        return

    db = connect_db()
    c = db.cursor()

    c.execute("SELECT qty FROM books WHERE book_id=%s",(book,))
    stock = c.fetchone()

    if not stock:
        messagebox.showerror("Error","Book not found")
        db.close()
        return

    if stock[0] <= 0:
        messagebox.showinfo("Out of Stock","No books available")
        db.close()
        return

    issue = datetime.now().strftime("%Y-%m-%d")
    due = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    try:
        c.execute(
            "INSERT INTO transactions VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (trans, book, mem, issue, due, "", "Issued")
        )
        c.execute("UPDATE books SET qty=qty-1 WHERE book_id=%s",(book,))
        db.commit()
        messagebox.showinfo("Issued",f"Due Date: {due}")
        refresh_issue_table()
    except Exception as e:
        messagebox.showerror("Error",str(e))

    db.close()

def return_book():
    trans = transaction_entry.get()
    if not trans:
        return

    db = connect_db()
    c = db.cursor()

    c.execute("SELECT book_id FROM transactions WHERE transaction_id=%s",(trans,))
    b = c.fetchone()
    if not b:
        messagebox.showerror("Error","Transaction not found")
        db.close()
        return
    ret = datetime.now().strftime("%Y-%m-%d")

    try:
        c.execute("UPDATE transactions SET return_date=%s,status=%s WHERE transaction_id=%s",(ret,"Returned",trans))
        c.execute("UPDATE books SET qty=qty+1 WHERE book_id=%s",(b[0],))
        db.commit()
        messagebox.showinfo("Returned","Book Returned")
        refresh_issue_table()
    except Exception as e:
        messagebox.showerror("Error",str(e))
    db.close()

# UI SETUP
root = tk.Tk()
root.title("Library Management System")
root.geometry("1250x600")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

#BOOK TAB
book_tab = ttk.Frame(notebook)
notebook.add(book_tab, text="Books")

book_form = tk.Frame(book_tab,padx=20,pady=20)
book_form.pack(side="left",fill="y")

labels = ["Book ID","Title","Author","Category","Publisher","Price","Quantity"]
entries=[]
for i,txt in enumerate(labels):
    tk.Label(book_form,text=txt).grid(row=i,column=0,sticky="w",pady=4)
    e = tk.Entry(book_form)
    e.grid(row=i,column=1,pady=4)
    entries.append(e)

book_id_entry, title_entry, author_entry, category_entry, publisher_entry, price_entry, qty_entry = entries

tk.Button(book_form,text="Add",command=lambda:insert_book((
    book_id_entry.get(),title_entry.get(),author_entry.get(),
    category_entry.get(),publisher_entry.get(),
    float(price_entry.get() or 0),int(qty_entry.get() or 0)
)),width=15).grid(row=7,column=0,pady=6)

tk.Button(book_form,text="Update",command=lambda:update_book((
    title_entry.get(),author_entry.get(),category_entry.get(),
    publisher_entry.get(),float(price_entry.get() or 0),int(qty_entry.get() or 0)
)),width=15).grid(row=7,column=1,pady=6)

tk.Button(book_form,text="Delete",command=delete_book,width=15).grid(row=8,column=0)
tk.Button(book_form,text="Clear",command=clear_book_form,width=15).grid(row=8,column=1)

book_table_frame = tk.Frame(book_tab)
book_table_frame.pack(side="right",fill="both",expand=True,padx=20)

cols=("book_id","title","author","category","publisher","price","qty")
book_table = ttk.Treeview(book_table_frame,columns=cols,show="headings")
for c in cols:
    book_table.heading(c,text=c.upper())
    book_table.column(c,width=140)
book_table.pack(fill="both",expand=True)
book_table.bind("<ButtonRelease-1>",book_row_click)

refresh_book_table()

# MEMBER TAB 
member_tab = ttk.Frame(notebook)
notebook.add(member_tab, text="Members")

member_form = tk.Frame(member_tab,padx=20,pady=20)
member_form.pack(side="left",fill="y")

m_labels = ["Member ID","Name","Email","Phone","Address"]
m_entries=[]
for i,txt in enumerate(m_labels):
    tk.Label(member_form,text=txt).grid(row=i,column=0,sticky="w",pady=4)
    e=tk.Entry(member_form)
    e.grid(row=i,column=1,pady=4)
    m_entries.append(e)

member_id_entry,name_entry,email_entry,phone_entry,address_entry = m_entries

tk.Button(member_form,text="Add",command=lambda:add_member((
    member_id_entry.get(),name_entry.get(),email_entry.get(),phone_entry.get(),address_entry.get()
)),width=15).grid(row=6,column=0)

tk.Button(member_form,text="Update",command=lambda:update_member((
    name_entry.get(),email_entry.get(),phone_entry.get(),address_entry.get()
)),width=15).grid(row=6,column=1)

tk.Button(member_form,text="Delete",command=delete_member,width=15).grid(row=7,column=0)
tk.Button(member_form,text="Clear",command=clear_member_form,width=15).grid(row=7,column=1)

member_table_frame=tk.Frame(member_tab)
member_table_frame.pack(side="right",fill="both",expand=True,padx=20)

m_cols=("member_id","name","email","phone","address")
member_table=ttk.Treeview(member_table_frame,columns=m_cols,show="headings")
for c in m_cols:
    member_table.heading(c,text=c.upper())
    member_table.column(c,width=140)
member_table.pack(fill="both",expand=True)
member_table.bind("<ButtonRelease-1>",member_row_click)

refresh_member_table()

#  TRANSACTION TAB
trans_tab = ttk.Frame(notebook)
notebook.add(trans_tab, text="Transactions")

trans_form=tk.Frame(trans_tab,padx=20,pady=20)
trans_form.pack(side="left",fill="y")

tk.Label(trans_form,text="Transaction ID").grid(row=0,column=0,sticky="w",pady=4)
transaction_entry=tk.Entry(trans_form)
transaction_entry.grid(row=0,column=1,pady=4)

tk.Label(trans_form,text="Book ID").grid(row=1,column=0,sticky="w",pady=4)
book_trans_entry=tk.Entry(trans_form)
book_trans_entry.grid(row=1,column=1,pady=4)

tk.Label(trans_form,text="Member ID").grid(row=2,column=0,sticky="w",pady=4)
member_trans_entry=tk.Entry(trans_form)
member_trans_entry.grid(row=2,column=1,pady=4)

tk.Button(trans_form,text="Issue",command=issue_book,width=15).grid(row=4,column=0,pady=6)
tk.Button(trans_form,text="Return",command=return_book,width=15).grid(row=4,column=1,pady=6)

issue_table_frame=tk.Frame(trans_tab)
issue_table_frame.pack(side="right",fill="both",expand=True,padx=20)

t_cols=("transaction_id","book_id","member_id","issue_date","due_date","return_date","status")
issue_table=ttk.Treeview(issue_table_frame,columns=t_cols,show="headings")
for c in t_cols:
    issue_table.heading(c,text=c.upper())
    issue_table.column(c,width=140)
issue_table.pack(fill="both",expand=True)
refresh_issue_table()

root.mainloop()
