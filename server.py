import socket
import sys
from threading import *
from datetime import datetime


# Book class to store information related to books.
class Book:
    def __init__(self, book_id, title, author, cost, copies):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.cost = cost
        self.copies = copies


# Book Handler class to manage the copies of books
class BooksHandler:
    def __init__(self, books_file_name):
        self.books_file_name = books_file_name
        self.books = {}

        books_file = open_file("books.txt")
        # Read lines from the books_file and remove the newline character '\n' from each line.
        books_data = [x.replace("\n", "") for x in books_file.readlines()]

        for book in books_data:
            # Split each line into parts using a semi-colon as a separator.
            book_split = book.split(";")
            # Store the book's id and password in the books dictionary.
            self.books[book_split[0]] = Book(book_split[0], book_split[1], book_split[2], float(book_split[3]),
                                             int(book_split[4]))

        books_file.close()

    # Get the book from id
    def getBook(self, book_id):
        return self.books[book_id]

    # Check if the book have enough copies
    def isBookAvailable(self, book_id):
        return self.books[book_id].copies > 0

    # Increase the number of copies of the book
    def increaseCopies(self, book_id):
        self.books[book_id].copies += 1
        self.updateBooksFile()

    # Decrease the number of copies of the book
    def decreaseCopies(self, book_id):
        self.books[book_id].copies -= 1
        self.updateBooksFile()

    # Update the book file after changing the number of copies
    def updateBooksFile(self):
        books_file = open_file("books.txt", "w")
        for book in self.books.values():
            books_file.write(f"{book.book_id};{book.title};{book.author};{book.cost};{book.copies}\n")
        books_file.close()


# Rent class to manage a book's rent
class Rent:
    def __init__(self, book_id, username, rent_date, total_copies_rented):
        self.book_id = book_id
        self.username = username
        self.rent_date = rent_date
        self.total_copies_rented = total_copies_rented


