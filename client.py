from socket import *
from tkinter import *
from tkinter import messagebox

# Manager Screen
class ManagerScreen(Frame):
    def __init__(self, client):
        Frame.__init__(self)
        self.pack()
        self.client = client
        self.master.title('Manager Panel')

        # Frame for the heading
        self.frame0 = Frame(self)
        self.frame0.pack(padx=2, pady=2)

        self.headingLabel = Label(self.frame0, justify=CENTER, text="REPORTS")
        self.headingLabel.pack(padx=2, pady=2)

        # Frame for the reports choice
        self.reports = [
            'What is the most rented book?',
            'Which librarian has the highest number of operations?',
            'What is the total generated revenue by the library?',
            'What is the average rental period for "Harry Potter" book?'
        ]
        self.report_choice = StringVar()
        self.report_choice.set(self.reports[0])

        # Frame for the reports choice
        for i, report in enumerate(self.reports):
            self.frame = Frame(self)
            self.frame.pack(fill=X)
            radio_button = Radiobutton(self.frame, justify=LEFT, text="(" + str(i + 1) + ") " + report, value=report,
                                       variable=self.report_choice)
            radio_button.pack(side=LEFT, fill=X)

        # Frame for the buttons
        self.frame1 = Frame(self)
        self.frame1.pack(padx=5, pady=5)

        # Create and Close buttons
        self.create_button = Button(self.frame1, text="Create", command=self.showReport)
        self.create_button.pack(side=LEFT, padx=5, pady=5)

        self.close_button = Button(self.frame1, text="Close", command=self.close)
        self.close_button.pack(side=RIGHT, padx=5, pady=5)

    # Show the report
    def showReport(self):
        # Get the selected report
        selected_report = self.report_choice.get()

        # Send the report code to the server
        server_msg = 'report' + str(self.reports.index(selected_report) + 1)
        self.client.send(server_msg.encode())

        # Receive the report answers from the server
        server_response = self.client.recv(1024).decode()

        # Show the report answers in a message box
        answers = server_response.split(';')
        title = answers[0]
        message = "\n".join(answers[1:])
        messagebox.showinfo(title, message)

    # Close the connection
    def close(self):
        self.client.send("terminate".encode())
        self.client.close()
        self.master.destroy()

# Book class for the Librarian Screen
class Book:
    def __init__(self, book_id, title, author, frame):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.is_checked = BooleanVar()
        self.frame = frame

# Librarian Screen
class LibrarianScreen(Frame):
    def __init__(self, client, username):
        Frame.__init__(self)
        self.client = client
        self.username = username
        self.books = {}

        # Get the books from the server, their names authors and ids.
        self.getBooksFromServer()

        self.pack()
        self.master.title("Librarian Panel")

        # Frame for the heading
        self.frame1 = Frame(self)
        self.frame1.pack(padx=5, pady=5)

        self.headingLabel = Label(self.frame1, justify=CENTER, text="Books", font="Helvetica 16 bold")
        self.headingLabel.pack(padx=5, pady=5)

        # Frame for the books
        # Create a frame for each book
        # Add a label for the book name and author
        # Add a checkbox for the book
        for book in self.books.values():
            book.frame.pack(padx=5, fill=X)

            book_label = Label(book.frame, justify=LEFT, text=book.title + " by " + book.author, font="Helvetica 10")
            book_label.pack(side=LEFT, padx=5, fill=X)
            book_checkbox = Checkbutton(book.frame, anchor="e", text="", variable=book.is_checked)
            book_checkbox.pack(side=RIGHT, padx=5)

        # Frame for the date
        self.frame2 = Frame(self)
        self.frame2.pack(padx=5, pady=5)

        self.dateLabel = Label(self.frame2, text="Date (dd.mm.yyyy): ")
        self.dateLabel.pack(side=LEFT, padx=5, pady=5)

        self.dateEntry = Entry(self.frame2)
        self.dateEntry.pack(side=LEFT, padx=5, pady=5)

        # Frame for the client name
        self.frame3 = Frame(self)
        self.frame3.pack(padx=5, pady=5)

        self.clientNameLabel = Label(self.frame3, text="Client's Name: ")
        self.clientNameLabel.pack(side=LEFT, padx=5, pady=5)

        self.clientNameEntry = Entry(self.frame3)
        self.clientNameEntry.pack(side=LEFT, padx=5, pady=5)

        # Frame for the buttons
        self.frame4 = Frame(self)
        self.frame4.pack(padx=5, pady=5)

        self.rentButton = Button(self.frame4, text="Rent", command=self.rentBooks)
        self.rentButton.pack(side=LEFT, padx=5, pady=5)
        self.returnButton = Button(self.frame4, text="Return", command=self.returnBooks)
        self.returnButton.pack(side=LEFT, padx=5, pady=5)
        self.closeButton = Button(self.frame4, text="Close", command=self.close)
        self.closeButton.pack(side=LEFT, padx=5, pady=5)

    # Rent the selected books
    def rentBooks(self):
        msg = "rent;" + self.username + ";" + self.clientNameEntry.get() + ";" + self.dateEntry.get()
        # Get the selected books
        for book in self.books.values():
            if book.is_checked.get():
                msg += ";" + book.book_id
        self.client.send(msg.encode())

        server_msg = self.client.recv(1024).decode().split(';')

        # Show the appropriate message box according to the server response
        if server_msg[0] == "rentsuccess":
            messagebox.showinfo("Message", "Rent Successful!")

        elif server_msg[0] == "availabilityerror":

            error_msg = "Following books are not available:\n"
            # Get the names of the books that are not available
            for not_available_book_id in server_msg[1:]:
                book = self.books[not_available_book_id]
                error_msg += book.title + " by " + book.author + "\n"

            messagebox.showerror("Error", error_msg)

        elif server_msg[0] == "renterror":
            error_msg = "You have to return the following books first:\n"
            # Get the names of the books that the client has to return first
            for rented_book_id in server_msg[1:]:
                book = self.books[rented_book_id]
                error_msg += book.title + " by " + book.author + "\n"

            messagebox.showerror("Error", error_msg)

    # Return the selected books
    def returnBooks(self):
        msg = "return;" + self.username + ";" + self.clientNameEntry.get() + ";" + self.dateEntry.get()
        # Get the selected books
        for book in self.books.values():
            if book.is_checked.get():
                msg += ";" + book.book_id

        self.client.send(msg.encode())
        server_msg = self.client.recv(1024).decode().split(';')

        # Show the appropriate message box according to the server response
        if server_msg[0] == "returnsuccess":
            messagebox.showinfo("Message", "Return Successful!\nYour total cost is: " + server_msg[1] + " TL")

        elif server_msg[0] == "returnerror":
            if server_msg[1] == "-1":
                messagebox.showerror("Error", "You have not rented any books")
                return

            error_msg = "You have not rented the following books:\n"
            # Get the names of the books that the client has not rented
            for not_rented_book_id in server_msg[1:]:
                book = self.books[not_rented_book_id]
                error_msg += book.title + " by " + book.author + "\n"

            messagebox.showerror("Error", error_msg)

    # Close the connection
    def close(self):
        self.client.send("terminate".encode())
        self.client.close()
        self.master.destroy()

    # Get the books from the server
    def getBooksFromServer(self):
        client_msg = "getbooks;"
        self.client.send(client_msg.encode())

        server_msg = self.client.recv(1024).decode()

        # Get the books from the server, until the server sends "endofbooks"
        while server_msg != "endofbooks":
            server_msg = server_msg.split(';')

            if server_msg[0] == "sendingbooks":
                book_msg = server_msg[1].split(',')
                # Create a book object for each book
                self.books[book_msg[0]] = Book(book_msg[0], book_msg[1], book_msg[2], Frame(self))
                self.client.send("ack".encode())

            server_msg = self.client.recv(1024).decode()


