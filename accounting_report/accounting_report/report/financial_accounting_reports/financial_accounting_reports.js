// Copyright (c) 2024, Bytepanda technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Financial Accounting Reports"] = {
  initial_depth: 0,
  name_field: "ledger_code",
  parent_field: "group",
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      width: "80",
      reqd: 1,
      default: frappe.datetime.year_start(),
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      width: "80",
      reqd: 1,
      default: frappe.datetime.year_end(),
    },
    {
      fieldname: "report",
      label: __("Report"),
      fieldtype: "Select",
      options: ["Profit and Loss Statement", "Balance Sheet", "Cash Flow"],
      default: "Balance Sheet",
      reqd: 1,
    },
  ],
};
