# Copyright (c) 2025, Dhwani RIS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PCATSubmission(Document):
	def on_trash(self):
		"""Remove corresponding LMS Quiz Submission when PCAT Submission is deleted"""
		try:
			# Find the LMS Quiz Submission that was marked as PCAT for this user and quiz
			lms_submission = frappe.db.get_value(
				"LMS Quiz Submission",
				{
					"quiz": self.quiz,
					"member": self.user,
					"custom_is_pcat_submission": 1
				},
				"name"
			)
			
			print(lms_submission)
			if lms_submission:
				# Delete the LMS Quiz Submission
				frappe.delete_doc("LMS Quiz Submission", lms_submission, ignore_permissions=True)
				frappe.log_error(f"Corresponding LMS Quiz Submission {lms_submission} has been deleted.")
				
		except Exception as e:
			frappe.log_error(f"Error deleting LMS Quiz Submission for PCAT Submission {self.name}: {str(e)}")
			frappe.msgprint("Warning: Could not delete corresponding LMS Quiz Submission.", indicator="orange")

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
