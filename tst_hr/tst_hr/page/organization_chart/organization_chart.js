frappe.pages["organization-chart"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Organizational Chart"),
		single_column: true,
	});

	const department_filter = page.add_field({
		label: "Department",
		fieldname: "department",
		fieldtype: "Link",
		options: "Department",
		change() {
			render_chart();
		}
	});

	const branch_filter = page.add_field({
		label: "Branch",
		fieldname: "branch",
		fieldtype: "Link",
		options: "Branch",
		change() {
			render_chart();
		}
	});

	const section_filter = page.add_field({
		label: "Section",
		fieldname: "section",
		fieldtype: "Link",
		options: "Sections",
		change() {
			render_chart();
		}
	});

	let organizational_chart;

	$(wrapper).bind("show", () => {
		frappe.require("hierarchy-chart.bundle.js", () => {
			const method = "tst_hr.tst_hr.page.organization_chart.organization_chart.get_children";

			if (frappe.is_mobile()) {
				organizational_chart = new hrms.HierarchyChartMobile("Employee", wrapper, method);
			} else {
				organizational_chart = new hrms.HierarchyChart("Employee", wrapper, method);
			}

			frappe.breadcrumbs.add("HR");
            organizational_chart.show();

			// Override show to add filters
			organizational_chart.show = function (filters = {}) {
				const args = {
					parent: "",
					company: frappe.defaults.get_user_default("company"),
					...filters
				};

				// Call frappe.call with your filters
				frappe.call({
					method: this.method,
					args: args,
					callback: (r) => {
						if (r.message) {
                            if (typeof this._draw === "function") {
                                this._draw(r.message);
                            } else if (typeof this.render === "function") {
                                this.render(r.message);
                            } else {
                                this.data = r.message; // Update internal data if possible
                                console.log("Organizational chart updated data:", r.message);
                                // Optionally try refreshing manually
                            }
                        }

					}
				});
                
			};

			// Expose render_chart globally
			window.render_chart = function () {
				const filters = {
					department: department_filter.get_value(),
					branch: branch_filter.get_value(),
					section: section_filter.get_value()
				};
				organizational_chart.show(filters);
			};

			// Initial load
			render_chart();
		});
	});
};