# Operations Handler class to manage the operations of the library
class OperationsHandler:
    def __init__(self, operations_file_name, books_handler):
        self.operations_file_name = operations_file_name
        # Book Handler to manage the book copies
        self.books_handler = books_handler
        self.rents = {}

        operations_file = open_file(operations_file_name)
        # Read lines from the operations_file and remove the newline character '\n' from each line.
        operations_data = [x.replace("\n", "") for x in operations_file.readlines()]

        # Add rent information to the rents dictionary
        for operation in operations_data:
            # Split each line into parts using a semi-colon as a separator.
            operation_split = operation.split(";")
            if operation_split[0] == "rent":
                rentee = operation_split[2]
                if rentee not in self.rents:
                    self.rents[rentee] = {}
                date = operation_split[3]
                book_ids = operation_split[4:]

                for book_id in book_ids:
                    if book_id in self.rents[rentee]:
                        self.rents[rentee][book_id].total_copies_rented += 1
                        if date > self.rents[rentee][book_id].rent_date:
                            self.rents[rentee][book_id].rent_date = date
                    else:
                        self.rents[rentee][book_id] = Rent(book_id, rentee, date, 1)

        # Remove rent information from the rents dictionary for those who have returned their books.
        for operation in operations_data:
            # Split each line into parts using a semi-colon as a separator.
            operation_split = operation.split(";")
            if operation_split[0] == "return":
                rentee = operation_split[2]
                book_ids = operation_split[5:]
                if rentee not in self.rents:
                    continue
                for book_id in book_ids:
                    if book_id in self.rents[rentee]:
                        self.rents[rentee][book_id].total_copies_rented -= 1
                        if self.rents[rentee][book_id].total_copies_rented == 0:
                            del self.rents[rentee][book_id]

        operations_file.close()

    # Check if the client has rented any books
    def hasRents(self, username):
        if username not in self.rents:
            return False
        return len(self.rents[username]) > 0

    # Return the books and calculate the cost
    def returnBooks(self, username, librarian, date, book_ids):
        # The client does not exist.
        if username not in self.rents:
            return "returnerror;-1"

        # List of books that the client did not rent, but has selected.
        books_not_to_return = []
        for book_id in book_ids:
            if book_id not in self.rents[username]:
                books_not_to_return.append(book_id)

        # The client has selected books that he did not rent.
        if len(books_not_to_return) > 0:
            msg = "returnerror"
            for book_id in books_not_to_return:
                msg += ";" + book_id
            return msg

        total_cost = 0
        return_date = datetime.strptime(date, "%d.%m.%Y").date()

        # Calculate the cost of the books, that  the client is going to return.
        for book_id in book_ids:
            rent = self.books_handler.getBook(book_id).cost
            rent_date = datetime.strptime(self.rents[username][book_id].rent_date, "%d.%m.%Y").date()
            days = (return_date - rent_date).days
            # If the client return the book on same day, still apply 1 day cost.
            if days == 0:
                days = 1
            cost = rent * days
            total_cost += float(cost)
            self.books_handler.increaseCopies(book_id)
            del self.rents[username][book_id]

        # Add the return operation to the operations file.
        self.addReturnOperationToFile(librarian, username, date, total_cost, book_ids)

        return "returnsuccess;" + str(total_cost)

    # Add the return operation to the operations file.
    def addReturnOperationToFile(self, librarian, username, return_date, cost, book_ids):
        operations_file = open_file(self.operations_file_name, "a")
        books = ";".join(book_ids)
        operations_file.write(f"\nreturn;{librarian};{username};{return_date};{cost};{books}")
        operations_file.close()

    # Rent the books
    def rentBooks(self, username, librarian, date, book_ids):
        # List of books that are not available. (copies = 0)
        not_available_books = []
        for book_id in book_ids:
            if not self.books_handler.isBookAvailable(book_id):
                not_available_books.append(book_id)

        # The client has selected books that are not available.
        if len(not_available_books) > 0:
            msg = "availabilityerror"
            for book_id in not_available_books:
                msg += ";" + book_id
            return msg

        # The client has already rented books, so he cannot rent more.
        if self.hasRents(username):
            msg = "renterror"
            for book_id in self.rents[username].keys():
                msg += ";" + book_id

            return msg
        else:
            self.rents[username] = {}

        # Rent the books and add the rent operation to the operations file.
        for book_id in book_ids:
            self.books_handler.decreaseCopies(book_id)
            self.rents[username][book_id] = Rent(book_id, username, date, 1)

        self.addRentOperationToFile(librarian, username, date, book_ids)
        return "rentsuccess"

    # Add the rent operation to the operations file.
    def addRentOperationToFile(self, librarian, username, date, book_ids):
        operations_file = open_file(self.operations_file_name, "a")
        book_ids_str = ";".join(book_ids)
        operations_file.write(f"\nrent;{librarian};{username};{date};{book_ids_str}")
        operations_file.close()

    # Generate the report
    def generateReport(self, report_num, avg_rental_book_id):
        operations_file = open_file(self.operations_file_name)
        operations_data = [x.replace("\n", "") for x in operations_file.readlines()]
        to_return = ""
        report1 = {}
        report2 = {}
        report3 = 0
        report4_rentees = {}
        report4_rentals = []

        # Go through the operations and generate the report.
        for operation in operations_data:
            operation_split = operation.split(";")
            librarian = operation_split[1]
            rentee = operation_split[2]
            date = operation_split[3]
            report2[librarian] = report2.get(librarian, 0) + 1


            if operation_split[0] == "rent":
                book_ids = operation_split[4:]
                for book_id in book_ids:
                    # If the book is not in the report1 dictionary, add it, to get the max value later.
                    report1[book_id] = report1.get(book_id, 0) + 1

                    if book_id == avg_rental_book_id:
                        if rentee not in report4_rentees:
                            # Store the rentee and the date of the rent. for Harry Potter, to calculate the average rental period.
                            report4_rentees[rentee] = []
                        report4_rentees[rentee] = date

            if operation_split[0] == "return":
                book_ids = operation_split[5:]
                # Add the cost of the books to the report3.
                report3 += float(operation_split[4])
                for book_id in book_ids:
                    if book_id == avg_rental_book_id:
                        # If the rentee has rented Harry Potter, calculate the average rental period.
                        if rentee in report4_rentees:
                            rent_date = datetime.strptime(report4_rentees[rentee], "%d.%m.%Y").date()
                            return_date = datetime.strptime(date, "%d.%m.%Y").date()
                            days = (return_date - rent_date).days

                            report4_rentals.append(days)

        # Generate the report for max rented books.
        if report_num == 1:
            max_value = max(report1.values())
            books_with_highest_rent = []
            for book_id in report1.keys():
                if report1[book_id] == max_value:
                    books_with_highest_rent.append(self.books_handler.getBook(book_id).title)

            to_return = "report1;" + ";".join(books_with_highest_rent)

        # Generate the report for the librarian with the highest number of operations.
        elif report_num == 2:
            max_value = max(report2.values())
            librarian_with_highest_ops = []
            for librarian in report2.keys():
                if report2[librarian] == max_value:
                    librarian_with_highest_ops.append(librarian)
            to_return = "report2;" + ";".join(librarian_with_highest_ops)

        # Generate the report for the total generated revenue by the library.
        elif report_num == 3:
            to_return = "report3;" + str(report3)

        # Generate the report for the average rental period for "Harry Potter" book.
        elif report_num == 4:
            if len(report4_rentals) == 0:
                to_return = "report4;0"
            else:
                avg_rental = sum(report4_rentals) / len(report4_rentals)
                to_return = "report4;" + str(avg_rental)

        operations_file.close()
        return to_return


thread_lock = RLock()

