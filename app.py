import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from database import LibraryDB
from auth import Authentication
import tkinter.simpledialog as simpledialog

class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📚 Library Management System")
        self.geometry("1000x700")
        
        # Initialize systems
        self.auth = Authentication()
        self.db = LibraryDB()
        
        # Show login screen first
        self.show_login_screen()
    
    def show_login_screen(self):
        """Show login window"""
        self.login_window = tk.Toplevel(self)
        self.login_window.title("Login - Library System")
        self.login_window.geometry("300x200")
        self.login_window.transient(self)
        self.login_window.grab_set()
        
        # Center the login window
        self.login_window.geometry("+%d+%d" % (self.winfo_x() + 50, self.winfo_y() + 50))
        
        
        ttk.Label(self.login_window, text="🔐 Library Login", font=("Arial", 14, "bold")).pack(pady=20)
        
        ttk.Label(self.login_window, text="Username:").pack()
        self.username_entry = ttk.Entry(self.login_window, width=25)
        self.username_entry.pack(pady=5)
        self.username_entry.focus()
        
        ttk.Label(self.login_window, text="Password:").pack()
        self.password_entry = ttk.Entry(self.login_window, width=25, show="*")
        self.password_entry.pack(pady=5)
        
        ttk.Button(self.login_window, text="Login", 
                  command=self.attempt_login, width=20).pack(pady=10)
        
        # Bind Enter key to login
        self.login_window.bind('<Return>', lambda e: self.attempt_login())
    
    def attempt_login(self):
        """Attempt to login with provided credentials"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Validation", "Please enter both username and password.")
            return
        
        user = self.auth.login(username, password)
        if user:
            self.login_window.destroy()
            self.current_user = user
            self.initialize_main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password!")
    
    def initialize_main_app(self):
        """Initialize the main application after successful login"""
        self.style_setup()
        self.create_widgets()
        self.refresh_books()
        self.refresh_issued()
        self.update_user_display()
    
    def style_setup(self):
        """Your beautiful styling - UNCHANGED"""
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure("TFrame", background="#f5f7fb")
        style.configure("Header.TLabel", font=("Arial", 18, "bold"), background="#3b82f6", foreground="white")
        style.configure("Accent.TLabel", font=("Arial", 11), background="#e6eefc")
        style.configure("TLabel", background="#f5f7fb")
        style.configure("TButton", font=("Arial", 10, "bold"), padding=6)
        style.configure("Accent.TButton", background="#3b82f6", foreground="white")
        style.map("Accent.TButton", background=[("active", "#2563eb")])
        style.configure("Treeview", font=("Arial", 10), rowheight=26)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
    
    def create_widgets(self):
        """Enhanced UI with new features but same beautiful design"""
        # Header with user info
        header = ttk.Frame(self)
        header.pack(fill="x")
        
        # Left side: Title
        title_frame = ttk.Frame(header)
        title_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(title_frame, text="Library Management System", 
                 style="Header.TLabel", anchor="center").pack(fill="x", pady=8)
        
        # Right side: User info
        user_frame = ttk.Frame(header)
        user_frame.pack(side="right", padx=10)
        self.user_label = ttk.Label(user_frame, text="", background="#3b82f6", 
                                   foreground="white", font=("Arial", 10))
        self.user_label.pack(pady=5)
        
        # Create Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        
        # Tab 1: Main Library (Your original interface)
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="📖 Main Library")
        
        # Tab 2: Analytics Dashboard
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="📊 Analytics")
        
        # Tab 3: Search & Export
        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="🔍 Search & Export")
        
        # Build each tab
        self.build_main_tab()
        self.build_dashboard_tab()
        self.build_search_tab()
    
    def build_main_tab(self):
        """Your original beautiful interface - EXACTLY THE SAME"""
        main = ttk.Frame(self.main_tab, padding=(12, 10, 12, 10))
        main.pack(fill="both", expand=True)

        # Left panel
        left = ttk.Frame(main, width=320)
        left.pack(side="left", fill="y", padx=(0, 12))

        # Add book form
        form_card = ttk.Frame(left, padding=12, relief="ridge")
        form_card.pack(fill="x", pady=(0, 12))

        ttk.Label(form_card, text="Add Book", style="Accent.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 8))

        self.title_entry = self.add_form_row(form_card, "Title:", 1)
        self.author_entry = self.add_form_row(form_card, "Author:", 2)
        self.year_entry = self.add_form_row(form_card, "Year:", 3)
        self.isbn_entry = self.add_form_row(form_card, "ISBN:", 4)

        ttk.Label(form_card, text="Copies:").grid(row=5, column=0, sticky="w")
        self.copies_spin = ttk.Spinbox(form_card, from_=1, to=999, width=7)
        self.copies_spin.set(1)
        self.copies_spin.grid(row=5, column=1, sticky="w", pady=4)

        ttk.Button(form_card, text="Add Book", command=self.add_book, style="Accent.TButton").grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        # Issue Book Section
        issue_card = ttk.Frame(left, padding=8, relief="ridge")
        issue_card.pack(fill="x", pady=(0, 12))
        ttk.Label(issue_card, text="Issue Book", style="Accent.TLabel").grid(row=0, column=0, columnspan=2)
        ttk.Label(issue_card, text="Book ID:").grid(row=1, column=0, sticky="w")
        self.sel_book_id_lbl = ttk.Label(issue_card, text="-", width=18)
        self.sel_book_id_lbl.grid(row=1, column=1, sticky="w")

        ttk.Label(issue_card, text="Borrower:").grid(row=2, column=0, sticky="w")
        self.borrower_entry = ttk.Entry(issue_card, width=24)
        self.borrower_entry.grid(row=2, column=1, sticky="w", pady=4)

        ttk.Button(issue_card, text="Issue Book", command=self.issue_book, style="Accent.TButton").grid(row=3, column=0, columnspan=2, pady=(8, 0), sticky="ew")

        # Return Book Section
        return_card = ttk.Frame(left, padding=8, relief="ridge")
        return_card.pack(fill="x", pady=(0, 12))
        ttk.Label(return_card, text="Return Book", style="Accent.TLabel").pack(anchor="w")
        ttk.Button(return_card, text="Return Selected", command=self.return_selected, style="Accent.TButton").pack(fill="x", pady=8)

        # Logout Button
        logout_card = ttk.Frame(left, padding=8, relief="ridge")
        logout_card.pack(fill="x", pady=(0, 12))
        ttk.Button(logout_card, text="🚪 Logout", command=self.logout, 
                  style="Accent.TButton").pack(fill="x", pady=8)

        # Right Panel
        right = ttk.Frame(main)
        right.pack(side="left", fill="both", expand=True)

        # Books Table
        ttk.Label(right, text="Books Collection", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 6))
        cols = ("ID", "Title", "Author", "Year", "ISBN", "Copies")
        self.books_tree = ttk.Treeview(right, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.books_tree.heading(c, text=c)
            self.books_tree.column(c, width=120)
        self.books_tree.pack(fill="both", expand=True)
        self.books_tree.bind("<<TreeviewSelect>>", self.on_book_select)

        # Issued Table
        ttk.Label(right, text="Issued Books", font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 6))
        issued_cols = ("IssueID", "BookID", "Title", "Borrower", "IssueDate", "ReturnDate")
        self.issued_tree = ttk.Treeview(right, columns=issued_cols, show="headings", selectmode="browse")
        for c in issued_cols:
            self.issued_tree.heading(c, text=c)
            self.issued_tree.column(c, width=140)
        self.issued_tree.pack(fill="both", expand=True)
    
    def build_dashboard_tab(self):
        """New Analytics Dashboard"""
        dashboard = ttk.Frame(self.dashboard_tab, padding=15)
        dashboard.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(dashboard, text="📊 Library Analytics Dashboard", 
                 font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 15))
        
        # Stats Cards Frame
        stats_frame = ttk.Frame(dashboard)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        # Refresh Analytics Button
        ttk.Button(stats_frame, text="🔄 Refresh Analytics", 
                  command=self.refresh_dashboard).pack(anchor="e", pady=(0, 10))
        
        # Stats Cards will be created in refresh_dashboard
        self.stats_cards_frame = ttk.Frame(stats_frame)
        self.stats_cards_frame.pack(fill="x")
        
        # Popular Books Section
        ttk.Label(dashboard, text="🏆 Most Popular Books", 
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.popular_tree = ttk.Treeview(dashboard, columns=("Title", "Author", "Times Borrowed"), 
                                        show="headings", height=6)
        for col in ("Title", "Author", "Times Borrowed"):
            self.popular_tree.heading(col, text=col)
            self.popular_tree.column(col, width=200)
        self.popular_tree.pack(fill="x", pady=(0, 20))
        
        # Recent Activity Section
        ttk.Label(dashboard, text="📈 Recent Activity", 
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.recent_tree = ttk.Treeview(dashboard, 
                                       columns=("Book", "Borrower", "Issue Date", "Status"), 
                                       show="headings", height=6)
        for col in ("Book", "Borrower", "Issue Date", "Status"):
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=150)
        self.recent_tree.pack(fill="x")
        
        # Initial load
        self.refresh_dashboard()
    
    def build_search_tab(self):
        """New Search and Export Tab"""
        search_tab = ttk.Frame(self.search_tab, padding=15)
        search_tab.pack(fill="both", expand=True)
        
        # Search Section
        ttk.Label(search_tab, text="🔍 Advanced Search", 
                 font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))
        
        search_frame = ttk.Frame(search_tab)
        search_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(search_frame, text="Search Books:").pack(side="left", padx=(0, 10))
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        ttk.Button(search_frame, text="Search", 
                  command=self.perform_search).pack(side="left", padx=(0, 10))
        ttk.Button(search_frame, text="Clear", 
                  command=self.clear_search).pack(side="left")
        
        # Search Results
        ttk.Label(search_tab, text="Search Results", 
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.search_tree = ttk.Treeview(search_tab, 
                                       columns=("ID", "Title", "Author", "Year", "ISBN", "Copies"), 
                                       show="headings")
        for col in ("ID", "Title", "Author", "Year", "ISBN", "Copies"):
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=100)
        self.search_tree.pack(fill="both", expand=True, pady=(0, 20))
        
        # Export Section
        ttk.Label(search_tab, text="📤 Export Data", 
                 font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 10))
        
        export_frame = ttk.Frame(search_tab)
        export_frame.pack(fill="x")
        
        ttk.Button(export_frame, text="Export Books to CSV", 
                  command=self.export_books, width=20).pack(side="left", padx=(0, 10))
        ttk.Button(export_frame, text="Export Issues to CSV", 
                  command=self.export_issues, width=20).pack(side="left")
    
    def add_form_row(self, frame, label_text, row):
        ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky="w")
        entry = ttk.Entry(frame, width=30)
        entry.grid(row=row, column=1, sticky="w", pady=4)
        return entry
    
    # ===== ENHANCED FUNCTIONALITIES =====
    
    def update_user_display(self):
        """Update user info in header"""
        user = self.auth.get_current_user()
        if user:
            self.user_label.config(text=f"👤 {user['name']} ({user['role'].title()})")
    
    def logout(self):
        """Logout and return to login screen"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.auth.logout()
            self.destroy()
            # Restart application
            app = LibraryApp()
            app.mainloop()
    
    def refresh_dashboard(self):
        """Refresh analytics dashboard"""
        analytics = self.db.get_library_analytics()
        
        # Clear existing stats cards
        for widget in self.stats_cards_frame.winfo_children():
            widget.destroy()
        
        # Create stats cards
        stats_data = [
            ("📚 Total Books", analytics['total_books'], "#3b82f6"),
            ("📖 Total Issues", analytics['total_issues'], "#10b981"), 
            ("🔴 Active Issues", analytics['active_issues'], "#ef4444"),
            ("📊 Popular Tracked", len(analytics['popular_books']), "#f59e0b")
        ]
        
        for i, (title, value, color) in enumerate(stats_data):
            card = self.create_stat_card(self.stats_cards_frame, title, value, color)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="ew", ipadx=10)
            self.stats_cards_frame.grid_columnconfigure(i, weight=1)
        
        # Popular books
        for item in self.popular_tree.get_children():
            self.popular_tree.delete(item)
        
        for book in analytics['popular_books']:
            self.popular_tree.insert("", "end", values=(
                book['title'], book['author'], book['times_borrowed']
            ))
        
        # Recent activity
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        
        for issue in analytics['recent_issues']:
            status = "📗 Returned" if issue['return_date'] else "📕 Issued"
            self.recent_tree.insert("", "end", values=(
                issue['title'], issue['borrower'], 
                issue['issue_date'], status
            ))
    
    def create_stat_card(self, parent, title, value, color):
        """Create a beautiful stat card"""
        card = tk.Frame(parent, bg=color, relief="raised", bd=2)
        
        title_label = tk.Label(card, text=title, bg=color, fg="white", 
                              font=("Arial", 10, "bold"))
        title_label.pack(padx=15, pady=(10, 0))
        
        value_label = tk.Label(card, text=value, bg=color, fg="white",
                              font=("Arial", 18, "bold"))
        value_label.pack(padx=15, pady=(0, 10))
        
        return card
    
    def perform_search(self):
        """Perform advanced search"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Search", "Please enter a search term.")
            return
        
        results = self.db.search_books(search_term)
        
        # Clear previous results
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        if results:
            for book in results:
                self.search_tree.insert("", "end", values=(
                    book['id'], book['title'], book['author'], 
                    book['year'], book['isbn'], book['copies']
                ))
            messagebox.showinfo("Search Results", f"Found {len(results)} books matching '{search_term}'")
        else:
            messagebox.showinfo("Search Results", f"No books found matching '{search_term}'")
    
    def clear_search(self):
        """Clear search results"""
        self.search_entry.delete(0, tk.END)
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
    
    def export_books(self):
        """Export books to CSV"""
        csv_data = self.db.export_books_to_csv()
        filename = f"library_books_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        messagebox.showinfo("Export Successful", 
                          f"Books exported successfully to:\n{filename}")
    
    def export_issues(self):
        """Export issues to CSV"""
        csv_data = self.db.export_issues_to_csv()
        filename = f"library_issues_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(csv_data)
        
        messagebox.showinfo("Export Successful", 
                          f"Issues exported successfully to:\n{filename}")
    
    # ===== YOUR ORIGINAL CORE FUNCTIONS (UNCHANGED) =====
    
    def add_book(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Validation", "Title is required.")
            return
        author = self.author_entry.get().strip()
        year = self.year_entry.get().strip()
        isbn = self.isbn_entry.get().strip()
        try:
            copies = int(self.copies_spin.get())
        except ValueError:
            messagebox.showwarning("Validation", "Copies must be a number.")
            return
        
        result = self.db.add_book(title, author, year, isbn, copies)
        if result:
            messagebox.showinfo("Success", f"Book '{title}' added successfully!")
            self.clear_form()
            self.refresh_books()
            self.refresh_dashboard()  # Refresh analytics too
        else:
            messagebox.showerror("Error", "Failed to add book to database.")

    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.isbn_entry.delete(0, tk.END)
        self.copies_spin.set(1)

    def refresh_books(self):
        for r in self.books_tree.get_children():
            self.books_tree.delete(r)
        books = self.db.get_all_books()
        for b in books:
            self.books_tree.insert("", "end", values=(
                b["id"], b["title"], b["author"], b["year"], b["isbn"], b["copies"]
            ))

    def refresh_issued(self):
        for r in self.issued_tree.get_children():
            self.issued_tree.delete(r)
        issued_books = self.db.get_all_issued_books()
        for i in issued_books:
            return_date = i["return_date"] if i["return_date"] else "Not Returned"
            self.issued_tree.insert("", "end", values=(
                i["issue_id"], i["book_id"], i["title"], i["borrower"], 
                i["issue_date"], return_date
            ))

    def on_book_select(self, event):
        sel = self.books_tree.selection()
        if not sel:
            return
        book_id = self.books_tree.item(sel[0], "values")[0]
        self.sel_book_id_lbl.config(text=str(book_id))

    def issue_book(self):
        book_id_label = self.sel_book_id_lbl.cget("text")
        if book_id_label == "-":
            messagebox.showwarning("Select Book", "Select a book to issue.")
            return
        borrower = self.borrower_entry.get().strip()
        if not borrower:
            messagebox.showwarning("Validation", "Borrower name required.")
            return

        book_id = int(book_id_label)
        book = self.db.get_book_by_id(book_id)
        if not book:
            messagebox.showerror("Error", "Book not found!")
            return
            
        if book["copies"] <= 0:
            messagebox.showwarning("Unavailable", "No copies available.")
            return
        
        issue_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = self.db.issue_book(book_id, book["title"], borrower, issue_date)
        
        if result:
            self.db.update_book_copies(book_id, book["copies"] - 1)
            self.borrower_entry.delete(0, tk.END)
            messagebox.showinfo("Success", f"Book '{book['title']}' issued to {borrower}!")
            self.refresh_books()
            self.refresh_issued()
            self.refresh_dashboard()  # Refresh analytics too
        else:
            messagebox.showerror("Error", "Failed to issue book.")

    def return_selected(self):
        sel = self.issued_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select an issued book to return.")
            return
        
        issue_id = int(self.issued_tree.item(sel[0], "values")[0])
        issued_book = self.db.get_issued_book_by_id(issue_id)
        if not issued_book:
            messagebox.showerror("Error", "Issued book record not found!")
            return
            
        if issued_book["return_date"]:
            messagebox.showinfo("Returned", "This book is already returned.")
            return
        
        return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = self.db.return_book(issue_id, return_date)
        
        if result:
            book = self.db.get_book_by_id(issued_book["book_id"])
            if book:
                self.db.update_book_copies(book["id"], book["copies"] + 1)
            messagebox.showinfo("Success", "Book returned successfully!")
            self.refresh_books()
            self.refresh_issued()
            self.refresh_dashboard()  # Refresh analytics too
        else:
            messagebox.showerror("Error", "Failed to return book.")

if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()