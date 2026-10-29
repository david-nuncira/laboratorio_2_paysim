# Datos

Coloque aquí el archivo `transacciones.csv` si desea ejecutar el proyecto sin pasar `--data`.

Esquema esperado:

| Columna | Tipo esperado | Descripción |
|---|---|---|
| `id_transaccion` | entero | Identificador de la transacción |
| `step` | entero | Índice horario de PaySim |
| `tipo_transaccion` | categórica nominal | Tipo de operación |
| `monto` | continua | Monto de la transacción |
| `cuenta_origen` | categórica nominal | Cuenta que inicia la operación |
| `cuenta_destino` | categórica nominal | Cuenta receptora |
| `tipo_cuenta_destino` | categórica nominal | Tipo de cuenta receptora |

El ZIP completo incluye el CSV en esta carpeta. El archivo no se versiona en Git. Si se recibe solo la carpeta de código, copie el CSV aquí o indique su ruta con `--data`.

