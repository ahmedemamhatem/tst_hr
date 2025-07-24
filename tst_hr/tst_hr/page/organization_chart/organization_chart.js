frappe.pages["organization-chart"].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Organizational Chart"),
        single_column: true,
    });

    let organizational_chart;

    $(wrapper).bind("show", () => {
        frappe.require("hierarchy-chart.bundle.js", () => {
            const method = "tst_hr.tst_hr.page.organization_chart.organization_chart.get_children";
            
            class SafeHierarchyChart extends hrms.HierarchyChart {
                render_node(node, parent_node) {
                    try {
                        if (!parent_node) {
                            parent_node = this.create_default_container();
                        }
                        return super.render_node(node, parent_node);
                    } catch (error) {
                        console.error("Error rendering node:", error);
                        return null;
                    }
                }
                
                create_default_container() {
                    const container = document.createElement('div');
                    container.className = 'org-chart-default-container';
                    this.container.appendChild(container);
                    return container;
                }
                
                show() {
                    this.setup_actions();
                    if (this.page.main.find('[data-fieldname="company"]').length) return;
                    
                    let me = this;
                    let filters = {};

                    // Company Filter
                    let company = this.page.add_field({
                        fieldtype: "Link",
                        options: "Company",
                        fieldname: "company",
                        placeholder: __("Select Company"),
                        default: frappe.defaults.get_default("company"),
                        reqd: 1,
                        change: () => {
                            me.company = company.get_value();
                            $("#hierarchy-chart-wrapper").remove();
                            if (me.company) {
                                me.make_svg_markers();
                                me.setup_hierarchy();
                                me.render_root_nodes();
                                me.all_nodes_expanded = false;
                            }
                        }
                    });

                    // Department Filter
                    let department = this.page.add_field({
                        label: "Department",
                        fieldname: "department",
                        fieldtype: "Link",
                        options: "Department",
                        only_select: true,
                        change: () => {
                            me.department = department.get_value();
                            $("#hierarchy-chart-wrapper").remove();
                            me.make_svg_markers();
                            me.setup_hierarchy();
                            me.render_root_nodes();
                            me.all_nodes_expanded = false;
                        }
                    });

                    // Designation Filter
                    let designation = this.page.add_field({
                        label: "Designation",
                        fieldname: "designation",
                        fieldtype: "Link",
                        options: "Designation",
                        only_select: true,
                        change: () => {
                            me.designation = designation.get_value();
                            $("#hierarchy-chart-wrapper").remove();
                            me.make_svg_markers();
                            me.setup_hierarchy();
                            me.render_root_nodes();
                            me.all_nodes_expanded = false;
                        }
                    });

                    // Branch Filter
                    let branch = this.page.add_field({
                        label: "Branch",
                        fieldname: "branch",
                        fieldtype: "Link",
                        options: "Branch",
                        only_select: true,
                        change: () => {
                            me.branch = branch.get_value();
                            $("#hierarchy-chart-wrapper").remove();
                            me.make_svg_markers();
                            me.setup_hierarchy();
                            me.render_root_nodes();
                            me.all_nodes_expanded = false;
                        }
                    });

                    // Style all filters consistently
                    $('[data-fieldname="company"], [data-fieldname="department"], [data-fieldname="designation"], [data-fieldname="branch"]')
                        .find('.control-input')
                        .css({
                            "position": "relative",
                            "z-index": 2
                        });

                    company.refresh();
                    department.refresh();
                    designation.refresh();
                    branch.refresh();

                    $(`[data-fieldname="company"]`).trigger("change");
					$(`[data-fieldname="company"]`).trigger("change");
					$(`[data-fieldname="company"] .link-field`).css("z-index", 1);
					$(`[data-fieldname="department"] .link-field`).css("z-index", 1);
					$(`[data-fieldname="branch"] .link-field`).css("z-index", 1);
					$(`[data-fieldname="designation"] .link-field`).css("z-index", 1);
                }
            }

            class SafeHierarchyChartMobile extends hrms.HierarchyChartMobile {
                render_node(node, parent_node) {
                    try {
                        if (!parent_node) {
                            parent_node = this.create_default_container();
                        }
                        return super.render_node(node, parent_node);
                    } catch (error) {
                        console.error("Mobile node error:", error);
                        return null;
                    }
                }
                
                create_default_container() {
                    const container = $('<div class="mobile-default-container"></div>');
                    this.$sibling_group.append(container);
                    return container[0];
                }
                
                show() {
                    if (this.page.main.find('[data-fieldname="company"]').length) return;
                    
                    let me = this;
                    let filters = {};

                    // Company Filter
                    let company = this.page.add_field({
                        fieldtype: "Link",
                        options: "Company",
                        fieldname: "company",
                        placeholder: __("Select Company"),
                        default: frappe.defaults.get_default("company"),
                        only_select: true,
                        reqd: 1,
                        change: () => {
                            me.company = company.get_value();
                            if (me.$sibling_group) me.$sibling_group.remove();
                            me.$sibling_group = $(`<div class="sibling-group mt-4 mb-4"></div>`);
                            me.page.main.append(me.$sibling_group);
                            me.make_svg_markers();
                            me.setup_hierarchy();
                            me.render_root_nodes();
                        }
                    });

                    // Department Filter
                    let department = this.page.add_field({
                        label: "Department",
                        fieldname: "department",
                        fieldtype: "Link",
                        options: "Department",
                        only_select: true,
                        change: () => {
                            me.department = department.get_value();
                            if (me.$sibling_group) me.$sibling_group.remove();
                            me.$sibling_group = $(`<div class="sibling-group mt-4 mb-4"></div>`);
                            me.page.main.append(me.$sibling_group);
                            me.make_svg_markers();
                            me.setup_hierarchy();
                            me.render_root_nodes();
                        }
                    });

                    // Designation Filter
                    let designation = this.page.add_field({
                        label: "Designation",
                        fieldname: "designation",
                        fieldtype: "Link",
                        options: "Designation",
                        only_select: true,
                        change: () => {
                            me.designation = designation.get_value();
                            if (me.$sibling_group) me.$sibling_group.remove();
                            me.$sibling_group = $(`<div class="sibling-group mt-4 mb-4"></div>`);
                            me.page.main.append(me.$sibling_group);
                            me.make_svg_markers();
                            me.setup_hierarchy();
                            me.render_root_nodes();
                        }
                    });

                    // Branch Filter
                    let branch = this.page.add_field({
                        label: "Branch",
                        fieldname: "branch",
                        fieldtype: "Link",
                        options: "Branch",
                        only_select: true,
                        change: () => {
                            me.branch = branch.get_value();
                            if (me.$sibling_group) me.$sibling_group.remove();
                            me.$sibling_group = $(`<div class="sibling-group mt-4 mb-4"></div>`);
                            me.page.main.append(me.$sibling_group);
                            me.make_svg_markers();
                            me.setup_hierarchy();
                            me.render_root_nodes();
                        }
                    });

                    company.refresh();
                    department.refresh();
                    designation.refresh();
                    branch.refresh();

                    $(`[data-fieldname="company"]`).trigger("change");
					$(`[data-fieldname="company"] .link-field`).css("z-index", 1);
					$(`[data-fieldname="department"] .link-field`).css("z-index", 1);
					$(`[data-fieldname="branch"] .link-field`).css("z-index", 1);
					$(`[data-fieldname="designation"] .link-field`).css("z-index", 1);
                }
            }

            if (frappe.is_mobile()) {
                organizational_chart = new SafeHierarchyChartMobile("Employee", wrapper, method);
            } else {
                organizational_chart = new SafeHierarchyChart("Employee", wrapper, method);
            }

            frappe.breadcrumbs.add("HR");
            organizational_chart.show();
        });
    });
};	