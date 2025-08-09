import frappe
def on_submit(doc, method=None):
    """Hook to update Final Settlement when Salary Slip is submitted"""
    update_final_settlement(doc)

def update_final_settlement(doc):
    """
    Updates the Final Settlement document with the net pay from the Salary Slip
    
    Args:
        doc: The Salary Slip document
    """
    if not doc.payroll_entry:
        return  # Not created from payroll entry
    
    try:
        # Get payroll reference info
        payroll_reference = frappe.db.get_value(
            "Payroll Entry",
            doc.payroll_entry,
            ["custom_reference_doctype", "custom_reference_link"],
            as_dict=True
        )
        
        # Validate if created from Final Settlement
        if not (payroll_reference and 
               payroll_reference.get("custom_reference_doctype") == "Final Settlement" and
               payroll_reference.get("custom_reference_link")):
            return
            
        
        # update final settlement by net salary
        frappe.db.sql("""
                    update `tabFinal Settlement` set net_salary = %(net_salary)s where name = %(document_id)s
                      """,{
                          "net_salary":doc.net_pay,
                          "document_id":payroll_reference["custom_reference_link"]
                      })
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(
            title="Failed to update Final Settlement",
            message=f"Error updating Final Settlement from Salary Slip {doc.name}\n{str(e)}"
        )
        raise