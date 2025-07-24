import frappe
from datetime import datetime,date, timedelta
from frappe import _ 

@frappe.whitelist()
def daily():
    send_insurance_expiry_report()
    send_iqama_expiry_report()
    """Scheduled job to send reminder emails for sponsorship transfer and probation/confirmation."""
    send_email()
    
def send_email():
    # get email setting for (sponsorship transfer), (Probation and Confirmation Schedule)
    sponsorship_transfer_schedule = get_schedule("sponsorship_transfer_schedule")
    probation_and_confirmation_schedule = get_schedule("probation_and_confirmation_schedule")
    # get users to send email for 
    users,sent_to_employee_manager = get_recipients()
    
    if sponsorship_transfer_schedule:
        employees = get_employees(sponsorship_transfer_schedule,"custom_sponsorship_transfer")
        if employees:
            send_bulk_employee_emails(employees,users,sent_to_employee_manager,"sponsorship_transfer")
    if probation_and_confirmation_schedule:
        employees = get_employees(probation_and_confirmation_schedule,"custom_probation_and_confirmation_period")
        if employees:
            send_bulk_employee_emails(employees,users,sent_to_employee_manager,"probation_and_confirmation_period")
        



def get_schedule(parent_field):
    return frappe.db.sql("""
                        select 
                            send_after_days,
                            have_extension
                        from
                            `tabEmail Schedule` 
                        where 
                            parentfield = %s
                        and 
                            parenttype = "Email Settings"
                        order by send_after_days asc
                            """,parent_field,as_dict = True)
    
    
def get_employees(schedule, field):
    employees_data = []
    for row in schedule:
        query = f"""
            SELECT 
                name,
                first_name,
                reports_to,
                %(have_extension)s AS have_extension
            FROM
                `tabEmployee` 
            WHERE 
                `{field}` NOT IN ('No', 'Yes', 'Confirmed', 'Not Confirmed')
                AND DATEDIFF(CURDATE(), date_of_joining) = %(no_days)s
        """

        employees = frappe.db.sql(
            query,
            {
                "have_extension": row.have_extension,
                "no_days": int(row.send_after_days)
            },
            as_dict=True
        )

        if employees:
            employees_data.extend(employees)

    return employees_data

def get_recipients():
    users = frappe.db.sql(
        """
        SELECT 
            u.name
        FROM 
            `tabUser` u
        JOIN 
            `tabHas Role` r ON r.parent = u.name
        WHERE 
            r.role IN (
                SELECT 
                    role
                FROM 
                    `tabEmail Recipient Role`
                WHERE 
                    parenttype = "Email Settings"
                    AND parentfield = "email_recipient_role"
            ) 
        """)
    
    # Extract just the usernames from the result
    if users:
        users = [user[0] for user in users]
    else:
        users = []

    # Get whether to send mail to employee's manager
    sent_to_employee_manager = frappe.db.get_single_value("Email Settings", "employee_manager")
    
    return users, sent_to_employee_manager

        
def send_bulk_employee_emails(employees,users,sent_to_employee_manager,type):
    if type == "sponsorship_transfer":
        for employee in employees:
            if sent_to_employee_manager and employee.reports_to:
                reports_to_user = frappe.get_cached_value("Employee",{"name":employee.reports_to},"user_id")
                if reports_to_user:
                    users.append(reports_to_user)
            send_email_sponsorship_transfer_to_hr(employee.name,employee.first_name,users,employee.have_extension)
            
    if type == "probation_and_confirmation_period":
        for employee in employees:
            if sent_to_employee_manager and employee.reports_to:
                reports_to_user = frappe.get_cached_value("Employee",{"name":employee.reports_to},"user_id")
                if reports_to_user:
                    users.append(reports_to_user)
            send_email_probation_and_confirmation_period_to_hr(employee.name,employee.first_name,users,employee.have_extension)
            
        
        
def send_email_probation_and_confirmation_period_to_hr(employee_id, employee_name,recipients, include_extend_option=True):
    base_url = frappe.utils.get_url()

    subject = f" برجاء مراجعه مدير الموظف {employee_name}"

    # yes_link = f"{base_url}/api/method/tst_hr.tasks.confirmation_response?employee_id={employee_id}&response=Confirmed"
    # no_link = f"{base_url}/api/method/tst_hr.tasks.confirmation_response?employee_id={employee_id}&response=Not Confirmed"

    message = f"""

    برجاء مراجعه مدير الموظف  **{employee_name}**:

    """
    # <ul>
    #   <li><a href="{yes_link}">✔️ تثبيت الموظف</a></li>
    #   <li><a href="{no_link}">❌ عدم التثبيت</a></li>

    # if include_extend_option:
    #     extend_link = f"{base_url}/api/method/tst_hr.tasks.confirmation_response?employee_id={employee_id}&response=180 Days"
    #     message += f'<li><a href="{extend_link}">🔁 180 طلب تمديد</a></li>'

    # message += "</ul>"

    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message
    )
    
