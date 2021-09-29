# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "Bbt Bpm",
			"color": "grey",
			"icon": "octicon octicon-file-directory",
			"type": "module",
			"label": _("Bbt Bpm"),
			"onboard_present": 1
		},
		{
            "type": "Page",
            "icon": "octicon octicon-file-directory",
            "name": "customer_portal",
            "label": _("Customer Portal"),
            "onboard": 1,
            'link':'/desk#home'
        }
	]
