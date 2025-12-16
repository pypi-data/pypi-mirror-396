#!/usr/bin/env python3
import sys, os, re, getpass, shutil
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv
from .llm_providers import get_provider, PROVIDERS


def get_config_dir() -> Path:
    return Path.home() / ".config" / "autocmd"

def get_settings_file() -> Path:
    return get_config_dir() / "settings"

def get_setting(key: str, default: str = "") -> str:
    settings_file = get_settings_file()
    if not settings_file.exists():
        return default

    content = settings_file.read_text()
    for line in content.split('\n'):
        if '=' in line:
            k, v = line.split('=', 1)
            if k.strip() == key:
                return v.strip()
    return default

def set_setting(key: str, value: str) -> None:
    settings_file = get_settings_file()
    settings_file.parent.mkdir(parents=True, exist_ok=True)

    # Read existing settings
    settings = {}
    if settings_file.exists():
        content = settings_file.read_text()
        for line in content.split('\n'):
            if '=' in line:
                k, v = line.split('=', 1)
                settings[k.strip()] = v.strip()

    # Update setting
    settings[key] = value

    # Write back
    settings_file.write_text('\n'.join([f"{k}={v}" for k, v in settings.items()]))

def is_shell_setup() -> bool:
    return (get_config_dir() / ".shell_setup_done").exists()

def detect_shell() -> Tuple[Optional[str], Optional[Path]]:
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return "zsh", Path.home() / ".zshrc"
    elif "bash" in shell:
        bashrc = Path.home() / ".bashrc"
        return "bash", bashrc if bashrc.exists() else Path.home() / ".bash_profile"
    return None, None

def setup_shell_integration() -> bool:
    shell_type, rc_file = detect_shell()
    if not shell_type:
        print("Unsupported shell.", file=sys.stderr)
        return False

    print("\nLet's go through a quick setup.", file=sys.stderr)
    print("Shell integration injects commands into your shell for easy editing.", file=sys.stderr)
    print("Enable? (y/n): ", end='', file=sys.stderr, flush=True)
    if input().strip().lower() != 'y':
        print("Skipping shell integration. Commands will be printed only.", file=sys.stderr)
        get_config_dir().mkdir(parents=True, exist_ok=True)
        (get_config_dir() / ".shell_setup_done").touch()
        return False

    autocmd_cmd = shutil.which("autocmd") or "uv tool run --from autocmd-cli autocmd"

    if shell_type == "zsh":
        wrapper = f'''
# autocmd
autocmd() {{
    # Handle triple quotes by preserving them as literal strings
    local args="$*"
    local cmd=$({autocmd_cmd} "$args")
    [ -n "$cmd" ] && print -z "$cmd"
}}
'''
    else:
        wrapper = f'''
# autocmd
autocmd() {{
    # Handle triple quotes by preserving them as literal strings
    local args="$*"
    local cmd=$({autocmd_cmd} "$args")
    [ -n "$cmd" ] && {{ READLINE_LINE="$cmd"; READLINE_POINT=${{#READLINE_LINE}}; }}
}}
'''

    if rc_file.exists() and "# autocmd" in rc_file.read_text():
        get_config_dir().mkdir(parents=True, exist_ok=True)
        (get_config_dir() / ".shell_setup_done").touch()
        return True

    with open(rc_file, "a") as f:
        f.write(wrapper)

    get_config_dir().mkdir(parents=True, exist_ok=True)
    (get_config_dir() / ".shell_setup_done").touch()
    return True

def get_provider_name() -> str:
    """Get the provider name from environment or settings."""
    return os.environ.get("AUTOCMD_PROVIDER") or get_setting("provider", "anthropic")

