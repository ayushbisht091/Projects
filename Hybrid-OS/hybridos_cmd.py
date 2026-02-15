# hybridos_cmd.py
from hybridos_core import HybridOS

def main():
    os_shell = HybridOS()
    print("Welcome to HybridOS CLI. Type 'help' for commands.\n")

    while True:
        cmd_input = input(f"{os_shell.current_dir} > ")
        output = os_shell.execute(cmd_input)

        if output == "exit":
            print("Exiting HybridOS...")
            break
        else:
            print(output) 

if __name__ == "__main__":
    
    main()