def send_email_sponsorship_transfer_to_hr(employee_id, employee_name, recipients,include_extend_option=True):
    base_url = frappe.utils.get_url()

    subject = f" توصيه في نقل كفاله الموظف – {employee_name}"

    yes_link = f"{base_url}/api/method/tst_hr.tasks.handle_kafala_response?employee_id={employee_id}&response=Yes"
    no_link = f"{base_url}/api/method/tst_hr.tasks.handle_kafala_response?employee_id={employee_id}&response=No"

    message = f"""

    توصيه في نقل كفاله الموظف **{employee_name}**:

    <ul>
      <li><a href="{yes_link}">✔️ نعم</a></li>
      <li><a href="{no_link}">❌ لا</a></li>
    """

    if include_extend_option:
        extend_link = f"{base_url}/api/method/tst_hr.tasks.handle_kafala_response?employee_id={employee_id}&response=Request Extension"
        message += f'<li><a href="{extend_link}">🔁 طلب تمديد</a></li>'

    message += "</ul>"

    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message
    )
    
@frappe.whitelist(allow_guest=True)
def confirmation_response(employee_id, response):
    if not employee_id or not response:
        frappe.throw(_("Missing employee or response"))

    # Update recommendation status in Employee
    frappe.db.set_value("Employee", employee_id, "custom_probation_and_confirmation_period", response)
    frappe.db.commit()

    return f"Thank you! Your response '{response}' has been recorded for employee {employee_id}."

@frappe.whitelist(allow_guest=True)
def handle_kafala_response(employee_id, response):
    if not employee_id or not response:
        frappe.throw(_("Missing employee or response"))

    # Update recommendation status in Employee
    frappe.db.set_value("Employee", employee_id, "custom_sponsorship_transfer", response)
    frappe.db.commit()

    return f"Thank you! Your response '{response}' has been recorded for employee {employee_id}."



def send_iqama_expiry_report():
    # get users to send email for 
    users,sent_to_employee_manager = get_recipients()
    today = date.today()
    one_month_later = today + timedelta(days=30)

    employees = frappe.db.get_all(
        "Employee",
        filters={
            "status": "Active",
            "custom_iqama_expiry_date": ["between", [today, one_month_later]]
        },
        fields=[
            "employee_name",
            "custom_iqama_number",
            "designation",
            "department",
            "custom_renewal_type",
            "custom_sponsor",
            "custom_iqama_expiry_date"
        ],
        order_by="custom_iqama_expiry_date asc"
    )

    if not employees:
        return

    # Build HTML table
    html = """
        <h3>Employees with Iqama Expiry Within 30 Days</h3>
        <table border="1" cellspacing="0" cellpadding="5">
            <tr>
                <th>Employee Name</th>
                <th>Iqama No</th>
                <th>Renewal Type</th>
                <th>Sponsorship</th>
                <th>Iqama Expiry Date</th>
            </tr>
    """

    for emp in employees:
        html += f"""
            <tr>
                <td>{emp.employee_name}</td>
                <td>{emp.custom_iqama_number or ''}</td>
                <td>{emp.custom_renewal_type or ''}</td>
                <td>{emp.custom_sponsorship or ''}</td>
                <td>{emp.custom_iqama_expiry_date}</td>
            </tr>
        """

    html += "</table>"

    # Send email
    frappe.sendmail(
        recipients=users,
        subject="Iqama Expiry Report",
        message=html
    )
    
def send_insurance_expiry_report():
    # get users to send email for 
    users,sent_to_employee_manager = get_recipients()
    today = date.today()
    one_month_later = today + timedelta(days=30)

    employees = frappe.db.get_all(
        "Employee",
        filters={
            "status": "Active",
            "custom_expiry_date": ["between", [today, one_month_later]]
        },
        fields=[
            "employee_name",
            "custom_iqama_number",
            "custom_expiry_date"
        ],
        order_by="custom_expiry_date asc"
    )

    if not employees:
        return

    # Build HTML table
    html = """
        <h3>Employees with Insurance Expiry Within 30 Days</h3>
        <table border="1" cellspacing="0" cellpadding="5">
            <tr>
                <th>Employee Name</th>
                <th>Iqama No</th>
                <th>Insurance Expiry Date</th>
            </tr>
    """

    for emp in employees:
        html += f"""
            <tr>
                <td>{emp.employee_name}</td>
                <td>{emp.custom_iqama_number or ''}</td>
                <td>{emp.custom_expiry_date}</td>
            </tr>
        """

    html += "</table>"

    # Send email
    frappe.sendmail(
        recipients=users,
        subject="Insurance Expiry Report",
        message=html
    )
    
    
