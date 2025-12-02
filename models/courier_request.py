# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api


class CourierRequest(models.Model):
    _inherit = 'dev.courier.request'
    
    # Automation fields
    auto_filled = fields.Boolean(
        string='Auto Filled',
        default=False,
        help='Indicates if this record was auto-filled with user defaults'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to implement auto-fill functionality"""
        # Process each dictionary in vals_list
        for vals in vals_list:
            # Auto-fill courier data if user has the option enabled
            if not vals.get('user_id'):
                vals['user_id'] = self.env.user.id
                
            user = self.env['res.users'].browse(vals['user_id'])
            if user.auto_fill_courier_data and user.automation_enabled:
                # Auto-fill fields if they are not already set
                auto_filled_fields = []
                
                if not vals.get('sender_id') and user.default_sender_id:
                    vals['sender_id'] = user.default_sender_id.id
                    auto_filled_fields.append('sender_id')
                    
                if not vals.get('courier_type_id') and user.default_courier_type_id:
                    vals['courier_type_id'] = user.default_courier_type_id.id
                    auto_filled_fields.append('courier_type_id')
                    
                if not vals.get('category_id') and user.default_category_id:
                    vals['category_id'] = user.default_category_id.id
                    auto_filled_fields.append('category_id')
                    
                if not vals.get('priority_id') and user.default_priority_id:
                    vals['priority_id'] = user.default_priority_id.id
                    auto_filled_fields.append('priority_id')
                    
                if not vals.get('tag_ids') and user.default_tag_ids:
                    vals['tag_ids'] = [(6, 0, user.default_tag_ids.ids)]
                    auto_filled_fields.append('tag_ids')
                
                # Mark as auto-filled if any fields were filled
                if auto_filled_fields:
                    vals['auto_filled'] = True
        
        return super(CourierRequest, self).create(vals_list)

    @api.model
    def default_get(self, fields_list):
        """Prefill fields when opening the form, before saving."""
        defaults = super(CourierRequest, self).default_get(fields_list)

        # Resolve user
        user_id = defaults.get('user_id') or self.env.user.id
        user = self.env['res.users'].browse(user_id)

        if getattr(user, 'auto_fill_courier_data', False) and getattr(user, 'automation_enabled', True):
            # Only set if not already provided by context/defaults
            if 'sender_id' in fields_list and not defaults.get('sender_id') and getattr(user, 'default_sender_id', False):
                defaults['sender_id'] = user.default_sender_id.id
            if 'courier_type_id' in fields_list and not defaults.get('courier_type_id') and getattr(user, 'default_courier_type_id', False):
                defaults['courier_type_id'] = user.default_courier_type_id.id
            if 'category_id' in fields_list and not defaults.get('category_id') and getattr(user, 'default_category_id', False):
                defaults['category_id'] = user.default_category_id.id
            if 'priority_id' in fields_list and not defaults.get('priority_id') and getattr(user, 'default_priority_id', False):
                defaults['priority_id'] = user.default_priority_id.id
            if 'tag_ids' in fields_list and not defaults.get('tag_ids') and getattr(user, 'default_tag_ids', False):
                defaults['tag_ids'] = [(6, 0, user.default_tag_ids.ids)]

        return defaults

    @api.onchange('user_id')
    def _onchange_user_id_apply_defaults(self):
        """When changing user on the form, apply that user's defaults if enabled."""
        user = self.user_id or self.env.user
        # today_date = datetime.now().date()

        if getattr(user, 'auto_fill_courier_data', False) and getattr(user, 'automation_enabled', True):
            values_to_apply = {}
            if not self.sender_id and getattr(user, 'default_sender_id', False):
                values_to_apply['sender_id'] = user.default_sender_id.id
            if not self.courier_type_id and getattr(user, 'default_courier_type_id', False):
                values_to_apply['courier_type_id'] = user.default_courier_type_id.id
            if not self.category_id and getattr(user, 'default_category_id', False):
                values_to_apply['category_id'] = user.default_category_id.id
            if not self.priority_id and getattr(user, 'default_priority_id', False):
                values_to_apply['priority_id'] = user.default_priority_id.id
            if not self.tag_ids and getattr(user, 'default_tag_ids', False):
                values_to_apply['tag_ids'] = [(6, 0, user.default_tag_ids.ids)]
            if values_to_apply:
                self.update(values_to_apply)
