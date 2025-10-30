# database.py
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class Database:
    def __init__(self):
        self.config = DB_CONFIG
    
    def connect(self):
        """Create database connection"""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            print(f"❌ MySQL Connection Error: {e}")
            return None
    
    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        """Execute SQL query with proper error handling"""
        connection = None
        try:
            connection = self.connect()
            if connection and connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params or ())
                
                if fetch:
                    result = cursor.fetchall()
                elif fetch_one:
                    result = cursor.fetchone()
                else:
                    connection.commit()
                    result = cursor.lastrowid
                
                cursor.close()
                return result
                
        except Error as e:
            print(f"❌ MySQL Query Error: {e}")
            return None
        finally:
            if connection and connection.is_connected():
                connection.close()

class LibraryDB:
    def __init__(self):
        self.db = Database()
    
    # ===== CORE BOOK OPERATIONS =====
    def get_all_books(self):
        query = "SELECT * FROM books ORDER BY id"
        result = self.db.execute_query(query, fetch=True)
        return result or []
    
    def add_book(self, title, author, year, isbn, copies):
        query = """
        INSERT INTO books (title, author, year, isbn, copies) 
        VALUES (%s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (title, author, year, isbn, copies))
    
    def update_book_copies(self, book_id, copies):
        query = "UPDATE books SET copies = %s WHERE id = %s"
        return self.db.execute_query(query, (copies, book_id))
    
    def get_book_by_id(self, book_id):
        query = "SELECT * FROM books WHERE id = %s"
        return self.db.execute_query(query, (book_id,), fetch_one=True)
    
    def search_books(self, search_term):
        """Advanced search across title, author, and ISBN"""
        query = """
        SELECT * FROM books 
        WHERE title LIKE %s OR author LIKE %s OR isbn LIKE %s 
        ORDER BY id
        """
        search_pattern = f"%{search_term}%"
        return self.db.execute_query(query, (search_pattern, search_pattern, search_pattern), fetch=True) or []
    
    # ===== ISSUED BOOKS OPERATIONS =====
    def get_all_issued_books(self):
        query = "SELECT * FROM issued_books ORDER BY issue_id"
        result = self.db.execute_query(query, fetch=True)
        return result or []
    
    def issue_book(self, book_id, title, borrower, issue_date):
        query = """
        INSERT INTO issued_books (book_id, title, borrower, issue_date, return_date) 
        VALUES (%s, %s, %s, %s, NULL)
        """
        return self.db.execute_query(query, (book_id, title, borrower, issue_date))
    
    def return_book(self, issue_id, return_date):
        query = "UPDATE issued_books SET return_date = %s WHERE issue_id = %s"
        return self.db.execute_query(query, (return_date, issue_id))
    
    def get_issued_book_by_id(self, issue_id):
        query = "SELECT * FROM issued_books WHERE issue_id = %s"
        return self.db.execute_query(query, (issue_id,), fetch_one=True)
    
    # ===== ANALYTICS & REPORTS =====
    def get_library_analytics(self):
        """Get comprehensive library analytics for dashboard"""
        analytics = {}
        
        # Basic counts
        analytics['total_books'] = self.db.execute_query(
            "SELECT COUNT(*) as count FROM books", fetch_one=True)['count']
        
        analytics['total_issues'] = self.db.execute_query(
            "SELECT COUNT(*) as count FROM issued_books", fetch_one=True)['count']
        
        analytics['active_issues'] = self.db.execute_query(
            "SELECT COUNT(*) as count FROM issued_books WHERE return_date IS NULL", 
            fetch_one=True)['count']
        
        # Popular books (most issued)
        analytics['popular_books'] = self.db.execute_query("""
            SELECT b.title, b.author, COUNT(ib.issue_id) as times_borrowed
            FROM books b 
            LEFT JOIN issued_books ib ON b.id = ib.book_id 
            GROUP BY b.id, b.title, b.author
            ORDER BY times_borrowed DESC 
            LIMIT 5
        """, fetch=True) or []
        
        # Recent activity
        analytics['recent_issues'] = self.db.execute_query("""
            SELECT * FROM issued_books 
            ORDER BY issue_date DESC 
            LIMIT 5
        """, fetch=True) or []
        
        return analytics
    
    def export_books_to_csv(self):
        """Export all books to CSV format"""
        books = self.get_all_books()
        csv_data = "ID,Title,Author,Year,ISBN,Copies\n"
        for book in books:
            csv_data += f"{book['id']},{book['title']},{book['author']},{book['year']},{book['isbn']},{book['copies']}\n"
        return csv_data
    
    def export_issues_to_csv(self):
        """Export all issue records to CSV format"""
        issues = self.get_all_issued_books()
        csv_data = "IssueID,BookID,Title,Borrower,IssueDate,ReturnDate\n"
        for issue in issues:
            return_date = issue['return_date'] if issue['return_date'] else "Not Returned"
            csv_data += f"{issue['issue_id']},{issue['book_id']},{issue['title']},{issue['borrower']},{issue['issue_date']},{return_date}\n"
        return csv_data