def onboarding() -> None:
    """Interactive onboarding to configure provider, API key, and model."""
    print("\nLet's configure your LLM provider.", file=sys.stderr)
    print("", file=sys.stderr)

    # Provider selection
    print(f"Available providers: {', '.join(PROVIDERS.keys())}", file=sys.stderr)
    print("Choose a provider (default: anthropic): ", end='', file=sys.stderr, flush=True)
    provider = input().strip().lower() or "anthropic"

    while provider not in PROVIDERS:
        print(f"Unknown provider '{provider}'. Please choose from: {', '.join(PROVIDERS.keys())}", file=sys.stderr)
        print("Choose a provider: ", end='', file=sys.stderr, flush=True)
        provider = input().strip().lower()

    set_setting("provider", provider)
    print(f"Provider set to {provider}.", file=sys.stderr)
    print("", file=sys.stderr)

    # API Key
    env_var = PROVIDERS[provider].env_var_name()
    print(f"Enter your {provider.capitalize()} API key (will be stored in {get_settings_file()}):", file=sys.stderr)
    print(f"Alternatively, you can set the {env_var} environment variable.", file=sys.stderr)
    print("API key: ", end='', file=sys.stderr, flush=True)
    api_key = getpass.getpass("").strip()

    if api_key:
        set_setting("api_key", api_key)
        print("API key saved.", file=sys.stderr)
    else:
        print(f"No API key entered. You'll need to set {env_var} environment variable.", file=sys.stderr)

    print("", file=sys.stderr)

    # Model (optional)
    default_model = PROVIDERS[provider]("dummy").default_model()
    print(f"Default model for {provider}: {default_model}", file=sys.stderr)
    print("Enter a different model name or press Enter to use default: ", end='', file=sys.stderr, flush=True)
    model = input().strip()

    if model:
        set_setting("model", model)
        print(f"Model set to {model}.", file=sys.stderr)
    else:
        print(f"Using default model: {default_model}", file=sys.stderr)

    print("", file=sys.stderr)

def manage_settings() -> None:
    print("autocmd settings:", file=sys.stderr)
    print("", file=sys.stderr)

    # Provider setting
    current_provider = get_setting("provider", "anthropic")
    print(f"Current provider: {current_provider}", file=sys.stderr)
    print(f"Available providers: {', '.join(PROVIDERS.keys())}", file=sys.stderr)
    print("Change provider? (Enter provider name or press Enter to skip): ", end='', file=sys.stderr, flush=True)
    choice = input().strip().lower()
    if choice and choice in PROVIDERS:
        set_setting("provider", choice)
        current_provider = choice
        print(f"Provider set to {choice}.", file=sys.stderr)
    elif choice:
        print(f"Unknown provider '{choice}'. No changes made.", file=sys.stderr)

    print("", file=sys.stderr)

    # API Key setting
    env_var = PROVIDERS[current_provider].env_var_name()
    print(f"API key is read from {env_var} environment variable or settings file.", file=sys.stderr)
    print("Update API key? (y/n): ", end='', file=sys.stderr, flush=True)
    choice = input().strip().lower()
    while choice not in ['y', 'n']:
        print("Please enter 'y' or 'n': ", end='', file=sys.stderr, flush=True)
        choice = input().strip().lower()

    if choice == 'y':
        print(f"Enter API key for {current_provider}: ", end='', file=sys.stderr, flush=True)
        api_key = getpass.getpass("").strip()
        if api_key:
            set_setting("api_key", api_key)
            print("API key saved.", file=sys.stderr)
        else:
            print("No API key entered.", file=sys.stderr)

    print("", file=sys.stderr)

    # Model setting
    current_model = get_setting("model", "")
    default_model = PROVIDERS[current_provider]("dummy").default_model()
    print(f"Current model: {current_model or f'{default_model} (default)'}", file=sys.stderr)
    print("Change model? (Enter model name or press Enter to skip): ", end='', file=sys.stderr, flush=True)
    choice = input().strip()
    if choice:
        set_setting("model", choice)
        print(f"Model set to {choice}.", file=sys.stderr)

    print("", file=sys.stderr)

    # Streaming setting
    current_streaming = get_setting("streaming", "true")
    print(f"Current streaming: {current_streaming}", file=sys.stderr)
    print("Enable streaming output? (y/n): ", end='', file=sys.stderr, flush=True)
    choice = input().strip().lower()
    while choice not in ['y', 'n']:
        print("Please enter 'y' or 'n': ", end='', file=sys.stderr, flush=True)
        choice = input().strip().lower()

    if choice == 'y':
        set_setting("streaming", "true")
        print("Streaming enabled.", file=sys.stderr)
    else:
        set_setting("streaming", "false")
        print("Streaming disabled.", file=sys.stderr)

def reset_autocmd() -> None:
    config_dir = get_config_dir()
    if config_dir.exists():
        shutil.rmtree(config_dir)

    shell_type, rc_file = detect_shell()
    if rc_file and rc_file.exists():
        content = rc_file.read_text()
        if "# autocmd" in content:
            lines = content.split('\n')
            new_lines = []
            skip = False
            for line in lines:
                if "# autocmd" in line:
                    skip = True
                elif skip and '}' in line:
                    skip = False
                    continue
                elif not skip:
                    new_lines.append(line)
            rc_file.write_text('\n'.join(new_lines))
            print(f"Reset complete. Run: source {rc_file}", file=sys.stderr)
        else:
            print("Reset complete.", file=sys.stderr)

