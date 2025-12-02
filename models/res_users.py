# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = "res.users"

    auto_fill_courier_data = fields.Boolean(
        string='Auto Fill Courier Data',
        default=False,
        help='When enabled, automatically fills courier request fields based on user preferences'
    )
    
    # Default courier data fields for auto-fill
    default_sender_id = fields.Many2one(
        'res.partner', 
        string='Default Sender', 
        domain=[('courier', '=', True)],
        help='Default sender for courier requests'
    )
    default_courier_type_id = fields.Many2one(
        'dev.courier.type', 
        string='Default Courier Type',
        help='Default courier type for new requests'
    )
    default_category_id = fields.Many2one(
        'dev.courier.category', 
        string='Default Category',
        help='Default category for new requests'
    )
    default_priority_id = fields.Many2one(
        'dev.courier.priority', 
        string='Default Priority',
        help='Default priority for new requests'
    )
    default_tag_ids = fields.Many2many(
        'dev.courier.tags', 
        string='Default Tags',
        help='Default tags for new requests'
    )
    
    # Automation settings
    automation_enabled = fields.Boolean(
        string='Enable Automation',
        default=False,
        help='Enable automation features for this user'
    )
