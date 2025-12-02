# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AutomationRule(models.Model):
    _name = 'mgp.automation.rule'
    _description = 'Automation Rule'
    _order = 'sequence, name'
    
    name = fields.Char(
        string='Rule Name',
        required=True,
        help='Name of the automation rule'
    )
    description = fields.Text(
        string='Description',
        help='Description of what this rule does'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this rule is active'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of execution (lower numbers execute first)'
    )
    
    # Rule scope
    user_id = fields.Many2one(
        'res.users',
        string='User',
        help='User this rule applies to (leave empty for all users)'
    )
    model_name = fields.Selection(
        selection='_get_model_selection',
        string='Model',
        required=True,
        help='Model this rule applies to'
    )
    
    # Conditions
    condition_type = fields.Selection([
        ('always', 'Always'),
        ('field_value', 'Field Value'),
        ('custom', 'Custom Python Code'),
    ], string='Condition Type', default='always', required=True)
    
    condition_field = fields.Char(
        string='Field Name',
        help='Field to evaluate (e.g., state, priority_id)'
    )
    condition_operator = fields.Selection([
        ('=', 'Equals'),
        ('!=', 'Not Equals'),
        ('>', 'Greater Than'),
        ('<', 'Less Than'),
        ('>=', 'Greater or Equal'),
        ('<=', 'Less or Equal'),
        ('in', 'In'),
        ('not in', 'Not In'),
        ('like', 'Contains'),
        ('not like', 'Not Contains'),
    ], string='Operator', default='=')
    condition_value = fields.Char(
        string='Value',
        help='Value to compare against'
    )
    condition_code = fields.Text(
        string='Python Code',
        help='Custom Python code for condition evaluation. Use "record" as the record variable.'
    )
    
    # Actions
    action_type = fields.Selection([
        ('set_field', 'Set Field Value'),
        ('set_fields', 'Set Multiple Fields'),
        ('custom', 'Custom Python Code'),
    ], string='Action Type', default='set_field', required=True)
    
    action_field = fields.Char(
        string='Field Name',
        help='Field to set (e.g., priority_id, category_id)'
    )
    action_value = fields.Char(
        string='Value',
        help='Value to set'
    )
    action_fields = fields.Text(
        string='Field Values (JSON)',
        help='JSON format: {"field1": "value1", "field2": "value2"}'
    )
    action_code = fields.Text(
        string='Python Code',
        help='Custom Python code for action execution. Use "record" as the record variable.'
    )
    
    # Statistics
    execution_count = fields.Integer(
        string='Executions',
        default=0,
        help='Number of times this rule has been executed'
    )
    last_execution = fields.Datetime(
        string='Last Execution',
        help='When this rule was last executed'
    )
    
    @api.model
    def _get_model_selection(self):
        """Get available models for automation rules"""
        return [
            ('dev.courier.request', 'Courier Request'),
            ('res.partner', 'Partner'),
            ('sale.order', 'Sale Order'),
            ('account.move', 'Invoice'),
        ]
    
    @api.constrains('condition_code', 'action_code')
    def _check_code_safety(self):
        """Basic safety check for Python code"""
        dangerous_keywords = ['import', 'exec', 'eval', '__', 'open', 'file']
        
        for record in self:
            if record.condition_code:
                for keyword in dangerous_keywords:
                    if keyword in record.condition_code.lower():
                        raise ValidationError(
                            _('Code contains potentially dangerous keyword: %s') % keyword
                        )
            
            if record.action_code:
                for keyword in dangerous_keywords:
                    if keyword in record.action_code.lower():
                        raise ValidationError(
                            _('Code contains potentially dangerous keyword: %s') % keyword
                        )
    
    def _evaluate_conditions(self, record):
        """Evaluate if the conditions are met for the given record"""
        self.ensure_one()
        
        if self.condition_type == 'always':
            return True
            
        elif self.condition_type == 'field_value':
            if not self.condition_field:
                return False
                
            field_value = getattr(record, self.condition_field, None)
            if field_value is None:
                return False
                
            # Convert condition value to appropriate type
            condition_value = self._convert_value(field_value, self.condition_value)
            
            # Apply operator
            if self.condition_operator == '=':
                return field_value == condition_value
            elif self.condition_operator == '!=':
                return field_value != condition_value
            elif self.condition_operator == '>':
                return field_value > condition_value
            elif self.condition_operator == '<':
                return field_value < condition_value
            elif self.condition_operator == '>=':
                return field_value >= condition_value
            elif self.condition_operator == '<=':
                return field_value <= condition_value
            elif self.condition_operator == 'in':
                return field_value in condition_value
            elif self.condition_operator == 'not in':
                return field_value not in condition_value
            elif self.condition_operator == 'like':
                return str(condition_value).lower() in str(field_value).lower()
            elif self.condition_operator == 'not like':
                return str(condition_value).lower() not in str(field_value).lower()
                
        elif self.condition_type == 'custom':
            if not self.condition_code:
                return False
                
            try:
                # Create safe execution context
                safe_globals = {
                    'record': record,
                    'env': self.env,
                    'fields': fields,
                }
                safe_locals = {}
                
                exec(self.condition_code, safe_globals, safe_locals)
                return safe_locals.get('result', False)
                
            except Exception as e:
                # Log error but don't break the process
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning('Automation rule condition error: %s', str(e))
                return False
                
        return False
    
    def _execute_actions(self, record):
        """Execute the actions for the given record"""
        self.ensure_one()
        
        if self.action_type == 'set_field':
            if self.action_field and self.action_value:
                value = self._convert_value(
                    getattr(record, self.action_field, None), 
                    self.action_value
                )
                record.write({self.action_field: value})
                
        elif self.action_type == 'set_fields':
            if self.action_fields:
                try:
                    import json
                    field_values = json.loads(self.action_fields)
                    # Convert values appropriately
                    converted_values = {}
                    for field, value in field_values.items():
                        if hasattr(record, field):
                            converted_values[field] = self._convert_value(
                                getattr(record, field, None), 
                                value
                            )
                    if converted_values:
                        record.write(converted_values)
                except Exception as e:
                    import logging
                    _logger = logging.getLogger(__name__)
                    _logger.warning('Automation rule action error: %s', str(e))
                    
        elif self.action_type == 'custom':
            if self.action_code:
                try:
                    # Create safe execution context
                    safe_globals = {
                        'record': record,
                        'env': self.env,
                        'fields': fields,
                    }
                    safe_locals = {}
                    
                    exec(self.action_code, safe_globals, safe_locals)
                    
                except Exception as e:
                    import logging
                    _logger = logging.getLogger(__name__)
                    _logger.warning('Automation rule action error: %s', str(e))
        
        # Update statistics
        self.write({
            'execution_count': self.execution_count + 1,
            'last_execution': fields.Datetime.now(),
        })
    
    def _convert_value(self, field_value, string_value):
        """Convert string value to appropriate type based on field type"""
        if field_value is None:
            return string_value
            
        if isinstance(field_value, bool):
            return string_value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(field_value, int):
            try:
                return int(string_value)
            except ValueError:
                return string_value
        elif isinstance(field_value, float):
            try:
                return float(string_value)
            except ValueError:
                return string_value
        else:
            return string_value
    
    def action_test_rule(self):
        """Test this rule against sample data"""
        self.ensure_one()
        
        if not self.model_name:
            raise ValidationError(_('Please select a model first'))
            
        # Create a test record
        model = self.env[self.model_name]
        test_record = model.new()
        
        # Evaluate conditions
        conditions_met = self._evaluate_conditions(test_record)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Rule Test',
                'message': f'Conditions met: {conditions_met}',
                'type': 'success' if conditions_met else 'info',
            }
        }
