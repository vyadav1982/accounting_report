# Copyright (c) 2024, Bytepanda technologies and contributors
# For license information, please see license.txt

from datetime import datetime
import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []

    if not filters:
        return columns, data

    if filters.get("report") == "Balance Sheet":
        return get_bs_report(filters)
    elif filters.get("report") == "Profit and Loss Statement":
        return get_pnl_report(filters)
    else:
        return get_cash_flow_report(filters)


def get_pnl_report(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    columns = [
        {
            "label": _("Group"),
            "fieldname": "group",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": _("Ledger Code"),
            "fieldname": "ledger_code",
            "fieldtype": "Link",
            "options": "Trial Balance Ledgers",
            "width": 180,
        },
        {
            "label": _("Ledger Name"),
            "fieldname": "ledger_name",
            "fieldtype": "Data",
            "width": 260,
        },
    ]

    if from_date is not None:
        from_date = datetime.strptime(from_date, "%Y-%m-%d")
    if to_date is not None:
        to_date = datetime.strptime(to_date, "%Y-%m-%d")

    datafilters = [
        {"trial_balance_date": [">=", from_date]},
        {"trial_balance_date": ["<=", to_date]},
    ]

    tbs = frappe.db.get_all(
        "Trial Balance",
        filters=datafilters,
        fields=["name", "trial_balance_date", "upload_date"],
        order_by="trial_balance_date",
    )

    data = []

    all_ledgers = frappe.db.get_all(
        "Trial Balance Ledgers",
        fields=["ledger_code", "ledger_name", "group"],
        filters=[["group", "in", ["Revenue", "Expense"]]],
        order_by="ledger_code",
    )

    data.extend(
        [
            {"group": "Revenue", "indent": 0},
        ]
    )

    for ledger in all_ledgers:
        if ledger.group == "Revenue":
            data.append(
                {
                    "ledger_code": ledger.ledger_code,
                    "ledger_name": ledger.ledger_name,
                    "group": ledger.group,
                    "indent": 1,
                }
            )

    data.extend(
        [
            {"group": "Expense", "indent": 0},
        ]
    )

    for ledger in all_ledgers:
        if ledger.group == "Expense":
            data.append(
                {
                    "ledger_code": ledger.ledger_code,
                    "ledger_name": ledger.ledger_name,
                    "group": ledger.group,
                    "indent": 1,
                }
            )
    data.extend(
        [
            {"group": "Profit/Loss", "indent": 0},
        ]
    )

    chart_labels = []
    chart_revenue = []
    chart_expense = []
    chart_pnl = []

    for tb in tbs:
        chart_labels.append(tb.trial_balance_date.strftime("%d-%m-%Y"))
        columns.extend(
            [
                {
                    "label": tb.trial_balance_date,
                    "fieldname": tb.trial_balance_date.strftime("%d-%m-%Y"),
                    "fieldtype": "Float",
                    "width": 180,
                    "precision": "0",
                }
            ]
        )

        ledgers = frappe.db.get_all(
            "Trial Balance Child",
            filters=[{"parent": tb.name}],
            fields=["ledger_code", "balance"],
            order_by="ledger_code",
        )
        tbdate = tb.trial_balance_date.strftime("%d-%m-%Y")

        revenue = 0.0
        expense = 0.0

        for ledger in ledgers:
            old_data = [a for a in data if a.get("ledger_code") == ledger.ledger_code]
            if len(old_data) > 0:
                old_data[0][tbdate] = ledger.balance

                if old_data[0]["group"] == "Revenue":
                    revenue += ledger.balance
                else:
                    expense += ledger.balance

        old_data = [
            a for a in data if a["group"] == "Revenue" and a.get("ledger_code") is None
        ]
        old_data[0][tbdate] = -revenue
        chart_revenue.append(-revenue)
        old_data = [
            a for a in data if a["group"] == "Expense" and a.get("ledger_code") is None
        ]
        old_data[0][tbdate] = -expense
        old_data = [
            a
            for a in data
            if a["group"] == "Profit/Loss" and a.get("ledger_code") is None
        ]
        old_data[0][tbdate] = -revenue - expense
        chart_expense.append(-expense)
        chart_pnl.append(-revenue - expense)

    message = None

    chart = {
        "data": {
            "labels": chart_labels,
            "datasets": [
                {
                    "name": "Revenue",
                    "values": [int(v) for v in chart_revenue],
                    "chartType": "bar",
                },
                {
                    "name": "Expense",
                    "values": [int(v) for v in chart_expense],
                    "chartType": "bar",
                },
                {
                    "name": "Profit/Loss",
                    "values": [int(v) for v in chart_pnl],
                    "chartType": "line",
                },
            ],
        },
        "type": "axis-mixed",
    }

    report_summary = [
        {
            "label": "Duration Profit/Loss",
            "value": f"{sum(chart_pnl):,.0f}" if len(chart_pnl) else "--",
            "indicator": "Red" if chart_pnl[-1] < 0 else "Green",
        }
    ]

    return columns, data, message, chart, report_summary, True


def get_bs_report(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    columns = [
        {
            "label": _("Group"),
            "fieldname": "group",
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "label": _("Ledger Code"),
            "fieldname": "ledger_code",
            "fieldtype": "Link",
            "options": "Trial Balance Ledgers",
            "width": 180,
        },
        {
            "label": _("Ledger Name"),
            "fieldname": "ledger_name",
            "fieldtype": "Data",
            "width": 260,
        },
    ]

    if from_date is not None:
        from_date = datetime.strptime(from_date, "%Y-%m-%d")
    if to_date is not None:
        to_date = datetime.strptime(to_date, "%Y-%m-%d")

    datafilters = [
        {"trial_balance_date": [">=", from_date]},
        {"trial_balance_date": ["<=", to_date]},
    ]

    tbs = frappe.db.get_all(
        "Trial Balance",
        filters=datafilters,
        fields=["name", "trial_balance_date", "upload_date"],
        order_by="trial_balance_date",
    )

    data = []

    all_ledgers = frappe.db.get_all(
        "Trial Balance Ledgers",
        fields=["ledger_code", "ledger_name", "group"],
        filters=[["group", "in", ["Asset", "Liability"]]],
        order_by="ledger_code",
    )

    data.extend(
        [
            {"group": "Asset", "indent": 0},
        ]
    )

    for ledger in all_ledgers:
        if ledger.group == "Asset":
            data.append(
                {
                    "ledger_code": ledger.ledger_code,
                    "ledger_name": ledger.ledger_name,
                    "group": ledger.group,
                    "indent": 1,
                }
            )

    data.extend(
        [
            {"group": "Liability", "indent": 0},
        ]
    )

    for ledger in all_ledgers:
        if ledger.group == "Liability":
            data.append(
                {
                    "ledger_code": ledger.ledger_code,
                    "ledger_name": ledger.ledger_name,
                    "group": ledger.group,
                    "indent": 1,
                }
            )

    data.extend(
        [
            {"group": "Retained Earnings", "indent": 0},
        ]
    )

    chart_labels = []
    chart_assets = []
    chart_liabilties = []
    chart_retained = []
    for tb in tbs:
        chart_labels.append(tb.trial_balance_date.strftime("%d-%m-%Y"))
        columns.extend(
            [
                {
                    "label": tb.trial_balance_date,
                    "fieldname": tb.trial_balance_date.strftime("%d-%m-%Y"),
                    "fieldtype": "Float",
                    "width": 180,
                    "precision": "0",
                }
            ]
        )

        ledgers = frappe.db.get_all(
            "Trial Balance Child",
            filters=[{"parent": tb.name}],
            fields=["ledger_code", "balance"],
            order_by="ledger_code",
        )
        tbdate = tb.trial_balance_date.strftime("%d-%m-%Y")

        assets = 0.0
        liabilities = 0.0

        for ledger in ledgers:
            old_data = [a for a in data if a.get("ledger_code") == ledger.ledger_code]
            if len(old_data) > 0:
                old_data[0][tbdate] = ledger.balance

                if old_data[0]["group"] == "Asset":
                    assets += ledger.balance
                else:
                    liabilities += ledger.balance

        old_data = [
            a for a in data if a["group"] == "Asset" and a.get("ledger_code") is None
        ]
        old_data[0][tbdate] = assets
        chart_assets.append(assets)
        old_data = [
            a
            for a in data
            if a["group"] == "Liability" and a.get("ledger_code") is None
        ]
        old_data[0][tbdate] = liabilities
        old_data = [
            a
            for a in data
            if a["group"] == "Retained Earnings" and a.get("ledger_code") is None
        ]
        old_data[0][tbdate] = assets + liabilities
        chart_liabilties.append(liabilities)
        chart_retained.append(assets + liabilities)

    message = None

    chart = {
        "data": {
            "labels": chart_labels,
            "datasets": [
                {
                    "name": "Assets",
                    "values": [int(v) for v in chart_assets],
                    "chartType": "bar",
                },
                {
                    "name": "Liability",
                    "values": [int(v) for v in chart_liabilties],
                    "chartType": "bar",
                },
                {
                    "name": "retained",
                    "values": [int(v) for v in chart_retained],
                    "chartType": "bar",
                },
            ],
        },
        "type": "bar",
    }

    report_summary = [
        {
            "label": "Retained Earning",
            "value": f"{chart_retained[-1]:,.0f}" if len(chart_retained) else "--",
            "indicator": "Red" if chart_retained[-1] < 0 else "Green",
        }
    ]

    return columns, data, message, chart, report_summary


def get_cash_flow_report(filters):
    return [], []
