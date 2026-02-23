from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """Crea el dashboard del mes actual luego de instalar el modulo."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    if 'sale.order' in env:
        env['dashboard.executive'].action_create_current_month_dashboard()