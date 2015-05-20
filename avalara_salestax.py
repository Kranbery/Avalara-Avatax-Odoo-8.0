# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields,osv


class tax_schedule(osv.osv):
    _name = "tax.schedule"
    _description = "Tax Schedule"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=32),
        'jurisdiction_code_ids': fields.one2many('jurisdiction.code', 'tax_schedule_id', 'Jurisdiction Codes'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'country_id': fields.many2one('res.country', 'Country', required=True),
    }
    _defaults = {
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'tax.schedule', context=c),
    }

tax_schedule()

class jurisdiction_code(osv.osv):
    _name = "jurisdiction.code"
    _description = "Jurisdiction Code"
    _columns = {
        'name': fields.char('Description', size=32, required=True),
        'type': fields.selection([('country', 'Country'), ('composite', 'Composite'), ('state', 'State'),
                          ('county', 'County'), ('city', 'City'), ('special', 'Special')], 'Type', required=True,
                          help="Type of tax jurisdiction"),
        'state_id': fields.many2one('res.country.state', 'State', required=True, help="State for which the tax jurisdiction is defined"),
        'code':fields.char('Code', size=32),
        'tax_schedule_id': fields.many2one('tax.schedule', 'Tax Schedule'),
        'account_collected_id':fields.many2one('account.account', 'Invoice Tax Account', required=True, help="Use this tax account for Invoices"),
        'account_paid_id':fields.many2one('account.account', 'Refund Tax Account', required=True, help="Use this tax account for Refunds"),
        'base_code_id': fields.many2one('account.tax.code', 'Account Base Code', help="Use this base code for the Invoices"),
        'tax_code_id': fields.many2one('account.tax.code', 'Account Tax Code', help="Use this tax code for the Invoices"),
        'base_sign': fields.float('Base Code Sign', help="Usually 1 or -1"),
        'tax_sign': fields.float('Tax Code Sign', help="Usually 1 or -1"),
        'ref_base_code_id': fields.many2one('account.tax.code', 'Refund Base Code', help="Use this base code for the Refunds"),
        'ref_tax_code_id': fields.many2one('account.tax.code', 'Refund Tax Code', help="Use this tax code for the Refunds"),
        'ref_base_sign': fields.float('Base Code Sign', help="Usually 1 or -1"),
        'ref_tax_sign': fields.float('Tax Code Sign', help="Usually 1 or -1"),
    }
    _defaults = {
        'ref_tax_sign': 1,
        'ref_base_sign': 1,
        'tax_sign': 1,
        'base_sign': 1,
    }

jurisdiction_code()

class exemption_code(osv.osv):
    _name = 'exemption.code'
    _description = 'Exemption Code'
    _columns = {
        'name': fields.char('Name', size=64),
        'code': fields.char('Code', size=1),
    }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = '(' + record['code'] + ')' + ' ' + name
            res.append((record['id'], name))
        return res

exemption_code()

