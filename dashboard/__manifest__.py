# -*- coding: utf-8 -*-
{
    'name': 'Dashboard Ejecutivo',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Dashboard ejecutivo con KPIs de ventas y métricas clave',
    'description': """
        Dashboard Ejecutivo - Módulo de Análisis de Ventas
        ==================================================

        Este módulo proporciona un dashboard ejecutivo completo con:

        **KPIs de Ventas:**
        - Ventas del mes actual
        - Comparación con mes anterior
        - Porcentaje de crecimiento
        - Ticket promedio

        **KPIs de Facturación:**
        - Facturación pendiente
        - Facturas vencidas
        - Total de facturas pendientes/vencidas

        **KPIs Adicionales:**
        - Margen del mes
        - Porcentaje de margen
        - Cantidad de productos vendidos

        **Top Rankings:**
        - Top 5 clientes por ventas (usando read_group)
        - Top 5 productos por ventas (usando read_group)

        **Gráficos de Tendencia:**
        - Evolución de ventas históricas
        - Datos mensuales para análisis de tendencia

        **Características Técnicas:**
        - Campos computados para cálculos en tiempo real
        - Uso de read_group para optimización de agregados
        - Vista Kanban estilo tarjetas con métricas
        - Vistas Tree, Form y Kanban para todos los modelos
        - Acciones para navegar a registros relacionados
        - Botón de actualización de dashboard

        **Dependencias:**
        - sale: Para datos de órdenes de venta
        - account: Para datos de facturación
        - stock: Para datos de inventario
    """,
    'author': 'Felipe',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['sale', 'sale_margin', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}