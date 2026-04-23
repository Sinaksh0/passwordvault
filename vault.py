import json
import os
import emoji
import hashlib
import sys
import re
import random
import string
from datetime import datetime
from colorama import Fore, Style

class Vault_Pass():
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
            master = input('Enter a main password to lock your file: ')
            hashed = self.hash_pass(master)
            with open(self.lock , 'w') as file:
                json.dump({
                    "master": hashed,
                    "answer": hashed_answer
                    }, file, indent=4)
            print(emoji.emojize(Fore.GREEN + 'Your main password and answer of security question was saved :check_mark_button:' + Style.RESET_ALL))
        else:
            self.check_master_password()
            
    def check_master_password(self):
        with open(self.lock, 'r') as file:
            saved = json.load(file)
        try:
            print('You have THREE chance to enter the password')
            game = False
            for _ in range(3):
                attempt = input('Enter a main password to unlock your file: ')
                if self.hash_pass(attempt) == saved['master']:
                    print(emoji.emojize(Fore.GREEN + 'Your password is correct :check_mark_button:' + Style.RESET_ALL))
                    game = True
                    return
                else:
                    print(emoji.emojize(Fore.RED + 'Incorrect password :cross_mark:' + Style.RESET_ALL))
            if not game:
                print(emoji.emojize(Fore.RED + 'You lose! :cross_mark: please recover your password' + Style.RESET_ALL))
                self.recover_password()
                
        except Exception as e:
            print(f'The error is : {e}')
    
    def recover_password(self):
        if not os.path.exists(self.lock):
            print(emoji.emojize(Fore.RED + "There is any file :cross_mark:" + Style.RESET_ALL))
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
                print(emoji.emojize(Fore.GREEN + 'The new password was changed successfully :check_mark_button:' + Style.RESET_ALL))
                self.check_master_password()
                play = True
                return
            else:
                print(emoji.emojize(Fore.RED + 'Your answer is not correct :cross_mark:' + Style.RESET_ALL))
        if not play:
            print(emoji.emojize(Fore.RED + 'You cannot geuss the answer :cross_mark:' + Style.RESET_ALL))
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
        
    def check_pass_strength(self, password):
        score = 0
        result = []

        if len(password) >= 8:
            score += 1
        else:
            result.append('The password length is less than eight character!')
        
        if re.search(r"[a-z]", password):
            score += 1
        else:
            result.append('There is not any small words (a-z) in the password!')
        
        if re.search(r"[A-Z]", password):
            score += 1
        else:
            result.append('There is not any captal words (A-Z) in the password!')
        
        if re.search(r"\d", password):
            score += 1
        else:
            result.append('There is not digit in the password!')
        
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 1
        else:
            result.append('There is not punctuation mark in the password!')
        
        if score == 5:
            level = 'Great!'
            status = False
        elif score >= 3:
            level = 'Good!'
            status = False
        else:
            level = 'Weak!'
            status = True
        
        return level, result, status
    
    def check_pass_to_add(func):
        def wrapper(self, Name, Password):
            level, result, status = self.check_pass_strength(Password)
            while status:
                print(f'Your level password: {level}')
                if result:
                    for res in result:
                        print(f'- {res}')
                Q = input('Do you want to save it (y,n)? ')
                if Q.upper() == 'Y':
                    return func(self, Name, Password)
                else:
                    Password = input('Enter a stronger password: ')
                    level, result, status = self.check_pass_strength(Password)
            if not status:
                return func(self, Name, Password)
        return wrapper

    def check_pass_level(self):
        if self.vault:
            attempts = 1
            print('Look at your password level')
            for check in self.vault:
                print(f'{attempts}:')
                level, result, status = self.check_pass_strength(check['Password'])
                print(f'Your password level: {level}')
                if result:
                    print(Fore.YELLOW + 'The problems of your password:' + Style.RESET_ALL)
                    for problem in result:
                        print(f'- {problem}')
                attempts += 1
        else:
            print(emoji.emojize("There is not passwords to check them yet! :cross_mark:"))

    @check_pass_to_add
    def add_pass(self, Name, password):
        Name = Name.strip()
        password = password.strip()
        self.vault.append({
            'Name of the web': Name,
            'Password': password,
            'Saved_at': datetime.now().isoformat()
            })
        self.save_data()
        print(emoji.emojize(Fore.GREEN + f'Password {password} added :check_mark_button:' + Style.RESET_ALL))
        
    def search_pass(self, Name):
        Name = Name.strip()
        found = False
        for pas in self.vault:
            if Name in pas['Name of the web']: 
                print(f'Your Name of the pass is: {pas["Name of the web"]} and the password is: {pas["Password"]}')
                found = True
                    
        if not found:
            print(emoji.emojize(Fore.RED + f'There is not {Name} here :cross_mark:' + Style.RESET_ALL))
                
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
            print(emoji.emojize(Fore.RED + 'Not found :cross_mark:' + Style.RESET_ALL))
            
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
                print(emoji.emojize(Fore.GREEN + 'Password updated successfully :check_mark_button:' + Style.RESET_ALL))
                found = True
                break
        
        if not found:
            print(emoji.emojize(Fore.RED + 'Password not found :cross_mark:' + Style.RESET_ALL))
        
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
            print(emoji.emojize(Fore.RED + 'Now, There is no password here :cross_mark:' + Style.RESET_ALL))
    
    def remove_weak_password(self):
        if self.vault:
            print('Checking all your passwords...')
            for pas in self.vault:
                level, result, status = self.check_pass_strength(pas['Password'])
                print(f'Password {pas['Name']} is {level}')
                if status:
                    while True:
                        try:
                            Q = int(input('Do you want to change or remove the password (1,2)? '))
                            break
                        except ValueError:
                            print("Just enter a number!")

                    if Q == 1:
                        while status:
                            new_password = input(f'Enter a new password for {pas['Name of the web']}: ')
                            level, result, status = self.check_pass_strength(new_password)
                            if status:
                                print(Fore.YELLOW + f'Your password is still weak!')
                        pas['Password'] = new_password
                        pas['Saved_at'] = datetime.now().isoformat()
                        self.save_data()
                        print('The password changed successfully')
                    elif Q == 2:
                        self.vault.remove(pas)
                        self.save_data()
                        print(emoji.emojize(f'Your password: {pas['Password']} is removed :check_mark_button:'))
                    else:
                        continue
        else:
            print(emoji.emojize(Fore.RED + "There is not passwords to remove them yet! :cross_mark:" + Style.RESET_ALL))

    def generate_password(self, length=8):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = []
        if length < 4:
            length = 4
        for _ in range(length):
            password.append(random.choice(characters))
        
        random.shuffle(password)
        result = "".join(password)
        print(f'The Generation Password is: {result}')
        Q = input('Do you want to save it (y,n)? ')
        if Q.upper() == 'Y':
            Name = input('Enter a name for it: ')
            self.vault.append({
                'Name of the web': Name,
                'Password': result,
                'Saved_at': datetime.now().isoformat()
            })
            self.save_data()
            print(emoji.emojize(Fore.GREEN + 'The Generation Password was saved successfully :check_mark:' + Style.RESET_ALL))
    
    def os_remove_lock(self):
        if os.path.exists(self.lock):
            os.remove(self.lock)
            return
        else:
            print(emoji.emojize(Fore.RED + 'There is no file on your system :cross_mark:' + Style.RESET_ALL))
            return 
            
    def os_remove_file(self):
        if os.path.exists(self.filename):
            confirm = input("Are you sure you want to delete your security question and password for lock the file? (y,n): ")
            if confirm.upper() == 'Y':
                os.remove(self.filename)
                print(emoji.emojize(Fore.GREEN + 'The file was deleted! :check_mark_button:' + Style.RESET_ALL))
            else:
                print("Okay!")
            return
        else:
            print(emoji.emojize(Fore.RED + 'There is not any file on your system :cross_mark:' + Style.RESET_ALL))
            return
    
    def continue_program(self):
        Q = input('Do you want to continue Password Manager (y,n)? ')
        if Q.upper() == 'Y':
            return True
        else:
            print(emoji.emojize('Goodbye:hand_with_fingers_splayed:'))
            return False
            
