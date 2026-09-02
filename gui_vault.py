import json
import os
import hashlib
import re
import random
import string
import uuid
import pyperclip
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

APP_VERSION = '1.1.0'
VERSION_FILE = 'version.txt'

class Vault_Pass():
    def __init__(self, filename = 'My_Pass.json', lock = 'lock.json'):
        self.lock = lock
        self.filename = filename
        self.version = self.show_version_update()
        self.question = self.load_question()
        self.vault = self.load_data()

    def show_version_update(self):
        old_version = None
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as file:
                old_version = file.read().strip()

        if old_version == APP_VERSION:
            return old_version
        else:
            with open(VERSION_FILE, 'w') as file:
                file.write(APP_VERSION)
            return APP_VERSION

    def load_data(self):   
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                return json.load(file)
        else:
            return []
        
    def save_data(self):
        with open(self.filename, 'w') as file:
            return json.dump(self.vault, file, indent=4)

    def load_question(self):
        if not os.path.exists('question.txt'):
            return None
        
        with open('question.txt', 'r', encoding='utf-8') as file:
            text = file.read()
        if text == 'False':
            return False
        elif text == 'True':
            return True

    def hash_pass(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
        
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
        def wrapper(self, Name, Password, root):
            level, result, status = self.check_pass_strength(Password)
            while status:
                messagebox.showwarning("Warn", f'Password level: {level}', parent=root)
                if result:
                    for res in result:
                        messagebox.showinfo("Resut", f'- {res}', parent=root)
                Q = messagebox.askyesno('Question', 'Do you want to save it?', parent=root)
                if Q:
                    return func(self, Name, Password, root)
                else:
                    Password = simpledialog.askstring('New Password', 'Enter a stronger password:')
                    level, result, status = self.check_pass_strength(Password)
            if not status:
                return func(self, Name, Password, root)
        return wrapper

    @check_pass_to_add
    def add_pass(self, Name, password, root):
        Name = Name.strip()
        password = password.strip()
        if any(pas['Name'] == Name and pas['Password'] == password for pas in self.vault):
            messagebox.showwarning("Warning", f"The name '{Name}' or password '{password}' is already exists", parent=root)
            return
        
        self.vault.append({
            'id': str(uuid.uuid4()),
            'Name': Name,
            'Password': password,
            'create_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
            })
        
        self.save_data()
        messagebox.showinfo("Successful", f"Password '{password}' added", parent=root)
        
    def search_pass(self, search: str):
        search = search.strip()
        found = [pas for pas in self.vault if search.lower() in pas['Name'].lower() or search.lower() in pas['Password'].lower()]

        if not found:
            return f"'{search}' not found"
        return found
    
    def delete_id_by_name(self, id):
        self.vault = [pas for pas in self.vault if pas['id'] != id]
        self.save_data()

    def remove_by_name(self, Name: str, root):
        Name = Name.strip()

        found = [pas for pas in self.vault if pas['Name'].lower() == Name.lower()]
        if not found:
            messagebox.showwarning('Not Found', f"'{Name}' was not found", parent=root)
            return None

        if len(found) == 1:
            self.delete_id_by_name(found[0]['id'])
            messagebox.showinfo('Successful', f"Your password: '{found[0]['Password']}' is removed", parent=root)
            return None
        else:
            return found

    def edit_pass(self, Name: str, old_password: str, root):
        Name = Name.strip()
        old = old_password.strip()
        found = False
        for pas in self.vault:
            if pas['Name'] == Name and pas['Password'] == old:
                new = simpledialog.askstring('New Password', "Enter a new password:", parent=root)
                if new == '':
                    messagebox.showwarning('Empty Field', 'The field cannot be empty!', parent=root)
                    return
                if not new:
                    return
                pas['Password'] = new
                pas['updated_at'] = datetime.now().isoformat()
                self.save_data()
                messagebox.showinfo('Successful', 'Password updated successfully', parent=root)
                found = True
                break
        
        if not found:
            messagebox.showerror('Not Found', f"Password for '{Name}' not found", parent=root)
            return

    def remove_weak_password(self):
        if self.vault:
            for pas in self.vault:
                level, result, status = self.check_pass_strength(pas['Password'])
                messagebox.showinfo('Level', f"Password '{pas['Name']}' is {level}")
                if status:
                    Q = messagebox.askyesno('Question', f'Do you want to change the password for {pas['Name']}?')
                            
                    if Q:
                        while status:
                            new_password = simpledialog.askstring('New Password', f'Enter a new password for {pas['Name']}:')
                            if new_password == '':
                                messagebox.showwarning('Empty Field', 'The field cannot be empty!')
                                return
                            if not new_password:
                                return
                            level, result, status = self.check_pass_strength(new_password)
                            if status:
                                messagebox.showwarning('Still Weak', f'Your password is still weak!')
                        pas['Password'] = new_password
                        pas['create_at'] = datetime.now().isoformat()
                        pas['updated_at'] = datetime.now().isoformat()
                        self.save_data()
                        messagebox.showinfo('Successful', f"Your password: '{pas['Password']}' is changed successfully")
                    else:
                        remove = messagebox.askyesno('Question', 'Do you want to remove the password?')
                        if remove:
                            self.vault.remove(pas)
                            self.save_data()
                            messagebox.showinfo('Successful', f"Your password: '{pas['Password']}' is removed")
        else:
            messagebox.showerror('No Password', "There is not passwords to remove them yet!")

    def generate_password(self, root, letter: bool = True, digit: bool = True, punctuation: bool = True, length=8):
        if not any([letter, digit, punctuation]):
            messagebox.showwarning('No Select', 'You must select at least one character type!', parent=root)
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
        return result

    def security_scan(self, root):
        if not self.vault:
            messagebox.showerror('Not Found', 'There is not any passwords to scan', parent=root)
            return

        weak_password = []
        duplicate_password = []
        password_map = {}

        for pas in self.vault:
            password = pas['Password']

            level, problems, status = self.check_pass_strength(password)

            if status:
                weak_password.append(pas)

            if password in password_map:
                duplicate_password.append((password_map[password], pas))
            else:
                password_map[password] = pas['Name']

        total = len(self.vault)

        score = self.calculte_security_score(total, len(weak_password), len(duplicate_password))
        return total, weak_password, duplicate_password, score


    def calculte_security_score(self, total, weak, duplicate):
        score = 100

        score -= (weak / total) * 50
        score -= (duplicate / total) * 50

        return max(0, round(score))

    def os_remove_file(self): 
        confirm = messagebox.askyesno('Reset Factory Warning', "Are you sure you want to delete your all password and lock file?")
        if confirm:
            if os.path.exists(self.filename):
                os.remove(self.filename)
            if os.path.exists(self.lock):
                os.remove(self.lock)
            if os.path.exists('status.txt'):
                os.remove('status.txt')
            if os.path.exists(VERSION_FILE):
                os.remove(VERSION_FILE)
            if os.path.exists('question.txt'):
                os.remove('question.txt')
            messagebox.showinfo('Successful', 'The files were removed!')


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Personal Security Center')
        self.root.configure(bg="#0f1419")
        self.vault = Vault_Pass()
        self.current_theme = 'dark'
        self.theme = {
            'dark': {
                'bg': '#0f1419',
                'fg': '#00d9d4',
                'button_bg': '#00bfb7',
                'button_fg': '#0f1419',
                'activebg': '#00e0d8',
                'activefg': '#000000',
                'bg_exit': '#ef4444',
                'fg_exit': '#ffffff',
                'abg_exit': '#dc2626',
                'afg_exit': '#ffffff',
                'frame_bg': '#1a1f26'
            },
            'light': {
                'bg': '#f3f4f6',
                'fg': '#0f172a',
                'button_bg': '#2563eb',
                'button_fg': '#ffffff',
                'activebg': '#1e40af',
                'activefg': '#ffffff',
                'bg_exit': '#ef4444',
                'fg_exit': '#ffffff',
                'abg_exit': '#dc2626',
                'afg_exit': '#ffffff',
                'frame_bg': '#ffffff'
            }
        }

        self.colors = self.theme['dark']

        if self.vault.question is None:
            Q = messagebox.askyesno('Lock File', 'Do you want to lock your file with a master password (y,n)? ')
            if Q:
                self.vault.question = True
                with open('question.txt', 'w', encoding='utf-8') as file:
                    file.write('True')
            else:
                self.vault.question = False
                with open('question.txt', 'w', encoding='utf-8') as file:
                    file.write('False')

        if self.vault.question:
            if os.path.exists(self.vault.lock):
                self.check_master()
            else:
                self.setup_window()
        else:
            self.main_menu()

    def clear(self):
        for wg in self.root.winfo_children():
            wg.destroy()

    def toggle_theme(self):
        theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.current_theme = theme
        self.colors = self.theme[theme]

        try:
            self.root.configure(bg=self.colors['bg'])
        except Exception:
            pass

        self.main_menu()

    def setup_window(self):
        self.clear()
        self.root.geometry("420x370")
        self.root.title("Setup Lock")

        tk.Label(self.root, text="Set up your lock", font=("Arial", 18, "bold"), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, columnspan=2, padx=10, pady=(18, 12), sticky="ew")

        question_var = tk.StringVar()
        password_var = tk.StringVar()
        confirm_var = tk.StringVar()

        tk.Label(self.root, text="Security Question:", font=(None, 10, "bold"), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=1, column=0, padx=12, pady=8, sticky="w")
        entry = tk.Entry(self.root, textvariable=question_var, bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])
        entry.grid(row=1, column=1, padx=12, pady=8, sticky="ew")

        tk.Label(self.root, text="Master Password:", font=(None, 10, "bold"), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=2, column=0, padx=12, pady=8, sticky="w")
        master_entry = tk.Entry(self.root, textvariable=password_var, show="*", bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])
        master_entry.grid(row=2, column=1, padx=12, pady=8, sticky="ew")

        tk.Label(self.root, text="Confirm Password:", font=(None, 10, "bold"), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=3, column=0, padx=12, pady=8, sticky="w")
        confirm_entry = tk.Entry(self.root, textvariable=confirm_var, show="*", bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])
        confirm_entry.grid(row=3, column=1, padx=12, pady=8, sticky="ew")

        entry.focus_set()

        def save():
            question = question_var.get().strip()
            password = password_var.get()
            confirm = confirm_var.get()

            if not question:
                messagebox.showerror("Error", "Security question is required.", parent=self.root)
                return

            if not password or not confirm:
                messagebox.showerror("Error", "Password fields cannot be empty.", parent=self.root)
                return

            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match.", parent=self.root)
                master_entry.delete(0, tk.END)
                confirm_entry.delete(0, tk.END)
                return

            data = {
                "master": self.vault.hash_pass(password),
                "answer": self.vault.hash_pass(question)
            }

            with open(self.vault.lock, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)

            with open('question.txt', 'w', encoding='utf-8') as file:
                file.write('True')

            messagebox.showinfo("Saved", "Lock setup completed successfully.", parent=self.root)
            self.main_menu()

        def cancel():
            with open('question.txt', 'w', encoding='utf-8') as file:
                file.write('False')
            self.main_menu()

        button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        button_frame.grid(row=4, column=0, columnspan=2, padx=12, pady=(12, 10), sticky="ew")

        tk.Button(button_frame, text="Save", command=save, width=12, bg=self.colors['button_bg'],fg=self.colors['button_fg'], activebackground=self.colors['activebg'], 
                activeforeground=self.colors['activefg'], relief="flat", cursor="hand2").grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        tk.Button(button_frame, text="Cancel", command=cancel, width=12, bg=self.colors['bg_exit'], fg=self.colors['fg_exit'], activebackground=self.colors['abg_exit'],
            activeforeground=self.colors['afg_exit'], relief="flat", cursor="hand2").grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.root.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

    def check_master(self):
        self.clear()
        self.root.geometry('330x160')
        self.root.title('Check Master Password')

        tk.Label(self.root, text="Check your password lock", font=("Arial", 18, "bold"), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, columnspan=2, padx=10, pady=(18, 12), sticky="ew")

        password_var = tk.StringVar()

        tk.Label(self.root, text="Master Password:", font=(None, 10, "bold"), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=1, column=0, padx=12, pady=8, sticky="w")
        entry = tk.Entry(self.root, textvariable=password_var, show="*", bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])
        entry.grid(row=1, column=1, padx=12, pady=8, sticky="ew")
        entry.focus_set()

        def check():
            password = password_var.get()

            if not password:
                messagebox.showerror("Error", "Password fields cannot be empty.", parent=self.root)
                return

            with open(self.vault.lock, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if self.vault.hash_pass(password) == data['master']:
                self.main_menu()
                return
            else:
                messagebox.showerror("Wrong Password", "Your Master Password is not correct!", parent=self.root)
                entry.delete(0, tk.END)


        button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        button_frame.grid(row=2, column=0, columnspan=2, padx=12, pady=(12, 10), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        tk.Button(button_frame, text="Continue", command=check, width=12, bg=self.colors['button_bg'],fg=self.colors['button_fg'], activebackground=self.colors['activebg'], 
                activeforeground=self.colors['activefg'], relief="flat", cursor="hand2").grid(row=0, column=0, columnspan=2, padx=5, pady=5)

    def change_master_password(self):
        self.clear()
        self.root.geometry("340x180")
        self.root.title("Change Lock")

        tk.Label(self.root, text="Change your password lock", font=("Arial", 18, "bold"), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, columnspan=2, padx=10, pady=(18, 12), sticky="ew")

        question_var = tk.StringVar()
        password_var = tk.StringVar()

        question_label = tk.Label(self.root, text="Security Question:", font=(None, 10, "bold"), bg=self.colors['bg'], fg=self.colors['fg'])
        question_label.grid(row=1, column=0, padx=12, pady=8, sticky="w")

        question_entry = tk.Entry(self.root, textvariable=question_var, bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])
        question_entry.grid(row=1, column=1, padx=12, pady=8, sticky="ew")
        question_entry.focus_set()

        new_password_label = tk.Label(self.root, text="New Master Password:", font=(None, 10, "bold"), bg=self.colors['bg'], fg=self.colors['fg'])
        new_password_entry = tk.Entry(self.root, textvariable=password_var, show="*", bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])

        def save():
            password = password_var.get().strip()

            if not password:
                messagebox.showerror('Empty Field', 'Password fields cannot be empty!', parent=self.root)
                return

            with open(self.vault.lock, 'r', encoding='utf-8') as file:
                data = json.load(file)

            data['master'] = self.vault.hash_pass(password)

            with open(self.vault.lock, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)

            messagebox.showinfo('Successful', 'New Master Password is saved successfully!', parent=self.root)
            self.setting()

        def cont():
            question = question_var.get().strip()

            if not question:
                messagebox.showerror('Empty Fields', 'The fields cannot be empty!', parent=self.root)
                return

            with open(self.vault.lock, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if self.vault.hash_pass(question) != data['answer']:
                messagebox.showerror('Not Correct', 'The Security Question is not corrcet!', parent=self.root)
                return

            question_label.grid_forget()
            question_entry.grid_forget()
            new_password_label.grid(row=1, column=0, padx=12, pady=8, sticky="w")
            new_password_entry.grid(row=1, column=1, padx=12, pady=8, sticky="ew")
            new_password_entry.focus_set()
            continue_btn.configure(text='Save', command=save)

        button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        button_frame.grid(row=2, column=0, columnspan=2, padx=12, pady=(12, 10), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        continue_btn = tk.Button(button_frame, text="Continue", command=cont, width=12, bg=self.colors['button_bg'],fg=self.colors['button_fg'], activebackground=self.colors['activebg'], 
                activeforeground=self.colors['activefg'], relief="flat", cursor="hand2")
        continue_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        tk.Button(button_frame, text="Back", command=self.setting, width=12, bg=self.colors['bg_exit'], fg=self.colors['fg_exit'], activebackground=self.colors['abg_exit'],
            activeforeground=self.colors['afg_exit'], relief="flat", cursor="hand2").grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def change_security_question(self):
        self.clear()
        self.root.geometry("380x180")
        self.root.title("Change Security Question")

        tk.Label(self.root, text="Change your Security Question", font=("Arial", 18, "bold"), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, columnspan=2, padx=10, pady=(18, 12), sticky="ew")

        question_var = tk.StringVar()
        new_question_var = tk.StringVar()

        current_label = tk.Label(self.root, text="Security Question:", font=(None, 10, "bold"), bg=self.colors['bg'], fg=self.colors['fg'])
        current_label.grid(row=1, column=0, padx=12, pady=8, sticky="w")

        current_entry = tk.Entry(self.root, textvariable=question_var, bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])
        current_entry.grid(row=1, column=1, padx=12, pady=8, sticky="ew")
        current_entry.focus_set()

        new_label = tk.Label(self.root, text="New Security Question:", font=(None, 10, "bold"), bg=self.colors['bg'], fg=self.colors['fg'])
        new_entry = tk.Entry(self.root, textvariable=new_question_var, bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])

        def save():
            new_question = new_question_var.get().strip()

            if not new_question:
                messagebox.showwarning('Empty Field', 'The field cannot be empty!', parent=self.root)
                return

            with open(self.vault.lock, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if self.vault.hash_pass(new_question) == data['answer']:
                messagebox.showwarning('Warning', f"This '{new_question}' is already existed!", parent=self.root)
                return

            data['answer'] = self.vault.hash_pass(new_question)

            with open(self.vault.lock, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)

            messagebox.showinfo('Successful', 'Security question saved successfully!', parent=self.root)
            self.setting()

        def cont():
            question = question_var.get().strip()

            if not question:
                messagebox.showwarning('Empty Field', 'The field cannot be empty!', parent=self.root)
                return

            with open(self.vault.lock, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if self.vault.hash_pass(question) != data['answer']:
                messagebox.showerror('Not Correct', 'The Security Question is not corrcet!', parent=self.root)
                return

            current_label.grid_forget()
            current_entry.grid_forget()
            new_label.grid(row=1, column=0, padx=12, pady=8, sticky="w")
            new_entry.grid(row=1, column=1, padx=12, pady=8, sticky="ew")
            new_entry.focus_set()
            continue_btn.configure(text='Save', command=save)

        button_frame = tk.Frame(self.root, bg=self.colors['bg'])
        button_frame.grid(row=2, column=0, columnspan=2, padx=12, pady=(12, 10), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        continue_btn = tk.Button(button_frame, text="Continue", command=cont, width=12, bg=self.colors['button_bg'],fg=self.colors['button_fg'], activebackground=self.colors['activebg'], 
                activeforeground=self.colors['activefg'], relief="flat", cursor="hand2")
        continue_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        tk.Button(button_frame, text="Back", command=self.setting, width=12, bg=self.colors['bg_exit'], fg=self.colors['fg_exit'], activebackground=self.colors['abg_exit'],
            activeforeground=self.colors['afg_exit'], relief="flat", cursor="hand2").grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
    def main_menu(self):
        self.clear()
        self.root.geometry('370x175')

        label = tk.Label(self.root, text="Personal Security", font=("Arial", 17, 'bold'), bg=self.colors['bg'], fg=self.colors['fg'])
        label.grid(row=0, column=0, columnspan=2, padx=25, pady=10, sticky="ew")

        label = tk.Label(self.root, text=f'v{self.vault.version}', font=("Arial", 13, 'bold'), bg=self.colors['bg'], fg=self.colors['fg'])
        label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        password_btn = tk.Button(self.root, text="Password Manager", width=20, font=(None, 10, 'bold'), command=self.password_manager,
                                bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        password_btn.grid(row=1, column=0, padx=8, pady=5, sticky="nsew")

        check_btn = tk.Button(self.root, text="Security Report", width=20, font=(None, 10, 'bold'), command=self.report,
                            bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        check_btn.grid(row=1, column=1, padx=8, pady=5, sticky="nsew")

        encrypt_btn = tk.Button(self.root, text="Generate Password", width=20, font=(None, 10, 'bold'), command=self.generation_password,
                            bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        encrypt_btn.grid(row=2, column=0, padx=8, pady=5, sticky="nsew")

        brute_btn = tk.Button(self.root, text="Setting", width=20, font=(None, 10, 'bold'), command=self.setting,
                            bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        brute_btn.grid(row=2, column=1, padx=8, pady=5, sticky="nsew")

        exit_btn = tk.Button(self.root, text="Exit", width=10, font=(None, 10, 'bold'), command=self.root.quit,
                            bg=self.colors['bg_exit'], fg=self.colors['fg_exit'], activebackground=self.colors['abg_exit'], activeforeground=self.colors['afg_exit'], relief='flat', cursor='hand2')
        exit_btn.grid(row=3, column=0, columnspan=2, padx=5, pady=6)

        btn_text = "🌙" if self.current_theme == 'dark' else "☀️"
        theme_btn = tk.Button(
            self.root,
            text=btn_text,
            width=3,
            height=1,
            font=("Segoe UI Emoji", 12),
            command=self.toggle_theme,
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            activebackground=self.colors['activebg'],
            activeforeground=self.colors['activefg'],
            relief="raised",
            bd=1,
            highlightthickness=0,
            cursor="hand2"
        )
        theme_btn.grid(row=0, column=1, padx=12, pady=10, sticky="e")


    def password_manager(self):
        self.clear()
        self.root.geometry("290x230")

        label = tk.Label(self.root, text="Password Manager", font=("Arial", 20, 'bold'), bg=self.colors['bg'], fg=self.colors['fg'])
        label.grid(row=0, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")

        add_btn = tk.Button(self.root, text="Add Password", width=15, font=(None, 10, 'bold'), command=self.add_password,
                    bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        add_btn.grid(row=1, column=0, padx=8, pady=5, sticky="nsew")

        remove_btn = tk.Button(self.root, text="Remove Password", width=15, font=(None, 10, 'bold'), command=self.remove_password,
                    bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        remove_btn.grid(row=1, column=1, padx=8, pady=5, sticky="nsew")

        search_btn = tk.Button(self.root, text="Search Password", width=15, font=(None, 10, 'bold'), command=self.search_password,
                    bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        search_btn.grid(row=2, column=0, padx=8, pady=5, sticky="nsew")

        edit_btn = tk.Button(self.root, text="Edit Password", width=15, font=(None, 10, 'bold'), command=self.edit_password,
                    bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        edit_btn.grid(row=2, column=1, padx=8, pady=5, sticky="nsew")

        show_btn = tk.Button(self.root, text="Show All Passwords", width=15, font=(None, 10, 'bold'), command=self.show_passwords,
                    bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        show_btn.grid(row=3, column=0, columnspan=2, padx=8, pady=5, sticky="nsew")

        back_btn = tk.Button(self.root, text="Back", width=10, font=(None, 10, 'bold'), command=self.main_menu,
                    bg=self.colors['bg_exit'], fg=self.colors['fg_exit'], activebackground=self.colors['abg_exit'], activeforeground=self.colors['afg_exit'], relief='flat', cursor='hand2')
        back_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def report(self):
        self.clear()
        self.root.geometry("380x230")

        label = tk.Label(self.root, text='Security Report', font=('Arial', 20, 'bold'), bg=self.colors['bg'], fg=self.colors['fg'])
        label.grid(row=0, column=0, columnspan=2, padx=10, pady=15, sticky='nsew')

        run_btn = tk.Button(self.root, text="Run Security Scan", width=20, font=(None, 10, 'bold'), command=self.run_scan,
                    bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        run_btn.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        check_btn = tk.Button(self.root, text="Check Password Level", width=20, font=(None, 10, 'bold'), command=self.check_password,
                    bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        check_btn.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        remove_btn = tk.Button(self.root, text="Remove Weak Password", width=20, font=(None, 10, 'bold'), command=self.vault.remove_weak_password,
                    bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        remove_btn.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        back_btn = tk.Button(self.root, text="Back", width=20, font=(None, 10, 'bold'), command=self.main_menu,
                    bg=self.colors['bg_exit'], fg=self.colors['fg_exit'], activebackground=self.colors['abg_exit'], activeforeground=self.colors['afg_exit'], relief='flat', cursor='hand2')
        back_btn.grid(row=2, column=1, columnspan=2, padx=10, pady=10)

    def generation_password(self):
        self.clear()
        self.root.geometry("310x210")

        tk.Label(self.root, text="Generation Password", font=("Arial", 20, 'bold'), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")

        tk.Label(self.root, text="Length (DEFAULT IS 8):", font=(None, 10), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        length_entry = tk.Entry(self.root, bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])
        length_entry.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        length_entry.focus_set()

        result_label = tk.Label(self.root, text="", font=(None, 10), bg=self.colors['bg'], fg=self.colors['fg'])
        result_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        def generate():
            global result
            try:
                length = length_entry.get().strip()
                if length == '':
                    result = self.vault.generate_password(self.root, letter, digit, punctuation)
                else:
                    length = int(length)
                    result = self.vault.generate_password(self.root, letter, digit, punctuation, length)
                length_entry.delete(0, tk.END)
                result_label.configure(text=result)
                gen_btn.destroy()
                save_btn.grid(row=0, column=0, padx=5, pady=5)
                copy_btn.grid(row=0, column=1, padx=5, pady=5)
                back_btn.grid(row=0, column=2, padx=5, pady=5)
            except ValueError:
                messagebox.showwarning('Warning', 'Please enter a valid number.', parent=self.root)

        def save():
            Name = simpledialog.askstring('Input', 'Enter a name for it:', parent=self.root)
            if Name == '':
                messagebox.showwarning('Empty Field', 'The field cannot be empty!', parent=self.root)
                return
            if not Name:
                return

            self.vault.vault.append({
                'id': str(uuid.uuid4()),
                'Name': Name,
                'Password': result,
                'create_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
            self.vault.save_data()
            messagebox.showinfo('Successful', 'The generated password was saved successfully', parent=self.root)

        def copy():
            try:
                pyperclip.copy(result)
                messagebox.showinfo('Successful', 'The generated password copied to the clipboard successfully', parent=self.root)
            except pyperclip.PyperclipException as e:
                messagebox.showerror('Error Copy', e, parent=self.root)

        frame_button = tk.Frame(self.root, bg=self.colors['frame_bg'])
        frame_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)
        
        gen_btn = tk.Button(frame_button, text="Generate", command=generate, width=10, bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], 
                        activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        gen_btn.grid(row=0, column=0, padx=5, pady=5)

        save_btn = tk.Button(frame_button, text='Save', command=save, width=10, bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], 
                        activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')

        copy_btn = tk.Button(frame_button, text='Copy', command=copy, width=10, bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], 
                        activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')

        back_btn = tk.Button(frame_button, text="Back", command=self.main_menu, width=10, bg=self.colors['bg_exit'], fg=self.colors['fg_exit'], activebackground=self.colors['abg_exit'], 
                        activeforeground=self.colors['afg_exit'], relief='flat', cursor='hand2')
        back_btn.grid(row=0, column=1, padx=5, pady=5)

        acci = messagebox.askyesno('', 'Do you want the alphabet for generation password=?', parent=self.root)
        if acci:
            letter = True
        else:
            letter = False

        number = messagebox.askyesno('', 'Do you want numbers for generation password?', parent=self.root)
        if number:
            digit = True
        else:
            digit = False

        pun = messagebox.askyesno('', 'Do you want the punctuation mark for generation password?', parent=self.root)
        if pun:
            punctuation = True
        else:
            punctuation = False

    def setting(self):
        self.clear()
        self.root.geometry("380x220")

        label = tk.Label(self.root, text="Setting", font=("Arial", 20, 'bold'), bg=self.colors['bg'], fg=self.colors['fg'])
        label.grid(row=0, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")

        set_btn = tk.Button(self.root, text="Set Master Password", width=20, font=(None, 10, 'bold'), command=self.setup_master,
                    bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        set_btn.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        change_btn = tk.Button(self.root, text="Change Master Password", width=20, font=(None, 10, 'bold'), command=self.change_master,
                    bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        change_btn.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        question_btn = tk.Button(self.root, text="Change Security Question", width=20, font=(None, 10, 'bold'), command=self.change_security,
                    bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        question_btn.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        reset_btn = tk.Button(self.root, text="Reset Factory", width=20, font=(None, 10, 'bold'), command=self.vault.os_remove_file,
                    bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2')
        reset_btn.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        back_btn = tk.Button(self.root, text="Back", width=10, font=(None, 10, 'bold'), command=self.main_menu,
                    bg=self.colors['bg_exit'], fg=self.colors['fg_exit'], activebackground=self.colors['abg_exit'], activeforeground=self.colors['afg_exit'], relief='flat', cursor='hand2')
        back_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def add_password(self):
        self.clear()
        self.root.geometry("220x220")

        tk.Label(self.root, text="Add Password", font=("Arial", 20, 'bold'), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")

        tk.Label(self.root, text="Name:", font=(None, 10), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        name_entry = tk.Entry(self.root, width=15, bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])
        name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        tk.Label(self.root, text="Password:", font=(None, 10), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        pass_entry = tk.Entry(self.root, show="*", width=15, bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])
        pass_entry.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        name_entry.focus_set()
        
        def add():
            name = name_entry.get()
            password = pass_entry.get()
            if not name or not password:
                messagebox.showerror("Error", "Name and password cannot be empty.", parent=self.root)
                return

            name_entry.delete(0, tk.END)
            pass_entry.delete(0, tk.END)
            self.vault.add_pass(name, password, self.root)

        frame_button = tk.Frame(self.root, bg=self.colors['frame_bg'])
        frame_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)
        tk.Button(frame_button, text="Add", command=add, width=10,
            bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor="hand2").grid(row=0, column=0, padx=5, pady=5)
        
        tk.Button(frame_button, text="Back", command=self.password_manager, width=10,
            bg=self.colors['bg_exit'], fg=self.colors['fg_exit'], activebackground=self.colors['abg_exit'], activeforeground=self.colors['afg_exit'], relief="flat", cursor="hand2").grid(row=0, column=1, padx=5, pady=5)

    def remove_password(self):
        if not self.vault.vault:
            messagebox.showerror("Empty", "There is no password to remove!", parent=self.root)
            return
        
        self.clear()
        self.root.geometry("270x170")

        tk.Label(self.root, text="Remove Password", font=("Arial", 20, 'bold'), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")

        name_label = tk.Label(self.root, text="Name:", font=(None, 10), bg=self.colors['bg'], fg=self.colors['fg'])
        name_label.grid(row=1, column=0, padx=(30, 0), pady=10, sticky="nsew")
        name_entry = tk.Entry(self.root, width=17, bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])
        name_entry.grid(row=1, column=1, padx=(0, 30), pady=10)

        name_entry.focus_set()

        list_frame = tk.Frame(self.root, bg=self.colors['frame_bg'])
        label = tk.Label(list_frame, text="Choose:", font=(None, 10, 'bold'), bg=self.colors['frame_bg'], fg=self.colors['fg'])
        self.listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, bg=self.colors['bg'], fg=self.colors['fg'], selectbackground=self.colors['activebg'], selectforeground=self.colors['activefg'], width=60, height=10)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)

                
        def remove():
            global found
            name = name_entry.get()
            if not name:
                messagebox.showerror("Error", "Name cannot be empty.", parent=self.root)
                return

            name_entry.delete(0, tk.END)
            found = self.vault.remove_by_name(name, self.root)
            if found is None:
                return

            self.root.geometry("410x320")
            name_label.destroy()
            name_entry.destroy()
            list_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
            label.grid(row=0, column=0, pady=0, sticky='w')
            self.listbox.grid(row=1, column=0, padx=5, pady=5)
            scrollbar.grid(row=1, column=1, sticky="ns")
            self.listbox.config(yscrollcommand=scrollbar.set)
            remove_btn.configure(command=delete)
            refresh_listbox(found)

        def refresh_listbox(found):
            self.listbox.delete(0, tk.END)
            for password in found:
                self.listbox.insert(tk.END, f"{password['Name']}: {password['Password']}")

        def delete():
            select = self.listbox.curselection()
            if not select:
                messagebox.showerror('Select Error', 'Please choose to remove!', parent=self.root)
                return

            Q = messagebox.askyesno("Confirm", "Are you sure you want to remove?", parent=self.root)
            if Q:
                for index in reversed(select):
                    self.vault.delete_id_by_name(found[index]['id'])
                    self.listbox.delete(index)
                messagebox.showinfo("Success", "Password deleted successfully.", parent=self.root)
                self.password_manager()
            
        frame_button = tk.Frame(self.root, bg=self.colors['frame_bg'])
        frame_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        
        remove_btn = tk.Button(frame_button, text="Remove", command=remove, width=10, bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], 
                    activeforeground=self.colors['activefg'], relief="flat", cursor="hand2")
        remove_btn.grid(row=0, column=0, padx=5, pady=5)
        
        tk.Button(frame_button, text="Back", command=self.password_manager, width=10,
            bg=self.colors['bg_exit'], fg=self.colors['fg_exit'], activebackground=self.colors['abg_exit'], activeforeground=self.colors['afg_exit'], relief="flat", cursor="hand2").grid(row=0, column=1, padx=5, pady=5)

    def search_password(self):
        if not self.vault.vault:
            messagebox.showerror("Empty", "There is no password to search!", parent=self.root)
            return
        
        self.clear()
        self.root.geometry("260x170")

        tk.Label(self.root, text="Search Password", font=("Arial", 20, 'bold'), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")

        tk.Label(self.root, text="Name,Password:", font=(None, 10), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        name_entry = tk.Entry(self.root, width=10, bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])
        name_entry.grid(row=1, column=1, padx=(0, 20), pady=5, sticky="nsew")
        name_entry.focus_set()

        def search():
            name = name_entry.get()
            if not name:
                messagebox.showerror('Empty Field', 'The field cannot be empty!')
                return
            
            name_entry.delete(0, tk.END)
            result = self.vault.search_pass(name)
            if type(result) is str:
                messagebox.showerror('Not Found', result, parent=self.root)
                return
            elif type(result) is list:
                if len(result) == 1:
                    messagebox.showinfo('Found', f"Name: {result[0]['Name']}\nPassword: {result[0]['Password']}", parent=self.root)
                else:
                    self.clear()
                    self.root.geometry("360x320")
                    tk.Label(self.root, text="Search Results", font=("Arial", 18, 'bold'), 
                        bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        
                    frame = tk.Frame(self.root, bg=self.colors['frame_bg'])
                    frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
                    
                    text = tk.Text(frame, bg=self.colors['bg'], fg=self.colors['fg'], height=12, width=40)
                    text.grid(row=0, column=0, sticky="nsew")
                    
                    scrollbar = tk.Scrollbar(frame, command=text.yview)
                    scrollbar.grid(row=0, column=1, sticky="ns")
                    text.config(yscrollcommand=scrollbar.set)
                    
                    text.insert("end", f"Found {len(result)} result(s):\n\n")
                    for idx, pas in enumerate(result, 1):
                        text.insert("end", f"{idx}.\nName: {pas['Name']}\n")
                        text.insert("end", f"Password: {pas['Password']}\n")
                        text.insert("end", "-" * 40 + "\n\n")
                    
                    text.config(state="disabled")

                    button = tk.Frame(self.root, bg=self.colors['frame_bg'])
                    button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
                    tk.Button(button, text="Back", command=self.password_manager, width=10, bg=self.colors['bg_exit'], fg=self.colors['fg_exit'], activebackground=self.colors['abg_exit'], 
                            activeforeground=self.colors['afg_exit'], relief='flat', cursor='hand2').grid(row=0, column=0, padx=5, pady=5)
        
        frame_button = tk.Frame(self.root, bg=self.colors['frame_bg'])
        frame_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        
        tk.Button(frame_button, text="Search", command=search, width=10,
            bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor='hand2').grid(row=0, column=0, padx=5, pady=5)
                
        tk.Button(frame_button, text="Back", command=self.password_manager, width=10,
            bg=self.colors['bg_exit'], fg=self.colors['fg_exit'], activebackground=self.colors['abg_exit'], activeforeground=self.colors['afg_exit'], relief='flat', cursor='hand2').grid(row=0, column=1, padx=5, pady=5)

    def edit_password(self):
        if not self.vault.vault:
            messagebox.showerror("Empty", "There is no password to edit!", parent=self.root)
            return
        
        self.clear()
        self.root.geometry("260x220")

        tk.Label(self.root, text="Edit Password", font=("Arial", 20, 'bold'), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")

        tk.Label(self.root, text="Name:", font=(None, 10), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        name_entry = tk.Entry(self.root, bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])
        name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        tk.Label(self.root, text="Old Password:", font=(None, 10), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        old_entry = tk.Entry(self.root, show="*", bg=self.colors['frame_bg'], fg=self.colors['fg'], insertbackground=self.colors['fg'])
        old_entry.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

        name_entry.focus_set()

        def edit():
            name = name_entry.get()
            old = old_entry.get()
            if not name or not old:
                messagebox.showerror("Error", "Name and old password required.", parent=self.root)
                return

            name_entry.delete(0, tk.END)
            old_entry.delete(0, tk.END)
            self.vault.edit_pass(name, old, self.root)

        frame_button = tk.Frame(self.root, bg=self.colors['frame_bg'])
        frame_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        tk.Button(frame_button, text="Edit", command=edit, width=10,
            bg=self.colors['button_bg'], fg=self.colors['button_fg'], activebackground=self.colors['activebg'], activeforeground=self.colors['activefg'], relief="flat", cursor="hand2").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(frame_button, text="Back", command=self.password_manager, width=10,
            bg=self.colors['bg_exit'], fg=self.colors['fg_exit'], activebackground=self.colors['abg_exit'], activeforeground=self.colors['afg_exit'], relief="flat", cursor="hand2").grid(row=0, column=1, padx=5, pady=5)

    def show_passwords(self):
        if not self.vault.vault:
            messagebox.showerror("Empty", "There is no password to show!", parent=self.root)
            return
        
        self.clear()
        self.root.geometry("610x520")

        tk.Label(self.root, text="All Passwords", font=("Arial", 20, 'bold'), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")

        frame = tk.Frame(self.root, bg=self.colors['frame_bg'], relief="ridge")
        frame.grid(row=1, column=0, padx=10, pady=10)
        text = tk.Text(frame, bg=self.colors['bg'], fg=self.colors['fg'], font=("Courier", 9), relief="flat")
        text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        scrollbar = tk.Scrollbar(frame, command=text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        text.config(yscrollcommand=scrollbar.set)


        text.insert("end", f"You have {len(self.vault.vault)} password(s):\n\n")
        for pas in self.vault.vault:
            text.insert("end", f"Name: {pas['Name']}\nPassword: {pas['Password']}\n")
            text.insert("end", "=" * 80 +"\n")

        frame_button = tk.Frame(self.root, bg="#1a1f26")
        frame_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        tk.Button(frame_button, text="Back", command=self.password_manager, width=10,
                bg="#ef4444", fg="#ffffff", activebackground="#dc2626", activeforeground="#ffffff").grid(row=0, column=0, padx=5, pady=5)

    def run_scan(self):
        if not self.vault.vault:
            messagebox.showerror("Empty", "There is no password to show!", parent=self.root)
            return
        
        self.clear()
        self.root.geometry('610x300')
        tk.Label(self.root, text="Scaning Passwords", font=("Arial", 20, 'bold'), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")

        frame = tk.Frame(self.root, bg=self.colors['frame_bg'], relief="ridge")
        frame.grid(row=1, column=0, padx=10, pady=10)
        text = tk.Text(frame, height=10, bg=self.colors['bg'], fg=self.colors['fg'], font=("Courier", 9), relief="flat")
        text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        scrollbar = tk.Scrollbar(frame, command=text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        text.config(yscrollcommand=scrollbar.set)

        total, weak, duplicate, score = self.vault.security_scan(self.root)
        text.insert('end', f'Total Passwords: {total}\n')
        text.insert('end', f'Weak Paswords: {len(weak)}\n')
        text.insert('end', f'Duplicate Passwords: {len(duplicate)}\n')
        text.insert('end', f'Security Score: {score}/100\n')

        if weak:
            text.insert('end', '\nWeak Password:\n')
            for entry in weak:
                text.insert('end', f'- {entry['Name']} is weak\n')
        if duplicate:
            text.insert('end', '\nDuplicate Password:\n')
            for first, second in duplicate:
                text.insert('end', f'- {first} and {second['Name']} use the same password.\n')
        text.config(state='disabled')
        
        frame_button = tk.Frame(self.root, bg="#1a1f26")
        frame_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        tk.Button(frame_button, text="Back", command=self.report, width=10,
                bg="#ef4444", fg="#ffffff", activebackground="#dc2626", activeforeground="#ffffff").grid(row=0, column=0, padx=5, pady=5)

    def check_password(self):
        if not self.vault.vault:
            messagebox.showwarning('Warning', 'There are no passwords here to check them!', parent=self.root)
            return

        self.clear()
        self.root.geometry("610x520")

        tk.Label(self.root, text="All Password Levels", font=("Arial", 20, 'bold'), bg=self.colors['bg'], fg=self.colors['fg']).grid(row=0, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")

        frame = tk.Frame(self.root, bg=self.colors['frame_bg'], relief="ridge")
        frame.grid(row=1, column=0, padx=10, pady=10)
        text = tk.Text(frame, bg=self.colors['bg'], fg=self.colors['fg'], font=("Courier", 9), relief="flat")
        text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        scrollbar = tk.Scrollbar(frame, command=text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        text.config(yscrollcommand=scrollbar.set)

        for index, check in enumerate(self.vault.vault, 1):
            level, result, status = self.vault.check_pass_strength(check['Password'])
            text.insert("end", f"{index}.\nName: {check['Name']}\nLevel: {level}\n")
            if result:
                text.insert("end", "Problems:\n")
                for problem in result:
                    text.insert("end", f"- {problem}\n")
            text.insert("end", "=" * 80 + "\n")

        frame_button = tk.Frame(self.root, bg="#1a1f26")
        frame_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        tk.Button(frame_button, text="Back", command=self.report, width=10,
                bg="#ef4444", fg="#ffffff", activebackground="#dc2626", activeforeground="#ffffff").grid(row=0, column=0, padx=5, pady=5)

    def setup_master(self):
        if os.path.exists(self.vault.lock):
            messagebox.showwarning("Warn", "You already setup master password!", parent=self.root)
            return
        self.setup_window()

    def change_master(self):
        if not os.path.exists(self.vault.lock):
            messagebox.showwarning('Warning', 'You do not have a master password yet', parent=self.root)
            return
        self.change_master_password()

    def change_security(self):
        if not os.path.exists(self.vault.lock):
            messagebox.showwarning('Warning', 'You do not have a master password yet', parent=self.root)
            return
        self.change_security_question()

if __name__ == '__main__':
    app = App()
    app.root.mainloop()
