import os
from dotenv import load_dotenv
import mysql.connector as mys
from mysql.connector import Error
from datetime import date, timedelta

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

# =========================================================
# CONSTANTS
# =========================================================

LOAN_DAYS = 7
FINE_PER_DAY = 5

# =========================================================
# DATABASE CONNECTION
# =========================================================

try:

    mycon = mys.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        autocommit=False
    )

    mycur = mycon.cursor(buffered=True)

    if mycon.is_connected():
        print("\nDatabase Connected Successfully.\n")

except Error as e:
    print("Database Connection Error:", e)
    exit()

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def line():
    print("." * 120)


def heading(title):
    print("\n" + "=" * 120)
    print(title.center(120))
    print("=" * 120)


def pause():
    input("\nPress ENTER to continue...")


def clear_transaction():

    if mycon.in_transaction:
        mycon.rollback()


def print_rows(headers, rows, widths):

    total = sum(widths)

    print("-" * total)

    for header, width in zip(headers, widths):
        print(f"{header:<{width}}", end="")

    print()
    print("-" * total)

    for row in rows:

        for value, width in zip(row, widths):
            print(f"{str(value):<{width}}", end="")

        print()

# =========================================================
# SEARCH BOOK
# =========================================================

def search_book():

    heading("BOOK SEARCH MENU")

    while True:

        a = input(
            "\nEnter Book ID or Book Name\n"
            "*   -> Show All Books\n"
            "$   -> Available Books\n"
            "$$  -> Issued Books\n"
            "EXIT -> Main Menu\n\n"
            "Enter Choice : "
        ).strip()

        if a.upper() == "EXIT":
            break

        try:

            # SHOW ALL BOOKS
            if a == "*":

                query = """
                SELECT
                    b.id,
                    b.name,
                    b.author,
                    CASE
                        WHEN EXISTS (
                            SELECT 1
                            FROM issued_books ib
                            WHERE ib.book_id = b.id
                            AND ib.return_date IS NULL
                        )
                        THEN 'Issued'
                        ELSE 'Available'
                    END AS status
                FROM books b
                """

                mycur.execute(query)

            # AVAILABLE BOOKS
            elif a == "$":

                query = """
                SELECT
                    b.id,
                    b.name,
                    b.author,
                    'Available'
                FROM books b
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM issued_books ib
                    WHERE ib.book_id = b.id
                    AND ib.return_date IS NULL
                )
                """

                mycur.execute(query)

            # ISSUED BOOKS
            elif a == "$$":

                query = """
                SELECT
                    b.id,
                    b.name,
                    b.author,
                    CONCAT('Issued To User ID ', ib.user_id)
                FROM books b
                JOIN issued_books ib
                    ON b.id = ib.book_id
                WHERE ib.return_date IS NULL
                """

                mycur.execute(query)

            # SEARCH BY ID
            elif a.isdigit():

                query = """
                SELECT
                    b.id,
                    b.name,
                    b.author,
                    CASE
                        WHEN EXISTS (
                            SELECT 1
                            FROM issued_books ib
                            WHERE ib.book_id = b.id
                            AND ib.return_date IS NULL
                        )
                        THEN 'Issued'
                        ELSE 'Available'
                    END AS status
                FROM books b
                WHERE b.id = %s
                """

                mycur.execute(query, (int(a),))

            # SEARCH BY NAME
            else:

                query = """
                SELECT
                    b.id,
                    b.name,
                    b.author,
                    CASE
                        WHEN EXISTS (
                            SELECT 1
                            FROM issued_books ib
                            WHERE ib.book_id = b.id
                            AND ib.return_date IS NULL
                        )
                        THEN 'Issued'
                        ELSE 'Available'
                    END AS status
                FROM books b
                WHERE b.name LIKE %s
                """

                mycur.execute(query, ('%' + a + '%',))

            data = mycur.fetchall()

            if data:

                headers = ["ID", "BOOK NAME", "AUTHOR", "STATUS"]
                widths = [10, 40, 40, 30]

                print_rows(headers, data, widths)

            else:
                print("\nNo Book Found.")

        except Error as e:
            print("Error:", e)

        line()

# =========================================================
# SEARCH USER
# =========================================================

