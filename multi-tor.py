
import os,sys
from rich.console import Console
import subprocess
import socket
import time

console = Console()
USER = os.getlogin()
def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM)as ex:
        return ex.connect_ex(('127.0.0.1',port)) == 0

def create_instance(n):
    console.print(f"[bold green][+]Creating {n} instance...[/bold green]")
    bsock = 9050
    control = 9150
    for i in range(n):
        instance = f"/etc/tor/instances/instance_{i+1}"
        subprocess.run(["sudo","mkdir","-p",instance],check=True)
        # os.makedirs(instance,exist_ok=True)
        port = bsock + i
        sock = control + i

        data_dir = f"/var/lib/tor-instance-{port}"
        torrc_file = f"{instance}/torrc"

        subprocess.run(["sudo","mkdir","-p",instance],check=True)
        subprocess.run(["sudo","mkdir","-p",data_dir],check=True)
        try:
            # subprocess.run(["chown","-R",f"{USER}:{USER}",data_dir],check=True)
            
            config = (
            f"SocksPort {port}\n"
            f"ControlPort {sock}\n"
            f"DataDirectory {data_dir}\n"
            )

            with open(torrc_file, "w") as f:
                f.write(config)

            subprocess.run(["sudo","chown","-R","debian-tor:debian-tor",data_dir],check=True)
            subprocess.run(["sudo","chmod","700",data_dir],check=True)
            subprocess.run(["sudo","chown","root:root",torrc_file],check=True)
            subprocess.run(["sudo","chmod","644",torrc_file],check=True)
        except Exception as e:
            console.print(e)
    console.print("[bold green]\n[+] All instances created![/bold green]")

def run_instance(n):
    proxies = []
    bsock = 9050
    console.print("[bold green]\n[+] Starting instances....[/bold green]")
    
    for i in range(1,n+1):
        instance_dir = f"/etc/tor/instances/instance_{i}"
        torrc_path = f"{instance_dir}/torrc"
        log_path = f"{instance_dir}/tor.log"
        
        if not os.path.exists(torrc_path):
            console.print(f"[red][!] Config missing for instance {i}. Run Create first.[/red]")
            continue

        sock_port = bsock + i-1
        
        if check_port(sock_port):
            proxies.append(sock_port)
            console.print(f"[bold yellow][!] Warning: Port {sock_port} is already in use. Skipping.[/bold yellow]")
            continue

        try:
            with open(log_path, "w") as log_file:
                process = subprocess.Popen(
                    ["sudo","-u","debian-tor","tor","-f",torrc_path],
                    stdout=log_file,
                    stderr=subprocess.STDOUT
                )
            # console.print("\r\033", end="")
            print("\r\033", end="")
            console.print(f"[blue] -> Waiting for instance {i} to bootstrap...[/blue]")
        
            bootstrapped = False
            start_time = time.time()
            
            while time.time() - start_time < 20:
                if process.poll() is not None:
                    print("\r\033", end="")
                    console.print(f"[bold red][!] Instance {i} died immediately![/bold red]")
                    with open(log_path, "r") as lf:
                        console.print(f"[red]{lf.read()}[/red]")
                    break
                try:
                    with open(log_path, "r") as lf:
                        log_content = lf.read()
                        if "Bootstrapped 100%" in log_content:
                            bootstrapped = True
                            proxies.append(sock_port)
                            break
                except:
                    pass
                time.sleep(0.5)

            if bootstrapped:
                print("\r\033", end="")
                with open('proxy.txt','w')as f:
                    for proxy in proxies:
                        f.write(f"{proxy}\n")
                console.print(f"[bold green][+] {i} instance started at port {sock_port} [/bold green]")
            elif process.poll() is None:
                proxies.append(sock_port)
                console.print(f"[yellow][!] Instance {i} started but bootstrap timed out (check logs).[/yellow]")
            
        except Exception as e:
            console.print(f"[red][!] Exception starting instance {i}: {e}[/red]")
    print("\r\033", end="")
    console.print("[bold green][+] Operation completed! [/bold green]")

def stop_instance(i):
    control_port = 9150 + i

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", control_port))
            s.sendall(b'AUTHENTICATE ""\r\n')
            s.sendall(b'SIGNAL SHUTDOWN\r\n')
            console.print(f"[green][+] Clean shutdown sent to instance {i} [/green]")
    except:
        console.print(f"[yellow][!] Instance {i} not running or no control port[/yellow]")

def stop_all_instances():
    subprocess.run(["sudo","pkill", "-f", "tor -f /etc/tor/instances/instance_"], check=False)
    with open('proxy.txt','w')as f:
        f.write('')
    console.print("[red][-] All TOR instances killed[/red]")

def main(): 
    # if os.geteuid() != 0:
    #     console.print("[bold red][-] Please run this script as root: sudo python3 multi-tor.py[/bold red]")
    #     sys.exit(1)

    console.print(f"[bold blue]------TOR instance Menu--------[/bold blue]")
    console.print(f"[bold blue]1. Create TOR instance [/bold blue]")
    console.print(f"[bold blue]2. Run TOR instance [/bold blue]")
    console.print(f"[bold blue]3. Stop TOR instance [/bold blue]")
    console.print(f"[bold blue]4. Stop All TOR instance [/bold blue]")
    c = int(input("~: "))
    match c:
        case 1:
            try:
                n = input("How Many instance do you want? (Default: 5): ")
                n = 5 if not n else int(n)
                create_instance(n)
            except Exception as e:
                print(f"Invalid input: {e}")
        case 2:
            try:
                n = int(input("How Many instance do you want to start?: "))
                run_instance(n)
            except Exception as e:
                print(f"Invalid input: {e}")
        case 3:
            try:
                i = int(input("Which instance number to stop?: "))
                stop_instance(i)
            except Exception as e:
                print(f"Invalid input: {e}")

        case 4:
            stop_all_instances()
if __name__ == "__main__":
    main()