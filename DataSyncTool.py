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
DATASETS = []
EXCLUDE_PATHS = []
INCLUDE_PATHS = []


def run_rsync(destination):
    # Comando base
    rsync_cmd = ["rsync", "-avz"]

    for path in EXCLUDE_PATHS:
        relative_path = path.replace("/mnt/", "", 1)  # Convertir en ruta relativa
        rsync_cmd.append(f"--exclude={relative_path}")

    # Agregar rutas incluidas
    rsync_cmd.append(WORK_PATH)

    # Agregar el destino remoto
    rsync_cmd.append(destination)

    # Ejecutar el comando
    '''
    print("🚀 Ejecutando rsync:")
    print(" ".join(rsync_cmd))  # Muestra el comando antes de ejecutarlo
    subprocess.run(rsync_cmd)
    '''
    print(rsync_cmd)


def get_vms():
    result = subprocess.run(["midclt", "call", "vm.query"], capture_output=True, text=True)

    try:
        vms = json.loads(result.stdout)
        return vms
    except json.JSONDecodeError:
        print("Error to get VMs")
        return []


def backup():
    global backup_folder

    print("\nSelect Datasets:")
    for folder in os.listdir(WORK_PATH):
        if os.path.isdir(os.path.join(WORK_PATH, folder)):
            select = input(f"{folder} (Y/n): ")
            if select == "y" or select == "":
                DATASETS.append(folder)
                INCLUDE_PATHS.append(f"{WORK_PATH}{folder}")
            else:
                EXCLUDE_PATHS.append(f"{WORK_PATH}{folder}")

        else:
            EXCLUDE_PATHS.append(f"{WORK_PATH}{folder}")

    if len(INCLUDE_PATHS) == 0:
        print("Datasets not found or not selected")
        sys.exit(0)

    for dataset in DATASETS:
        if os.path.exists(f"{WORK_PATH}{dataset}/ix-applications"):
            print(f"\n{RED}ix-applications found in {dataset}{RESET}")
            option = input("Do you want to include ix-applications in the backup? (Y/n): ")

            if option == "y" or option == "":
                backup_folder = f"{WORK_PATH}Backup-data"
                if not f"{WORK_PATH}Backup" in INCLUDE_PATHS:
                    INCLUDE_PATHS.append(backup_folder)

                os.system(f'mkdir -p {backup_folder}')
                os.system(f'zfs list -H -o name | grep "^{dataset}/ix-applications" >> {backup_folder}/{dataset}-datasets.txt')

    vms = get_vms()
    if len(vms) > 0:
        print(f"\n{RED}Virtual Machine found:{RESET}")
        for vm in vms:
            select = input(f"{vm['name']} (Y/n): ")
            if select == "y" or select == "":
                # almacena en json de forma individual por maquina virtual
                with open(f"{backup_folder}/{vm['name']}-vm.json", "w") as f:
                    json.dump(vm, f)


    # solicutar datos al usuario
    print("\nEnter the destination data:")
    SERVER = input("Server: ")
    USER = input("User: ")
    FOLDER = input("Folder: ")
    destination = f"{USER}@{SERVER}:{FOLDER}"

    # Resumen de la configuración
    print()
    print(f"{BOLD}{CYAN}-= Configuration Summary =-{RESET}")
    print(f"{BOLD} Source Directory:{RESET} {YELLOW}{', '.join(INCLUDE_PATHS)}{RESET}")
    print(f"{BOLD} Excluded Directories:{RESET} {', '.join(EXCLUDE_PATHS) if EXCLUDE_PATHS else 'None'}")
    print(f"{BOLD} Destination Server:{RESET} {GREEN}{USER}@{SERVER}{RESET}")
    print(f"{BOLD} Destination Folder:{RESET} {FOLDER}")
    print("-" * 40)
    input(f"{CYAN} Press Enter to continue...{RESET}\n")

    run_rsync(destination)



def banner():
    os.system('clear')

    print('8888888b.           888              .d8888b.                         88888888888                888')
    print('888  "Y88b          888             d88P  Y88b                            888                    888')
    print('888    888          888             Y88b.                                 888                    888')
    print('888    888  8888b.  888888  8888b.   "Y888b.   888  888 88888b.   .d8888b 888   .d88b.   .d88b.  888')
    print('888    888     "88b 888        "88b     "Y88b. 888  888 888 "88b d88P"    888  d88""88b d88""88b 888')
    print('888    888 .d888888 888    .d888888       "888 888  888 888  888 888      888  888  888 888  888 888')
    print('888  .d88P 888  888 Y88b.  888  888 Y88b  d88P Y88b 888 888  888 Y88b.    888  Y88..88P Y88..88P 888')
    print('8888888P"  "Y888888  "Y888 "Y888888  "Y8888P"   "Y88888 888  888  "Y8888P 888   "Y88P"   "Y88P"  888')
    print('                                                    888                                             ')
    print('                                               Y8b d88P                                             ')
    print('                                                "Y88P"                                              ')
    print()



def menu():
    print(" 1. Backup")
    print(" 2. Restore")
    print("------------")

    opcion = input("Select mode: ")

    if opcion == "1":
        backup()

    elif opcion == "2":
        print("\nEjecutando restore...")


def main():
    parser = argparse.ArgumentParser(description="Herramienta de sincronizacion de datos")
    parser.add_argument("--mode", choices=["backup", "restore"], help="Modo de operacion: backup o restore")
    args = parser.parse_args()

    if args.mode == "backup":
        banner()
        print("\n-- Backup mode  --")
        backup()

    elif args.mode == "restore":
        banner()
        print("\n-- Restore mode  --")

    else:
        banner()
        menu()


if __name__ == "__main__":
    main()
