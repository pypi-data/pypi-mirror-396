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
    ORANGE = '\033[38;2;103;190;217m'  # #67BED9 - Custom blue-cyan
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    
    # Background colors
    BG_DARK = '\033[48;5;235m'  # Dark background for boxes
    BG_ORANGE = '\033[48;2;103;190;217m'  # #67BED9 - Custom blue-cyan background


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
    
    # Box width (60 chars total, 58 inner width)
    inner_width = 58
    
    # Box with blue-cyan border (#67BED9)
    print(f"\n{Colors.ORANGE}╔{'═' * inner_width}╗{Colors.RESET}")
    
    # Header: "💡 Tips" (no semicolon) - use new color instead of yellow
    header_text = "Tips:"
    # Calculate padding: inner_width - header_text length - 1 space after ║
    header_padding = inner_width - len(header_text) - 1
    print(f"{Colors.ORANGE}║{Colors.RESET} {Colors.BOLD}{Colors.ORANGE}{header_text}{Colors.RESET}{' ' * header_padding}{Colors.ORANGE}║{Colors.RESET}")
    
    print(f"{Colors.ORANGE}╠{'═' * inner_width}╣{Colors.RESET}")
    
    # Tips: Use simple ASCII bullet to avoid wide character rendering issues
    # Line structure: ║ + prefix + tip_text + padding + ║ = 60 chars total
    for tip in tips:
        # Use simple ASCII bullet "-" instead of Unicode "•" to avoid width issues
        prefix = "  - "  # 4 chars: 2 spaces + dash + 1 space
        tip_text = tip.strip()  # Remove any whitespace issues
        
        # Calculate the exact content length (prefix + text)
        content_length = len(prefix) + len(tip_text)
        
        # Calculate padding needed to reach inner_width (58)
        padding_needed = inner_width - content_length
        
        # Ensure padding is non-negative
        if padding_needed < 0:
            padding_needed = 0
        
        # Build the complete line content (without borders)
        line_content = prefix + tip_text + (' ' * padding_needed)
        
        # CRITICAL: Ensure line is exactly inner_width characters
        # This handles any edge cases where character counting might be off
        line_content = (line_content + ' ' * inner_width)[:inner_width]
        
        # Print with borders
        print(f"{Colors.ORANGE}║{Colors.RESET}{line_content}{Colors.ORANGE}║{Colors.RESET}")
    
    print(f"{Colors.ORANGE}╚{'═' * inner_width}╝{Colors.RESET}\n")


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
