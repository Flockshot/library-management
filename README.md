# Multithreaded TCP Library Management System

Built a multithreaded client-server library management system in Python that supports concurrent librarian and manager operations via a Tkinter GUI, with persistent file-based data storage and secure synchronization.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg?logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange.svg)
![Networking](https://img.shields.io/badge/Networking-TCP/IP_Sockets-00758F.svg)
![Concurrency](https://img.shields.io/badge/Concurrency-Multithreading-blue.svg)

---

## 🏛️ System Architecture

[cite_start]This application uses a client-server model designed to handle multiple users at once[cite: 4454].

* **Server (`server.py`):** A multithreaded TCP server. [cite_start]It listens for incoming connections and spawns a new, dedicated thread for each client[cite: 4454]. This allows multiple librarians and managers to be connected and performing operations simultaneously. The server is responsible for all business logic, data validation, and file I/O.
* [cite_start]**Client (`client.py`):** A Tkinter-based GUI application that serves as the user-facing terminal[cite: 4451, 4454]. It connects to the server via TCP and provides a role-specific dashboard based on user authentication.
* **Data Persistence:** The system uses three flat files as its database:
    * [cite_start]`users.txt`: Stores user credentials and roles (librarian/manager) [cite: 4484-4488].
    * [cite_start]`books.txt`: Manages the book inventory, including title, price, and available copies [cite: 4489-4500].
    * [cite_start]`operations.txt`: A transaction log that records every "rent" and "return" action for statistical analysis [cite: 4501-4506].

> **[Image: Login Window from library-management.pdf]**
>
> [cite_start]*(**Developer Note:** Place the screenshot of the Login Window from **Page 3 of `library-management.pdf`**  here.)*

---

## ✨ Features & Functionality

### 1. User Authentication
* [cite_start]Users are greeted with a login screen that sends credentials to the server[cite: 4513, 4521].
* [cite_start]The server validates the `username` and `password` against `users.txt`[cite: 4521].
* [cite_start]On success, the server returns the user's `role` [cite: 4521][cite_start], and the client application dynamically loads the appropriate dashboard (Librarian or Manager)[cite: 4523].

### 2. Librarian Panel
* [cite_start]**Rent Books:** Librarians can select one or more books, enter a client's name and date, and submit a "rent" request[cite: 4525, 4527].
* **Server-Side Validation (Rent):** The server enforces business rules:
    1.  [cite_start]**Availability Check:** Rejects the rental if any selected book has 0 copies available in `books.txt` [cite: 4553-4556].
    2.  [cite_start]**Outstanding Rentals Check:** Rejects the rental if the client has previously rented books that have not yet been returned (by checking `operations.txt`) [cite: 4557-4559].
* [cite_start]**Return Books:** Librarians can select books, enter the client's name and date, and submit a "return" request[cite: 4561].
* [cite_start]**Server-Side Validation (Return):** The server checks `operations.txt` to ensure the books were actually rented by that client and not already returned [cite: 4562-4563].
* [cite_start]**File Updates:** On a successful operation, the server updates `books.txt` (decrementing/incrementing `copiesAvailable`) and appends the transaction to `operations.txt`[cite: 4560, 4564].

> **[Image: Librarian Panel GUI from library-management.pdf]**
>
> [cite_start]*(**Developer Note:** Place the screenshot of the Librarian Panel from **Page 3 of `library-management.pdf`**  here.)*

### 3. Manager Panel
* [cite_start]**Generate Reports:** Managers can request 4 different statistical reports[cite: 4569, 4579].
* [cite_start]The server computes these metrics on the fly from `operations.txt` and sends back the result to be displayed in a message box [cite: 4570-4571].
* **Available Reports:**
    1.  [cite_start]Most rented book(s) overall[cite: 4482].
    2.  [cite_start]Librarian(s) with the highest number of operations[cite: 4482].
    3.  [cite_start]Total generated revenue by the library[cite: 4482].
    4.  [cite_start]Average rental period for "Harry Potter"[cite: 4482].

> **[Image: Manager Panel GUI from library-management.pdf]**
>
> [cite_start]*(**Developer Note:** Place the screenshot of the Manager Panel from **Page 4 of `library-management.pdf`**  here.)*

### 4. Thread-Safe Synchronization
* [cite_start]To prevent data corruption from multiple librarians accessing the files simultaneously, the server uses **`threading.RLock`**[cite: 4584].
* [cite_start]This re-entrant lock ensures that all read/write operations on the shared `books.txt` and `operations.txt` files are atomic and thread-safe, preventing race conditions[cite: 4585].

---

## 🚀 How to Run

### Prerequisites
* Python 3.x
* Tkinter (usually included with Python)

### 1. Prepare Data Files
Ensure the following files are in the same directory as the server:
* [cite_start]`users.txt` (with user credentials, e.g., `greg;b123;librarian`) [cite: 4486-4488]
* [cite_start]`books.txt` (with book data) [cite: 4489-4500]
* [cite_start]`operations.txt` (can be empty initially) [cite: 4501]

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
* [cite_start]**Username:** `greg`, **Password:** `b123` (for Librarian) [cite: 4486]
* [cite_start]**Username:** `simon`, **Password:** `7684` (for Manager) [cite: 4488]