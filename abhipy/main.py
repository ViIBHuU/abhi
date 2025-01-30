print("this is a pyyhton program")
print("this is change 1")


import sqlite3
import pandas as pd

class Account:
    def __init__(self, account_number, name, account_type, balance=0):
        self.account_number = account_number
        self.name = name
        self.account_type = account_type
        self.balance = balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            print(f"₹{amount} deposited successfully. New balance: ₹{self.balance}")
        else:
            print("Invalid deposit amount.")

    def withdraw(self, amount):
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            print(f"₹{amount} withdrawn successfully. New balance: ₹{self.balance}")
        else:
            print("Insufficient balance or invalid amount.")

    def get_details(self):
        return {
            "Account Number": self.account_number,
            "Name": self.name,
            "Account Type": self.account_type,
            "Balance": self.balance
        }

class Bank:
    def __init__(self):
        self.conn = sqlite3.connect('bank.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Creating Accounts table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Accounts (
                               AccountNumber TEXT PRIMARY KEY,
                               Name TEXT,
                               AccountType TEXT,
                               Balance REAL)''')

        # Creating Transactions table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Transactions (
                               TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
                               AccountNumber TEXT,
                               TransactionType TEXT,
                               Amount REAL,
                               Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               FOREIGN KEY (AccountNumber) REFERENCES Accounts (AccountNumber))''')
        self.conn.commit()

    def add_account(self, account_number, name, account_type, balance=0):
        self.cursor.execute("SELECT * FROM Accounts WHERE AccountNumber = ?", (account_number,))
        if self.cursor.fetchone():
            print("Account number already exists!")
        else:
            if account_type.lower() in ['saving', 'salary']:
                self.cursor.execute("INSERT INTO Accounts (AccountNumber, Name, AccountType, Balance) VALUES (?, ?, ?, ?)",
                                    (account_number, name, account_type, balance))
                self.conn.commit()
                print("Account created successfully!")
            else:
                print("Invalid account type. Choose either 'Saving' or 'Salary'.")

    def get_account_details(self, account_number):
        df = pd.read_sql_query("SELECT * FROM Accounts WHERE AccountNumber = ?", self.conn, params=(account_number,))
        if not df.empty:
            return df.to_dict(orient='records')[0]
        else:
            return "Account not found!"

    def get_all_account_details(self):
        try:
            df = pd.read_sql_query("SELECT * FROM Accounts", self.conn)
            if not df.empty:
                return df
            else:
                return "No accounts found!"
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def log_transaction(self, account_number, transaction_type, amount):
        self.cursor.execute("INSERT INTO Transactions (AccountNumber, TransactionType, Amount) VALUES (?, ?, ?)",
                            (account_number, transaction_type, amount))
        self.conn.commit()

    def transaction(self, account_number, amount, transaction_type):
        df = pd.read_sql_query("SELECT Balance FROM Accounts WHERE AccountNumber = ?", self.conn, params=(account_number,))
        if not df.empty:
            balance = df.iloc[0]['Balance']
            if transaction_type.lower() == 'deposit':
                new_balance = balance + amount
            elif transaction_type.lower() == 'withdraw' and balance >= amount:
                new_balance = balance - amount
            else:
                print("Invalid transaction or insufficient funds.")
                return
            self.cursor.execute("UPDATE Accounts SET Balance = ? WHERE AccountNumber = ?", (new_balance, account_number))
            self.conn.commit()

            # Log the transaction
            self.log_transaction(account_number, transaction_type, amount)

            print(f"Transaction successful. New balance: ₹{new_balance}")
        else:
            print("Account not found!")

bank = Bank()
while True:
    print("\nBanking System")
    print("1. Add Account")
    print("2. Get Account Details")
    print("3. Deposit")
    print("4. Withdraw")
    print("5. Get all Accounts")
    print("6. Get all Transactions")
    print("7. Exit")

    # choice = input("Enter your choice: ")
    choice=7

    if choice == '1':
        acc_num = input("Enter Account Number: ")
        name = input("Enter Name: ")
        acc_type = input("Enter Account Type (Saving/Salary): ")
        balance = float(input("Enter Initial Balance: "))
        bank.add_account(acc_num, name, acc_type, balance)
    elif choice == '2':
        acc_num = input("Enter Account Number: ")
        print(bank.get_account_details(acc_num))
    elif choice == '3':
        acc_num = input("Enter Account Number: ")
        amount = float(input("Enter Deposit Amount: "))
        bank.transaction(acc_num, amount, "deposit")
    elif choice == '4':
        acc_num = input("Enter Account Number: ")
        amount = float(input("Enter Withdrawal Amount: "))
        bank.transaction(acc_num, amount, "withdraw")
    elif choice == '5':
        print(bank.get_all_account_details())
    elif choice == '6':
        df = pd.read_sql_query("SELECT * FROM Transactions", bank.conn)
        if not df.empty:
            print(df)
        else:
            print("No transactions found!")
    elif choice == '7':
        print("Exiting... Thank you!")
        break
    else:
        print("Invalid choice! Please enter a valid option.")

