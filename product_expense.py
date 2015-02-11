# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Autor:Kevin Kong (kfx2007@163.com)
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

from openerp import api,models,_,fields
from openerp import workflow
from openerp.exceptions import except_orm

class product_expense(models.Model):
	_name='product.expense'
	
	name = fields.Char('Name',readonly=True)
	staff = fields.Many2one('hr.employee','Employee',required=True)
	department = fields.Many2one('hr.department','Department')
	date = fields.Date('Date')
        expense_line = fields.One2many('product.expense.line','expense_id','Products',states={'draft':[('readonly',False)],'confirm':[('readonly',True)],'accepted':[('readonly',True)],'waiting':[('readonly',True)],'done':[('readonly',True)],'refused':[('readonly',True)]})
	state = fields.Selection(selection=[('draft','Draft'),('confirm','Confirm'),('accepted','Accepted'),('waiting','Waiting'),('done','Done'),('refused','Refused')],string="Status")
	amount = fields.Float('Amount',compute="_get_amount")
	note = fields.Text('Free Notes')
        ref_no = fields.Many2one('stock.picking','Ref Delivery',readonly=True)

	@api.one
	def _get_amount(self):
	    for line in self.expense_line:
		    self.amount += line.subtotal
	
	def action_confirm(self):
		self.state='confirm'

	def action_accept(self):
		self.state='accepted'

	def action_refuse(self):
		self.state='refused'

	def do_transfer(self):
            if self.on_ship_create():
                self.state='waiting'
	

        @api.one
	def on_ship_create(self):
		"""
		Create the delivery order according to product expense order.
		"""
		picking_obj = self.env['stock.picking']
		picking_type_obj = self.env['stock.picking.type']
		picking_type = picking_type_obj.search([('default_location_src_id','=',self.staff.department_id.expense_location.id),('code','=','outgoing')])
		if not picking_type:
                    raise except_orm(_('Warning!'),_("there's no proper location for your department."))

                if not self.ref_no:
                    picking_id = picking_obj.create({
                            "partner_id":self.staff.address_home_id.id,
                            "picking_type_id":picking_type[0].id,
                            "origin":self.name,
                            })

                    self.ref_no = picking_id 

		stock_move_obj = self.env['stock.move']
		stock_quant_obj = self.env['stock.quant']
                expense_loc = self.env['stock.location'].search([('name','=','Expense')])
                if not expense_loc:
                    raise except_orm(_('Warning!'),_("You haven't set expense location"))
		for line in self.expense_line:
			#query per product's stock quant.
			quants = stock_quant_obj.search([('product_id','=',line.product.id),('location_id.usage','=','internal')])
			qty=0
			for quant in quants:
				qty +=quant.qty

			if not qty:
                            #if picking_id:
			    #	picking_obj.unlink(picking_id)
                            raise except_orm(_('Warning!'),_('Product '+line.product.name+' has not enough quantity.'))

			stock_move_obj.create({
				'picking_id':picking_id.id,
				'product_id':line.product.id,
				'procure_method':'make_to_stock',
				'product_uom_qty':line.quantity,
				'product_uom':line.price_unit.id,
				'name':self.name,
				'location_id':self.staff.department_id.expense_location.id,
				'location_dest_id':expense_loc.id,
				})
                return True

	@api.one
	@api.constrains('expense_line')
	def _check_expense_line(self):
		if not len(self.expense_line):
                    raise except_orm(_('Warning!'),_('You must add at least one product!'))

        @api.model
        def create(self,val):
            val['name'] = self.env['ir.sequence'].get('product.expense')
            return super(product_expense,self).create(val)

        @api.one
        def unlink(self):
            if self.ref_no:
                raise except_orm(_('Warning!'),_('You must delete the delivery order first!'))
            return super(product_expense,self).unlink()

        @api.onchange('staff')
        def _onchange_staff(self):
            self.department = self.staff.department_id

        @api.one
        def copy(self):
             p =  super(product_expense,self).copy()
             p.ref_no=None
             p.expense_line = self.expense_line.copy()
             p.state='draft'
             return p

        def do_ship_end(self):
            self.write({'state':'done'})
            #correcting the account according to the stratgy.
            #1.checking if there's one strategy fit department and product category requirement.
            strategy = self.env['product.expense.account'].search([('department','=',self.staff.department_id.id)])
            account_obj = self.env['account.move']
            account_moves = account_obj.search([('ref','=',self.ref_no.name)])
            if len(strategy):
                for line in self.expense_line:
                    res = [s_line for s_line in strategy.line_ids if s_line.product_category==line.product.categ_id]
                    if len(res):
                        if len(account_moves):
                            for account_move in account_moves:
                                for a_line in account_move.line_id:
                                    if a_line.product_id == line.product and a_line.credit !=0 and a_line.debit==0:
                                        a_line.write({'account_id':res[0].in_account.id})
                                    if a_line.product_id == line.product and a_line.debit !=0 and a_line.credit==0:
                                        a_line.write({'account_id':res[0].out_account.id})

        #@api.one
        #def test(self):
        #    account_obj = self.env['account.move']
        #    account_moves = account_obj.search([('ref','=',self.ref_no.name)])
        #    print account_moves.line_id
            

            

class product_expense_line(models.Model):
	_name="product.expense.line"
    
        expense_id = fields.Many2one('product.expense','Expense_id')
	product = fields.Many2one('product.product','Product',domain=[('hr_expense_ok','=',True)])
	expense_date = fields.Date('Expense Date')
	comment = fields.Char('Comment')
	price_unit = fields.Many2one('product.uom','Unit')
	price = fields.Float('Price')
	quantity = fields.Float('Quantity')
	subtotal = fields.Float('Subtotal',compute='_get_subtotal')

        @api.onchange('quantity')
        def _onchange_quantity(self):
            self.subtotal = self.price * self.quantity

	@api.one
	def _get_subtotal(self):
	    self.subtotal = self.price * self.quantity

	@api.onchange('product')
	def _onchange_product(self):
		self.price_unit = self.product.uom_id
		self.price = self.product.standard_price

        @api.constrains('quantity','price')
        def _check_quantity_price(self):
            if self.quantity==0 or self.price==0:
                raise except_orm(_('Warning!'),_('The Quantity Or Price Can not be Zero!'))

class product_hr_department(models.Model):
	_inherit='hr.department'

	expense_location = fields.Many2one('stock.location','Expense Location',domain=[('usage','=','internal')],required=True)
        strategy = fields.Many2one('product.expense.account','Strategy')

class product_expense_picking(models.Model):
    _inherit='stock.picking'

    @api.one
    def do_transfer(self):
        res =  super(product_expense_picking,self).do_transfer()
        if res:
            expense = self.env['product.expense'].search([('ref_no','=',self.id)])
            if expense:
                workflow.trg_validate(self.env.user.id,'product.expense',expense.id,'ship_end',self.env.cr)
        return res 
