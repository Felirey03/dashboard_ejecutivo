from odoo import models, fields, api


class DashboardTopCustomer(models.Model):
    """
    Guarda los clientes con mejores ventas dentro del periodo del dashboard.
    Cada registro representa un cliente rankeado.
    """
    _name = 'dashboard.top.customer'
    _description = 'Top Clientes del Dashboard'
    _order = 'rank, total_amount DESC'

    # Datos principales

    dashboard_id = fields.Many2one(
        'dashboard.executive',
        string='Dashboard',
        required=True,
        ondelete='cascade',
        help='Dashboard al que pertenece este registro'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        index=True,
        help='Cliente evaluado en el ranking'
    )

    partner_name = fields.Char(
        string='Nombre del Cliente',
        compute='_compute_partner_name',
        store=True,
        index=True
    )

    email = fields.Char(
        string='Email',
        related='partner_id.email',
        readonly=True
    )

    phone = fields.Char(
        string='Telefono',
        related='partner_id.phone',
        readonly=True
    )

    # Metricas

    total_amount = fields.Monetary(
        string='Total Ventas',
        required=True,
        currency_field='currency_id',
        help='Monto total vendido en el periodo'
    )

    order_count = fields.Integer(
        string='Cantidad Ordenes',
        required=True,
        help='Ordenes confirmadas en el periodo'
    )

    avg_order_value = fields.Monetary(
        string='Ticket Promedio',
        compute='_compute_avg_order_value',
        store=True,
        currency_field='currency_id',
        help='Promedio por orden'
    )

    rank = fields.Integer(
        string='Posicion',
        required=True,
        help='1 es el mejor cliente del periodo'
    )

    color = fields.Integer(
        string='Color',
        compute='_compute_color',
        store=True,
        help='Color usado en la vista kanban'
    )

    # Moneda

    currency_id = fields.Many2one(
        'res.currency',
        related='dashboard_id.currency_id',
        readonly=True,
        store=True
    )

    # Metodos computados

    @api.depends('partner_id.name')
    def _compute_partner_name(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_name = rec.partner_id.name
            else:
                rec.partner_name = ''

    @api.depends('total_amount', 'order_count')
    def _compute_avg_order_value(self):
        for rec in self:
            if rec.order_count and rec.order_count > 0:
                rec.avg_order_value = rec.total_amount / rec.order_count
            else:
                rec.avg_order_value = 0.0

    @api.depends('rank')
    def _compute_color(self):
        # Marco visualmente el top 3
        for rec in self:
            if rec.rank == 1:
                rec.color = 10
            elif rec.rank == 2:
                rec.color = 8
            elif rec.rank == 3:
                rec.color = 6
            else:
                rec.color = 0

    # Acciones

    def action_view_partner(self):
        # Abre el formulario del cliente
        self.ensure_one()

        return  {
            'type': 'ir.actions.act_window',
            'name': 'Cliente',
            'res_model': 'res.partner',
            'res_id': self.partner_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

        

    def action_view_client_orders(self):
        """
        Muestra las ordenes de venta del cliente
        dentro del mes seleccionado en el dashboard.
        """
        self.ensure_one()

        date_start = self.dashboard_id.date.replace(day=1)

        from dateutil.relativedelta import relativedelta
        date_end = (date_start + relativedelta(months=1)) - relativedelta(days=1)

        domain = [
            ('partner_id', '=', self.partner_id.id),
            ('date_order', '>=', date_start),
            ('date_order', '<=', date_end),
            ('state', 'in', ['sale', 'done']),
        ]

        return  {
            'name': 'Ordenes de %s' % self.partner_name,
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {},
            'target': 'current',
        }
