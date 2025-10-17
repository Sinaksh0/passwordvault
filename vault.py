import json
import os
import emoji
import hashlib
import sys
from datetime import datetime
class Vault_pass():
    def __init__(self, filename = 'My_pass.json', lock = 'lock'):
        self.lock = lock
        self.filename = filename
        self.vault = self.load_data()
    
    def hash_pass(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def setup_master_pass(self):
        if not os.path.exists(self.lock):
            print("What is your first school (THIS IS FOE RECOVER YOUR PASSWORD FOR UNLOCK THE FILE)?")
            answer = input('Enter your answer for security question: ').strip()
            hashed_answer = self.hash_pass(answer)
            master = input(f'Enter a main password to lock your file {self.filename}: ')
            hashed = self.hash_pass(master)
            with open(self.lock , 'w') as file:
                json.dump({
                    "master": hashed,
                    "answer": hashed_answer
                    }, file, indent=4)
            print(emoji.emojize('Your main password and answer of security question was saved :check_mark_button:'))
        else:
            self.check_master_password()
            
    def check_master_password(self):
        with open(self.lock, 'r') as file:
            saved = json.load(file)
        try:
            print('You have THREE chance to guess the password')
            game = False
            for _ in range(3):
                attempt = input('Enter a main password to unlock your file: ')
                if self.hash_pass(attempt) == saved['master']:
                    print(emoji.emojize('Your password is correct :check_mark_button:'))
                    game = True
                    return
                else:
                    print(emoji.emojize('Incorrect password :cross_mark:'))
            if not game:
                print(emoji.emojize('You lose! :cross_mark: please recover your password'))
                self.recover_password()
                
        except Exception as e:
            print(f'The error is : {e}')
    
    def recover_password(self):
        if not os.path.exists(self.lock):
            print(emoji.emojize("There is any file :cross_mark:"))
            return
        
        with open(self.lock, 'r') as file:
            data = json.load(file)
        print('What is your first school (THIS IS FOE RECOVER YOUR PASSWORD FOR UNLOCK THE FILE)?')
        print('You have THREE chance to guess the answer')
        play = False
        for _ in range(3):
            ans = input('What is your answer: ')
            if self.hash_pass(ans) == data['answer']:
                new_pass = input('Enter a new password for lock the file: ')
                data['answer'] = self.hash_pass(new_pass)
                with open(self.lock, 'w') as file:
                    json.dump(data, file, indent=4)
                print(emoji.emojize('The new password was changed successfully :check_mark_button:'))
                play = True
                return
            else:
                print(emoji.emojize('Your answer is not correct:cross_mark: try again'))
        if not play:
            print(emoji.emojize('You cannot geuss the answer :cross_mark:'))
            sys.exit()
        
    def load_data(self):
        if os.path.exists(self.lock):
            self.check_master_password()
        else:
            self.setup_master_pass()
            
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                return json.load(file)
        else:
            return []
        
    def save_data(self):
        with open(self.filename, 'w') as file:
            return json.dump(self.vault, file, indent=4)
    
    def add_pass(self, Name, password):
        Name = Name.strip()
        password = password.strip()
        if password in self.vault:
            print('The password already exists.')
            return
        else:    
            self.vault.append({
                'Name of the web': Name,
                'Password': password,
                'Saved_at': datetime.now().isoformat()
                })
            self.save_data()
            print(emoji.emojize(f'Password {password} added :check_mark_button:'))
        
    def search_pass(self, Name):
        Name = Name.strip()
        found = False
        for pas in self.vault:
            if Name in pas['Name of the web']: 
                print(f'Your Name of the pass is: {pas["Name of the web"]} and the password is: {pas["Password"]}')
                found = True
                
        if not found:
            print(emoji.emojize(f'There is not {Name} here :cross_mark:'))
                
    def remove(self, Name, password):
        Name = Name.strip()
        password = password.strip()
        found = False
        for pas in self.vault:
            if pas['Name of the web'] == Name and pas['Password'] == password:
                self.vault.remove(pas)
                self.save_data()
                print(emoji.emojize(f'Your password: {password} is removed :check_mark_button:'))
                found = True
                break
        if not found:
            print(emoji.emojize('Not found :cross_mark:'))
            
    def edit_pass(self, Name, old_password):
        Name = Name.strip()
        old = old_password.strip()
        found = False
        for pas in self.vault:
            if pas['Name of the web'] == Name and pas['Password'] == old:
                new = input("Enter a new password: ")
                pas['Password'] = new
                pas['Saved_at'] = datetime.now().isoformat()
                self.save_data()
                print(emoji.emojize('Password updated successfully :check_mark_button:'))
                found = True
                break
        
        if not found:
            print(emoji.emojize('Password not found :cross_mark:'))
        
    def show(self):
        if self.vault:
            print(emoji.emojize(f":clipboard: You have {len(self.vault)} passwords"))
            print('Choose sorting method:')
            print('1. Sort by name')
            print('2. Sort by date')
            try:
                choice = int(input('Enter 1 or 2: '))
            except ValueError:
                choice = int(input('Just enter 1 or 2: '))
            if choice == 1:
                sort = sorted(self.vault, key=lambda x: x['Name of the web'].lower())
            elif choice == 2:
                sort = sorted(self.vault, key=lambda x: x['Saved_at'])
            else:
                sort = self.vault
            print('Lock at your all password!')
            for pas in sort:
                print(emoji.emojize(f':locked_with_key: {pas["Name of the web"]}: {pas["Password"]}'))
        else:
            print(emoji.emojize('Now, There is no password here :cross_mark:'))
    
    def os_remove_lock(self):
        if os.path.exists(self.lock):
            confirm = input("Are you sure you want to delete your security question and password for lock the file? (y,n): ")
            if confirm.upper() == 'Y':
                os.remove(self.lock)
                print(emoji.emojize('The file was deleted! :check_mark_button:'))
            else:
                print("Okay!")
            return
        else:
            print(emoji.emojize('There is no file on your system :cross_mark:'))
            
    def os_remove_file(self):
        if os.path.exists(self.filename):
            confirm = input("Are you sure you want to delete your security question and password for lock the file? (y,n): ")
            if confirm.upper() == 'Y':
                os.remove(self.filename)
                print(emoji.emojize('The file was deleted! :check_mark_button:'))
            else:
                print("Okay!")
            return
        else:
            print(emoji.emojize('There is not any file on your system :cross_mark:'))
            
vault = Vault_pass()
def turn():
    me = True
    while me:
        print(emoji.emojize(':locked_with_key: Vault Menu: '))
        print(emoji.emojize('1. :plus: Add your password'))
        print(emoji.emojize('2. :wastebasket: Remove your password'))
        print(emoji.emojize('3. :magnifying_glass_tilted_left: Search your password'))
        print(emoji.emojize('4. :clipboard: Show all your password'))
        print(emoji.emojize('5. :pencil: Edit your password'))
        print(emoji.emojize('6. :locked_with_key: Change your password for lock the file'))
        print(emoji.emojize('7. :bomb: Delete all my password'))
        print(emoji.emojize('8. :firecracker: Delete my password and question for lock the file'))
        print(emoji.emojize('9. :cross_mark: Exit'))
    
        try:
            choose = int(input('Enter a number from the List: '))
        except ValueError:
            choose = int(input('You can just enter a number of the list: '))
            continue
        
        if choose == 1:
            Name = input("Enter a name of your password (Like: instagram): ")
            password = input('Enter your password: ')
            vault.add_pass(Name, password)
            QN = input('Do you want to continue (y,n)? ')
            if QN.upper() == 'Y':
                me = True
            else:
                print(emoji.emojize('Goodbye:hand_with_fingers_splayed:'))
                me = False
                break
        elif choose == 2:
            Name = input('Enter a name to remove it: ')
            password = input('Enter your password to remove it: ')
            vault.remove(Name,password)
            QN = input('Do you want to continue (y,n)? ')
            if QN.upper() == 'Y':
                me = True
            else:
                print(emoji.emojize('Goodbye:hand_with_fingers_splayed:'))
                me = False
                break
        elif choose == 3:
            Name = input('Enter a name of your password to search it: ')
            vault.search_pass(Name)
            QN = input('Do you want to continue (y,n)? ')
            if QN.upper() == 'Y':
                me = True
            else:
                print(emoji.emojize('Goodbye:hand_with_fingers_splayed:'))
                me = False
                break
        elif choose == 4:
            vault.show()
            QN = input('Do you want to continue (y,n)? ')
            if QN.upper() == 'Y':
                me = True
            else:
                print(emoji.emojize('Goodbye:hand_with_fingers_splayed:'))
                me = False
                break
        elif choose == 5:
            name = input('Enter the name of the password to edit: ')
            old = input('Enter the old password: ')
            vault.edit_pass(name, old)
            QN = input('Do you want to continue (y,n)? ')
            if QN.upper() == 'Y':
                me = True
            else:
                print(emoji.emojize('Goodbye:hand_with_fingers_splayed:'))
                me = False
                break
        elif choose == 6:
            vault.recover_password()
            QN = input('Do you want to continue (y,n)? ')
            if QN.upper() == 'Y':
                me = True
            else:
                print(emoji.emojize('Goodbye:hand_with_fingers_splayed:'))
                me = False
                break
        elif choose == 7:
            vault.os_remove_file()
            QN = input('Do you want to continue (y,n)? ')
            if QN.upper() == 'Y':
                me = True
            else:
                print(emoji.emojize('Goodbye:hand_with_fingers_splayed:'))
                me = False
                break
        elif choose == 8:
            vault.os_remove_lock()
            QN = input('Do you want to continue (y,n)? ')
            if QN.upper() == 'Y':
                me = True
            else:
                print(emoji.emojize('Goodbye:hand_with_fingers_splayed:'))
                me = False
                break
        elif choose == 9:
            print(emoji.emojize('Goodbye:hand_with_fingers_splayed:'))
            break
        else:
            print('Invalid number')
        
if __name__ == '__main__':
    turn()