# Login Screen
class ClientScreen(Frame):
    def __init__(self, client):
        Frame.__init__(self)
        self.client = client
        self.pack()

        self.master.title("Login")

        # Frame for username
        self.frame1 = Frame(self)
        self.frame1.pack(padx=5, pady=5)

        self.UserNameLabel = Label(self.frame1, text="Username")
        self.UserNameLabel.pack(side=LEFT, padx=5, pady=5)

        self.UserName = Entry(self.frame1)
        self.UserName.pack(side=LEFT, padx=5, pady=5)

        # Frame for password
        self.frame2 = Frame(self)
        self.frame2.pack(padx=5, pady=5)

        self.PasswordLabel = Label(self.frame2, text="Password")
        self.PasswordLabel.pack(side=LEFT, padx=5, pady=5)

        self.Password = Entry(self.frame2, show="*")
        self.Password.pack(side=LEFT, padx=5, pady=5)

        # Frame for login button
        self.frame3 = Frame(self)
        self.frame3.pack(padx=5, pady=5)

        self.LoginButton = Button(self.frame3, text="Login", command=self.login)
        self.LoginButton.pack(padx=5, pady=5)

    # Show a message box if the login failed
    def loginFailed(self):
        messagebox.showerror('Error', 'Failed to login')

    # Handle the manager login
    def handleManagerLogin(self, username):
        # Create a manager screen
        manager = ManagerScreen(self.client)
        manager.mainloop()

    # Handle the librarian login
    def handleLibrarianLogin(self, username):
        # Create a librarian screen
        librarian = LibrarianScreen(self.client, username)
        librarian.mainloop()

    # Send the login information to the server
    def login(self):
        client_msg = "login;"
        username = self.UserName.get() + ";"
        password = self.Password.get() + ";"
        client_msg += username + password
        print(client_msg)
        self.client.send(client_msg.encode())

        server_msg = self.client.recv(1024).decode()
        print(server_msg)

        # Show a message box if the login failed
        if server_msg == "loginfailure":
            self.loginFailed()
            return

        server_msg = server_msg.split(';')

        # Handle the login according to the user role
        if server_msg[0] == "loginsuccess":
            username = server_msg[1]
            user_role = server_msg[-1]
            print(f"Login success: {username} {user_role}")

            self.destroy()
            if user_role == "manager":
                self.handleManagerLogin(username)
            elif user_role == "librarian":
                self.handleLibrarianLogin(username)


if __name__ == "__main__":

    HOST = "127.0.0.1"
    PORT = 6000
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((HOST, PORT))

    # Receive the connection success message from the server
    while True:
        data = client.recv(1024).decode()
        if data == "connectionsuccess":
            break

    window = ClientScreen(client)
    window.mainloop()

    print("Terminating connection")
    try:
        client.send("terminate".encode())
        client.close()
    except Exception as e:
        print(f"Error terminating connection: {e}")
