# hybridos_core.py
import os
import subprocess
import platform
import shutil
import datetime
import getpass
from pathlib import Path

class HybridOS:
    def __init__(self):
        self.commands = {
            "help": self.help,
            "exit": self.exit,
            "ls": self.ls,
            "dir": self.ls,  # Windows alias
            "pwd": self.pwd,
            "cd": self.cd,
            "mkdir": self.mkdir,
            "rmdir": self.rmdir,
            "rm": self.rm,
            "del": self.rm,  # Windows alias
            "cat": self.cat,
            "type": self.cat,  # Windows alias
            "echo": self.echo,
            "whoami": self.whoami,
            "date": self.date,
            "time": self.date,  # Windows alias
            "clear": self.clear,
            "cls": self.clear,  # Windows alias
            "touch": self.touch,
            "mv": self.mv,
            "move": self.mv,  # Windows alias
            "cp": self.cp,
            "copy": self.cp,  # Windows alias
            "find": self.find,
            "grep": self.grep,
            "findstr": self.grep,  # Windows alias
            "ps": self.ps,
            "tasklist": self.ps,  # Windows alias
            "kill": self.kill,
            "taskkill": self.kill,  # Windows alias
            "uname": self.uname,
            "systeminfo": self.uname,  # Windows alias
            "df": self.df,
            "du": self.du,
            "history": self.history,
            "env": self.env,
            "set": self.env,  # Windows alias
            "which": self.which,
            "where": self.which,  # Windows alias
            "head": self.head,
            "tail": self.tail,
            "wc": self.wc,
            "sort": self.sort,
            "chmod": self.chmod,
            "ping": self.ping,
            "ipconfig": self.ipconfig,
            "ifconfig": self.ipconfig,  # Linux alias
            "netstat": self.netstat,
            "hostname": self.hostname,
            "ver": self.ver,
            "calc": self.calc,
            "notepad": self.notepad,
            "python": self.python_cmd,
            "pip": self.pip,
        }
        self.command_history = []

    def _normalize_path(self, path):
        """Normalize a path, handling both absolute and relative paths on Windows and Unix"""
        path = path.strip()
        if not path:
            return path
        
        # Remove surrounding quotes if present
        if (path.startswith('"') and path.endswith('"')) or (path.startswith("'") and path.endswith("'")):
            path = path[1:-1].strip()
        
        # Handle Windows absolute paths (C:\... or C:/...)
        if platform.system() == "Windows":
            # Check if it's an absolute Windows path (drive letter)
            if len(path) >= 2 and path[1] == ':':
                # It's an absolute Windows path, normalize it
                return os.path.normpath(path)
            # Check if it's a Unix-style absolute path (starts with /)
            elif path.startswith('/'):
                # Unix-style absolute path on Windows (e.g., /mnt/e, /c/Users)
                # Try to convert WSL-style paths to Windows paths
                # /mnt/e -> E:\
                # /mnt/e/some/path -> E:\some\path
                # /c/Users -> C:\Users
                # /c/Users/path -> C:\Users\path
                if path.startswith('/mnt/'):
                    # WSL mount point: /mnt/e -> E:\
                    # /mnt/e/path -> E:\path
                    # Remove /mnt/ prefix
                    remaining = path[5:]  # Everything after /mnt/
                    if remaining:
                        # Split drive letter and rest of path
                        if '/' in remaining:
                            drive_letter = remaining.split('/')[0].upper()
                            rest = '/'.join(remaining.split('/')[1:])
                            windows_path = f"{drive_letter}:\\{rest}".replace('/', '\\')
                        else:
                            # Just /mnt/e (no subdirectory)
                            drive_letter = remaining.upper()
                            windows_path = f"{drive_letter}:\\"
                        return os.path.normpath(windows_path)
                    else:
                        # Just /mnt/ (invalid, but handle gracefully)
                        return os.path.normpath(path)
                elif len(path) > 1 and path[1] != '/':
                    # /c/Users style (Git Bash style)
                    # /c -> C:\
                    # /c/Users -> C:\Users
                    remaining = path[1:]  # Everything after first /
                    if remaining:
                        if '/' in remaining:
                            drive_letter = remaining.split('/')[0].upper()
                            rest = '/'.join(remaining.split('/')[1:])
                            windows_path = f"{drive_letter}:\\{rest}".replace('/', '\\')
                        else:
                            # Just /c (no subdirectory)
                            drive_letter = remaining.upper()
                            windows_path = f"{drive_letter}:\\"
                        return os.path.normpath(windows_path)
                else:
                    # Just normalize as-is (might be a valid path in some contexts)
                    return os.path.normpath(path)
            else:
                # Relative path, expand user and normalize
                return os.path.normpath(os.path.expanduser(path))
        else:
            # Linux/Mac - expand user and normalize
            # Check if it's an absolute path (starts with /)
            if path.startswith('/'):
                # Absolute path, just normalize
                return os.path.normpath(path)
            else:
                # Relative path, expand user and normalize
                return os.path.normpath(os.path.expanduser(path))

    def _parse_command(self, cmd):
        """Parse command line, handling quoted arguments"""
        cmd = cmd.strip()
        if not cmd:
            return None, ""
        
        parts = []
        current = ""
        in_quotes = False
        quote_char = None
        
        i = 0
        while i < len(cmd):
            char = cmd[i]
            
            if char in ['"', "'"] and (i == 0 or cmd[i-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                    # Don't add quote to current, skip it
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                    # Don't add quote to current, skip it
                else:
                    # Different quote type inside quotes - add it
                    current += char
            elif char == ' ' and not in_quotes:
                if current:
                    parts.append(current)
                    current = ""
            else:
                current += char
            
            i += 1
        
        if current:
            parts.append(current)
        
        if not parts:
            return None, ""
        
        cmd_name = parts[0].lower()
        # Join remaining parts with spaces
        args = ' '.join(parts[1:]) if len(parts) > 1 else ""
        
        return cmd_name, args

    def execute(self, cmd):
        cmd = cmd.strip()
        if not cmd:
            return ""
        
        # Add to history
        self.command_history.append(cmd)
        
        # Parse command and arguments (handling quotes)
        cmd_name, args = self._parse_command(cmd)
        
        if not cmd_name:
            return ""
        
        if cmd_name in self.commands:
            try:
                return self.commands[cmd_name](args)
            except Exception as e:
                return f"Error executing {cmd_name}: {e}"
        else:
            return f"Unknown command: {cmd_name}. Type 'help' to see available commands."

    # ---- Built-in Commands ----
    def help(self, args=""):
        commands_list = sorted(self.commands.keys())
        return "Available commands:\n" + ", ".join(commands_list) + "\n\nType 'help <command>' for more info on a specific command."

    def exit(self, args=""):
        return "exit"

    # ---- File System Commands ----
    def ls(self, args=""):
        try:
            if platform.system() == "Windows":
                cmd = "dir" + (" " + args if args else "")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            else:
                cmd = "ls" + (" " + args if args else " -la")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error: {e}"

    def pwd(self, args=""):
        try:
            return os.getcwd()
        except Exception as e:
            return f"Error: {e}"

    def cd(self, args=""):
        try:
            if not args:
                home = os.path.expanduser("~")
                os.chdir(home)
                return f"Changed to: {home}"
            
            path = self._normalize_path(args)
            
            # Check if path exists
            if not os.path.exists(path):
                return f"Error: Directory not found: {args.strip()}"
            
            # Check if it's a directory
            if not os.path.isdir(path):
                return f"Error: Not a directory: {args.strip()}"
            
            # Change directory
            os.chdir(path)
            return f"Changed to: {os.getcwd()}"
        except FileNotFoundError:
            return f"Error: Directory not found: {args.strip()}"
        except PermissionError:
            return f"Error: Permission denied: {args.strip()}"
        except Exception as e:
            return f"Error: {e}"

    def mkdir(self, args=""):
        if not args:
            return "Usage: mkdir <directory_name>"
        try:
            path = self._normalize_path(args)
            os.makedirs(path, exist_ok=True)
            return f"Created directory: {path}"
        except Exception as e:
            return f"Error: {e}"

    def rmdir(self, args=""):
        if not args:
            return "Usage: rmdir <directory_name>"
        try:
            path = self._normalize_path(args)
            os.rmdir(path)
            return f"Removed directory: {path}"
        except Exception as e:
            return f"Error: {e}"

    def rm(self, args=""):
        if not args:
            return "Usage: rm <file_or_directory>"
        try:
            path = self._normalize_path(args)
            if os.path.isdir(path):
                shutil.rmtree(path)
                return f"Removed directory: {path}"
            else:
                os.remove(path)
                return f"Removed file: {path}"
        except Exception as e:
            return f"Error: {e}"

    def cat(self, args=""):
        if not args:
            return "Usage: cat <filename>"
        try:
            path = self._normalize_path(args)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except FileNotFoundError:
            return f"Error: File not found: {args}"
        except Exception as e:
            return f"Error: {e}"

    def touch(self, args=""):
        if not args:
            return "Usage: touch <filename>"
        try:
            path = self._normalize_path(args)
            Path(path).touch()
            return f"Created/updated file: {path}"
        except Exception as e:
            return f"Error: {e}"

    def mv(self, args=""):
        if not args:
            return "Usage: mv <source> <destination>"
        try:
            parts = args.split(None, 1)
            if len(parts) < 2:
                return "Usage: mv <source> <destination>"
            src = self._normalize_path(parts[0])
            dst = self._normalize_path(parts[1])
            shutil.move(src, dst)
            return f"Moved {src} to {dst}"
        except Exception as e:
            return f"Error: {e}"

    def cp(self, args=""):
        if not args:
            return "Usage: cp <source> <destination>"
        try:
            parts = args.split(None, 1)
            if len(parts) < 2:
                return "Usage: cp <source> <destination>"
            src = self._normalize_path(parts[0])
            dst = self._normalize_path(parts[1])
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
            return f"Copied {src} to {dst}"
        except Exception as e:
            return f"Error: {e}"

    # ---- Text Processing Commands ----
    def echo(self, args=""):
        return args if args else ""

    def head(self, args=""):
        if not args:
            return "Usage: head <filename> [lines]"
        try:
            parts = args.split()
            filename = self._normalize_path(parts[0])
            n_lines = int(parts[1]) if len(parts) > 1 else 10
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:n_lines]
                return ''.join(lines)
        except Exception as e:
            return f"Error: {e}"

    def tail(self, args=""):
        if not args:
            return "Usage: tail <filename> [lines]"
        try:
            parts = args.split()
            filename = self._normalize_path(parts[0])
            n_lines = int(parts[1]) if len(parts) > 1 else 10
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[-n_lines:]
                return ''.join(lines)
        except Exception as e:
            return f"Error: {e}"

    def wc(self, args=""):
        if not args:
            return "Usage: wc <filename>"
        try:
            filename = self._normalize_path(args)
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.count('\n')
                words = len(content.split())
                chars = len(content)
                return f"{lines} lines, {words} words, {chars} characters"
        except Exception as e:
            return f"Error: {e}"

    def sort(self, args=""):
        if not args:
            return "Usage: sort <filename>"
        try:
            filename = self._normalize_path(args)
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                return ''.join(sorted(lines))
        except Exception as e:
            return f"Error: {e}"

    def grep(self, args=""):
        if not args:
            return "Usage: grep <pattern> <filename>"
        try:
            parts = args.split(None, 1)
            if len(parts) < 2:
                return "Usage: grep <pattern> <filename>"
            pattern = parts[0]
            filename = self._normalize_path(parts[1])
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                matching = [line for line in lines if pattern in line]
                return ''.join(matching) if matching else f"No matches found for '{pattern}'"
        except Exception as e:
            return f"Error: {e}"

    # ---- System Commands ----
    def whoami(self, args=""):
        try:
            return getpass.getuser()
        except Exception as e:
            return f"Error: {e}"

    def date(self, args=""):
        try:
            now = datetime.datetime.now()
            return now.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            return f"Error: {e}"

    def clear(self, args=""):
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
        return ""

    def uname(self, args=""):
        try:
            if platform.system() == "Windows":
                result = subprocess.run("systeminfo", shell=True, capture_output=True, text=True, timeout=5)
                return result.stdout[:500]  # Limit output
            else:
                result = subprocess.run("uname -a", shell=True, capture_output=True, text=True)
                return result.stdout
        except Exception as e:
            return f"Error: {e}"

    def ps(self, args=""):
        try:
            if platform.system() == "Windows":
                result = subprocess.run("tasklist", shell=True, capture_output=True, text=True)
            else:
                result = subprocess.run("ps aux", shell=True, capture_output=True, text=True)
            return result.stdout[:1000]  # Limit output
        except Exception as e:
            return f"Error: {e}"

    def kill(self, args=""):
        if not args:
            return "Usage: kill <process_id>"
        try:
            pid = int(args.strip())
            if platform.system() == "Windows":
                subprocess.run(f"taskkill /PID {pid} /F", shell=True, capture_output=True)
            else:
                subprocess.run(f"kill {pid}", shell=True, capture_output=True)
            return f"Terminated process {pid}"
        except Exception as e:
            return f"Error: {e}"

    def df(self, args=""):
        try:
            if platform.system() == "Windows":
                result = subprocess.run("wmic logicaldisk get size,freespace,caption", shell=True, capture_output=True, text=True)
            else:
                result = subprocess.run("df -h", shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Error: {e}"

    def du(self, args=""):
        if not args:
            args = "."
        try:
            path = self._normalize_path(args)
            if platform.system() == "Windows":
                result = subprocess.run(f'powershell -Command "(Get-ChildItem -Path \'{path}\' -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB"', shell=True, capture_output=True, text=True)
                return f"Size of {path}: {result.stdout.strip()} MB"
            else:
                result = subprocess.run(f"du -sh {path}", shell=True, capture_output=True, text=True)
                return result.stdout
        except Exception as e:
            return f"Error: {e}"

    def find(self, args=""):
        if not args:
            return "Usage: find <filename_pattern>"
        try:
            pattern = args.strip()
            results = []
            for root, dirs, files in os.walk(os.getcwd()):
                for name in files + dirs:
                    if pattern in name:
                        results.append(os.path.join(root, name))
            return '\n'.join(results[:50]) if results else f"No files found matching '{pattern}'"
        except Exception as e:
            return f"Error: {e}"

    def chmod(self, args=""):
        if platform.system() == "Windows":
            return "chmod is not available on Windows"
        if not args:
            return "Usage: chmod <permissions> <filename>"
        try:
            parts = args.split(None, 1)
            if len(parts) < 2:
                return "Usage: chmod <permissions> <filename>"
            perms = parts[0]
            filename = self._normalize_path(parts[1])
            os.chmod(filename, int(perms, 8))
            return f"Changed permissions of {filename} to {perms}"
        except Exception as e:
            return f"Error: {e}"

    # ---- Network Commands ----
    def ping(self, args=""):
        if not args:
            return "Usage: ping <hostname_or_ip>"
        try:
            if platform.system() == "Windows":
                result = subprocess.run(f"ping -n 4 {args.strip()}", shell=True, capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run(f"ping -c 4 {args.strip()}", shell=True, capture_output=True, text=True, timeout=10)
            return result.stdout
        except Exception as e:
            return f"Error: {e}"

    def ipconfig(self, args=""):
        try:
            if platform.system() == "Windows":
                result = subprocess.run("ipconfig", shell=True, capture_output=True, text=True)
            else:
                result = subprocess.run("ifconfig", shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"Error: {e}"

    def netstat(self, args=""):
        try:
            if platform.system() == "Windows":
                result = subprocess.run("netstat -an", shell=True, capture_output=True, text=True)
            else:
                result = subprocess.run("netstat -an", shell=True, capture_output=True, text=True)
            return result.stdout[:1000]  # Limit output
        except Exception as e:
            return f"Error: {e}"

    # ---- Utility Commands ----
    def which(self, args=""):
        if not args:
            return "Usage: which <command>"
        try:
            if platform.system() == "Windows":
                result = subprocess.run(f"where {args.strip()}", shell=True, capture_output=True, text=True)
            else:
                result = subprocess.run(f"which {args.strip()}", shell=True, capture_output=True, text=True)
            return result.stdout if result.stdout else f"Command '{args.strip()}' not found"
        except Exception as e:
            return f"Error: {e}"

    def env(self, args=""):
        try:
            if platform.system() == "Windows":
                result = subprocess.run("set", shell=True, capture_output=True, text=True)
            else:
                result = subprocess.run("env", shell=True, capture_output=True, text=True)
            return result.stdout[:1000]  # Limit output
        except Exception as e:
            return f"Error: {e}"

    def history(self, args=""):
        if not self.command_history:
            return "No command history"
        # Show last 20 commands
        recent = self.command_history[-20:]
        return '\n'.join(f"{i+1}: {cmd}" for i, cmd in enumerate(recent))

    def hostname(self, args=""):
        try:
            import socket
            return socket.gethostname()
        except Exception as e:
            return f"Error: {e}"

    def ver(self, args=""):
        try:
            if platform.system() == "Windows":
                result = subprocess.run("ver", shell=True, capture_output=True, text=True)
                return result.stdout.strip()
            else:
                result = subprocess.run("uname -r", shell=True, capture_output=True, text=True)
                return f"Kernel version: {result.stdout.strip()}"
        except Exception as e:
            return f"Error: {e}"

    def calc(self, args=""):
        if platform.system() != "Windows":
            return "Calculator is only available on Windows"
        try:
            subprocess.Popen("calc.exe")
            return "Calculator opened"
        except Exception as e:
            return f"Error: {e}"

    def notepad(self, args=""):
        if platform.system() != "Windows":
            return "Notepad is only available on Windows"
        try:
            if args:
                file_path = self._normalize_path(args)
                subprocess.Popen(["notepad.exe", file_path])
                return f"Opening {file_path} in Notepad"
            else:
                subprocess.Popen("notepad.exe")
                return "Notepad opened"
        except Exception as e:
            return f"Error: {e}"

    def python_cmd(self, args=""):
        if not args:
            return "Usage: python <code_or_file>\nExample: python print('Hello')"
        try:
            # Check if it's a file path
            normalized_path = self._normalize_path(args)
            if os.path.isfile(normalized_path):
                result = subprocess.run(["python", normalized_path], capture_output=True, text=True)
                return result.stdout + result.stderr
            else:
                # Try to execute as Python code
                result = subprocess.run(["python", "-c", args], capture_output=True, text=True)
                return result.stdout + result.stderr
        except Exception as e:
            return f"Error: {e}"

    def pip(self, args=""):
        if not args:
            return "Usage: pip <command>\nExample: pip list, pip install <package>"
        try:
            result = subprocess.run(["pip"] + args.split(), capture_output=True, text=True)
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error: {e}"
