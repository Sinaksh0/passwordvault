import json
import os
import emoji
import hashlib
import sys
import re
import random
import string
import uuid
import pyperclip
from datetime import datetime
from colorama import Fore, Style

APP_VERSION = '0.5.0'
VERSION_FILE = 'version.txt'

class Vault_Pass():
    def __init__(self, filename = 'My_Pass.json', lock = 'lock.json'):
        self.lock = lock
        self.filename = filename
        self.show_version_update()
        self.vault = self.go_update()

    def show_version_update(self):
        old_version = None
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as file:
                old_version = file.read().strip()

        if old_version != APP_VERSION:
            if old_version:
                print('Application updated:' + Fore.GREEN + f' v{old_version} -> v{APP_VERSION}' + Style.RESET_ALL)
            with open(VERSION_FILE, 'w') as file:
                file.write(APP_VERSION)
        else:
            print('Application version:' + Fore.GREEN + f' v{APP_VERSION}' + Style.RESET_ALL)

    def status_update(self):
        try:
            with open('status.txt', 'r') as file:
                status = file.read()

                if status == 'False':
                    return False
                else:
                    return None
        except FileNotFoundError:
            return None

    def write_false_status(self):
        with open('status.txt', 'w') as file:
            file.write('False')

    def go_update(self):
        if self.status_update() is False:
            return self.load_data()
        
        if not os.path.exists(self.filename):
            self.write_false_status()
            return self.load_data()

        with open(self.filename, 'r') as file:
            data = json.load(file)
        if not data:
            self.write_false_status()
            return self.load_data()

        print(emoji.emojize(Fore.YELLOW + f'Your data is old. Updating it for app v{APP_VERSION}... :warning:' + Style.RESET_ALL))
        update_data = []
        for old in data:
            update_data.append({
                'id': str(uuid.uuid4()),
                'Name': old.get('Name of the web', ''),
                'Password': old.get('Password', ''),
                'create_at': old.get('Saved_at', datetime.now().isoformat()),
                'updated_at': old.get('Saved_at', datetime.now().isoformat())
            })

        with open(self.filename, 'w') as file:
            json.dump(update_data, file, indent=4)

        self.write_false_status()
        print(emoji.emojize(Fore.GREEN + f'Your data was migrated to app v{APP_VERSION} :check_mark_button:' + Style.RESET_ALL))
        return self.load_data()

    def hash_pass(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def setup_master_pass(self):
        if not os.path.exists(self.lock):
            print("What is your first school (THIS IS FOR UNLOCK THE FILE)?")
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
                data['master'] = self.hash_pass(new_pass)
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

        if len(password) >= 12:
            score += 1
        elif len(password) >= 8:
            score += 1
        else:
            result.append('Password length must be at least 8 characters.')

        if re.search(r"[a-z]", password):
            score += 1
        else:
            result.append('Add at least one lowercase letter.')

        if re.search(r"[A-Z]", password):
            score += 1
        else:
            result.append('Add at least one uppercase letter.')

        if re.search(r"\d", password):
            score += 1
        else:
            result.append('Add at least one number.')

        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 1
        else:
            result.append('Add at least one special character.')

        if score == 5:
            level = 'Very Strong!'
            status = False
        elif score >= 4:
            level = 'Strong!'
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
                print(Fore.YELLOW + f'Password level: {level}' + Style.RESET_ALL)
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

    @check_pass_to_add
    def add_pass(self, Name, password):
        Name = Name.strip()
        password = password.strip()
        if any(pas['Name'] == Name and pas['Password'] == password for pas in self.vault):
            print(emoji.emojize(Fore.RED + f"The name '{Name}' or password '{password}' is already exists :cross_mark:" + Style.RESET_ALL))
            return
        
        self.vault.append({
            'id': str(uuid.uuid4()),
            'Name': Name,
            'Password': password,
            'create_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
            })
        
        self.save_data()
        print(emoji.emojize(Fore.GREEN + f"Password '{password}' added :check_mark_button:" + Style.RESET_ALL))
        
    def search_pass(self, Name):
        Name = Name.strip()
        found = False
        for pas in self.vault:
            if Name in pas['Name']: 
                print(f'Name: {pas["Name"]}\nPassword is: {pas["Password"]}')
                found = True
                    
        if not found:
            print(emoji.emojize(Fore.RED + f"There is not '{Name}' here :cross_mark:" + Style.RESET_ALL))

    def delete_id_by_name(self, id):
        self.vault = [pas for pas in self.vault if pas['id'] != id]

    def remove_by_name(self, Name: str):
        Name = Name.strip()

        found = [pas for pas in self.vault if pas['Name'].lower() == Name.lower()]
        if not found:
            print(emoji.emojize(Fore.RED + f"The name '{Name}' was not found :cross_mark:" + Style.RESET_ALL))

        if len(found) == 1:
            self.delete_id_by_name(found[0]['id'])
            self.save_data()
            print(emoji.emojize(Fore.GREEN + f"Your password: '{found[0]['Password']}' is removed :check_mark_button:" + Style.RESET_ALL))
        else:
            print(emoji.emojize(Fore.YELLOW + f"There are {len(found)} passwords with the name: '{Name}'" + Style.RESET_ALL))
            for idx, pas in enumerate(found):
                print(f'{idx}. {pas["Name"]}: {pas["Password"]}')

            while True:
                try:
                    choice = int(input("What do you choose to remove? "))
                    break
                except ValueError:
                    print(Fore.YELLOW + 'Please enter a valid number.' + Style.RESET_ALL)

            if 0 <= choice < len(found):
                self.delete_id_by_name(found[choice]['id'])
                self.save_data()
                print(emoji.emojize(Fore.GREEN + f"Your password: '{found[choice]['Password']}' is removed successfully :check_mark_button:" + Style.RESET_ALL))
            else:
                print(emoji.emojize(Fore.RED + 'Invalid choice :cross_mark:' + Style.RESET_ALL))

    def edit_pass(self, Name, old_password):
        Name = Name.strip()
        old = old_password.strip()
        found = False
        for pas in self.vault:
            if pas['Name'] == Name and pas['Password'] == old:
                new = input("Enter a new password: ")
                pas['Password'] = new
                pas['updated_at'] = datetime.now().isoformat()
                self.save_data()
                print(emoji.emojize(Fore.GREEN + 'Password updated successfully :check_mark_button:' + Style.RESET_ALL))
                found = True
                break
        
        if not found:
            print(emoji.emojize(Fore.RED + f"Password for '{Name}' not found :cross_mark:" + Style.RESET_ALL))

    def show(self):
        if not self.vault:
            print(emoji.emojize(Fore.RED + 'There are no passwords saved yet :cross_mark:' + Style.RESET_ALL))
            return

        print(emoji.emojize(f":clipboard: You have {len(self.vault)} saved password(s)."))
        print('Choose sorting method:')
        print('1. Sort by name')
        print('2. Sort by date')

        while True:
            try:
                choice = int(input('Enter 1 or 2: '))
                break
            except ValueError:
                print('Just enter a number!')

        if choice == 1:
            sort = sorted(self.vault, key=lambda x: x['Name'].lower())
        elif choice == 2:
            sort = sorted(self.vault, key=lambda x: x['updated_at'])
        else:
            sort = self.vault

        print(emoji.emojize(':locked_with_key: Look at your all password!'))
        for idx, pas in enumerate(sort, start=1):
            print(emoji.emojize(f' {idx}. {pas["Name"]}: {pas["Password"]} at {pas["updated_at"]} :locked_with_key:'))

        Q = input('Do you want copy to clipboard (y,n)? ')
        if Q.lower() == 'y':
            while True:
                try:
                    print(Fore.MAGENTA + '1.Name\n2.Password' + Style.RESET_ALL)
                    question = int(input('Enter your choice: '))
                    if question == 1:
                        index = int(input('Enter the number to copy name: '))
                        if 1 <= index <= len(sort):
                            try:
                                pyperclip.copy(sort[index - 1]['Name'])
                                print(emoji.emojize(Fore.GREEN + f"Name '{sort[index - 1]['Name']}' copied to clipboard :clipboard:" + Style.RESET_ALL))
                                break
                            except pyperclip.PyperclipException:
                                print(Fore.RED + 'Failed to copy to clipboard. Please ensure you have a clipboard available.' + Style.RESET_ALL)
                                break
                        else:
                            print(Fore.YELLOW + 'Invalid number. Please enter a valid number in the range.' + Style.RESET_ALL)

                    elif question == 2:
                        index = int(input('Enter the number to copy password: '))
                        if 1 <= index <= len(sort):
                            try:
                                pyperclip.copy(sort[index - 1]['Password'])
                                print(emoji.emojize(Fore.GREEN + f"Password '{sort[index - 1]['Password']}' copied to clipboard :clipboard:" + Style.RESET_ALL))
                                break
                            except pyperclip.PyperclipException:
                                print(Fore.RED + 'Failed to copy to clipboard. Please ensure you have a clipboard available.' + Style.RESET_ALL)
                                break
                        else:
                            print(Fore.YELLOW + 'Invalid number. Please enter a valid number in the range.' + Style.RESET_ALL)

                    else:
                        print(Fore.YELLOW + 'Invalid choice. Please enter 1 or 2.' + Style.RESET_ALL)
                        continue
                except ValueError:
                    print(Fore.YELLOW + 'Please enter a valid number.' + Style.RESET_ALL)

    def remove_weak_password(self):
        if self.vault:
            print('Checking all your passwords...')
            for pas in self.vault:
                level, result, status = self.check_pass_strength(pas['Password'])
                print(f"Password '{pas['Name']}' is {level}")
                if status:
                    Q = input('Do you want to change or remove the password (y,n)? ')
                            
                    if Q.lower() == 'y':
                        while status:
                            new_password = input(f'Enter a new password for {pas['Name']}: ')
                            level, result, status = self.check_pass_strength(new_password)
                            if status:
                                print(Fore.YELLOW + f'Your password is still weak!')
                        pas['Password'] = new_password
                        pas['create_at'] = datetime.now().isoformat()
                        pas['updated_at'] = datetime.now().isoformat()
                        self.save_data()
                        print(emoji.emojize(Fore.GREEN + f"Your password: '{pas['Password']}' is changed successfully :check_mark_button:" + Style.RESET_ALL))
                    elif Q.lower() == 'n':
                        self.vault.remove(pas)
                        self.save_data()
                        print(emoji.emojize(Fore.GREEN + f"Your password: '{pas['Password']}' is removed :check_mark_button:" + Style.RESET_ALL))
                    else:
                        continue
        else:
            print(emoji.emojize(Fore.RED + "There is not passwords to remove them yet! :cross_mark:" + Style.RESET_ALL))

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

    def generate_password(self, letter: bool = True, digit: bool = True, punctuation: bool = True, length=8):
        if not any([letter, digit, punctuation]):
            print((Fore.RED + 'You must select at least one character type!' + Style.RESET_ALL))
            return

        if letter and digit and punctuation:
            characters = string.ascii_letters + string.digits + string.punctuation
        elif letter and digit:
            characters = string.ascii_letters + string.digits
        elif letter and punctuation:
            characters = string.ascii_letters + string.punctuation
        elif digit and punctuation:
            characters = string.digits + string.punctuation
        elif letter:
            characters = string.ascii_letters
        elif digit:
            characters = string.digits
        else:
            characters = string.punctuation

        if length < 4:
            length = 4

        password = []
        for _ in range(length):
            password.append(random.choice(characters))

        random.shuffle(password)
        result = "".join(password)
        print('Generated Password:' + Fore.LIGHTGREEN_EX + f' {result}' + Style.RESET_ALL)
        Q = input('Do you want to save it (y,n)? ')
        if Q.upper() == 'Y':
            Name = input('Enter a name for it: ')
            self.vault.append({
                'id': str(uuid.uuid4()),
                'Name': Name,
                'Password': result,
                'create_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
            self.save_data()
            print(emoji.emojize(Fore.GREEN + 'The generated password was saved successfully :check_mark:' + Style.RESET_ALL))
            
    def os_remove_file(self):
        if not os.path.exists(self.filename) and not os.path.exists(self.lock):
            print(emoji.emojize(Fore.RED + 'There is not any file on your system :cross_mark:' + Style.RESET_ALL))
            return
        
        confirm = input("Are you sure you want to delete your all password and lock file? (y,n): ")
        if confirm.upper() == 'Y':
            if os.path.exists(self.filename):
                os.remove(self.filename)
            if os.path.exists(self.lock):
                os.remove(self.lock)
            if os.path.exists('status.txt'):
                os.remove('status.txt')
            if os.path.exists(VERSION_FILE):
                os.remove(VERSION_FILE)
            print(emoji.emojize(Fore.GREEN + 'The files were removed! :check_mark_button:' + Style.RESET_ALL))

    
    def continue_program(self):
        Q = input('Do you want to continue Password Manager (y,n)? ')
        if Q.upper() == 'Y':
            return True
        else:
            print(emoji.emojize('Goodbye:hand_with_fingers_splayed:'))
            return False

            
def password_manager(vault_class):
    vault = vault_class()
    play = True
    
    while play:
        print(emoji.emojize(f'\n--- Password Manager v{APP_VERSION} ---'))
        print(emoji.emojize('1. Add a password :plus:'))
        print(emoji.emojize('2. Remove a password :wastebasket:'))
        print(emoji.emojize('3. Search a password :magnifying_glass_tilted_left:'))
        print(emoji.emojize('4. Show all passwords :clipboard:'))
        print(emoji.emojize('5. Edit a password :pencil:'))
        print(emoji.emojize('6. Check password strength :bar_chart:'))
        print(emoji.emojize('7. Replace weak passwords :shield:'))
        print(emoji.emojize('8. Generate a password :game_die:'))
        print(emoji.emojize('9. Change your master password :locked_with_key:'))
        print(emoji.emojize('10. Reset all data :bomb:'))
        print(emoji.emojize('11. Exit :cross_mark:'))

        while True:
            try:
                choose = int(input('Enter a number from the List: '))
                break
            except ValueError:
                print('Just enter a number')
        
        if choose == 1:
            Name = input('Enter a name for this password (for example: instagram): ').strip()
            password = input('Enter your password: ').strip()
            if not Name or not password:
                print(Fore.RED + 'Name and password cannot be empty.' + Style.RESET_ALL)
                play = vault.continue_program()
            else:
                vault.add_pass(Name, password)
                play = vault.continue_program()

        elif choose == 2:
            if vault.vault:
                Name = input('Enter a name to remove it: ')
                vault.remove_by_name(Name)
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
            vault.check_pass_level()
            play = vault.continue_program()

        elif choose == 7:
            vault.remove_weak_password()
            play = vault.continue_program()

        elif choose == 8:
            acci = input('Do you want the alphabet for generation password (y,n)? ')
            if acci.lower() == 'y':
                letter = True
            else:
                letter = False

            number = input('Do you want numbers for generation password (y,n)? ')
            if number.lower() == 'y':
                digit = True
            else:
                digit = False

            pun = input('Do you want the punctuation mark for generation password (y,n)? ')
            if pun.lower() == 'y':
                punctuation = True
            else:
                punctuation = False

            play = True
            while play:
                try: 
                    length = input('Enter a length of the password (DEFAULT IS 8): ')
                    if length == '':
                        vault.generate_password(letter, digit, punctuation)
                        play = False
                        break
                    length = int(length)
                    break
                except ValueError:
                    print(Fore.YELLOW + 'Please enter a valid number.' + Style.RESET_ALL)

            if play:
                vault.generate_password(letter, digit, punctuation, length)
            play = vault.continue_program()

        elif choose == 9:
            vault.recover_password()
            continue

        elif choose == 10:
            vault.os_remove_file()
            break

        elif choose == 11:
            print(emoji.emojize('Goodbye:hand_with_fingers_splayed:'))
            break
        else:
            print(emoji.emojize(Fore.RED + 'Invalid number :cross_mark:' + Style.RESET_ALL))

def turn():
    password_manager(Vault_Pass)
        
if __name__ == '__main__':
    turn()