def search_user():

    heading("USER SEARCH MENU")

    while True:

        a = input(
            "\nEnter User ID or User Name\n"
            "*   -> Show All Users\n"
            "$   -> Users Without Books\n"
            "$$  -> Users With Books\n"
            "EXIT -> Main Menu\n\n"
            "Enter Choice : "
        ).strip()

        if a.upper() == "EXIT":
            break

        try:

            # ALL USERS
            if a == "*":

                query = """
                SELECT id, name, phone_number
                FROM users
                """

                mycur.execute(query)

            # USERS WITHOUT BOOKS
            elif a == "$":

                query = """
                SELECT u.id, u.name, u.phone_number
                FROM users u
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM issued_books ib
                    WHERE ib.user_id = u.id
                    AND ib.return_date IS NULL
                )
                """

                mycur.execute(query)

            # USERS WITH BOOKS
            elif a == "$$":

                query = """
                SELECT DISTINCT
                    u.id,
                    u.name,
                    u.phone_number
                FROM users u
                JOIN issued_books ib
                    ON u.id = ib.user_id
                WHERE ib.return_date IS NULL
                """

                mycur.execute(query)

            # SEARCH BY ID
            elif a.isdigit():

                query = """
                SELECT id, name, phone_number
                FROM users
                WHERE id = %s
                """

                mycur.execute(query, (int(a),))

            # SEARCH BY NAME
            else:

                query = """
                SELECT id, name, phone_number
                FROM users
                WHERE name LIKE %s
                """

                mycur.execute(query, ('%' + a + '%',))

            data = mycur.fetchall()

            if data:

                headers = ["ID", "NAME", "PHONE NUMBER"]
                widths = [10, 40, 20]

                print_rows(headers, data, widths)

            else:
                print("\nNo User Found.")

        except Error as e:
            print("Error:", e)

        line()

# =========================================================
# ISSUE BOOK
# =========================================================

def issue_book():

    heading("ISSUE BOOK MENU")

    while True:

        book_id = input("\nEnter Book ID (EXIT to stop): ").strip()

        if book_id.upper() == "EXIT":
            break

        user_id = input("Enter User ID : ").strip()

        if user_id.upper() == "EXIT":
            break

        if not book_id.isdigit() or not user_id.isdigit():
            print("Please Enter Valid Numeric IDs.")
            line()
            continue

        try:

            clear_transaction()

            # CHECK BOOK EXISTS
            query = """
            SELECT id
            FROM books
            WHERE id = %s
            """

            mycur.execute(query, (int(book_id),))
            book = mycur.fetchone()

            if not book:
                print("Book Does Not Exist.")
                line()
                continue

            # CHECK IF BOOK IS ALREADY ISSUED
            query = """
            SELECT 1
            FROM issued_books
            WHERE book_id = %s
            AND return_date IS NULL
            """

            mycur.execute(query, (int(book_id),))

            if mycur.fetchone():
                print("Book Already Issued.")
                line()
                continue

            # CHECK USER EXISTS
            query = """
            SELECT id
            FROM users
            WHERE id = %s
            """

            mycur.execute(query, (int(user_id),))
            user = mycur.fetchone()

            if not user:
                print("User Does Not Exist.")
                line()
                continue

            issue_date = date.today()
            due_date = issue_date + timedelta(days=LOAN_DAYS)

            # INSERT ISSUE RECORD
            query = """
            INSERT INTO issued_books(
                user_id,
                book_id,
                issue_date,
                due_date
            )
            VALUES(%s, %s, %s, %s)
            """

            mycur.execute(
                query,
                (
                    int(user_id),
                    int(book_id),
                    issue_date,
                    due_date
                )
            )

            mycon.commit()

            print("\nBook Issued Successfully.")
            print("Due Date:", due_date)

        except Error as e:

            mycon.rollback()
            print("Error:", e)

        line()

# =========================================================
# RETURN BOOK
# =========================================================

def return_book():

    heading("RETURN BOOK MENU")

    while True:

        book_id = input("\nEnter Book ID (EXIT to stop): ").strip()

        if book_id.upper() == "EXIT":
            break

        if not book_id.isdigit():
            print("Please Enter Valid Book ID.")
            line()
            continue

        try:

            clear_transaction()

            query = """
            SELECT issue_id, due_date
            FROM issued_books
            WHERE book_id = %s
            AND return_date IS NULL
            """

            mycur.execute(query, (int(book_id),))
            data = mycur.fetchone()

            if not data:
                print("Book Was Not Issued.")
                line()
                continue

            issue_id = data[0]
            due_date = data[1]

            today = date.today()

            # UPDATE RETURN DATE
            query = """
            UPDATE issued_books
            SET return_date = %s
            WHERE issue_id = %s
            """

            mycur.execute(query, (today, issue_id))

            mycon.commit()

            fine = 0

            if today > due_date:
                days_late = (today - due_date).days
                fine = days_late * FINE_PER_DAY

            print("\nBook Returned Successfully.")

            if fine > 0:
                print(f"Late Fine : ₹{fine}")

        except Error as e:

            mycon.rollback()
            print("Error:", e)

        line()

