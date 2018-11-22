#Importing Modules
import sqlite3
import datetime
import pytz
import sys


#Creating The Database 
db = sqlite3.connect("accounts.sqlite", detect_types= sqlite3.PARSE_DECLTYPES)
db.execute("CREATE TABLE IF NOT EXISTS accounts (name TEXT PRIMARY KEY NOT NULL, balance INTEGER NOT NULL)")
db.execute("CREATE TABLE IF NOT EXISTS history (time TIMESTAMP NOT NULL,"
           " account TEXT NOT NULL, amount INTEGER NOT NULL, PRIMARY KEY (time, account))")

db.execute("CREATE VIEW IF NOT EXISTS localhistory AS"
           " SELECT strftime('%Y-%m-%d %H:%M:%f', history.time, 'localtime') AS localtime,"
           " history.account, history.amount FROM history ORDER BY history.time")

#Account Object
class Account:

    #Providing time stamps for entries       
    def _current_time():
        return pytz.utc.localize(datetime.datetime.utcnow())
        
    #Intialize account
    def __init__(self, name: str, opening_balance: int = 0):
        cursor = db.execute("SELECT name, balance FROM accounts WHERE (name = ?)", (name,))
        row = cursor.fetchone()

        #Check if account exists   
        if row:
            self.name, self._balance = row
            print("Account Already Exists For {}. ".format(self.name), end='')
        else:
            self.name = name
            self._balance = opening_balance
            cursor.execute("INSERT INTO accounts VALUES(?, ?)", (name, opening_balance))
            cursor.connection.commit()
            print("Account Created For {}. ".format(self.name), end='')
        self.show_balance()

    #Save change in value
    def _save_update(self, amount):
        new_balance = self._balance + amount
        deposit_time = Account._current_time()
        try:
            db.execute("UPDATE accounts SET balance = ? WHERE (name = ?)", (new_balance, self.name))
            db.execute("INSERT INTO history VALUES(?, ?, ?)", (deposit_time, self.name, amount))
        except sqlite3.Error:
            db.rollback()
        else:
            db.commit()
            self._balance = new_balance      
        
    #Deposit value
    def deposit(self, amount: int) -> float:
        if amount > 0.0:
            self._save_update(amount)
            print("${:.2f} Deposited".format(amount / 100))
        return self._balance / 100
    
    #Intialize account
    def withdraw(self, amount: int) -> float:
        if 0 < amount <= self._balance:
            self._save_update(-amount)
            print("${:.2f} Withdrawn".format(amount / 100))
            return amount / 100
        else:
            print("Insufficient Funds")
            return 0.0
        
    #Display balances
    def show_balance(self):
        print("Balance On Account {} is ${:.2f}".format(self.name, self._balance / 100))
        
    #Display transaction history
    def transaction_history(self,name: str):
        print("\nNOTE THAT AMOUNT VALUES IN THE LAST TWO COLUMN ARE CENT VALUES!") 
        for row in db.execute(" SELECT strftime('%Y-%m-%d %H:%M:%f', history.time, 'localtime') AS localtime,"
           " history.account, history.amount FROM history WHERE history.account like '{}%' ORDER BY history.time".format(name)):
            print(row)
            
    #Delete account      
    def delete_info(self, name:str):
        db.execute("DELETE FROM accounts WHERE name like '%{}%'".format(name))
        db.execute(" DELETE FROM history WHERE history.account like '{}%'".format(name))
        db.commit()
        print("{}'s Successfully Deleted".format(name))
        

#Sanitization For Option Selection
def get_valid_input(prompt):
    
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Sorry, Your Response Must One Of The Options Listed."); print("="*80)
            
            continue
        if (value < 1) or (value>6):
            print("Sorry, Your Response Must One Of The Options Listed.");print("="*80)
            continue
        else:
            break
    return value


#Sanitization For Amount Input
def get_valid_input_two(prompt):
    
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Sorry, Your Input Must Be A Whole Number.\n")
            
            continue
        if (value<0):
            print("Sorry, Your Input Cannot Be Negative.\n")
            continue
        else:
            break
    return value


#Main Program
def main_program():
      
    while True:

        #Greetings And Option Selection
        print("="*80)
        option = get_valid_input(("Welcome To Your Personal Financial Manager!\n"
                                  "Press 1 To Create Account/View Exisiting Account, Press 2 For Deposits,\n"
                                  "Press 3 Withdraws, Press 4 To View Transaction History,\nPress 5 To Delete Account, Press 6 To Quit\n"))


        #Create Account/View Exisitng Account
        if (option==1):
            account_name = input(("Enter Full Name For New Account/Account You Want To View: "))
            account_pop = Account(str(account_name))

            
        #Deposits     
        elif (option==2):
            account_name = input(("Enter The Name Of The Person Depositing: "))
            name_deposit = Account(str(account_name))
            amount_deposit_dollars = get_valid_input_two(("Input Dollar Amount To Be Depositied: "))
            amount_deposit_cents = get_valid_input_two(("Input Cents Amount To Be Depositied: "))
            amount_deposit = (amount_deposit_dollars)*100 + amount_deposit_cents
            if amount_deposit == 0:
                print("No Money Has Been Depositied")
            else:
                name_deposit.deposit(amount_deposit)

                
        #Withdraws      
        elif (option==3):
            account_name = input(("Enter The Name Of The Person Withdrawing: "))
            name_withdraw = Account(str(account_name))
            amount_withdraw_dollars = get_valid_input_two(("Input Dollar Amount To Be Withdrawn: "))
            amount_withdraw_cents = get_valid_input_two(("Input Cents Amount To Be Withdrawn: "))
            amount_withdraw = (amount_withdraw_dollars)*100 + amount_withdraw_cents
            if amount_withdraw == 0:
                print("No Money Has Been Withdrawn")
            else:
                name_withdraw.withdraw(amount_withdraw)
                
        #Transaction History        
        elif (option ==4):
            account_name = input(("Enter The Name Of The Person Whose Transaction You Want To See: "))
            name_deposit = Account(str(account_name))
            name_deposit.transaction_history(account_name)

        #Delete Account  
        elif(option==5):
            account_name = input(("Enter The Name Of The Person Whose Account You Want To Delete: "))
            name_delete = Account(str(account_name))
            name_delete.delete_info(account_name)


        #Quit  
        else:
            print("Thanks For Using The Program! See You Later!")
            sys.exit()

#Execute Main Program             
main_program()
        

