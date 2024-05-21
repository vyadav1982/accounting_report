// Copyright (c) 2024, Bytepanda technologies and contributors
// For license information, please see license.txt

frappe.query_reports["Custom PnL Report"] = {
  initial_depth: 0,
  filters: [
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      width: "80",
      reqd: 1,
      default: frappe.datetime.add_days(frappe.datetime.get_today(), -90),
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      width: "80",
      reqd: 1,
      default: frappe.datetime.get_today(),
    },
  ],
};
