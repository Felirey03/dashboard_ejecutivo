# Dashboard Ejecutivo para Odoo

Este modulo agrega un tablero de control para ver el estado de las ventas y la facturacion de forma rapida. Fue pensado para tener toda la info clave en un solo lugar sin tener que entrar y salir de diferentes modulos de Odoo.

## Que hace el modulo
- Muestra el total de ventas del mes y lo compara con el mes pasado.
- Calcula el ticket promedio y el porcentaje de crecimiento.
- Muestra cuanta plata hay pendiente de cobrar y que facturas ya estan vencidas.
- Arma un ranking automatico con los 5 mejores clientes y los 5 productos mas vendidos.
- Tiene graficos de tendencia para ver la evolucion de los ultimos 12 meses.

## Como se usa
Una vez instalado, aparece un nuevo menu arriba que dice "Dashboard". 

Ahi adentro podes:
1. Ver las tarjetas por mes (vista Kanban).
2. Entrar a una y ver el detalle con los rankings.
3. Usar el boton "Ver Grafico" para abrir las visualizaciones de tendencia.
4. Darle al boton "Actualizar" para que el sistema recalcule todo en el momento.

## Instalacion y Dependencias
Para que funcione bien, el modulo necesita tener instalados:
- Ventas (sale)
- Margen de ventas (sale_margin)
- Facturacion (account)

Simplemente se instala como cualquier otro addon de Odoo. Si se instala en una base con datos cargados, va a intentar crear el dashboard del mes actual automaticamente.
