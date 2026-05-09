import mysql.connector as mys

# DATABASE CONNECTION
mycon = mys.connect(
    host='HOST',
    user='USERNAME',
    password='YOUR PASSWORD',
    database='LIBRARY_MANAGEMENT_SYSTEM'
)

mycur = mycon.cursor(buffered=True)


# FUNCTION FOR SEARCHING A BOOK
def search_book():

    a = input(
        "Enter Book ID or Book Name : \n"
        "#      '*' to see all books      # \n"
        "# '$' to see all available books # \n"
        "#  '$$' to see all issued books  # \n"
    )

    while True:

        if a.upper() == 'EXIT':
            break

        elif a == '*':
            query = "select * from books"

        elif a == '$':
            query = "select * from books where issued_to IS NULL"

        elif a == '$$':
            query = "select * from books where issued_to IS NOT NULL"

        elif a.isnumeric():
            query = "select * from books where id = {}".format(int(a))

        else:
            query = "select * from books where name = '{}'".format(a)

        mycur.execute(query)
        dt = mycur.fetchall()

        if dt != []:

            print('-' * 130)
            print('%5s' % 'ID',
                  '%30s' % 'Name',
                  '%30s' % "Author Name",
                  '%20s' % 'Issued To')

            print('-' * 130)

            for R in dt:
                print('%5s' % R[0],
                      '%30s' % R[1],
                      '%30s' % R[2],
                      '%20s' % R[3])

            break

        else:
            print('No such book found.\n')
            print('.' * 85)
            a = input('Enter a valid Book ID or Book Name : ')


# FUNCTION TO SEARCH USER
def search_user():

    a = input(
        'Enter User ID or User Name : \n'
        "#             '*' to see all users              # \n"
        "# '$' to see all users who haven’t issued books # \n"
        "#  '$$' to see all users who have issued books  # \n"
    )

    while True:

        if a.upper() == 'EXIT':
            break

        elif a == '*':
            query = "select * from users"

        elif a == '$':
            query = "select * from users where books_assigned IS NULL"

        elif a == '$$':
            query = "select * from users where books_assigned IS NOT NULL"

        elif a.isnumeric():
            query = "select * from users where id = {}".format(int(a))

        else:
            query = "select * from users where name = '{}'".format(a)

        mycur.execute(query)
        dt = mycur.fetchall()

        if dt != []:

            print('-' * 100)
            print('%5s' % 'ID',
                  '%30s' % 'Name',
                  '%20s' % 'Phone Number',
                  '%20s' % 'Books Assigned')

            print('-' * 100)

            for R in dt:
                print('%5s' % R[0],
                      '%30s' % R[1],
                      '%20s' % R[2],
                      '%20s' % R[3])

            break

        else:
            print('No such User found.\n')
            print('.' * 85)
            a = input('Enter a Valid User ID or User Name : ')


# FUNCTION FOR ISSUING A BOOK
def issue_book():

    while True:

        a = input('Enter Book ID : ')

        if a.upper() == 'EXIT':
            break

        b = input('Enter User ID : ')

        if b.upper() == 'EXIT':
            break

        query = "select id from books where issued_to IS NULL"
        mycur.execute(query)
        dt = mycur.fetchall()

        query = "select id from users where books_assigned IS NULL"
        mycur.execute(query)
        ut = mycur.fetchall()

        if a.isnumeric() and b.isnumeric():

            if (int(a),) in dt and (int(b),) in ut:

                query = "update books set issued_to = {} where id = {}".format(int(b), int(a))
                mycur.execute(query)

                query = "update users set books_assigned = {} where id = {}".format(int(a), int(b))
                mycur.execute(query)

                mycon.commit()

                query = """
                select books.name, users.name
                from books, users
                where books.issued_to = users.id
                and books.id = {}
                """.format(a)

                mycur.execute(query)
                dt = mycur.fetchone()

                print(dt[0], 'is Issued to', dt[1])
                print('.' * 85)

            elif (int(b),) not in ut:

                print('User either not present or already has a book.')
                print('.' * 85)

            else:

                print('Sorry, the Book is unavailable.')
                print('.' * 85)

        else:

            print("Please Enter Numeric IDs or type 'EXIT'")
            print('.' * 85)


