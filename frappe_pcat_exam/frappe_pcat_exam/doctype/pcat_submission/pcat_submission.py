# Copyright (c) 2025, Dhwani RIS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PCATSubmission(Document):
	pass

def get_permission_query_conditions(user):
    """Return permission query conditions for PCAT Submission"""
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    # Users can only see their own submissions
    return f"`tabPCAT Submission`.user = '{user}'"

def has_permission(doc, ptype, user):
    """Check if user has permission for PCAT Submission"""
    if not user:
        user = frappe.session.user
    
    if "System Manager" in frappe.get_roles(user):
        return True
    
    # Users can only access their own submissions
    if doc.user == user:
        return True
    
    return False
