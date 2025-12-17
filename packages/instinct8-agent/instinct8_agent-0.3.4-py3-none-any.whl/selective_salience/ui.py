"""
Terminal UI utilities for Instinct8 - styled like Claude Code.
"""

# ANSI color codes
class Colors:
    """ANSI color codes for terminal styling."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Text colors
    WHITE = '\033[37m'
    GRAY = '\033[90m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    ORANGE = '\033[38;5;208m'  # Orange-brown like Claude Code
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    
    # Background colors
    BG_DARK = '\033[48;5;235m'  # Dark background for boxes
    BG_ORANGE = '\033[48;5;208m'


def print_logo():
    """Print Instinct8 logo (ASCII art unicorn)."""
    # Use raw string to avoid escape sequence warnings
    logo = f"""{Colors.ORANGE}
                             ,|
                           //|                              ,|
                         //,/                             -~ |
                       // / |                         _-~   /  ,
                     /'/ / /                       _-~   _/_-~ |
                    ( ( / /'                   _ -~     _-~ ,/'
                     \\~\\/'/|             __--~~__--\\ _-~  _/,
             ,,)))))));, \\/~-_     __--~~  --~~  __/~  _-~ /
          __))))))))))))));,>/\\   /        __--~~  \\-~~ _-~
         -\\(((((''''(((((((( >~\\/     --~~   __--~' _-~ ~|
--==//////((''  .     `)))))), /     ___---~~  ~~\\~~__--~
        ))| @    ;-.     (((((/           __--~~~'~~/
        ( `|    /  )      )))/      ~~~~~__\\__---~~/ ,(((((((
           |   |   |       (/      ---~~~/__-----~~\\)))))))))))
           o_);   ;        /      ----~~/           \\((((((((((((
                 ;        (      ---~~/         `:::|     ))))));,.
                |   _      `----~~~~'      /      `:|      ((((((((((
          ______/\\/~    |                 /        /         ))))))))))
        /~;;.____/;;'  /          ___----(   `;;;/                ((((
       / //  _;______;'------~~~~~    |;;/\\    /                    ))
      (<_  | ;                      /',/-----'  _>
      \\_| ||_                     //~;~~~~~~~~~
          `\\_|                   (,~~  -
                                  \\~\\
                                   ~~
{Colors.RESET}"""
    print(logo)


def print_welcome_box(version: str, project_name: str, git_branch: str = None, working_dir: str = None):
    """Print styled welcome box like Claude Code."""
    # Top border
    print(f"{Colors.ORANGE}{'═' * 60}{Colors.RESET}")
    
    # Version and logo
    print(f"{Colors.BOLD}{Colors.WHITE}Instinct8 Agent {Colors.ORANGE}v{version}{Colors.RESET}")
    print_logo()
    
    # Welcome message
    print(f"{Colors.WHITE}Welcome back!{Colors.RESET}\n")
    
    # Project info
    print(f"{Colors.CYAN}📁{Colors.RESET} {Colors.BOLD}Project:{Colors.RESET} {Colors.WHITE}{project_name}{Colors.RESET}")
    if git_branch:
        print(f"{Colors.GREEN}🌿{Colors.RESET} {Colors.BOLD}Branch:{Colors.RESET} {Colors.WHITE}{git_branch}{Colors.RESET}")
    if working_dir:
        print(f"{Colors.BLUE}📂{Colors.RESET} {Colors.BOLD}Working directory:{Colors.RESET} {Colors.DIM}{working_dir}{Colors.RESET}")
    
    # Bottom border
    print(f"\n{Colors.ORANGE}{'═' * 60}{Colors.RESET}")


def print_tips_box():
    """Print tips box with colored border."""
    tips = [
        "Just type your prompt and press Enter",
        "Type 'help' for commands",
        "Type 'quit' or Ctrl+C to exit",
        "Type 'stats' to see context usage",
    ]
    
    # Box with orange border
    print(f"\n{Colors.ORANGE}╔{'═' * 58}╗{Colors.RESET}")
    print(f"{Colors.ORANGE}║{Colors.RESET} {Colors.BOLD}{Colors.YELLOW}💡 Tips:{Colors.RESET}{' ' * 48}{Colors.ORANGE}║{Colors.RESET}")
    print(f"{Colors.ORANGE}╠{'═' * 58}╣{Colors.RESET}")
    for tip in tips:
        print(f"{Colors.ORANGE}║{Colors.RESET}  {Colors.WHITE}•{Colors.RESET} {Colors.DIM}{tip}{Colors.RESET}{' ' * (56 - len(tip))}{Colors.ORANGE}║{Colors.RESET}")
    print(f"{Colors.ORANGE}╚{'═' * 58}╝{Colors.RESET}\n")


def get_input_prompt() -> str:
    """Get styled input prompt."""
    return f"{Colors.GREEN}{Colors.BOLD}>{Colors.RESET} {Colors.WHITE}instinct8{Colors.DIM}>{Colors.RESET} "


def print_response(text: str):
    """Print agent response with styling."""
    # Simple styling for now - can be enhanced
    print(f"{Colors.WHITE}{text}{Colors.RESET}")


def print_action(action: str):
    """Print action taken (file created, command executed, etc.)."""
    if "Created file" in action:
        print(f"{Colors.GREEN}✅ {action}{Colors.RESET}")
    elif "Executed" in action:
        print(f"{Colors.CYAN}⚡ {action}{Colors.RESET}")
    elif "Failed" in action or "Error" in action:
        print(f"{Colors.ORANGE}❌ {action}{Colors.RESET}")
    else:
        print(f"{Colors.DIM}📝 {action}{Colors.RESET}")