# FUNCTION FOR RETURNING A BOOK
def return_book():

    a = input('Enter Book ID : ')

    while True:

        if a.upper() == 'EXIT':
            break

        query = "select id from books where issued_to IS NOT NULL"
        mycur.execute(query)
        dt = mycur.fetchall()

        if a.isnumeric() and (int(a),) in dt:

            query = "update books set issued_to = NULL where id = {}".format(int(a))
            mycur.execute(query)

            query = "update users set books_assigned = NULL where books_assigned = {}".format(int(a))
            mycur.execute(query)

            mycon.commit()

            print('The Book is Returned.')
            break

        else:

            print('The Book was Not Issued.')
            print('.' * 85)
            a = input("Enter Book ID of an Issued Book : ")


# FUNCTION FOR ADDING BOOKS
def add_books():

    while True:

        nm = input('Enter Book Name : ').upper()

        if nm.upper() == 'EXIT':
            break

        an = input('Enter Author Name : ').title()

        if an.upper() == 'EXIT':
            break

        query = "insert into books(name, author) values('{}','{}')".format(nm, an)

        mycur.execute(query)
        mycon.commit()

        print('Book Added Successfully.')
        print('.' * 85)


# FUNCTION FOR ADDING USERS
def add_users():

    while True:

        nm = input('Enter User Name : ').capitalize()

        if nm.upper() == 'EXIT':
            break

        pn = input('Enter Phone Number : ')

        if pn.upper() == 'EXIT':
            break

        if pn.isnumeric() and len(pn) == 10:

            query = """
            insert into users(name, phone_number)
            values('{}','{}')
            """.format(nm, pn)

            mycur.execute(query)
            mycon.commit()

            print('User Added Successfully.')

        else:

            print('Please Enter Valid Phone Number.')

        print('.' * 85)


# MAIN MENU
def main_menu(n):

    while True:

        if n == 1:

            print('=' * 133)
            print(' ' * 60, 'BOOK SEARCH MENU\n')

            search_book()

            print('=' * 133)
            break

        elif n == 2:

            print('=' * 133)
            print(' ' * 60, 'USER SEARCH MENU\n')

            search_user()

            print('=' * 133)
            break

        elif n == 3:

            print('=' * 133)
            print(' ' * 60, 'ISSUE BOOK MENU\n')

            issue_book()

            print('=' * 133)
            break

        elif n == 4:

            print('=' * 133)
            print(' ' * 60, 'RETURN BOOK MENU\n')

            return_book()

            print('=' * 133)
            break

        elif n == 5:

            print('=' * 133)
            print(' ' * 60, 'ADD BOOKS MENU\n')

            add_books()

            print('=' * 133)
            break

        elif n == 6:

            print('=' * 133)
            print(' ' * 60, 'ADD USERS MENU\n')

            add_users()

            print('=' * 133)
            break

        else:

            n = int(input('Please Enter Valid Choice : '))


# MAIN PROGRAM
while True:

    print('=' * 133)

    print(' ' * 60, 'MAIN MENU')

    print(
        'Hey, What would you like to do?\n'
        ' [1] Search Book from Record\n'
        ' [2] Search User from Record\n'
        ' [3] Issue a Book\n'
        ' [4] Return a Book\n'
        ' [5] Add Books\n'
        ' [6] Add Users\n'
    )

    print(' ' * 40, "** Type 'EXIT' anytime to stop **\n")

    n = input('Enter Desired Number Option : ')

    if n.upper() == 'EXIT':
        break

    elif n.isnumeric():

        n = int(n)
        main_menu(n)

    else:

        print('Please Enter Valid Option.')

# CLOSE CONNECTION
mycur.close()
mycon.close()
print("Connection Closed.")
