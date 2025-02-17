# DataSyncTool
## Automated Data Migration for TrueNAS

*DataSyncTool* is a tool for **extracting**, **compressing**, **transferring**, and **restoring** data between *TrueNAS* servers using rsync.
Its goal is to facilitate file migration efficiently and securely.

## Features
- *Extraction:* Identifies and selects files for migration.
- *Compression:* Reduces the size of files before transfer.
- *Secure Transfer:* Uses rsync over SSH to send data.
- *Restoration:* Decompresses and reorganizes files on the new server.
- *Verification:* Optionally validates the integrity of the data after migration.

## Usage
The backup and restore process is performed with the same command.

### Installation and execution
Run the following commands to clone the repository and execute the tool:

```shell
git clone https://github.com/TRuHa83/TrueNAS_DataSyncTool.git
cd TrueNAS_DataSyncTool
python DataSyncTool.py
```

### Backup
- The tool will automatically detect the available Datasets on the system.
- You will be prompted to select the Dataset you want to back up.
- A search for ix-applications and Virtual Machines will be performed:
  - If found, you will be asked if you want to include them in the backup.
- After confirmation, the backup process will proceed.