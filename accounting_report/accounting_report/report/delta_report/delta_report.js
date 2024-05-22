// Copyright (c) 2024, Bytepanda technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Delta Report"] = {
  initial_depth: 0,
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
  ],
};
