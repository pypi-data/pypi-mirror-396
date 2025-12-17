import argparse
import sys
import json
import re
from .client import M8

# --- ANSI Colors (No external deps) ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# --- Optional Prompt Toolkit Support (For Real-time Highlighting) ---
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.lexers import Lexer
    from prompt_toolkit.styles import Style
    
    class M8Lexer(Lexer):
        def lex_document(self, document):
            def get_line(lineno):
                text = document.lines[lineno]
                tokens = []
                
                # Regex patterns for M8 Syntax
                # Updated based on M8 Standard Library (stdlib.php)
                # Covers: Basic (store, stream, ret), Math (f32/i32), Assertions, 
                # LLM (llm_), Matrix (mat), and VectorDB (vdb_) ops.
                keyword_pattern = r'^(store|stream|dup|ret|return|stall|align|f32[a-z]+|i32[a-z]+|assert[a-z]+|llm_[a-z0-9_]+|mat[a-z0-9]+|vdb_[a-z0-9_]+)\b'
                variable_pattern = r'^<[^>]+>'
                string_pattern = r'^"[^"]*"'
                number_pattern = r'^\d+(\.\d+)?'
                
                i = 0
                while i < len(text):
                    substring = text[i:]
                    
                    # 1. Keywords (M8 Neon Green)
                    match = re.match(keyword_pattern, substring)
                    if match:
                        tokens.append(('class:keyword', match.group(0)))
                        i += len(match.group(0))
                        continue
                        
                    # 2. Variables (M8 Purple)
                    match = re.match(variable_pattern, substring)
                    if match:
                        tokens.append(('class:variable', match.group(0)))
                        i += len(match.group(0))
                        continue
                        
                    # 3. Strings
                    match = re.match(string_pattern, substring)
                    if match:
                        tokens.append(('class:string', match.group(0)))
                        i += len(match.group(0))
                        continue

                    # 4. Numbers
                    match = re.match(number_pattern, substring)
                    if match:
                        tokens.append(('class:number', match.group(0)))
                        i += len(match.group(0))
                        continue
                    
                    # 5. Default/Whitespace
                    tokens.append(('', substring[0]))
                    i += 1
                    
                return tokens
            return get_line

    HAS_TOOLKIT = True
except ImportError:
    HAS_TOOLKIT = False

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

    # --- m8-core stream <file> ---
    stream_parser = subparsers.add_parser("stream", help="Execute and stream an M8 script file")
    stream_parser.add_argument("file", help="Path to the .m8 script file")
    stream_parser.add_argument("--session", "-s", help="Session ID to run context in", required=True)
    stream_parser.add_argument("--host", help="Target M8P host URL", default=None)

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
    shell_parser.add_argument("--session", "-s", help="Session ID to attach to", default="m8_repl_default")
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
                print(f"{Colors.BOLD}🚀 Running '{args.file}' in session '{args.session}'...{Colors.ENDC}")
                resp = M8.RunSession(args.session, code, host=args.host)
            else:
                print(f"{Colors.BOLD}🚀 Running '{args.file}' (Dry Run)...{Colors.ENDC}")
                resp = M8.RunScript(code, host=args.host)
            
            print(json.dumps(resp, indent=2))
            
        except FileNotFoundError:
            print(f"{Colors.FAIL}❌ Error: File '{args.file}' not found.{Colors.ENDC}")
            sys.exit(1)
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
            sys.exit(1)

    elif args.command == "stream":
        try:
            with open(args.file, 'r') as f:
                code = f.read()
            
            print(f"{Colors.BOLD}🌊 Streaming '{args.file}' in session '{args.session}'...{Colors.ENDC}")
            
            for chunk in M8.StreamSession(args.session, code, host=args.host):
                sys.stdout.write(chunk)
                sys.stdout.flush()
            print() # Newline at end
            
        except FileNotFoundError:
            print(f"{Colors.FAIL}❌ Error: File '{args.file}' not found.{Colors.ENDC}")
            sys.exit(1)
        except Exception as e:
            print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
            sys.exit(1)

    elif args.command == "start":
        print(f"{Colors.GREEN}🔌 Initializing session: {args.session_id}...{Colors.ENDC}")
        resp = M8.EnsureExists(args.session_id, host=args.host)
        print(json.dumps(resp, indent=2))

    elif args.command == "stop":
        print(f"{Colors.WARNING}🗑️  Destroying session: {args.session_id}...{Colors.ENDC}")
        resp = M8.DestroySession(args.session_id, host=args.host)
        print(json.dumps(resp, indent=2))

    elif args.command == "shell":
        print(f"{Colors.HEADER}🤖 M8P Hypervisor Shell{Colors.ENDC} | Session: {Colors.BOLD}{args.session}{Colors.ENDC}")
        print(f"Target: {args.host or 'Default'}")
        print("Type 'exit' to quit.")
        
        # Ensure the session exists so variables persist
        M8.EnsureExists(args.session, code="ustall 1", host=args.host)

        # Setup Highlighting Session if toolkit is available
        session = None
        if HAS_TOOLKIT:
            m8_style = Style.from_dict({
                'keyword': '#00ff9d bold',   # M8 Neon Green
                'variable': '#bd00ff',       # M8 Purple
                'string': '#e5e5e5 italic',
                'number': '#00b0ff',
                'prompt': '#00ff9d bold',
            })
            session = PromptSession(lexer=M8Lexer(), style=m8_style)
        else:
            print(f"{Colors.WARNING}[Note] Run 'pip install prompt_toolkit' for syntax highlighting.{Colors.ENDC}")

        while True:
            try:
                # Prompt Logic
                if session:
                    user_input = session.prompt([('class:prompt', 'm8> ')])
                else:
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
                        tmf = ''
                        if tms:
                            tmf = (f"({Colors.WARNING}⏱️ {tms}{Colors.ENDC})")
                        
                        if ret_val is not None:
                            print(f"{Colors.CYAN} {ret_val}{Colors.ENDC} | {tmf}")
                        else:
                            print(f"{Colors.CYAN} [OK]{Colors.ENDC} | {tmf}")
                            
                    elif resp.get('Msg'):
                        print(f"{Colors.FAIL}❌ Error: {resp['Msg']}{Colors.ENDC}")
                    else:
                        print(json.dumps(resp, indent=2))
                else:
                    print(resp)
                    
            except KeyboardInterrupt:
                print("\nType 'exit' to quit.")
                continue
            except EOFError:
                break
        print("Session closed.")

    elif args.command == "help" or args.command is None:
        parser.print_help()

if __name__ == "__main__":
    main()