# =========================================================
# ADD BOOK
# =========================================================

def add_book():

    heading("ADD BOOK MENU")

    while True:

        name = input("\nEnter Book Name (EXIT to stop): ").strip()

        if name.upper() == "EXIT":
            break

        if not name:
            print("Book Name Cannot Be Empty.")
            continue

        author = input("Enter Author Name : ").strip()

        if author.upper() == "EXIT":
            break

        if not author:
            print("Author Name Cannot Be Empty.")
            continue

        category = input("Enter Category : ").strip()

        if not category:
            print("Category Cannot Be Empty.")
            continue

        try:

            query = """
            INSERT INTO books(name, author, category)
            VALUES(%s, %s, %s)
            """

            mycur.execute(
                query,
                (
                    name.title(),
                    author.title(),
                    category.title()
                )
            )

            mycon.commit()

            print("\nBook Added Successfully.")

        except Error as e:
            print("Error:", e)

        line()

# =========================================================
# ADD USER
# =========================================================

def add_user():

    heading("ADD USER MENU")

    while True:

        name = input("\nEnter User Name (EXIT to stop): ").strip()

        if name.upper() == "EXIT":
            break

        if not name:
            print("User Name Cannot Be Empty.")
            continue

        phone = input("Enter Phone Number : ").strip()

        if phone.upper() == "EXIT":
            break

        if not phone.isdigit() or len(phone) != 10:
            print("Invalid Phone Number.")
            line()
            continue

        try:

            query = """
            INSERT INTO users(name, phone_number)
            VALUES(%s, %s)
            """

            mycur.execute(
                query,
                (
                    name.title(),
                    phone
                )
            )

            mycon.commit()

            print("\nUser Added Successfully.")

        except Error as e:
            print("Error:", e)

        line()

# =========================================================
# DELETE BOOK
# =========================================================

def delete_book():

    heading("DELETE BOOK MENU")

    book_id = input("\nEnter Book ID : ").strip()

    if not book_id.isdigit():
        print("Invalid Book ID.")
        return

    try:

        # CHECK ACTIVE ISSUE
        query = """
        SELECT 1
        FROM issued_books
        WHERE book_id = %s
        AND return_date IS NULL
        """

        mycur.execute(query, (int(book_id),))

        if mycur.fetchone():
            print("Cannot Delete. Book Is Currently Issued.")
            return

        query = """
        DELETE FROM books
        WHERE id = %s
        """

        mycur.execute(query, (int(book_id),))
        mycon.commit()

        if mycur.rowcount > 0:
            print("Book Deleted Successfully.")
        else:
            print("Book Not Found.")

    except Error as e:
        print("Error:", e)

    line()

# =========================================================
# DELETE USER
# =========================================================

def delete_user():

    heading("DELETE USER MENU")

    user_id = input("\nEnter User ID : ").strip()

    if not user_id.isdigit():
        print("Invalid User ID.")
        return

    try:

        # CHECK ACTIVE ISSUE
        query = """
        SELECT 1
        FROM issued_books
        WHERE user_id = %s
        AND return_date IS NULL
        """

        mycur.execute(query, (int(user_id),))

        if mycur.fetchone():
            print("Cannot Delete. User Has Issued Books.")
            return

        query = """
        DELETE FROM users
        WHERE id = %s
        """

        mycur.execute(query, (int(user_id),))
        mycon.commit()

        if mycur.rowcount > 0:
            print("User Deleted Successfully.")
        else:
            print("User Not Found.")

    except Error as e:
        print("Error:", e)

    line()

# =========================================================
# MAIN MENU
# =========================================================

def main_menu():

    menu = {
        "1": search_book,
        "2": search_user,
        "3": issue_book,
        "4": return_book,
        "5": add_book,
        "6": add_user,
        "7": delete_book,
        "8": delete_user
    }

    while True:

        heading("LIBRARY MANAGEMENT SYSTEM")

        print("""
1. Search Book
2. Search User
3. Issue Book
4. Return Book
5. Add Book
6. Add User
7. Delete Book
8. Delete User
9. Exit
""")

        choice = input("Enter Your Choice : ").strip()

        if choice == "9":
            break

        elif choice in menu:
            menu[choice]()

        else:
            print("Invalid Choice.")

        pause()

# =========================================================
# START PROGRAM
# =========================================================

if __name__ == "__main__":

    try:
        main_menu()

    finally:

        if mycur:
            mycur.close()

        if mycon:
            mycon.close()

        print("\nDatabase Connection Closed.")