# Client Thread class to handle the client requests
class ClientThread(Thread):

    def __init__(self, client_socket, client_address, users, books, operations):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.users = users
        self.books = books
        self.operations = operations
        self.is_logined = False
        print("Connection from ", client_address)

    def run(self):
        # Send a connection success message to the client.
        self.client_socket.send("connectionsuccess".encode())

        # Handle the login process.
        to_run = self.handleLogin()

        # Handle the client requests.
        while to_run:
            client_msg = self.client_socket.recv(1024).decode()
            client_msg = client_msg.split(';')
            operation = client_msg[0]

            if operation == "getbooks":
                self.sendBooks()
            elif operation == "rent":
                self.handleRent(client_msg)
            elif operation == "return":
                self.handleReturn(client_msg)
            elif operation == "report1":
                self.handleReport(1)
            elif operation == "report2":
                self.handleReport(2)
            elif operation == "report3":
                self.handleReport(3)
            elif operation == "report4":
                self.handleReport(4)
            elif operation == "terminate":
                break

        print("Disconnected from ", self.client_address)
        self.client_socket.close()

    # Handle the login process.
    def handleLogin(self):
        # Keep looping until the client is logged in.
        while not self.is_logined:
            client_msg = self.client_socket.recv(1024).decode()
            login_info = client_msg.split(';')
            is_login = login_info[0]

            if is_login == "terminate":
                return False

            if is_login != "login":
                continue

            username = login_info[1]
            password = login_info[2]

            # Check if the username and password are correct.
            if username in users:
                if users[username][0] == password:
                    self.is_logined = True
                    send_msg = "loginsuccess;" + username + ";" + users[username][1]
                    self.client_socket.send(send_msg.encode())
                else:
                    self.client_socket.send("loginfailure".encode())
            else:
                self.client_socket.send("loginfailure".encode())

        return True

    # Send the book names, ids and authors to the client for display.
    def sendBooks(self):
        msg = "sendingbooks;"
        for book in self.books.books.values():
            acknowledged = False
            while not acknowledged:
                book_msg = msg + f"{book.book_id},{book.title},{book.author}"
                self.client_socket.send(book_msg.encode())
                client_msg = self.client_socket.recv(1024).decode()
                if client_msg == "ack":
                    acknowledged = True
        self.client_socket.send("endofbooks".encode())

    # Handle the rent process.
    def handleRent(self, client_msg):
        # Acquire lock to prevent other threads from accessing the dictionary and operations file.
        thread_lock.acquire()
        # Send the rent result to the client.
        msg = self.operations.rentBooks(client_msg[2], client_msg[1], client_msg[3], client_msg[4:])
        thread_lock.release()
        self.client_socket.send(msg.encode())

    # Handle the return process.
    def handleReturn(self, client_msg):
        # Acquire lock to prevent other threads from accessing the dictionary and operations file.
        thread_lock.acquire()
        # Send the return result to the client.
        msg = self.operations.returnBooks(client_msg[2], client_msg[1], client_msg[3], client_msg[4:])
        thread_lock.release()
        self.client_socket.send(msg.encode())

    # Handle the report process.
    def handleReport(self, report_num):

        # If the report is for the average rental period for "Harry Potter" book, get the book id.
        avg_rental_book_id = None
        if report_num == 4:
            for book in self.books.books.values():
                if book.title == "Harry Potter":
                    avg_rental_book_id = book.book_id
                    break

        # Acquire lock to prevent other threads from accessing the dictionary and operations file.
        thread_lock.acquire()
        # Send the report result to the client.
        msg = self.operations.generateReport(report_num, avg_rental_book_id)
        thread_lock.release()
        self.client_socket.send(msg.encode())


# Open the specified file in the specified mode.
def open_file(file_name, mode="r"):
    try:
        file = open(file_name, mode)  # Try to open the specified file in read mode
    except IOError:  # If an IOError occurs (file not found, permission issues, etc.)
        print("Error: could not open file: " + file_name)  # Print an error message
        sys.exit(1)  # Exit the program with a non-zero status code to indicate an error
    return file  # Return the file object if it was successfully opened

# Get the users data from the file, to store in the dictionary.
def getUserDataFromFile(file_name):
    users_file = open_file(file_name)
    users = {}
    # Read lines from the users_file and remove the newline character '\n' from each line.
    users_data = [x.replace("\n", "") for x in users_file.readlines()]

    # Iterate through the users' data.
    for user in users_data:
        # Split each line into parts using a semi-colon as a separator.
        user_split = user.split(";")
        # Store the user's id, password and role in the users dictionary.
        users[user_split[0]] = (user_split[1], user_split[2])
    users_file.close()

    return users


if __name__ == "__main__":
    users = getUserDataFromFile("users.txt")
    books = BooksHandler("books.txt")
    operations = OperationsHandler("operations.txt", books)

    HOST = "127.0.0.1"
    PORT = 6000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    print("Server is started")
    print("Waiting for connections")
    # Keep listening for incoming connections.
    while True:
        server.listen()
        client_socket, client_address = server.accept()
        # Create a new thread for each client.
        newThread = ClientThread(client_socket, client_address, users, books, operations)
        newThread.start()
