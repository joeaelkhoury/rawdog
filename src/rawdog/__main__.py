import argparse
import io

from contextlib import redirect_stdout

from rawdog.llm_client import LLMClient


def rawdog(prompt: str):
    output = None
    error, script = llm_client.get_script(prompt)
    def confirm_execution(script: str) -> bool:
        print("Dry run is enabled. The script to be executed is:")
        print(f"{80 * '-'}\n{script}\n{80 * '-'}")
        user_input = input("Proceed with execution? (y/N): ").strip().lower()
        return user_input == 'y'
    if script:
        try:
            if args.dry_run:
                if not confirm_execution(script):
                    print("Execution cancelled by user.")
                    return
            with io.StringIO() as buf, redirect_stdout(buf):
                exec(script, globals())
                output = buf.getvalue()
        except Exception as e:
            error = f"Executing the script raised an Exception: {e}"
    if error:
        print(f"Error: {error}")
        if script:
            print(f"{80 * '-'}{script}{80 * '-'}")
    return output


def banner():
    print("""   / \__
  (    @\___   ┳┓┏┓┏ ┓┳┓┏┓┏┓
  /         O  ┣┫┣┫┃┃┃┃┃┃┃┃┓
 /   (_____/   ┛┗┛┗┗┻┛┻┛┗┛┗┛
/_____/   U    Rawdog v0.1.0""")


# Main Loop
parser = argparse.ArgumentParser(description='A smart assistant that can execute Python code to help or hurt you.')
parser.add_argument('prompt', nargs='*', help='Prompt for direct execution. If empty, enter conversation mode')
parser.add_argument('--dry-run', action='store_true', help='Print the script before executing and prompt for confirmation.')
args = parser.parse_args()
llm_client = LLMClient()  # Will prompt for API key if not found

def main():
    if len(args.prompt) > 0:
        rawdog(" ".join(args.prompt))
    else:
        banner()
        while True:
            try:
                print("\nWhat can I do for you? (Ctrl-C to exit)")
                prompt = input("> ")
                print("")
                _continue = True
                while _continue is True:
                    try:
                        output = rawdog(prompt, silence=True)
                        _continue = output and output.strip().endswith("CONTINUE")
                        if args.dry_run or _continue is False:
                            print(output)
                        llm_client.conversation.append({"role": "system", "content": f"LAST SCRIPT OUTPUT:\n{output}"})
                    except KeyboardInterrupt:
                        print("Stopping current task...")
                        break
            except KeyboardInterrupt:
                print("Exiting...")
                break