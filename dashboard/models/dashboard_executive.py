from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta


class DashboardExecutive(models.Model):
    _name = 'dashboard.executive'
    _description = 'Dashboard Ejecutivo de Ventas'
    _order = 'date desc'

    # Campos basicos

    name = fields.Char(
        string='Periodo',
        compute='_compute_name',
        store=True,
        index=True
    )

    date = fields.Date(
        string='Fecha',
        default=fields.Date.today,
        required=True,
        index=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Compania',
        default=lambda self: self.env.company,
        required=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Moneda',
        readonly=True
    )

    color = fields.Integer(string='Color', default=0)
    notes = fields.Text(string='Notas')

    # Ventas del mes

    sales_month = fields.Monetary(
        string='Ventas del Mes',
        compute='_compute_sales_kpis',
        store=True,
        currency_field='currency_id'
    )

    sales_month_count = fields.Integer(
        string='Ordenes del Mes',
        compute='_compute_sales_kpis',
        store=True
    )

    sales_month_avg = fields.Monetary(
        string='Ticket Promedio',
        compute='_compute_sales_kpis',
        store=True,
        currency_field='currency_id'
    )

    # Comparacion con mes anterior

    sales_prev_month = fields.Monetary(
        string='Ventas Mes Anterior',
        compute='_compute_sales_kpis',
        store=True,
        currency_field='currency_id'
    )

    sales_prev_month_count = fields.Integer(
        string='Ordenes Mes Anterior',
        compute='_compute_sales_kpis',
        store=True
    )

    sales_growth = fields.Float(
        string='Crecimiento %',
        compute='_compute_sales_kpis',
        store=True,
        digits=(5, 2)
    )

    sales_growth_trend = fields.Selection([
        ('up', 'Positivo'),
        ('down', 'Negativo'),
        ('neutral', 'Neutral')
    ],
        string='Tendencia',
        compute='_compute_sales_kpis',
        store=True
    )

    # Facturacion

    pending_invoices = fields.Monetary(
        string='Facturacion Pendiente',
        compute='_compute_invoices_kpis',
        store=True,
        currency_field='currency_id'
    )

    pending_invoices_count = fields.Integer(
        string='Facturas Pendientes',
        compute='_compute_invoices_kpis',
        store=True
    )

    overdue_invoices = fields.Monetary(
        string='Facturas Vencidas',
        compute='_compute_invoices_kpis',
        store=True,
        currency_field='currency_id'
    )

    overdue_invoices_count = fields.Integer(
        string='Cant. Facturas Vencidas',
        compute='_compute_invoices_kpis',
        store=True
    )

    # Metricas adicionales

    margin_month = fields.Monetary(
        string='Margen del Mes',
        compute='_compute_additional_kpis',
        store=True,
        currency_field='currency_id'
    )

    margin_percent = fields.Float(
        string='Porcentaje de Margen',
        compute='_compute_additional_kpis',
        store=True,
        digits=(5, 2)
    )

    products_sold_count = fields.Integer(
        string='Productos Vendidos',
        compute='_compute_additional_kpis',
        store=True
    )

    # Relaciones con otros modelos

    top_customer_ids = fields.One2many(
        'dashboard.top.customer',
        'dashboard_id',
        string='Top Clientes'
    )

    top_clients_revenue = fields.Monetary(
        string='Ingresos Top Clientes',
        compute='_compute_top_clients_metrics',
        store=True,
        currency_field='currency_id'
    )

    top_product_ids = fields.One2many(
        'dashboard.top.product',
        'dashboard_id',
        string='Top Productos'
    )

    top_products_revenue = fields.Monetary(
        string='Ingresos Top Productos',
        compute='_compute_top_products_metrics',
        store=True,
        currency_field='currency_id'
    )

    trend_data_ids = fields.One2many(
        'dashboard.trend.data',
        'dashboard_id',
        string='Tendencia'
    )

    # Metodos computados

    @api.depends('date')
    def _compute_name(self):
        for record in self:
            if record.date:
                record.name = record.date.strftime('%B %Y').capitalize()
            else:
                record.name = 'Dashboard'

    @api.depends('date', 'company_id')
    def _compute_sales_kpis(self):
        SaleOrder = self.env['sale.order']

        for record in self:
            if not record.date:
                record.sales_month = 0
                record.sales_month_count = 0
                record.sales_month_avg = 0
                record.sales_prev_month = 0
                record.sales_prev_month_count = 0
                record.sales_growth = 0
                record.sales_growth_trend = 'neutral'
            else:
                date_start = record.date.replace(day=1)
                date_end = (date_start + relativedelta(months=1)) - relativedelta(days=1)
                prev_date_start = date_start - relativedelta(months=1)
                prev_date_end = date_start - relativedelta(days=1)

                domain_month = [
                    ('date_order', '>=', date_start),
                    ('date_order', '<=', date_end),
                    ('state', 'in', ['sale', 'done']),
                    ('company_id', '=', record.company_id.id),
                ]

                domain_prev = [
                    ('date_order', '>=', prev_date_start),
                    ('date_order', '<=', prev_date_end),
                    ('state', 'in', ['sale', 'done']),
                    ('company_id', '=', record.company_id.id),
                ]

                # Ventas del mes actual
                orders_month = SaleOrder.search(domain_month)
                sales_month = sum(o.amount_total for o in orders_month)
                sales_month_count = len(orders_month)

                # Ventas del mes anterior
                orders_prev = SaleOrder.search(domain_prev)
                sales_prev_month = sum(o.amount_total for o in orders_prev)
                sales_prev_month_count = len(orders_prev)

                # Ticket promedio
                sales_month_avg = sales_month / sales_month_count if sales_month_count else 0

                # Crecimiento
                if sales_prev_month > 0:
                    sales_growth = ((sales_month - sales_prev_month) / sales_prev_month) * 100
                    sales_growth_trend = 'up' if sales_growth >= 0 else 'down'
                else:
                    sales_growth = 0
                    sales_growth_trend = 'neutral'

                record.sales_month = sales_month
                record.sales_month_count = sales_month_count
                record.sales_month_avg = sales_month_avg
                record.sales_prev_month = sales_prev_month
                record.sales_prev_month_count = sales_prev_month_count
                record.sales_growth = sales_growth
                record.sales_growth_trend = sales_growth_trend

    @api.depends('date', 'company_id')
    def _compute_invoices_kpis(self):
        AccountMove = self.env['account.move']

        for record in self:
            if not record.date:
                record.pending_invoices = 0
                record.pending_invoices_count = 0
                record.overdue_invoices = 0
                record.overdue_invoices_count = 0
            else:
                domain_pending = [
                    ('state', '=', 'posted'),
                    ('move_type', '=', 'out_invoice'),
                    ('payment_state', 'in', ['not_paid', 'partial']),
                    ('company_id', '=', record.company_id.id),
                ]

                domain_overdue = domain_pending + [
                    ('invoice_date_due', '<', record.date),
                ]

                pending = AccountMove.search(domain_pending)
                record.pending_invoices = sum(inv.amount_residual for inv in pending)
                record.pending_invoices_count = len(pending)

                overdue = AccountMove.search(domain_overdue)
                record.overdue_invoices = sum(inv.amount_residual for inv in overdue)
                record.overdue_invoices_count = len(overdue)

    @api.depends('date', 'company_id')
    def _compute_additional_kpis(self):
        for record in self:
            if not record.date:
                record.margin_month = 0
                record.margin_percent = 0
                record.products_sold_count = 0
            else:
                date_start = record.date.replace(day=1)
                date_end = (date_start + relativedelta(months=1)) - relativedelta(days=1)

                domain = [
                    ('date_order', '>=', date_start),
                    ('date_order', '<=', date_end),
                    ('state', 'in', ['sale', 'done']),
                    ('company_id', '=', record.company_id.id),
                ]

                orders = self.env['sale.order'].search(domain)
                margin_month = sum(order.margin for order in orders)
                products_sold_count = sum(len(order.order_line) for order in orders)

                margin_percent = 0
                if record.sales_month > 0:
                    margin_percent = (margin_month / record.sales_month) * 100

                record.margin_month = margin_month
                record.margin_percent = margin_percent
                record.products_sold_count = products_sold_count

    @api.depends('top_customer_ids.total_amount')
    def _compute_top_clients_metrics(self):
        for record in self:
            record.top_clients_revenue = sum(c.total_amount for c in record.top_customer_ids)

    @api.depends('top_product_ids.total_amount')
    def _compute_top_products_metrics(self):
        for record in self:
            record.top_products_revenue = sum(p.total_amount for p in record.top_product_ids)

    # Acciones

    def action_generate_top_clients(self, top_n=5):
        SaleOrder = self.env['sale.order']

        for record in self:
            record.top_customer_ids.unlink()

            if record.date:
                date_start = record.date.replace(day=1)
                date_end = (date_start + relativedelta(months=1)) - relativedelta(days=1)

                domain = [
                    ('date_order', '>=', date_start),
                    ('date_order', '<=', date_end),
                    ('state', 'in', ['sale', 'done']),
                    ('company_id', '=', record.company_id.id),
                ]

                orders = SaleOrder.search(domain)

                # Agrupar ventas por cliente
                client_totals = {}
                for order in orders:
                    pid = order.partner_id.id
                    if pid not in client_totals:
                        client_totals[pid] = {
                            'partner_id': pid,
                            'total_amount': 0,
                            'order_count': 0,
                        }
                    client_totals[pid]['total_amount'] += order.amount_total
                    client_totals[pid]['order_count'] += 1

                # Ordenar por monto y tomar los top N
                sorted_clients = sorted(
                    client_totals.values(),
                    key=lambda c: c['total_amount'],
                    reverse=True
                )[:top_n]

                top_clients = []
                for idx, client in enumerate(sorted_clients, 1):
                    top_clients.append({
                        'dashboard_id': record.id,
                        'partner_id': client['partner_id'],
                        'total_amount': client['total_amount'],
                        'order_count': client['order_count'],
                        'rank': idx,
                    })

                if top_clients:
                    self.env['dashboard.top.customer'].create(top_clients)

        return True

    def action_generate_top_products(self, top_n=5):
        SaleOrderLine = self.env['sale.order.line']

        for record in self:
            record.top_product_ids.unlink()

            if record.date:
                date_start = record.date.replace(day=1)
                date_end = (date_start + relativedelta(months=1)) - relativedelta(days=1)

                domain = [
                    ('order_id.date_order', '>=', date_start),
                    ('order_id.date_order', '<=', date_end),
                    ('order_id.state', 'in', ['sale', 'done']),
                    ('order_id.company_id', '=', record.company_id.id),
                ]

                lines = SaleOrderLine.search(domain)

                # Agrupar por producto
                product_totals = {}
                for line in lines:
                    pid = line.product_id.id
                    if pid and pid not in product_totals:
                        product_totals[pid] = {
                            'product_id': pid,
                            'total_amount': 0,
                            'quantity': 0,
                        }
                    if pid:
                        product_totals[pid]['total_amount'] += line.price_subtotal
                        product_totals[pid]['quantity'] += line.product_uom_qty

                # Ordenar por monto y tomar los top N
                sorted_products = sorted(
                    product_totals.values(),
                    key=lambda p: p['total_amount'],
                    reverse=True
                )[:top_n]

                top_products = []
                for idx, product in enumerate(sorted_products, 1):
                    top_products.append({
                        'dashboard_id': record.id,
                        'product_id': product['product_id'],
                        'total_amount': product['total_amount'],
                        'quantity': product['quantity'],
                        'rank': idx,
                    })

                if top_products:
                    self.env['dashboard.top.product'].create(top_products)

        return True

    def action_generate_trend_data(self, months=12):
        SaleOrder = self.env['sale.order']

        for record in self:
            record.trend_data_ids.unlink()

            if record.date:
                trend_data = []
                current_date = record.date.replace(day=1)

                for i in range(months):
                    month_start = current_date
                    month_end = (month_start + relativedelta(months=1)) - relativedelta(days=1)

                    domain = [
                        ('date_order', '>=', month_start),
                        ('date_order', '<=', month_end),
                        ('state', 'in', ['sale', 'done']),
                        ('company_id', '=', record.company_id.id),
                    ]

                    orders = SaleOrder.search(domain)

                    trend_data.append({
                        'dashboard_id': record.id,
                        'date': month_start,
                        'label': month_start.strftime('%Y-%m'),
                        'sales': sum(o.amount_total for o in orders),
                        'order_count': len(orders),
                    })

                    current_date -= relativedelta(months=1)

                if trend_data:
                    self.env['dashboard.trend.data'].create(trend_data)

        return True

    def action_refresh_dashboard(self):
        self._compute_sales_kpis()
        self._compute_invoices_kpis()
        self._compute_additional_kpis()
        self.action_generate_top_clients()
        self.action_generate_top_products()
        self.action_generate_trend_data()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.model
    def action_create_current_month_dashboard(self):
        today = date.today()
        company_id = self.env.company.id
        date_start = today.replace(day=1)

        existing = self.search([
            ('date', '>=', date_start),
            ('date', '<=', (date_start + relativedelta(months=1)) - relativedelta(days=1)),
            ('company_id', '=', company_id),
        ], limit=1)

        if existing:
            dashboard = existing
            dashboard.date = today
        else:
            dashboard = self.create({
                'date': today,
                'company_id': company_id,
            })

        dashboard.action_refresh_dashboard()

        return dashboard