vault = Vault_Pass()
def turn():
    play = True
    while play:
        print(emoji.emojize('---Password Manager---'))
        print(emoji.emojize('1. Add Your Password :plus:'))
        print(emoji.emojize('2. Remove Your Password :wastebasket:'))
        print(emoji.emojize('3. Search Your Password :magnifying_glass_tilted_left:'))
        print(emoji.emojize('4. Show All Your Password :clipboard:'))
        print(emoji.emojize('5. Edit Your Password :pencil:'))
        print(emoji.emojize('6. Change Your Password For Lock The File :locked_with_key:'))
        print(emoji.emojize('7. Check Your All Password Level :bar_chart:'))
        print(emoji.emojize('8. Delete All Weak Password And Replace It :shield:'))
        print(emoji.emojize('9. Generate Passsword :game_die:'))
        print(emoji.emojize('10. Reset Factory :bomb:'))
        print(emoji.emojize('11. Exit :cross_mark:'))

        while True:
            try:
                choose = int(input('Enter a number from the List: '))
                break
            except ValueError:
                print('Just enter a number')
        
        if choose == 1:
            Name = input("Enter a name of your password (Like: instagram): ")
            password = input('Enter your password: ')
            vault.add_pass(Name, password)
            play = vault.continue_program()

        elif choose == 2:
            if vault.vault:
                Name = input('Enter a name to remove it: ')
                password = input('Enter your password to remove it: ')
                vault.remove(Name,password)
                play = vault.continue_program()
            else:
                print(emoji.emojize(Fore.RED + 'There is not any passwords here :cross_mark:' + Style.RESET_ALL))

        elif choose == 3:
            if vault.vault:
                Name = input('Enter a name of your password to search it: ')
                vault.search_pass(Name)
                play = vault.continue_program()
            else:
                print(emoji.emojize(Fore.RED + 'There is not any passwords here :cross_mark:' + Style.RESET_ALL))

        elif choose == 4:
            vault.show()
            play = vault.continue_program()

        elif choose == 5:
            if vault.vault:
                name = input('Enter the name of the password to edit: ')
                old = input('Enter the old password: ')
                vault.edit_pass(name, old)
                play = vault.continue_program()
            else:
                print(emoji.emojize(Fore.RED + 'There is not any passwords here :cross_mark:' + Style.RESET_ALL))

        elif choose == 6:
            vault.recover_password()
            play = vault.continue_program()

        elif choose == 7:
            vault.check_pass_level()
            play = vault.continue_program()

        elif choose == 8:
            vault.remove_weak_password()
            play = vault.continue_program()

        elif choose == 9:
            while True:
                try: 
                    length = int(input('Enter a length of the password (DEFAULT IS 8): '))
                    break
                except ValueError:
                    print("Just enter a number")

            vault.generate_password(length)
            play = vault.continue_program()

        elif choose == 10:
            vault.os_remove_file()
            vault.os_remove_lock()
            play = vault.continue_program()

        elif choose == 11:
            print(emoji.emojize('Goodbye:hand_with_fingers_splayed:'))
            break
        else:
            print(emoji.emojize(Fore.RED + 'Invalid number :cross_mark:' + Style.RESET_ALL))
        
if __name__ == '__main__':
    turn()
