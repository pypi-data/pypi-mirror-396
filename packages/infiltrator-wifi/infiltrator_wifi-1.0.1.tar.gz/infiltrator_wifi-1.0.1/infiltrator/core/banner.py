"""
Banner and branding for Infiltrator.
"""
from colorama import Fore, Style, init
# Initialize colorama for cross-platform color support
init(autoreset=True)

def display_banner():
    """Display the Infiltrator ASCII art banner."""
    banner = f"""
{Fore.RED}╔═══════════════════════════════════════════════════════════════════════════════════╗
{Fore.RED}║                                                                                   ║
{Fore.RED}║  {Fore.CYAN}██╗███╗   ██╗███████╗██╗██╗  ████████╗██████╗  █████╗ ████████╗ ██████╗ ██████╗  {Fore.RED}║
{Fore.RED}║  {Fore.CYAN}██║████╗  ██║██╔════╝██║██║  ╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗ {Fore.RED}║
{Fore.RED}║  {Fore.CYAN}██║██╔██╗ ██║█████╗  ██║██║     ██║   ██████╔╝███████║   ██║   ██║   ██║██████╔╝ {Fore.RED}║
{Fore.RED}║  {Fore.CYAN}██║██║╚██╗██║██╔══╝  ██║██║     ██║   ██╔══██╗██╔══██║   ██║   ██║   ██║██╔══██╗ {Fore.RED}║
{Fore.RED}║  {Fore.CYAN}██║██║ ╚████║██║     ██║███████╗██║   ██║  ██║██║  ██║   ██║   ╚██████╔╝██║  ██║ {Fore.RED}║
{Fore.RED}║  {Fore.CYAN}╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝ {Fore.RED}║
{Fore.RED}║                                                                                   ║
{Fore.RED}║                        {Fore.YELLOW}Wi-Fi Red Team Auditing Suite{Fore.RED}                              ║
{Fore.RED}║                      {Fore.GREEN}Dev: LAKSHMIKANTHAN K (letchupkt){Fore.RED}                            ║
{Fore.RED}║                                                                                   ║
{Fore.RED}╚═══════════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.YELLOW}[!] For Educational and Authorized Testing Only
{Fore.YELLOW}[!] Unauthorized access to computer networks is illegal{Style.RESET_ALL}
    """
    print(banner)