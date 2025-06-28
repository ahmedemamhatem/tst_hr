frappe.pages['leave-calendar'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Leave Calendar by Month',
        single_column: true
    });

    page.add_action_icon(
        'refresh',
        ()=>{
            load_calendar();
        }
    )

    // Create filters
    page.add_field({
        label: 'Designation',
        fieldtype: 'Link',
        fieldname: 'designation',
        options: 'Designation',
        change() {
            load_calendar();
        }
    });

    page.add_field({
        label: 'Department',
        fieldtype: 'Link',
        fieldname: 'department',
        options: 'Department',
        change() {
            load_calendar();
        }
    });

    // Placeholder for calendar
    const calendar_container = $('<div id="calendar" class="mt-4"></div>').appendTo(page.body);

    function load_calendar() {
        department = page.fields_dict.department.get_value();
        designation = page.fields_dict.designation.get_value();

        console.log(department)
        console.log(designation)
        frappe.call({
            method: 'tst_hr.tst_hr.page.leave_calendar.leave_calendar.get_monthly_leave_summary',
            args: {
                "department":department,
                "designation":designation
            },
            callback: function(r) {
                if (r.message) {
                    render_calendar(r.message);
                }
            }
        });
    }

    function render_calendar(data) {
        calendar_container.empty();

        const colors = {
            'none': '#b6fcb6',       // green
            'one': '#fffab3',        // yellow
            'multiple': '#ffb3b3'    // red
        };

        const month_names = [
            'January', 'February', 'March', 'April',
            'May', 'June', 'July', 'August',
            'September', 'October', 'November', 'December'
        ];

        for (let i = 0; i < 12; i++) {
            const count = data[i + 1] || 0;
            let status = 'none';
            if (count === 1) status = 'one';
            else if (count > 1) status = 'multiple';

            const box = $(`
                <div style="
                    display: inline-block;
                    width: 150px;
                    height: 100px;
                    margin: 10px;
                    text-align: center;
                    background: ${colors[status]};
                    border-radius: 8px;
                    box-shadow: 0 2px 6px #ccc;
                ">
                    <div style="margin-top: 35px;">
                        <strong>${month_names[i]}</strong><br>
                        (${count} approved)
                    </div>
                </div>
            `);

            calendar_container.append(box);
        }
    }
};
