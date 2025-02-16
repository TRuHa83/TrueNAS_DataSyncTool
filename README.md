# DataSyncTool - Migración de Datos Automatizada

*DataSyncTool* es una herramienta para la **extracción**, **compresión**, **transferencia** y **restauración** de datos entre servidores *TrueNAS* utilizando rsync.
Su objetivo es facilitar la migración de archivos de manera eficiente y segura.

## Características
- *Extracción:* Identifica y selecciona archivos para la migración.
- *Compresión:* Reduce el tamaño de los archivos antes de la transferencia.
- *Transferencia Segura:* Utiliza rsync sobre SSH para enviar datos.
- *Restauración:* Descomprime y reorganiza archivos en el nuevo servidor.
- *Verificación:* Opcionalmente, valida la integridad de los datos después de la migración.
