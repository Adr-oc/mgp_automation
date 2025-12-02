# -*- coding: utf-8 -*-

{
    'name': 'MGP Automation',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'Automation tools and utilities for MGP system',
    'description': """
        This module provides automation tools and utilities for the MGP system including:
        - Courier data auto-fill functionality
        - User preference management
        - Automated workflows
        - Custom automation rules
        
        Features:
        * Auto-fill courier request data based on user preferences
        * User-specific default values for courier fields
        * Automation rules and triggers
        * Custom workflow management
    """,
    'author': 'MRDC Tech',
    'website': 'https://mrdc.tech',
    'depends': [
        'base',
        'dev_courier_management',
    ],
    'data': [
#        'data/automation_data.xml',
#        'views/res_users_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
