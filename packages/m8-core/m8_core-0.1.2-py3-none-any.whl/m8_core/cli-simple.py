import argparse
import sys
import json
from .client import M8

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def main():
    parser = argparse.ArgumentParser(
        description="M8P Hypervisor Command Line Interface",
        prog="m8-core"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- m8-core run <file> ---
    run_parser = subparsers.add_parser("run", help="Execute an M8 script file")
    run_parser.add_argument("file", help="Path to the .m8 script file")
    run_parser.add_argument("--session", "-s", help="Session ID to run context in (Optional)", default=None)
    run_parser.add_argument("--host", help="Target M8P host URL", default=None)

    # --- m8-core start <session_id> ---
    start_parser = subparsers.add_parser("start", help="Initialize or Check a Session")
    start_parser.add_argument("session_id", help="The Session ID to initialize")
    start_parser.add_argument("--host", help="Target M8P host URL", default=None)

    # --- m8-core stop <session_id> ---
    stop_parser = subparsers.add_parser("stop", help="Destroy/Free a Session")
    stop_parser.add_argument("session_id", help="The Session ID to destroy")
    stop_parser.add_argument("--host", help="Target M8P host URL", default=None)

    # --- m8-core shell ---
    shell_parser = subparsers.add_parser("shell", help="Start an interactive M8 REPL session")
    shell_parser.add_argument("--session", "-s", help="Session ID to attach to", default=None)
    shell_parser.add_argument("--host", help="Target M8P host URL", default=None)

    # --- m8-core help ---
    subparsers.add_parser("help", help="Show this help message")

    # Parse args
    args = parser.parse_args()

    # Handle Commands
    if args.command == "run":
        try:
            with open(args.file, 'r') as f:
                code = f.read()
            
            if args.session:
                print(f"🚀 Running '{args.file}' in session '{args.session}'...")
                resp = M8.RunSession(args.session, code, host=args.host)
            else:
                print(f"🚀 Running '{args.file}' (Dry Run)...")
                resp = M8.RunScript(code, host=args.host)
            
            print(json.dumps(resp, indent=2))
            
        except FileNotFoundError:
            print(f"❌ Error: File '{args.file}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    elif args.command == "start":
        print(f"🔌 Initializing session: {args.session_id}...")
        resp = M8.EnsureExists(args.session_id, host=args.host)
        print(json.dumps(resp, indent=2))

    elif args.command == "shell":
        print(f"{Colors.HEADER}🤖 M8P Hypervisor Shell{Colors.ENDC} | Session: {Colors.BOLD}{args.session}{Colors.ENDC}")
        print(f"Target: {args.host or 'Default'}")
        print("Type 'exit' to quit.")
        # Ensure the session exists so variables persist
        M8.EnsureExists(args.session, host=args.host)

        while True:
            try:
                # Basic prompt
                user_input = input(f"{Colors.GREEN}m8>{Colors.ENDC} ")
                
                if user_input.strip().lower() in ["exit", "quit"]:
                    break
                if not user_input.strip():
                    continue
                
                # Execute line in session
                resp = M8.RunSession(args.session, user_input, host=args.host)
                
                # Format output nicely for a shell experience
                if isinstance(resp, dict):
                    if resp.get('Status') == 'OK':
                        # Show return value and latency
                        ret_val = resp.get('Ret', None)
                        tms = resp.get('Tms', '')
                        tms_f = ''

                        if tms:
                            tms_f = f"   ({Colors.WARNING}⏱️ {tms}{Colors.ENDC})"
                        
                        if ret_val is not None:
                            print(f"{Colors.CYAN} {ret_val}{Colors.ENDC} | {tms_f}")
                        else:
                            print(f"{Colors.CYAN} [OK]{Colors.ENDC} | {tms_f}")

                    elif resp.get('Msg'):
                        print(f"{Colors.FAIL}❌ Error: {resp['Msg']}{Colors.ENDC}")
                    else:
                        print(json.dumps(resp, indent=2))
                else:
                    print(resp)
                    
            except KeyboardInterrupt:
                print("\nType 'exit' to quit.")
            except EOFError:
                break
        print("Session closed.")

    elif args.command == "stop":
        print(f"🗑️  Destroying session: {args.session_id}...")
        resp = M8.DestroySession(args.session_id, host=args.host)
        print(json.dumps(resp, indent=2))

    elif args.command == "help" or args.command is None:
        parser.print_help()

if __name__ == "__main__":
    main()