def main() -> None:
    # Force unbuffered stderr
    if sys.stderr:
        sys.stderr.reconfigure(write_through=True) if hasattr(sys.stderr, 'reconfigure') else None

    load_dotenv()

    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_autocmd()
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == "--settings":
        manage_settings()
        sys.exit(0)

    if not is_shell_setup():
        print("Welcome to autocmd! The text-to-command assistant.", file=sys.stderr)
        setup_shell_integration()
        onboarding()
        shell_type, rc_file = detect_shell()
        if rc_file:
            print("Setup complete! Reload your shell to activate:", file=sys.stderr)
            print(f"  source {rc_file}", file=sys.stderr)
        sys.exit(0)

    if len(sys.argv) < 2:
        print('autocmd: The text-to-command assistant', file=sys.stderr)
        sys.exit(1)

    # Parse arguments - support both single quoted and triple-quoted strings
    user_input = ' '.join(sys.argv[1:])

    # Check if using triple quotes
    if '"""' in user_input:
        # Extract content between triple quotes
        parts = user_input.split('"""')
        if len(parts) >= 3:
            # Content is between first and second triple quotes
            user_prompt = parts[1]
        else:
            print("Error: Mismatched triple quotes.", file=sys.stderr)
            print('Usage: autocmd """your multiline prompt here"""', file=sys.stderr)
            sys.exit(1)
    else:
        # Validate that user provided a single quoted prompt (not multiple unquoted words)
        if len(sys.argv) > 2:
            print("Error: Prompt must be in double quotes.", file=sys.stderr)
            print(f'Usage: autocmd "your prompt here"', file=sys.stderr)
            print(f'   or: autocmd """your multiline prompt here"""', file=sys.stderr)
            print(f'   or: autocmd --settings', file=sys.stderr)
            print(f'   or: autocmd --reset', file=sys.stderr)
            sys.exit(1)
        user_prompt = sys.argv[1]

    streaming_enabled = get_setting("streaming", "true") == "true"
    provider_name = get_provider_name()

    try:
        # Get API key from settings if not in environment
        api_key = None
        if provider_name in PROVIDERS:
            env_var = PROVIDERS[provider_name].env_var_name()
            if not os.environ.get(env_var):
                api_key = get_setting("api_key")

        # Get model from settings or environment
        model = os.environ.get("AUTOCMD_MODEL") or get_setting("model") or None

        provider = get_provider(provider_name=provider_name, api_key=api_key, model=model)
        prompt = f"You are a command-line assistant. Convert the user's request to a single {os.environ.get('SHELL', 'bash')} command. Output ONLY the command, nothing else - no explanations, no markdown, no options, no alternatives. Just the one best command. Note: This tool is called 'autocmd' (package: autocmd-cli), so if asked to upgrade itself, use 'uv tool upgrade autocmd-cli' or 'pip install --upgrade autocmd-cli'.\n\nRequest: {user_prompt}"

        if streaming_enabled:
            full_response = ""
            for text in provider.generate_stream(prompt, max_tokens=200):
                if hasattr(sys.stderr, 'buffer'):
                    sys.stderr.buffer.write(text.encode('utf-8'))
                    sys.stderr.buffer.flush()
                else:
                    print(text, end="", flush=True, file=sys.stderr)
                full_response += text

            # Clear the streamed output
            if sys.stderr.isatty():
                num_lines = full_response.count('\n')
                if num_lines > 0:
                    print(f"\033[{num_lines}A", end="", file=sys.stderr)
                print("\r\033[J", end="", file=sys.stderr, flush=True)
            else:
                print("", file=sys.stderr)

            cmd = re.sub(r'^```\w*\n?|```$', '', full_response).strip()
            if not cmd:
                print("No command generated", file=sys.stderr)
                sys.exit(1)
            print(cmd)
        else:
            response = provider.generate(prompt, max_tokens=200)
            cmd = re.sub(r'^```\w*\n?|```$', '', response).strip()
            if not cmd:
                print("No command generated", file=sys.stderr)
                sys.exit(1)
            print(cmd)

    except KeyboardInterrupt:
        print("\nCancelled", file=sys.stderr)
        sys.exit(130)
    except ValueError as e:
        error_msg = str(e)
        if "API key not found" in error_msg:
            print(f"Error: {e}", file=sys.stderr)
            print(f"Configure with: autocmd --settings", file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: File system error - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
            print(f"Error: Invalid API key. Run 'autocmd --settings' to reconfigure.", file=sys.stderr)
        elif "rate" in error_msg.lower() or "quota" in error_msg.lower():
            print(f"Error: API rate limit or quota exceeded. Please try again later.", file=sys.stderr)
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            print(f"Error: Network connection failed. Check your internet connection.", file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
