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

# --- Standard Library Documentation ---
STDLIB_DOCS = {
    "Basic Operations": [
        "f32set <rage> 12.2",
        "i32set <r2> 5",
        "stream r2 is <r2>             # streams output (supports interpolation)",
        "store <r1> ..string...",
        "store <r3> My age is <rage>..",
        "dup <r1> <r2>                 # duplicate r1 to r2",
        "ret <r1> <r2>                 # multiple returns"
    ],
    "Assertions": [
        "assertcontains <r1> ...string...",
        "assertnotempty <r1>",
        "assertempty <r1>",
        "assertnil <r1>",
        "asserteq <r1> <r2>"
    ],
    "LLM Embeddings & Tokens": [
        "llm_embed <r1> <rv2> dim=16   # stores embedding in <rv2>",
        "llm_tokenize <r1> <r1tokens>",
        "llm_detokenize <r1tokens> <r4>"
    ],
    "Math Operations": [
        "f32add <r10> 23.44533",
        "f32sub <r10> 23.44533",
        "f32mul <r10> 23.44533",
        "f32set <r10> 78",
        "i32set <r9> 123",
        "i32add <r9> 123",
        "i32mul <r9> 123"
    ],
    "Matrix Operations": [
        "matn <r1> 1 376 306 ...       # variable width matrix",
        "mat8 <r1> 10 20 30 ...        # fixed width",
        "matsub <r1> <r2> <r3>",
        "matadd <r1> <r2> <r3>",
        "matmul <r1> <r2> <r3>",
        "matnorm <r1> <r1norm>",
        "matdot <w> <m> <res>          # dot product",
        "matcosim <w> <m> <res>        # cosine similarity",
        "matl2d <w> <m> <res>          # L2 distance"
    ],
    "Inference": [
        "llm_instance <r1> instname n_predict=24 temperature=0.5",
        "llm_instance <r1> instname ... force=true  # Ignore cache",
        "llm_instancestatus instname <r3>            # store result into <r3>",
        "stream <r3>                                 # realtime stream"
    ],
    "VectorDB Operations": [
        "vdb_instance MYDB dim=16 max_elements=500 M=16 ef_construction=200",
        "vdb_add MYDB <rv1> <r1>",
        "vdb_search MYDB <rv1> <res> distance=0.019",
        "align <r1> 16                 # align matrix for batch ops"
    ]
}

def traverse_stream(data):
    if 'event' in data:
        content = data['event']
        # Clean double serialization artifacts if present
        if isinstance(content, str):
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            content = content.replace('\\n', '\n').replace('\\"', '"')
        return content
    
    if data.get('choices'):
        choices = data['choices']
        for C in choices:
            if C.get('delta') and C.get('delta').get('content'):
                cfsx = C.get('delta').get('content')
                return cfsx

    if data.get('content'):
        content = data['content']
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
        content = content.replace('\\n', '\n').replace('\\"', '"')
        return content
    
    # 2. Print Latency (Status)
    if 'Tms' in data:
        tms = data['Tms']
        return tms
        
    # 3. Handle Errors
    if 'Status' in data and data['Status'] == 'FAILED':
        msg = data.get('Error', 'Unknown Error')
        return f"❌ Error: {msg}"

