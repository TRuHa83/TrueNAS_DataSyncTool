import os
import sys
import json
import argparse
import subprocess

# Definir códigos de colores ANSI
RED = "\033[31m"
CYAN = "\033[36m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

# paths
WORK_PATH = "/mnt/"
BACKUP_FOLDER = WORK_PATH + "Backup-data"

DATASETS = []
EXCLUDE_PATHS = []
INCLUDE_PATHS = []

DRY_MODE = False


def run_rsync(destination):
    # Comando base
    rsync_cmd = ["rsync", "-av"]

    # Modo seco
    if DRY_MODE:
        rsync_cmd.append("--dry-run")
        rsync_cmd.append("--progress")

    # Agregar rutas excluidas
    for path in EXCLUDE_PATHS:
        relative_path = path.replace("/mnt/", "", 1)
        rsync_cmd.append(f"--exclude={relative_path}")

    # Agregar work path
    rsync_cmd.append(WORK_PATH)

    # Agregar el destino remoto
    rsync_cmd.append(destination)

    # Ejecutar el comando
    print("\nRun rsync command, please be patient")

    try:
        print(rsync_cmd)
        #result = subprocess.run(rsync_cmd, check=True, capture_output=True, text=True)
        input("Press Enter to continue...")

    except subprocess.CalledProcessError as e:
        print(f"{RED}Error: rsync command failed with return code {e.returncode}{RESET}")
        print(f"{RED}rsync output: {e.stderr}{RESET}")

        if "ssh: connect to host" in e.stderr and "port 22: Connection refused" in e.stderr:
            print(f"{RED}SSH connection refused. Check if SSH is running on {destination}.{RESET}")

        elif "rsync error" in e.stderr:
            print(f"{RED}rsync encountered an error. Verify permissions and network connectivity.{RESET}")

        sys.exit(1)


def get_datasets(datasets):
    for folder in os.listdir(WORK_PATH):
        print(folder)
        if os.path.isdir(os.path.join(WORK_PATH, folder)) and folder in datasets:
            select = input(f"{folder} (Y/n): ")
            if select == "y" or select == "":
                DATASETS.append(folder)
                INCLUDE_PATHS.append(f"{WORK_PATH}{folder}")

            else:
                EXCLUDE_PATHS.append(f"{WORK_PATH}{folder}")

        elif not folder == "Backup-data":
            EXCLUDE_PATHS.append(f"{WORK_PATH}{folder}")


def get_applications(dataset):
    if os.path.exists(f"{WORK_PATH}{dataset}/ix-applications"):
        print(f"\n{RED}ix-applications found in {dataset}{RESET}")
        option = input("Do you want to include ix-applications in the backup? (Y/n): ")

        if option == "y" or option == "":
            if not f"{WORK_PATH}Backup" in INCLUDE_PATHS:
                INCLUDE_PATHS.append(BACKUP_FOLDER)

            os.system(f'mkdir -p {BACKUP_FOLDER}')
            os.system(
                f'zfs list -H -o name | grep "^{dataset}/ix-applications" >> {BACKUP_FOLDER}/{dataset}-datasets.txt')


def get_vms(vms):
    if len(vms) > 0:
        print(f"\n{RED}Virtual Machine found:{RESET}")
        for vm in vms:
            select = input(f"{vm['name']} (Y/n): ")
            if select == "y" or select == "":

                # almacena en json de forma individual por maquina virtual
                with open(f"{BACKUP_FOLDER}/{vm['name']}-vm.json", "w") as f:
                    json.dump(vm, f)


def backup():
    # Obtiene los datasets
    print("\nSelect Datasets:")
    result = subprocess.run(["zfs", "list", "-H", "-o", "name"], capture_output=True, text=True, check=True)

    datasets = result.stdout.splitlines()
    unique_datasets = set()

    for dataset in datasets:
        top_level = dataset.split("/")[0]
        unique_datasets.add(top_level)

    get_datasets(unique_datasets)

    if len(INCLUDE_PATHS) == 0:
        print("Datasets not found or not selected")
        sys.exit(0)

    # Verificar si existe ix-applications
    for dataset in DATASETS:
        get_applications(dataset)


    # Verificar si existen máquinas virtuales
    try:
        result = subprocess.run(["midclt", "call", "vm.query"], capture_output=True, text=True)
        vms = json.loads(result.stdout)
        get_vms(vms)

    except json.JSONDecodeError:
        print(f"{RED}Error to get VMs{RESET}")


    # solicutar datos al usuario
    print("\nEnter the destination data:")
    SERVER = input("Server: ")
    USER = input("User: ")
    FOLDER = input("Folder: ")

    if not FOLDER.endswith("/"):
        FOLDER += "/"

    destination = f"{USER}@{SERVER}:{FOLDER}"

    # Resumen de la configuración
    print()
    print(f"{BOLD}-= Configuration Summary =-{RESET}")
    print(f"{BOLD} Source Directory:{RESET} {YELLOW}{', '.join(INCLUDE_PATHS)}{RESET}")
    print(f"{BOLD} Excluded Directories:{RESET} {', '.join(EXCLUDE_PATHS) if EXCLUDE_PATHS else 'None'}")
    print(f"{BOLD} Destination Server:{RESET} {GREEN}{USER}@{SERVER}{RESET}")
    print(f"{BOLD} Destination Folder:{RESET} {FOLDER}")
    if DRY_MODE: print(f"{BOLD}{YELLOW} Dry Run Mode:{RESET} {DRY_MODE}")
    print("-" * 40)
    option = input(f" Continue? (y/N)\n")

    if option == "y":
        run_rsync(destination)

    else:
        print("Backup canceled")
        os.system(f'rm -R {BACKUP_FOLDER}')


def menu():
    os.system("clear")
    print("-= DataSyncTool =-\n")
    print(" 1. Backup")
    print(" 2. Restore")
    print("-------------")
    opcion = input("Select mode: ")

    if opcion == "1":
        backup()

    elif opcion == "2":
        print("\nEjecutando restore...")


def main():
    global DRY_MODE
    parser = argparse.ArgumentParser(description="Herramienta de sincronizacion de datos")
    parser.add_argument("--mode", choices=["backup", "restore"], help="Modo de operacion: backup o restore")
    parser.add_argument("--dry-mode", action="store_true", help="Ejecutar en modo seco")
    args = parser.parse_args()

    if args.dry_mode:
        print("Modo seco activado")
        DRY_MODE = True

    if args.mode == "backup":
        print("\n-= Backup mode  =-")
        backup()

    elif args.mode == "restore":
        print("\n-= Restore mode  =-")

    else:
        menu()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nBye!")
