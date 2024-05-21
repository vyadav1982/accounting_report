# Copyright (c) 2024, Bytepanda technologies and contributors
# For license information, please see license.txt

from datetime import datetime
import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []

    if not filters:
        return columns, data

    return get_columns_data(filters)


def get_columns_data(filters):
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
                }
            ]
        )

        ledgers = frappe.db.get_all(
            "Trial Balance Child",
            filters=[{"parent": tb.name}],
            fields=["ledger_code", "ledger_name", "balance"],
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
        chart_liabilties.append(liabilities)
        chart_retained.append(assets + liabilities)

    message = None

    chart = {
        "data": {
            "labels": chart_labels,
            "datasets": [
                {"name": "Assets", "values": chart_assets, "chartType": "bar"},
                {"name": "Liability", "values": chart_liabilties, "chartType": "bar"},
                {"name": "retained", "values": chart_retained, "chartType": "bar"},
            ],
        },
        "type": "bar",
    }

    report_summary = [
        {
            "label": "Retained Earning",
            "value": f"{chart_retained[-1]:,.2f}" if len(chart_retained) else "--",
            "indicator": "Red" if chart_retained[-1] < 0 else "Green",
        }
    ]

    return columns, data, message, chart, report_summary
