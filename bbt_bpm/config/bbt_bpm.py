from __future__ import unicode_literals
from frappe import _

def get_data():
    return [
        {
            "label": _("Customer Portal"),
            "icon": "octicon octicon-briefcase",
            "items": [
                {
                    "type": "page",
                    "name": "home",
                    "label": _("Customer Portal"),
                    "onboard": 1
                }
            ]
        }
        
    ]