# --- Optional Prompt Toolkit Support (For Real-time Highlighting) ---
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.lexers import Lexer
    from prompt_toolkit.styles import Style
    from prompt_toolkit.key_binding import KeyBindings
    
    class M8Lexer(Lexer):
        def lex_document(self, document):
            def get_line(lineno):
                text = document.lines[lineno]
                tokens = []
                
                # Regex patterns for M8 Syntax
                keyword_pattern = r'^(store|stream|dup|ret|return|stall|align|f32[a-z]+|i32[a-z]+|assert[a-z]+|llm_[a-z0-9_]+|mat[a-z0-9]+|vdb_[a-z0-9_]+)\b'
                variable_pattern = r'^<[^>]+>'
                string_pattern = r'^"[^"]*"'
                number_pattern = r'^\d+(\.\d+)?'
                
                i = 0
                while i < len(text):
                    substring = text[i:]
                    match = re.match(keyword_pattern, substring)
                    if match:
                        tokens.append(('class:keyword', match.group(0)))
                        i += len(match.group(0))
                        continue
                    match = re.match(variable_pattern, substring)
                    if match:
                        tokens.append(('class:variable', match.group(0)))
                        i += len(match.group(0))
                        continue
                    match = re.match(string_pattern, substring)
                    if match:
                        tokens.append(('class:string', match.group(0)))
                        i += len(match.group(0))
                        continue
                    match = re.match(number_pattern, substring)
                    if match:
                        tokens.append(('class:number', match.group(0)))
                        i += len(match.group(0))
                        continue
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

    # --- m8-core stream (REPL) ---
    stream_parser = subparsers.add_parser("stream", help="Start an interactive M8 Streaming REPL")
    stream_parser.add_argument("--session", "-s", help="Session ID to attach to", default="m8_stream_default")
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
    shell_parser = subparsers.add_parser("shell", help="Start an interactive M8 REPL session (Response Mode)")
    shell_parser.add_argument("--session", "-s", help="Session ID to attach to", default="m8_repl_default")
    shell_parser.add_argument("--host", help="Target M8P host URL", default=None)

    # --- m8-core stdlib ---
    subparsers.add_parser("stdlib", help="Print the M8 Standard Library Reference")

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
        print(f"{Colors.HEADER}🌊 M8P Streaming Shell{Colors.ENDC} | Session: {Colors.BOLD}{args.session}{Colors.ENDC}")
        print(f"Target: {args.host or 'Default'}")
        print(f"{Colors.CYAN}Ctrl+C -> to stop the streaming{Colors.ENDC}")
        print(f"{Colors.CYAN}Alt+Enter -> to enter a multiline script{Colors.ENDC}")
        print("Type 'exit' to quit.")
        
        # Ensure session exists
        M8.EnsureExists(args.session, code="ustall 1", host=args.host)

        # Setup Highlighting Session
        session = None
        if HAS_TOOLKIT:
            m8_style = Style.from_dict({
                'keyword': '#00ff9d bold', 'variable': '#bd00ff',
                'string': '#e5e5e5 italic', 'number': '#00b0ff', 'prompt': '#00ff9d bold',
            })
            
            # Key Bindings for Multiline
            # Note: 's-enter' (Shift+Enter) is often not supported by terminals/prompt_toolkit properly.
            # Using 'escape' + 'enter' (Alt+Enter) is standard for multiline in prompts.
            kb = KeyBindings()
            @kb.add('escape', 'enter')
            def _(event):
                event.current_buffer.insert_text('\n')
            @kb.add('enter')
            def _(event):
                event.current_buffer.validate_and_handle()

            session = PromptSession(lexer=M8Lexer(), style=m8_style, key_bindings=kb)
        else:
            print(f"{Colors.WARNING}[Note] Run 'pip install prompt_toolkit' for syntax highlighting.{Colors.ENDC}")

        while True:
            try:
                # Prompt
                if session:
                    user_input = session.prompt([('class:prompt', 'm8-stream> ')])
                else:
                    user_input = input(f"{Colors.GREEN}m8-stream>{Colors.ENDC} ")
                
                if user_input.strip().lower() in ["exit", "quit"]:
                    break
                if not user_input.strip():
                    continue

                user_input = '\n'.join(
                    map(lambda L: L.strip(), user_input.split(';'))
                )

                # Execute and Stream
                print(f"{Colors.CYAN}<={Colors.ENDC} ", end="", flush=True)
                
                buffer = ""
                for chunk in M8.StreamSession(args.session, user_input, host=args.host):
                    if isinstance(chunk, bytes):
                        chunk = chunk.decode('utf-8', errors='replace')
                    buffer += chunk
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line.startswith("data: "):  
                            try:
                                json_str = line[6:]
                                data = json.loads(json_str)
                                content_text = traverse_stream(data)
                                if content_text:
                                    sys.stdout.write(content_text)
                                    sys.stdout.flush()
                                else:
                                    # 1. Print Content (Event)
                                    if 'event' in data:
                                        content = data['event']
                                        # Clean double serialization artifacts if present
                                        if isinstance(content, str):
                                            if content.startswith('"') and content.endswith('"'):
                                                content = content[1:-1]
                                            content = content.replace('\\n', '\n').replace('\\"', '"')
                                        sys.stdout.write(content)
                                        sys.stdout.flush()
                                    elif data.get('choices'):
                                        choices = data['choices']
                                        i = 0
                                        for C in choices:
                                            if C.get('delta') and C.get('delta').get('content'):
                                                cfsx = C.get('delta').get('content')
                                                sys.stdout.write(cfsx)

                                            if C.get('message') and C.get('message').get('content'):
                                                msg = C.get('message')
                                                content = msg.get('content')
                                                role = msg.get('role', '')
                                                cfsx = f"{role}: {content}"
                                                sys.stdout.write(cfsx)

                                            if i%2==0:
                                                sys.stdout.flush()
                                            i += 1

                                        sys.stdout.flush()
                                    elif data.get('content'):
                                        content = data['content']
                                        if content.startswith('"') and content.endswith('"'):
                                            content = content[1:-1]
                                        content = content.replace('\\n', '\n').replace('\\"', '"')
                                        sys.stdout.write(content)
                                        sys.stdout.flush()
                                    else:
                                        sys.stdout.write(json_str)
                                        sys.stdout.flush()                                        
                                    
                                    # 2. Print Latency (Status)
                                    if 'Tms' in data:
                                        tms = data['Tms']
                                        sys.stdout.write(f" ({Colors.WARNING}⏱️ {tms}{Colors.ENDC})")
                                        sys.stdout.flush()
                                        
                                    # 3. Handle Errors
                                    if 'Status' in data and data['Status'] == 'FAILED':
                                        msg = data.get('Msg', 'Unknown Error')
                                        sys.stdout.write(f"\n{Colors.FAIL}❌ Error: {msg}{Colors.ENDC}")

                            except json.JSONDecodeError:
                                pass # Ignore parse errors in stream chunks
                        # else:
                        #     print("Line widthout data: ", line, buffer)

                print() # Newline after stream ends

            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}🛑 Interrupted.{Colors.ENDC}")
                continue
            except EOFError:
                break
        print("Session closed.")

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
        print(f"{Colors.CYAN}Ctrl+C -> to stop execution{Colors.ENDC}")
        print(f"{Colors.CYAN}Alt+Enter -> to enter a multiline script{Colors.ENDC}")
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
            
            # Key Bindings for Multiline
            kb = KeyBindings()
            @kb.add('escape', 'enter')
            def _(event):
                event.current_buffer.insert_text('\n')
            @kb.add('enter')
            def _(event):
                event.current_buffer.validate_and_handle()

            session = PromptSession(lexer=M8Lexer(), style=m8_style, key_bindings=kb)
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
                        ret_val = resp.get('R', None)
                        tms = resp.get('Tms', '')
                        tmf = ''
                        if tms:
                            tmf = (f"({Colors.WARNING}⏱️ {tms}{Colors.ENDC})")
                        
                        if ret_val is not None:
                            print(f"{Colors.CYAN}{ret_val}{Colors.ENDC} | {tmf}")
                        else:
                            print(f"{Colors.CYAN}[OK]{Colors.ENDC} | {tmf}")
                            
                    elif resp.get('Err'):
                        print(f"{Colors.FAIL}❌ Error: {resp['Err']}{Colors.ENDC}")
                    else:
                        print(json.dumps(resp, indent=2))
                else:
                    print(resp)
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}🛑 Interrupted.{Colors.ENDC}")
                continue
            except EOFError:
                break
        print("Session closed.")

    elif args.command == "stdlib":
        print(f"{Colors.HEADER}📚 M8P Standard Library Reference{Colors.ENDC}")
        print(f"{Colors.WARNING}https://m8-site.desktop.farm/stdlib.php{Colors.ENDC}\n")
        
        for section, commands in STDLIB_DOCS.items():
            print(f"{Colors.BOLD}{Colors.BLUE}### {section}{Colors.ENDC}")
            for cmd in commands:
                # Simple coloring for key parts of command string
                parts = cmd.split(' # ', 1)
                code_part = parts[0]
                comment = f" # {parts[1]}" if len(parts) > 1 else ""
                print(f"  {Colors.GREEN}{code_part:<50}{Colors.ENDC}{Colors.CYAN}{comment}{Colors.ENDC}")
            print()

    elif args.command == "help" or args.command is None:
        parser.print_help()

if __name__ == "__main__":
    main()