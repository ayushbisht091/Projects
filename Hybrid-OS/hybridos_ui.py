# hybridos_gui_unified.py
import tkinter as tk
from hybridos_core import HybridOS
import subprocess
import os
from tkinter import filedialog

class HybridGUI:
    def __init__(self, root):
        self.os_shell = HybridOS()
        self.root = root
        self.wsl_available = self._check_wsl_available()
        self.root.title("HybridOS Unified Terminal")
        self.root.configure(bg="#1e1e1e")
        self.root.geometry("900x550")

        # Color scheme
        self.bg_dark = "#1e1e1e"
        self.bg_medium = "#2d2d2d"
        self.bg_light = "#3d3d3d"
        self.fg_primary = "#ffffff"
        self.fg_secondary = "#cccccc"
        self.accent = "#0078d4"
        self.border = "#404040"

        # ---- Main Layout Frame ----
        main_frame = tk.Frame(root, bg=self.bg_dark)
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Configure grid: 2 columns
        main_frame.columnconfigure(0, weight=1, minsize=180)  # Left panel (buttons)
        main_frame.columnconfigure(1, weight=3)  # Right panel (terminal)
        main_frame.rowconfigure(0, weight=1)

        # ---- Left Side Buttons Panel ----
        side_frame = tk.Frame(main_frame, bg=self.bg_medium, relief=tk.RAISED, bd=1)
        side_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 8))
        
        # Panel title
        title_label = tk.Label(
            side_frame, text="Actions", 
            bg=self.bg_medium, fg=self.fg_primary,
            font=("Segoe UI", 12, "bold"), pady=10
        )
        title_label.pack(fill="x")
        
        # Separator
        separator = tk.Frame(side_frame, bg=self.border, height=1)
        separator.pack(fill="x", padx=10, pady=5)
        
        # Button container
        button_container = tk.Frame(side_frame, bg=self.bg_medium)
        button_container.pack(fill="both", expand=True, padx=10, pady=10)

        # ---- Buttons on Left Panel ----
        self._create_button(
            button_container, "▶ Run Script", "#FFD700", "black",
            self.run_script, "Run a Python script file"
        ).pack(fill="x", pady=5)
        
        self._create_button(
            button_container, "📂 Open File", "#9d4edd", "white",
            self.open_file, "Select and run any file (exe, py, etc.)"
        ).pack(fill="x", pady=5)
        
        self._create_button(
            button_container, "📁 Browse Folder", "#32CD32", "white",
            self.browse_folder, "Change working directory"
        ).pack(fill="x", pady=5)
        
        self._create_button(
            button_container, "🗑 Clear", "#1E90FF", "white",
            self.clear_text, "Clear terminal output"
        ).pack(fill="x", pady=5)
        
        self._create_button(
            button_container, "✖ Exit", "#dc3545", "white",
            root.destroy, "Exit application"
        ).pack(fill="x", pady=5)

        # ---- Right Side Terminal Area ----
        terminal_frame = tk.Frame(main_frame, bg=self.bg_dark)
        terminal_frame.grid(row=0, column=1, sticky="nswe")
        terminal_frame.columnconfigure(0, weight=1)
        terminal_frame.rowconfigure(0, weight=2)  # Top box → 2 parts
        terminal_frame.rowconfigure(1, weight=1)  # Bottom box → 1 part

        # ---- Top Half: Output / Welcome Text ----
        output_frame = tk.Frame(terminal_frame, bg=self.bg_medium, relief=tk.RAISED, bd=1)
        output_frame.grid(row=0, column=0, sticky="nswe", pady=(0, 8))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(1, weight=1)
        
        # Output label
        output_label = tk.Label(
            output_frame, text="Output", 
            bg=self.bg_medium, fg=self.fg_secondary,
            font=("Segoe UI", 10, "bold"), anchor="w", padx=10, pady=5
        )
        output_label.grid(row=0, column=0, sticky="ew")
        
        # Text area with scrollbar
        text_container = tk.Frame(output_frame, bg=self.bg_medium)
        text_container.grid(row=1, column=0, sticky="nswe", padx=2, pady=(0, 2))
        text_container.columnconfigure(0, weight=1)
        text_container.rowconfigure(0, weight=1)
        
        scrollbar_output = tk.Scrollbar(text_container)
        scrollbar_output.grid(row=0, column=1, sticky="ns")
        
        self.text_area = tk.Text(
            text_container, bg="#0d1117", fg="#c9d1d9",
            font=("Consolas", 10), 
            yscrollcommand=scrollbar_output.set,
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10, pady=10,
            insertbackground="#ffffff"
        )
        self.text_area.grid(row=0, column=0, sticky="nswe")
        scrollbar_output.config(command=self.text_area.yview)
        
        self._insert_welcome_message()
        self.text_area.config(state=tk.DISABLED)

        # ---- Bottom Half: Command Input ----
        input_frame = tk.Frame(terminal_frame, bg=self.bg_medium, relief=tk.RAISED, bd=1)
        input_frame.grid(row=1, column=0, sticky="nswe")
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(1, weight=1)
        
        # Input label with prompt
        input_label = tk.Label(
            input_frame, text="Command Input (Enter to execute)", 
            bg=self.bg_medium, fg=self.fg_secondary,
            font=("Segoe UI", 10, "bold"), anchor="w", padx=10, pady=5
        )
        input_label.grid(row=0, column=0, sticky="ew")
        
        # Input area with scrollbar
        input_container = tk.Frame(input_frame, bg=self.bg_medium)
        input_container.grid(row=1, column=0, sticky="nswe", padx=2, pady=(0, 2))
        input_container.columnconfigure(0, weight=1)
        input_container.rowconfigure(0, weight=1)
        
        scrollbar_input = tk.Scrollbar(input_container)
        scrollbar_input.grid(row=0, column=1, sticky="ns")
        
        self.entry_area = tk.Text(
            input_container, bg="#161b22", fg="#c9d1d9",
            font=("Consolas", 10),
            yscrollcommand=scrollbar_input.set,
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10, pady=10,
            insertbackground="#ffffff"
        )
        self.entry_area.grid(row=0, column=0, sticky="nswe")
        scrollbar_input.config(command=self.entry_area.yview)
        
        self.entry_area.bind("<Shift-Return>", lambda e: self.entry_area.insert(tk.END, "\n"))
        self.entry_area.bind("<Return>", self.run_command)
        self.entry_area.focus_set()
        
        # Placeholder text
        self.entry_area.insert("1.0", "Enter command here...")
        self.entry_area.config(fg="#6e7681")
        self.input_placeholder = True
        
        # Bind events to remove placeholder
        self.entry_area.bind("<FocusIn>", self._on_input_focus_in)
        self.entry_area.bind("<FocusOut>", self._on_input_focus_out)
        self.entry_area.bind("<Button-1>", self._on_input_click)  # Click handler
        self.entry_area.bind("<KeyPress>", self._on_input_keypress)  # Key press handler

    def _create_button(self, parent, text, bg, fg, command, tooltip=""):
        """Create a styled button with hover effects"""
        btn = tk.Button(
            parent, text=text, 
            bg=bg, fg=fg, 
            font=("Segoe UI", 10, "bold"),
            relief=tk.RAISED, bd=2,
            cursor="hand2",
            command=command,
            padx=10, pady=8,
            activebackground=self._lighten_color(bg),
            activeforeground=fg
        )
        return btn
    
    def _lighten_color(self, color):
        """Lighten a hex color"""
        if color.startswith("#"):
            rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            rgb = tuple(min(255, int(c * 1.2)) for c in rgb)
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        return color
    
    def _on_input_focus_in(self, event):
        """Handle input focus in - remove placeholder"""
        self._clear_placeholder()
    
    def _on_input_focus_out(self, event):
        """Handle input focus out - add placeholder if empty"""
        if not self.entry_area.get("1.0", "end").strip():
            self.entry_area.insert("1.0", "Enter command here...")
            self.entry_area.config(fg="#6e7681")
            self.input_placeholder = True
    
    def _on_input_click(self, event):
        """Handle click on input area - remove placeholder"""
        self._clear_placeholder()
    
    def _clear_placeholder(self):
        """Clear placeholder text if present"""
        if self.input_placeholder:
            self.entry_area.delete("1.0", tk.END)
            self.entry_area.config(fg="#c9d1d9")
            self.input_placeholder = False
    
    def _on_input_keypress(self, event):
        """Handle key press - remove placeholder when user starts typing"""
        if self.input_placeholder and event.char and event.char.isprintable():
            # Only handle printable characters, let special keys work normally
            self._clear_placeholder()
            # Let the normal key insertion happen

    def _check_wsl_available(self):
        """Check if WSL (Windows Subsystem for Linux) is available"""
        if os.name != 'nt':  # Not Windows
            return False
        try:
            result = subprocess.run(
                ["wsl", "--list", "--quiet"],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

    def _try_wsl_command(self, cmd):
        """Try to execute command through WSL"""
        if not self.wsl_available:
            return None
        try:
            result = subprocess.run(
                ["wsl", "bash", "-c", cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout + result.stderr
            return output if output or result.returncode == 0 else None
        except subprocess.TimeoutExpired:
            return "Error: Command timed out (WSL)"
        except Exception as e:
            return None

    def _insert_welcome_message(self):
        """Insert welcome message into text area"""
        self.text_area.insert(tk.END, "╔═══════════════════════════════════════════════════════╗\n")
        self.text_area.insert(tk.END, "║        Welcome to HybridOS Terminal                  ║\n")
        self.text_area.insert(tk.END, "╚═══════════════════════════════════════════════════════╝\n\n")
        self.text_area.insert(tk.END, "Type commands below or use the action buttons on the left.\n")
        self.text_area.insert(tk.END, "Press Enter to execute, Shift+Enter for new line.\n")
        if self.wsl_available:
            self.text_area.insert(tk.END, "\n✓ WSL (Windows Subsystem for Linux) detected!\n")
            self.text_area.insert(tk.END, "  Ubuntu/Linux commands will automatically run in WSL.\n")
            self.text_area.insert(tk.END, "  Use 'wsl <command>' to explicitly run in WSL.\n")
        self.text_area.insert(tk.END, "\n")

    # ---- Command Execution ----
    def run_command(self, event):
        cmd = self.entry_area.get("1.0", "end").strip()
        
        # Ignore if placeholder text or empty
        if not cmd or cmd == "Enter command here...":
            return "break"
        
        # Clear input and reset placeholder
        self.entry_area.delete("1.0", "end")
        self.entry_area.insert("1.0", "Enter command here...")
        self.entry_area.config(fg="#6e7681")
        self.input_placeholder = True
        
        # Get command name (first word)
        cmd_parts = cmd.split(None, 1)
        cmd_name = cmd_parts[0].lower() if cmd_parts else ""
        
        # Handle cls/clear command - clear the terminal
        if cmd_name in ["cls", "clear"]:
            self.clear_text()
            return "break"
        
        # Display command with prompt
        self._display_output(f"$ {cmd}", "#58a6ff")

        # Try HybridOS command
        output = self.os_shell.execute(cmd)
        if output != f"Unknown command: {cmd_name}. Type 'help' to see available commands.":
            # Handle empty output (like from cls/clear)
            if output:
                self._display_output(output, "#c9d1d9")
            if output == "exit":
                self.root.after(500, self.root.destroy)
            return "break"

        # Else, try system command
        # Check if command explicitly wants WSL
        if cmd_name == "wsl" and self.wsl_available:
            # Remove 'wsl' prefix and run in WSL
            wsl_cmd = ' '.join(cmd.split()[1:]) if len(cmd.split()) > 1 else ""
            if wsl_cmd:
                wsl_output = self._try_wsl_command(wsl_cmd)
                if wsl_output is not None:
                    self._display_output(wsl_output, "#c9d1d9")
                else:
                    self._display_output("Error: Failed to execute WSL command", "#f85149")
            else:
                self._display_output("Usage: wsl <command>\nExample: wsl ls -la", "#f85149")
            return "break"
        
        # Try Windows command first
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout + result.stderr
            
            # If command failed and WSL is available, try WSL
            if result.returncode != 0 and self.wsl_available and os.name == 'nt':
                wsl_output = self._try_wsl_command(cmd)
                if wsl_output is not None:
                    self._display_output(f"[Windows failed, trying WSL...]", "#6e7681")
                    self._display_output(wsl_output, "#c9d1d9")
                    return "break"
            
            if output:
                self._display_output(output, "#c9d1d9")
            elif result.returncode == 0:
                self._display_output("Command executed successfully.", "#7c3aed")
            else:
                # Command failed, try WSL if available
                if self.wsl_available and os.name == 'nt':
                    wsl_output = self._try_wsl_command(cmd)
                    if wsl_output is not None:
                        self._display_output(f"[Windows failed, trying WSL...]", "#6e7681")
                        self._display_output(wsl_output, "#c9d1d9")
                    else:
                        self._display_output(f"Command failed with exit code {result.returncode}", "#f85149")
                else:
                    self._display_output(f"Command failed with exit code {result.returncode}", "#f85149")
        except subprocess.TimeoutExpired:
            self._display_output("Error: Command timed out", "#f85149")
        except Exception as e:
            # Try WSL as fallback if available
            if self.wsl_available and os.name == 'nt':
                wsl_output = self._try_wsl_command(cmd)
                if wsl_output is not None:
                    self._display_output(f"[Windows error, trying WSL...]", "#6e7681")
                    self._display_output(wsl_output, "#c9d1d9")
                else:
                    self._display_output(f"Error: {e}", "#f85149")
            else:
                self._display_output(f"Error: {e}", "#f85149")

        return "break"  # Prevent default newline

    # ---- Output Display ----
    def _display_output(self, message, color="#c9d1d9"):
        self.text_area.config(state=tk.NORMAL)
        tag_name = f"color_{color.replace('#', '')}"
        self.text_area.insert(tk.END, message + "\n", (tag_name,))
        self.text_area.tag_configure(tag_name, foreground=color)
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    # ---- Run Script ----
    def run_script(self):
        file_path = filedialog.askopenfilename(
            title="Select Python Script", filetypes=[("Python Files", "*.py")]
        )
        if file_path:
            self._display_output(f"\n{'─' * 60}", "#404040")
            self._display_output(f"Running script: {os.path.basename(file_path)}", "#58a6ff")
            self._display_output(f"{'─' * 60}", "#404040")
            try:
                result = subprocess.run(["python", file_path], capture_output=True, text=True)
                output = result.stdout + result.stderr
                if output:
                    self._display_output(output, "#c9d1d9")
                else:
                    self._display_output("Script executed successfully (no output).", "#7c3aed")
            except Exception as e:
                self._display_output(f"Error running script: {e}", "#f85149")
            self._display_output(f"{'─' * 60}\n", "#404040")

    # ---- Open File ----
    def open_file(self):
        """Open and run any file type (exe, py, bat, etc.)"""
        file_path = filedialog.askopenfilename(
            title="Select File to Run",
            filetypes=[
                ("All Files", "*.*"),
                ("Executable Files", "*.exe"),
                ("Python Files", "*.py"),
                ("Batch Files", "*.bat;*.cmd"),
                ("PowerShell Scripts", "*.ps1"),
                ("Text Files", "*.txt"),
            ]
        )
        if file_path:
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            self._display_output(f"\n{'─' * 60}", "#404040")
            self._display_output(f"Opening file: {file_name}", "#58a6ff")
            self._display_output(f"File path: {file_path}", "#c9d1d9")
            self._display_output(f"{'─' * 60}", "#404040")
            
            try:
                # Determine how to run the file based on extension
                if file_ext == ".py":
                    # Python script
                    result = subprocess.run(
                        ["python", file_path], 
                        capture_output=True, 
                        text=True,
                        cwd=os.path.dirname(file_path) if os.path.dirname(file_path) else None
                    )
                    output = result.stdout + result.stderr
                    if output:
                        self._display_output(output, "#c9d1d9")
                    else:
                        self._display_output("Script executed successfully (no output).", "#7c3aed")
                elif file_ext == ".exe":
                    # Executable file
                    self._display_output("Running executable...", "#58a6ff")
                    # Run in background for GUI apps, or wait for console apps
                    process = subprocess.Popen(
                        [file_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=os.path.dirname(file_path) if os.path.dirname(file_path) else None
                    )
                    # Try to get output (non-blocking for GUI apps)
                    try:
                        stdout, stderr = process.communicate(timeout=1)
                        if stdout:
                            self._display_output(stdout, "#c9d1d9")
                        if stderr:
                            self._display_output(f"Errors: {stderr}", "#f85149")
                        if not stdout and not stderr:
                            self._display_output("Executable launched successfully.", "#7c3aed")
                    except subprocess.TimeoutExpired:
                        self._display_output("Executable launched (running in background).", "#7c3aed")
                elif file_ext in [".bat", ".cmd"]:
                    # Batch file
                    result = subprocess.run(
                        [file_path],
                        shell=True,
                        capture_output=True,
                        text=True,
                        cwd=os.path.dirname(file_path) if os.path.dirname(file_path) else None
                    )
                    output = result.stdout + result.stderr
                    if output:
                        self._display_output(output, "#c9d1d9")
                    else:
                        self._display_output("Batch file executed successfully.", "#7c3aed")
                elif file_ext == ".ps1":
                    # PowerShell script
                    result = subprocess.run(
                        ["powershell", "-ExecutionPolicy", "Bypass", "-File", file_path],
                        capture_output=True,
                        text=True,
                        cwd=os.path.dirname(file_path) if os.path.dirname(file_path) else None
                    )
                    output = result.stdout + result.stderr
                    if output:
                        self._display_output(output, "#c9d1d9")
                    else:
                        self._display_output("PowerShell script executed successfully.", "#7c3aed")
                else:
                    # Try to open with default system handler
                    self._display_output(f"Opening file with default application...", "#58a6ff")
                    if os.name == 'nt':  # Windows
                        os.startfile(file_path)
                        self._display_output("File opened with default application.", "#7c3aed")
                    elif os.name == 'posix':  # Linux/Mac
                        try:
                            # Try Linux first (xdg-open)
                            subprocess.run(["xdg-open", file_path], check=True)
                            self._display_output("File opened with default application.", "#7c3aed")
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            try:
                                # Try Mac (open)
                                subprocess.run(["open", file_path], check=True)
                                self._display_output("File opened with default application.", "#7c3aed")
                            except (subprocess.CalledProcessError, FileNotFoundError):
                                self._display_output("Could not open file. Please open it manually.", "#f85149")
                    
            except Exception as e:
                self._display_output(f"Error running file: {e}", "#f85149")
                self._display_output(f"Try running it manually or check file permissions.", "#f85149")
            
            self._display_output(f"{'─' * 60}\n", "#404040")

    # ---- Browse Folder ----
    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="Select a Folder")
        if folder_path:
            try:
                os.chdir(folder_path)
                self._display_output(f"\n{'─' * 60}", "#404040")
                self._display_output(f"Changed directory to:", "#58a6ff")
                self._display_output(f"  {folder_path}", "#c9d1d9")
                self._display_output(f"\nDirectory contents:", "#58a6ff")
                self._display_output(f"  (Use 'Open File' button to select and run files)", "#6e7681")
                self._display_output("", "#c9d1d9")
                
                files = os.listdir(folder_path)
                # Separate files and directories
                dirs = []
                exe_files = []
                py_files = []
                other_files = []
                
                for f in files:
                    full_path = os.path.join(folder_path, f)
                    if os.path.isdir(full_path):
                        dirs.append(f)
                    else:
                        ext = os.path.splitext(f)[1].lower()
                        if ext == ".exe":
                            exe_files.append(f)
                        elif ext == ".py":
                            py_files.append(f)
                        else:
                            other_files.append(f)
                
                # Display directories
                if dirs:
                    self._display_output("  📁 Directories:", "#58a6ff")
                    for d in sorted(dirs):
                        self._display_output(f"    • {d}/", "#c9d1d9")
                
                # Display executable files
                if exe_files:
                    self._display_output("  ⚙️  Executables (.exe):", "#58a6ff")
                    for f in sorted(exe_files):
                        self._display_output(f"    • {f}", "#7c3aed")
                
                # Display Python files
                if py_files:
                    self._display_output("  🐍 Python Files (.py):", "#58a6ff")
                    for f in sorted(py_files):
                        self._display_output(f"    • {f}", "#FFD700")
                
                # Display other files
                if other_files:
                    self._display_output("  📄 Other Files:", "#58a6ff")
                    for f in sorted(other_files):
                        self._display_output(f"    • {f}", "#c9d1d9")
                
                if not files:
                    self._display_output("  (Empty directory)", "#6e7681")
                
                self._display_output(f"{'─' * 60}\n", "#404040")
            except Exception as e:
                self._display_output(f"Error: {e}", "#f85149")

    # ---- Clear Output ----
    def clear_text(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete("1.0", tk.END)
        self._insert_welcome_message()
        self.text_area.config(state=tk.DISABLED)

# ---- Run App ----
if __name__ == "__main__":
    root = tk.Tk()
    gui = HybridGUI(root)
    root.mainloop()
