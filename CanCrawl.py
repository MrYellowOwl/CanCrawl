import socket
import concurrent.futures
import subprocess
import threading  # Import the threading module

# ANSI escape codes for colors
YELLOW = "\033[38;2;255;241;0m"
GREEN = "\033[38;2;0;255;0m"
RESET = "\033[0m"

def print_banner():
    print(YELLOW)
    print("          (,#                                                       @ &         ")
    print("         ,&#,&*                                                   #& &&         ")
    print("         .(&@.#&%                                               &&**&&,*        ")
    print("         &&#*&&,*&&&                                        .&&&.(&& &&%        ")
    print("           %&&&&&&#/&&&         &               *        ,&&&,&&&&&&&#          ")
    print("         .@&&&%%&&&&&%(&(       .&&*         (&&        &&,&&&&&&%&&&&&         ")
    print("         (*,,*#&&&&&&&&/&.%.     /%,%&#&&#&&#,&.     ,((&%&&&&&&&&(,,,*/        ")
    print("            .   &&&&&&&&.&.(./#/.&%&   &&&  ,%&(,((*.//&#&&&%&&&#  .            ")
    print("           .%&&&( (&&&&%,*&#**..*..&&&(#(&#@&%*,,../.&(% &&&&&, %&&&%           ")
    print("               ,&&&/.&/#&& .%*#&#. %##&%#&&(%# ,%&*##,,&&*%& #&&&               ")
    print("                   &.&%,&&%.*&%  ,%&&% &&&.&&&#.  &&.,&&%*&%,&                  ")
    print("                           *%&&&&(.&&#,&&@,/@& %&&&@#.                          ")
    print("                                     &&&&&&#                                    ")
    print("                               /@.(    *@.   /,/&,                              ")
    print("                                #& %.*.&/&( (/,&,.                              ")
    print("                                  %%,&.&&&.& &(                                 ")
    print("                                     % &&& *                                    ")
    print(" ________  ________  _________        ________  ________  ________  _________  ________  ________      ")
    print("|\\   ____\|\\   __  \|\___   ___\     |\   __  \|\   __  \|\   __  \|\___   ___\\   ____\|\_____  \     ")
    print("\ \  \___|\ \  \|\  \|___ \  \_|     \ \  \|\  \ \  \|\  \ \  \|\  \|___ \  \_\ \  \___|\|____|\  \    ")
    print(" \ \  \  __\ \  \\\  \   \ \  \       \ \   ____\ \  \\\  \ \   _  _\   \ \  \ \ \_____  \    \ \__\   ")
    print("  \ \  \|\  \ \  \\\  \   \ \  \       \ \  \___|\ \  \\\  \ \  \\  \|   \ \  \ \|____|\  \    \|__|   ")
    print("   \ \_______\ \_______\   \ \__\       \ \__\    \ \_______\ \__\\ _\    \ \__\  ____\_\  \       ___ ")
    print("    \|_______|\|_______|    \|__|        \|__|     \|_______|\|__|\|__|    \|__| |\_________\     |\__\\")
    print("                                                                                 \|_________|     \|__|")
    print("-By Mr Yellow Owl")
    print(RESET)


def validate_input():
    while True:
        target = input("Enter IP/Hostname to target: ")
        try:
            # Check if the input is a valid IP address
            socket.inet_aton(target)
            return target
        except socket.error:
            try:
                # If not a valid IP, try resolving it to an IP address
                ip = socket.gethostbyname(target)
                return ip
            except socket.error:
                print("Invalid IP address or hostname. Please try again.")

def scan_port(ip, port, stop_event):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as scanner:
        scanner.settimeout(0.5)
        try:
            result = scanner.connect_ex((ip, port))
            if result == 0:
                print(f"{GREEN}{port}...open{RESET}")
                return port
        except KeyboardInterrupt:
            stop_event.set()
    return None

def run_scanner(ip, stop_event):
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_port = {executor.submit(scan_port, ip, port, stop_event): port for port in range(1, 1025)}
        for future in concurrent.futures.as_completed(future_to_port):
            port = future_to_port[future]
            try:
                open_port = future.result()
                if open_port is not None:
                    open_ports.append(open_port)
            except Exception as e:
                print(f"Error scanning port {port}: {str(e)}")
    return open_ports

def print_results(ip, open_ports):
    print(f"{YELLOW}Getting Services & Versions!{RESET}")
    if open_ports:
        ports_str = ','.join(map(str, open_ports))
        nmap_cmd = f"nmap -Pn -sC -sV {ip} -p {ports_str}"
        try:
            subprocess.run(nmap_cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running nmap: {str(e)}")

if __name__ == "__main__":
    print_banner()
    try:
        target_ip = validate_input()
        stop_event = threading.Event()  # Use threading.Event
        open_ports = run_scanner(target_ip, stop_event)
        print_results(target_ip, open_ports)
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
