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

{
   "name":"Product Expense",
<<<<<<< HEAD
   "version":"2.0",
=======
>>>>>>> f619c586ca39770e321e0c9d06b854b7bb97e785
   "author":"Kevin Kong",
   "description":"",
   "depends":["base","hr","hr_expense"],
   "data":[
	   "security/product_expense_security.xml",
	   "security/ir.model.access.csv",
	   "product_expense_view.xml",
	   "product_expense_data.xml",
	   "product_expense_workflow.xml",
	   "department_account_view.xml",
	   ],
   "installable":True,
   "category":"hr",
}
