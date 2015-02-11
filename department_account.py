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

from openerp import fields,api,_,models

class department_account(models.Model):
    _name="product.expense.account"

    name=fields.Char('Name',required=True)
    department = fields.Many2one('hr.department','Department',required=True)
    line_ids = fields.One2many('product.expense.account.line','account_id','Lines')

class department_account_line(models.Model):
    _name='product.expense.account.line'

    account_id = fields.Many2one('product.expense.account')
    product_category = fields.Many2one('product.category','Product Category')
    in_account = fields.Many2one('account.account','In Account')
    out_account = fields.Many2one('account.account','Out Account')
