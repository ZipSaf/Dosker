import json
import os
import hashlib
import time
from datetime import datetime

# Paths for JSON storage
DATABASE_PATH = 'dosker_database.json'
FILESYSTEM_PATH = 'dosker_filesystem.json'

# Load or initialize databases
def load_database(path):
    if os.path.exists(path):
        with open(path, 'r') as file:
            return json.load(file)
    return {}

def save_database(data, path):
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)

# Initialize data if not present
users_db = load_database(DATABASE_PATH)
file_system = load_database(FILESYSTEM_PATH)

# Ensure root user exists
if 'root' not in users_db:
    users_db['root'] = {
        "password": hashlib.sha256("doskerrootuseradmin".encode()).hexdigest(),
        "files": [],
        "directories": ["/"]
    }
    save_database(users_db, DATABASE_PATH)

# Utility Functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Commands for the Dosker kernel
class DoskerKernel:
    def __init__(self):
        self.current_user = None
        self.current_dir = "/"
        self.prompt = "Dosker> "
        self.start_time = time.time()
        self.history = []

    def set_prompt(self):
        self.prompt = f"{self.current_user}@Dosker> " if self.current_user else "Dosker> "

    def startup(self):
        print("Welcome to Dosker Kernel!")
        print("Type 'rsu' to log in as the root user.")
        while not self.current_user:
            print("\n1. Sign In\n2. Sign Up\n3. Exit")
            choice = input("Choose an option: ")
            if choice == "1":
                self.signin()
            elif choice == "2":
                self.signup()
            elif choice == "3":
                print("Exiting Dosker...")
                exit()
            else:
                print("Invalid choice, please try again.")

    def signin_as_root(self):
        print("Logging in as root...")
        self.current_user = "root"
        self.set_prompt()
        print(f"Welcome, {self.current_user}!")

    def signup(self):
        print("Sign Up")
        username = input("Enter new username: ")
        if username in users_db or username == "root":
            print("Username already exists or is restricted.")
            return
        password = input("Enter new password: ")
        users_db[username] = {"password": hash_password(password), "files": [], "directories": ["/"]}
        save_database(users_db, DATABASE_PATH)
        print("Sign up successful! You are now signed in.")
        self.current_user = username
        self.set_prompt()

    def signin(self):
        print("Sign In")
        username = input("Username: ")
        password = input("Password: ")
        if username not in users_db or users_db[username]["password"] != hash_password(password):
            print("Invalid username or password.")
            return
        print(f"Welcome back, {username}!")
        self.current_user = username
        self.set_prompt()

    def help(self):
        print("""
Available Commands:
- help          : Show this help message.
- add_user      : Add a new user (syntax: add_user <username> <password>).
- del_user      : Delete a user (restricted to root, syntax: del_user <username>).
- resetdata     : Reset all user and file data (restricted to root).
- setprompt     : Set a custom prompt (syntax: setprompt <new_prompt>).
- dir           : List files in the current directory.
- cd            : Change directory (syntax: cd <directory>).
- create_file   : Create a file (syntax: create_file <filename> <content>).
- read_file     : Read a file (syntax: read_file <filename>).
- write_file    : Write to an existing file (syntax: write_file <filename> <content>).
- delete_file   : Delete a file (syntax: delete_file <filename>).
- view_files    : View user's files.
- uptime        : Display system uptime.
- history       : Show command history.
- logout        : Log out the current user.
- mkdir         : Create a new directory (syntax: mkdir <directory_name>).
- rmdir         : Remove an existing directory (syntax: rmdir <directory_name>).
- sysinfo       : Display system information.
- userlist      : List all users (restricted to root).
- memory        : Show simulated memory usage.
- exit          : Exit the Dosker kernel.
""")

    def add_user(self, username, password):
        if username in users_db or username == "root":
            print("User already exists or name is restricted.")
            return
        users_db[username] = {"password": hash_password(password), "files": [], "directories": ["/"]}
        save_database(users_db, DATABASE_PATH)
        print(f"User '{username}' added.")

    def del_user(self, username):
        if self.current_user == "root" and username != "root":
            if username in users_db:
                del users_db[username]
                save_database(users_db, DATABASE_PATH)
                print(f"User '{username}' deleted.")
            else:
                print("User not found.")
        else:
            print("Permission denied. Only root can delete users, and root cannot be deleted.")

    def resetdata(self):
        if self.current_user == "root":
            global users_db, file_system
            users_db = {"root": users_db["root"]}
            file_system = {}
            save_database(users_db, DATABASE_PATH)
            save_database(file_system, FILESYSTEM_PATH)
            print("All data reset.")
        else:
            print("Permission denied. Only root can reset data.")

    def setprompt(self, new_prompt):
        self.prompt = new_prompt

    def dir(self):
        if self.current_user:
            directories = users_db[self.current_user]["directories"]
            files = [f["filename"] for f in users_db[self.current_user]["files"]]
            print(f"Directories: {directories}")
            print(f"Files: {files if files else 'No files found.'}")
        else:
            print("No user signed in.")

    def cd(self, directory):
        if directory in users_db[self.current_user]["directories"]:
            self.current_dir = directory
            print(f"Current directory changed to: {self.current_dir}")
        else:
            print("Directory not found.")

    def create_file(self, filename, content):
        if self.current_user:
            file_entry = {"filename": filename, "content": content}
            users_db[self.current_user]["files"].append(file_entry)
            save_database(users_db, DATABASE_PATH)
            print(f"File '{filename}' created.")
        else:
            print("No user signed in.")

    def read_file(self, filename):
        if self.current_user:
            files = users_db[self.current_user]["files"]
            for file in files:
                if file["filename"] == filename:
                    print(f"Content of '{filename}': {file['content']}")
                    return
            print("File not found.")
        else:
            print("No user signed in.")

    def write_file(self, filename, content):
        if self.current_user:
            files = users_db[self.current_user]["files"]
            for file in files:
                if file["filename"] == filename:
                    file['content'] = content
                    save_database(users_db, DATABASE_PATH)
                    print(f"File '{filename}' updated.")
                    return
            print("File not found.")
        else:
            print("No user signed in.")

    def delete_file(self, filename):
        if self.current_user:
            files = users_db[self.current_user]["files"]
            for file in files:
                if file["filename"] == filename:
                    users_db[self.current_user]["files"].remove(file)
                    save_database(users_db, DATABASE_PATH)
                    print(f"File '{filename}' deleted.")
                    return
            print("File not found.")
        else:
            print("No user signed in.")

    def view_files(self):
        if self.current_user:
            files = users_db[self.current_user]["files"]
            print("Your files:", files if files else "No files.")
        else:
            print("No user signed in.")

    def uptime(self):
        uptime_duration = time.time() - self.start_time
        uptime_str = str(datetime.fromtimestamp(uptime_duration).strftime('%H:%M:%S'))
        print("System Uptime:", uptime_str)

    def history(self):
        print("Command History:")
        for i, command in enumerate(self.history, 1):
            print(f"{i}. {command}")

    def logout(self):
        if self.current_user:
            print(f"User '{self.current_user}' logged out.")
            self.current_user = None
            self.set_prompt()
            self.startup()  # Return to startup screen after logout

    def mkdir(self, directory_name):
        if self.current_user:
            if directory_name not in users_db[self.current_user]["directories"]:
                users_db[self.current_user]["directories"].append(directory_name)
                save_database(users_db, DATABASE_PATH)
                print(f"Directory '{directory_name}' created.")
            else:
                print("Directory already exists.")
        else:
            print("No user signed in.")

    def rmdir(self, directory_name):
        if self.current_user:
            if directory_name in users_db[self.current_user]["directories"] and directory_name != "/":
                users_db[self.current_user]["directories"].remove(directory_name)
                save_database(users_db, DATABASE_PATH)
                print(f"Directory '{directory_name}' removed.")
            else:
                print("Directory not found or cannot remove root directory.")
        else:
            print("No user signed in.")

    def sysinfo(self):
        print(f"Current User: {self.current_user if self.current_user else 'None'}")
        print(f"Directories: {users_db[self.current_user]['directories'] if self.current_user else 'N/A'}")
        print(f"Total Users: {len(users_db)}")

    def userlist(self):
        if self.current_user == "root":
            print("User List:")
            for user in users_db:
                print(user)
        else:
            print("Permission denied. Only root can view user list.")

    def memory(self):
        # Simulated memory usage
        print("Simulated Memory Usage: 64 MB used out of 256 MB.")

    def exit_kernel(self):
        print("Exiting Dosker kernel...")
        exit()

    def run(self):
        while True:
            command_input = input(self.prompt).strip()
            if command_input:
                self.history.append(command_input)
                args = command_input.split()
                cmd = args[0]
                args = args[1:]

                if cmd == "help":
                    self.help()
                elif cmd == "add_user" and self.current_user == "root":
                    self.add_user(*args)
                elif cmd == "del_user" and self.current_user == "root":
                    self.del_user(*args)
                elif cmd == "resetdata" and self.current_user == "root":
                    self.resetdata()
                elif cmd == "setprompt":
                    self.setprompt(" ".join(args))
                elif cmd == "dir":
                    self.dir()
                elif cmd == "cd":
                    self.cd(args[0])
                elif cmd == "create_file":
                    self.create_file(args[0], " ".join(args[1:]))
                elif cmd == "read_file":
                    self.read_file(args[0])
                elif cmd == "write_file":
                    self.write_file(args[0], " ".join(args[1:]))
                elif cmd == "delete_file":
                    self.delete_file(args[0])
                elif cmd == "view_files":
                    self.view_files()
                elif cmd == "uptime":
                    self.uptime()
                elif cmd == "history":
                    self.history()
                elif cmd == "logout":
                    self.logout()
                elif cmd == "mkdir":
                    self.mkdir(args[0])
                elif cmd == "rmdir":
                    self.rmdir(args[0])
                elif cmd == "sysinfo":
                    self.sysinfo()
                elif cmd == "userlist":
                    self.userlist()
                elif cmd == "memory":
                    self.memory()
                elif cmd == "exit":
                    self.exit_kernel()
                elif cmd == "rsu":
                    self.signin_as_root()
                else:
                    print("Unknown command.")

if __name__ == "__main__":
    kernel = DoskerKernel()
    kernel.startup()
    kernel.run()
