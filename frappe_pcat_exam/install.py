import frappe
from frappe import _

def install():
    """Install the PCAT Exam app"""
    create_default_riasec_categories()
    create_default_answer_options()
    frappe.msgprint(_("PCAT Exam app installed successfully!"))

def create_default_riasec_categories():
    """Create default RIASEC categories if they don't exist"""
    categories = [
        {
            "category": "R",
            "description": "Realistic",
            "category_order": "1"
        },
        {
            "category": "I",
            "description": "Investigative",
            "category_order": "2"
        },
        {
            "category": "A",
            "description": "Artistic",
            "category_order": "3"
        },
        {
            "category": "S",
            "description": "Social",
            "category_order": "4"
        },
        {
            "category": "E",
            "description": "Enterprising",
            "category_order": "5"
        },
        {
            "category": "C",
            "description": "Conventional",
            "category_order": "6"
        }
    ]
    
    for category_data in categories:
        if not frappe.db.exists("PCAT Question Category", category_data["category"]):
            doc = frappe.new_doc("PCAT Question Category")
            doc.category = category_data["category"]
            doc.description = category_data["description"]
            doc.category_order = category_data["category_order"]
            doc.insert()
            frappe.msgprint(_(f"Created category: {category_data['category']}"))

def create_default_answer_options():
    """Create default RIASEC answer options if they don't exist"""
    options = [
        {"option": "Strongly Disagree", "value": 1},
        {"option": "Somewhat Disagree", "value": 2},
        {"option": "Somewhat Agree", "value": 4},
        {"option": "Strongly Agree", "value": 5}
    ]
    
    for option_data in options:
        if not frappe.db.exists("RIASEC Answer Options", {"option": option_data["option"]}):
            doc = frappe.new_doc("RIASEC Answer Options")
            doc.option = option_data["option"]
            doc.value = option_data["value"]
            doc.insert()
            frappe.msgprint(_(f"Created answer option: {option_data['option']}"))

def before_install():
    """Run before app installation"""
    pass

def after_install():
    """Run after app installation"""
    install()

def before_uninstall():
    """Run before app uninstallation"""
    pass

def after_uninstall():
    """Run after app uninstallation"""
    # Optionally clean up custom fields
    pass 