class DashboardTopProduct(models.Model):
    _name = 'dashboard.top.product'
    _description = 'Top Productos del Dashboard'
    _order = 'rank, total_amount desc'

    dashboard_id = fields.Many2one(
        'dashboard.executive',
        string='Dashboard',
        required=True,
        ondelete='cascade'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True
    )

    product_name = fields.Char(
        string='Nombre del Producto',
        compute='_compute_product_name',
        store=True
    )

    total_amount = fields.Monetary(
        string='Monto Total',
        currency_field='currency_id'
    )

    quantity = fields.Float(string='Cantidad')

    rank = fields.Integer(string='Posicion', required=True, default=1)

    currency_id = fields.Many2one(
        'res.currency',
        related='dashboard_id.currency_id',
        readonly=True,
        store=True
    )

    @api.depends('product_id')
    def _compute_product_name(self):
        for rec in self:
            if rec.product_id:
                rec.product_name = rec.product_id.name
            else:
                rec.product_name = ''

    def action_view_sales(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ventas del Producto',
            'res_model': 'sale.order.line',
            'view_mode': 'tree,form',
            'domain': [('product_id', '=', self.product_id.id)],
        }


class DashboardTrendData(models.Model):
    _name = 'dashboard.trend.data'
    _description = 'Datos de Tendencia de Ventas'
    _order = 'date desc'

    dashboard_id = fields.Many2one(
        'dashboard.executive',
        string='Dashboard',
        required=True,
        ondelete='cascade'
    )

    date = fields.Date(string='Fecha', required=True)

    label = fields.Char(string='Etiqueta')

    sales = fields.Monetary(
        string='Ventas',
        currency_field='currency_id'
    )

    order_count = fields.Integer(string='Cantidad de Ordenes')

    currency_id = fields.Many2one(
        'res.currency',
        related='dashboard_id.currency_id',
        readonly=True,
        store=True
    )