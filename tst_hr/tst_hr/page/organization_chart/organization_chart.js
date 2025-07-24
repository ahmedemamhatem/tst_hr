// Enhanced Organization Chart Dashboard in Frappe
frappe.pages['organization-chart'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Organization Chart"),
        single_column: true
    });

    // Chart Container
    $('<div id="chartdiv" style="width:100vw;max-width:100%;height:calc(85vh - 35px);min-height:400px;margin-top:20px;background:#f8fafc;border-radius:14px;box-shadow:0 4px 24px rgba(44,62,80,0.07);overflow:auto;padding:10px"></div>')
        .appendTo(page.body);

    // Filters
    let department_filter = page.add_field({ label: __("Department"), fieldtype: "Link", fieldname: "department", options: "Department", change: fetch_and_render_chart });
    let branch_filter = page.add_field({ label: __("Branch"), fieldtype: "Link", fieldname: "branch", options: "Branch", change: fetch_and_render_chart });
    let section_filter = page.add_field({ label: __("Section"), fieldtype: "Link", fieldname: "section", options: "Section", change: fetch_and_render_chart });
    let company_filter = page.add_field({ label: __("Company"), fieldtype: "Link", fieldname: "company", options: "Company", change: fetch_and_render_chart });
    let chart_type_filter = page.add_field({
        label: __("Chart Type"),
        fieldtype: "Select",
        fieldname: "chart_type",
        options: [
            { label: "Horizontal Partition", value: "partition" },
            { label: "Tree Chart", value: "tree" },
            { label: "Sunburst Flavor Wheel", value: "sunburst" }
        ],
        default: "partition",
        change: fetch_and_render_chart
    });



    function load_amcharts(callback) {
        if (window.am5 && window.am5hierarchy && window.am5themes_Animated) return callback();
        let base = "https://cdn.amcharts.com/lib/5/";
        let scripts = ["index.js", "hierarchy.js", "themes/Animated.js"].map(f => base + f);
        let loaded = 0;
        scripts.forEach(src => {
            let s = document.createElement('script');
            s.src = src;
            s.onload = () => { if (++loaded === scripts.length) callback(); };
            document.body.appendChild(s);
        });
    }

    function add_default_values(node) {
        if (node.children?.length) {
            node.children.forEach(add_default_values);
            if (node.value === undefined) {
                node.value = node.children.reduce((sum, c) => sum + (c.value || 0), 0);
            }
        } else if (node.value === undefined) {
            node.value = 1;
        }
    }

    function assign_tree_colors(node, palette, depth = 0, branchIndex = 0, shade = 0) {
        if (!node) return;
        if (depth === 0) {
            node.nodeColor = 0xcccccc;
            node.children?.forEach((child, i) => assign_tree_colors(child, palette, 1, i, 0));
        } else if (depth === 1) {
            let color = palette[branchIndex % palette.length];
            node.nodeColor = color;
            node.children?.forEach(child => assign_tree_colors(child, palette, depth + 1, branchIndex, 1));
        } else {
            let baseColor = palette[branchIndex % palette.length];
            node.nodeColor = shadeColor(baseColor, -10 * shade);
            node.children?.forEach(child => assign_tree_colors(child, palette, depth + 1, branchIndex, shade + 1));
        }
    }

    function shadeColor(color, percent) {
        var R = (color >> 16) & 0xFF, G = (color >> 8) & 0xFF, B = color & 0xFF;
        R = Math.min(255, parseInt(R * (100 + percent) / 100));
        G = Math.min(255, parseInt(G * (100 + percent) / 100));
        B = Math.min(255, parseInt(B * (100 + percent) / 100));
        return (R << 16) + (G << 8) + B;
    }

    function get_text_width(text, font) {
        let canvas = get_text_width.canvas || (get_text_width.canvas = document.createElement("canvas"));
        let context = canvas.getContext("2d");
        context.font = font || "bold 15px Inter, Arial,sans-serif";
        return context.measureText(text).width;
    }

    function render_chart(data, chart_type) {
        if (window.am5chart_root) {
            window.am5chart_root.dispose();
        }
        let el = document.getElementById('chartdiv');
        if (!el) return frappe.msgprint("Chart container not found!");

        let root = am5.Root.new(el);
        window.am5chart_root = root;
        root.setThemes([am5themes_Animated.new(root)]);

        let flavorPalette = [0xf94144, 0xf3722c, 0xf8961e, 0xf9844a, 0xf9c74f, 0x90be6d, 0x43aa8b, 0x577590, 0x277da1];
        let colorSet = am5.ColorSet.new(root, { colors: flavorPalette.map(c => am5.color(c)), reuse: true });

        let series;

        if (chart_type === "partition") {
            series = root.container.children.push(am5hierarchy.Partition.new(root, {
                orientation: "horizontal", singleBranchOnly: false, downDepth: 10, initialDepth: 10,
                valueField: "value", categoryField: "name", childDataField: "children",
                nodePaddingOuter: 12, nodePaddingInner: 7, minNodeSize: 26, maxNodeSize: 56, sort: "none",
                colorSet: colorSet
            }));
            series.labels.template.setAll({ fontSize: 15, fontWeight: "600", fill: am5.color(0x273447), oversizedBehavior: "wrap", textAlign: "center" });

        } else if (chart_type === "tree") {
            assign_tree_colors(data, flavorPalette);
            series = root.container.children.push(am5hierarchy.Tree.new(root, {
                orientation: "vertical", singleBranchOnly: false, downDepth: 10, initialDepth: 10,
                valueField: "value", categoryField: "name", childDataField: "children",
                nodePaddingOuter: 15, nodePaddingInner: 8, sort: "none"
            }));
            series.circles.template.adapters.add("fill", (fill, target) => am5.color(target.dataItem?.dataContext?.nodeColor || 0xcccccc));
            series.labels.template.adapters.add("fill", (fill, target) => {
                let c = target.dataItem?.dataContext?.nodeColor || 0xffffff;
                let r = (c >> 16) & 0xff, g = (c >> 8) & 0xff, b = c & 0xff;
                return (0.299 * r + 0.587 * g + 0.114 * b) < 140 ? am5.color(0xffffff) : am5.color(0x273447);
            });
            series.circles.template.adapters.add("radius", function(radius, target) {
                let di = target.dataItem;
                if (!di || !di.dataContext || !di.dataContext.name) return 32;
                let d = di.dataContext;
                let indicator = (d.children && d.children.length ? " 🔽" : "");
                let fullText = d.name + indicator;
                let textWidth = get_text_width(fullText, "bold 15px Inter, Arial,sans-serif");
                let radiusFromText = (textWidth / 2) + 16;
                return Math.max(36, Math.min(80, radiusFromText));
            });
            series.labels.template.adapters.add("fontSize", function(fontSize, target) {
                let di = target.dataItem;
                if (!di || !di.dataContext) return fontSize;
                let name = di.dataContext.name;
                if (name.length > 25) return 10;
                if (name.length > 18) return 12;
                return 15;
            });
        } else if (chart_type === "sunburst") {
            series = root.container.children.push(am5hierarchy.Sunburst.new(root, {
                singleBranchOnly: false, downDepth: 10, initialDepth: 10, valueField: "value", categoryField: "name",
                childDataField: "children", innerRadius: am5.percent(18), radius: am5.percent(98), sort: "none",
                colorSet: colorSet
            }));
        } else {
            return frappe.msgprint("Unknown chart type.");
        }

        series.set("tooltipText", "{name}");
        series.labels.template.adapters.add("text", (text, target) => {
            let d = target.dataItem?.dataContext;
            return d?.name ? d.name + (d.children?.length ? " 🔽" : "") : "";
        });

        add_default_values(data);
        series.data.setAll([data]);
        series.set("selectedDataItem", series.dataItems[0]);
        series.appear(900, 100);
    }

    function fetch_and_render_chart() {
        load_amcharts(() => {
            frappe.call({
                method: "tst_hr.tst_hr.page.organization_chart.organization_chart.get_organization_tree",
                args: {
                    department: department_filter.get_value(),
                    branch: branch_filter.get_value(),
                    section: section_filter.get_value(),
                    company: company_filter.get_value()
                },
                callback: function (r) {
                    let data = r.message || {};
                    render_chart(data, chart_type_filter.get_value() || "partition");
                }
            });
        });
    }

    fetch_and_render_chart();
};
