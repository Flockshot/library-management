# Multithreaded TCP Library Management System

Built a multithreaded client-server library management system in Python that supports concurrent librarian and manager operations via a Tkinter GUI, with persistent file-based data storage and secure synchronization.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg?logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange.svg)
![Networking](https://img.shields.io/badge/Networking-TCP/IP_Sockets-00758F.svg)
![Concurrency](https://img.shields.io/badge/Concurrency-Multithreading-blue.svg)

---

## 🏛️ System Architecture

This application uses a client-server model designed to handle multiple users at once.

* **Server (`server.py`):** A multithreaded TCP server. It listens for incoming connections and spawns a new, dedicated thread for each client. This allows multiple librarians and managers to be connected and performing operations simultaneously. The server is responsible for all business logic, data validation, and file I/O.
* **Client (`client.py`):** A Tkinter-based GUI application that serves as the user-facing terminal. It connects to the server via TCP and provides a role-specific dashboard based on user authentication.
* **Data Persistence:** The system uses three flat files as its database:
    * `users.txt`: Stores user credentials and roles (librarian/manager).
    * `books.txt`: Manages the book inventory, including title, price, and available copies.
    * `operations.txt`: A transaction log that records every "rent" and "return" action for statistical analysis.

---

## ✨ Features & Functionality

### 1. User Authentication
* Users are greeted with a login screen that sends credentials to the server.
* The server validates the `username` and `password` against `users.txt`.
* On success, the server returns the user's `role`, and the client application dynamically loads the appropriate dashboard (Librarian or Manager).

![Image: Login Window GUI](.media/login_GUI.png)

### 2. Librarian Panel
* **Rent Books:** Librarians can select one or more books, enter a client's name and date, and submit a "rent" request.
* **Server-Side Validation (Rent):** The server enforces business rules:
    1.  **Availability Check:** Rejects the rental if any selected book has 0 copies available in `books.txt`.
    2.  **Outstanding Rentals Check:** Rejects the rental if the client has previously rented books that have not yet been returned (by checking `operations.txt`).
* **Return Books:** Librarians can select books, enter the client's name and date, and submit a "return" request.
* **Server-Side Validation (Return):** The server checks `operations.txt` to ensure the books were actually rented by that client and not already returned.
* **File Updates:** On a successful operation, the server updates `books.txt` (decrementing/incrementing `copiesAvailable`) and appends the transaction to `operations.txt`.

![Image: Librarian Panel GUI](.media/librarian_GUI.png)

### 3. Manager Panel
* **Generate Reports:** Managers can request 4 different statistical reports.
* The server computes these metrics on the fly from `operations.txt` and sends back the result to be displayed in a message box.
* **Available Reports:**
    1.  Most rented book(s) overall.
    2.  Librarian(s) with the highest number of operations.
    3.  Total generated revenue by the library.
    4.  Average rental period for "Harry Potter".

![Image: Manager Panel GUI](.media/manager_GUI.png)

### 4. Thread-Safe Synchronization
* To prevent data corruption from multiple librarians accessing the files simultaneously, the server uses **`threading.RLock`**.
* This re-entrant lock ensures that all read/write operations on the shared `books.txt` and `operations.txt` files are atomic and thread-safe, preventing race conditions.

---

## 🚀 How to Run

### Prerequisites
* Python 3.x
* Tkinter (usually included with Python)

### 1. Prepare Data Files
Ensure the following files are in the same directory as the server:
* `users.txt` (with user credentials, e.g., `greg;b123;librarian`)
* `books.txt` (with book data)
* `operations.txt` (can be empty initially)

### 2. Run the Server
Open a terminal and start the server. It will begin listening for connections.

```bash
python server.py
```

### 3. Run the Client(s)
Open one or more new terminal windows and run the client script. You can run this command multiple times to simulate multiple users.

```bash
python client.py
```

### 4. Log In
Use the credentials from your `users.txt` file to log in, for example:
* **Username:** `greg`, **Password:** `b123` (for Librarian)
* **Username:** `simon`, **Password:** `7684` (for Manager)