class avalara_salestax(osv.osv):
    _name = 'avalara.salestax'
    _description = 'AvaTax Configuration'
    __rec_name = 'account_number'
    
    def _get_avatax_supported_countries(self, cr, uid, context=None):
        """ Returns the countries supported by AvaTax Address Validation Service."""

        country_pool = self.pool.get('res.country')
        return country_pool.search(cr, uid, [('code', 'in', ['US', 'CA'])], context=context)
    
    def onchange_address_validation(self, cr, uid, add_id, context=None):
        res = {}
        if add_id:
            res['validation_on_save'] = False
            res['force_address_validation'] = False
            res['result_in_uppercase'] = False
            
        return {'value': res}

    # treat as radio button(s) 
    def onchange_disable_tax_calculation(self, cr, uid, ids, dtc, context=None):
        res = {}
        if dtc:
            res['disable_tax_reporting'] = False
            res['disable_tax_calculation'] = dtc
        return {'value': res}
       
    def onchange_tax_reporting(self, cr, uid, ids, dtr, context=None):
        res = {}
        if dtr:
            res['disable_tax_reporting'] = True
            res['disable_tax_calculation'] = False
        return {'value': res}
    
    def onchange_system_call1(self, cr, uid, ids, on_order, context=None):
        res = {}
        if on_order:
            res['on_order'] = on_order
            res['on_line'] = False            
        return {'value': res}

        
    def onchange_system_call2(self, cr, uid, ids, on_line, context=None):
        res = {}
        if on_line:
            res['on_order'] = False
            res['on_line'] = on_line            
        return {'value': res}                    


    
   
    _columns = {
        'account_number':fields.char('Account Number', size=64, required=True, help="Account Number provided by AvaTax"),
        'license_key': fields.char('License Key', size=64, required=True, help="License Key provided by AvaTax"),
        'service_url': fields.char('Service URL', size=64, required=True, help="The url to connect with"),
        'date_expiration': fields.date('Service Expiration Date', readonly=True, help="The expiration date of the service"),
        'request_timeout': fields.integer('Request Timeout', help="Defines AvaTax request time out length, AvaTax best practices prescribes default setting of 300 seconds"),
        'company_code': fields.char('Company Code', size=64, required=True, help="The company code as defined in the Admin Console of AvaTax"),
        'logging': fields.boolean('Enable Logging', help="Enables detailed AvaTax transaction logging within application"),
        'address_validation': fields.boolean('Attempt automatic address validation', help="Check to disable address validation"),
        'enable_address_validation': fields.boolean('Enable Address Validation', help="Check to Enable address validation"),
        'result_in_uppercase': fields.boolean('Return validation results in upper case', help="Check is address validation results desired to be in upper case"),
        'validation_on_save': fields.boolean('Force validate on save for customer profile', help="Validates the address and automatically saves when Customer profile is saved."),
        #'force_address_validation': fields.boolean('Force Address validation on customer profile save', help="Check if address validation should be done before tax calculation"),
        'auto_generate_customer_code': fields.boolean('Automatically generate customer code', help="This will generate customer code for customers in the system who do not have codes already created.  Each code is unique per customer.  When this is disabled, you will have to manually go to each customer and manually generate their customer code.  This is required for Avatax and is only generated one time."),                
        'disable_tax_calculation': fields.boolean('Disable Avalara Tax Calculation and reporting', help="Check to disable avalara tax calculation and reporting"),
        'disable_tax_reporting': fields.boolean('Disable Avalara Tax reporting only', help="Check to disable avalara tax reporting to Avatax Service.  You will not see the transactions on the Avalara transaction web portal."),
        'default_tax_schedule_id': fields.many2one('tax.schedule', 'Default Tax Schedule', help="Identifies customers using AVATAX. Only customers with AVATAX designation triggers tax calculation from AvaTax otherwise it will follow the normal tax calculation that OpenERP provides"),
        'default_shipping_code_id': fields.many2one('product.tax.code', 'Default Shipping Code', help="The default shipping code which will be passed to Avalara"),
        'country_ids': fields.many2many('res.country', 'avalara_salestax_country_rel', 'avalara_salestax_id', 'country_id', 'Countries', help="Countries where address validation will be used"),
        'active': fields.boolean('Active', help="Uncheck the active field to hide the record"),
        'company_id': fields.many2one('res.company', 'Company', required=True, help="Company which has subscribed to the AvaTax service"),
        'on_line': fields.boolean('Line-level', help="It will calculate tax line by line and also show."),
        'on_order': fields.boolean('Order-level', help="It will calculate tax for order not line by line."),
        'upc_enable': fields.boolean('Enable UPC Taxability', help="Allows ean13 to be reported in place of Item Reference as upc identifier."),
        
    }
    _defaults = {
        'active': True,
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'avalara.salestax', context=c),
        'request_timeout': 300,
        'country_ids': _get_avatax_supported_countries,
        'on_order': True,
        'address_validation': True,
        'auto_generate_customer_code': True,    
        'disable_tax_calculation' : False,    
        'disable_tax_calculation' : False, 
    }
    
    #constraints on uniq records creation with account_number and company_id
    _sql_constraints = [
        ('code_company_uniq', 'unique (company_code)', 'Avalara setting is already available for this company code'),
        ('account_number_company_uniq', 'unique (account_number, company_id)', 'The account number must be unique per company!'),
    ]

    def _get_avatax_config_company(self, cr, uid, context=None):
        """ Returns the AvaTax configuration for the user company """
        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid, context=context)
        avatax_config_ids = self.search(cr, uid, [('company_id', '=', user.company_id.id)], context=context)
        return avatax_config_ids and self.browse(cr, uid, avatax_config_ids[0], context=context) or False

avalara_salestax()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: