```python
import pandas as pd
from pathlib import Path

# ==================================================
# LOAD DATA
# ==================================================

DATA_FILE = Path("tickets.csv")

if not DATA_FILE.exists():
    raise FileNotFoundError(
        "tickets.csv was not found. "
        "Place the dataset in the same folder as auditor.py."
    )

tickets = pd.read_csv(DATA_FILE)

print("==============================================")
print("       VIREO SUPPORT POLICY AUDITOR")
print("==============================================")

print("\nTotal records:", len(tickets))
print("Unique ticket IDs:", tickets["ticket_id"].nunique())


# ==================================================
# 1. SLA AUDIT
# ==================================================

tickets["created_at"] = pd.to_datetime(
    tickets["created_at"],
    errors="coerce",
    utc=True
)

tickets["first_response_at"] = pd.to_datetime(
    tickets["first_response_at"],
    errors="coerce",
    utc=True
)

tickets["response_minutes"] = (
    tickets["first_response_at"]
    - tickets["created_at"]
).dt.total_seconds() / 60

sla_limits = {
    "chat": 15,
    "voice": 120,
    "social": 240,
    "email": 480
}

tickets["sla_limit"] = tickets["channel"].map(sla_limits)

tickets["sla_status"] = tickets.apply(
    lambda row:
        "Compliant"
        if row["response_minutes"] <= row["sla_limit"]
        else "Violation",
    axis=1
)

sla_compliant = (
    tickets["sla_status"] == "Compliant"
).sum()

sla_violation = (
    tickets["sla_status"] == "Violation"
).sum()

print("\n--- 1. SLA AUDIT ---")
print("Compliant:", sla_compliant)
print("Violations:", sla_violation)
print(
    "Violation rate:",
    round((sla_violation / len(tickets)) * 100, 2),
    "%"
)


# ==================================================
# 2. TEAM ROUTING AUDIT
# ==================================================

routing_rules = {
    "Billing & Payments": "Billing",
    "Delivery & Shipping": "Logistics",
    "Returns & Refunds": "Returns Desk",
    "Warranty & Repair": "Escalations & Warranty"
}


def check_routing(row):
    category = row["category"]

    if category not in routing_rules:
        return "Not Specified"

    if row["assigned_team"] == routing_rules[category]:
        return "Compliant"

    return "Violation"


tickets["routing_status"] = tickets.apply(
    check_routing,
    axis=1
)

routing_compliant = (
    tickets["routing_status"] == "Compliant"
).sum()

routing_violation = (
    tickets["routing_status"] == "Violation"
).sum()

routing_not_specified = (
    tickets["routing_status"] == "Not Specified"
).sum()

print("\n--- 2. TEAM ROUTING AUDIT ---")
print("Compliant:", routing_compliant)
print("Violations:", routing_violation)
print("Not specified by policy:", routing_not_specified)


# ==================================================
# 3. REFUND + REPLACEMENT AUDIT
# ==================================================

tickets["refund_amount_inr"] = pd.to_numeric(
    tickets["refund_amount_inr"],
    errors="coerce"
).fillna(0)

tickets["replacement_issued"] = (
    tickets["replacement_issued"]
    .astype(str)
    .str.strip()
    .str.upper()
)

both_compensation = (
    (tickets["refund_amount_inr"] > 0)
    & (tickets["replacement_issued"] == "Y")
)

double_compensation = both_compensation.sum()

print("\n--- 3. REFUND + REPLACEMENT AUDIT ---")
print(
    "Refund records:",
    (tickets["refund_amount_inr"] > 0).sum()
)

print(
    "Replacement records:",
    (tickets["replacement_issued"] == "Y").sum()
)

print(
    "Potential double-compensation cases:",
    double_compensation
)

if double_compensation > 0:
    print("\nPotential cases:")
    print(
        tickets.loc[
            both_compensation,
            [
                "ticket_id",
                "order_id",
                "refund_amount_inr",
                "replacement_issued"
            ]
        ].to_string(index=False)
    )


# ==================================================
# 4. TRANSFER COST AUDIT
# ==================================================

tickets["transfers"] = pd.to_numeric(
    tickets["transfers"],
    errors="coerce"
).fillna(0)

COST_PER_TRANSFER = 305

total_transfers = tickets["transfers"].sum()

transfer_cost = (
    total_transfers * COST_PER_TRANSFER
)

tickets_with_transfers = (
    tickets["transfers"] > 0
).sum()

print("\n--- 4. TRANSFER COST AUDIT ---")

print(
    "Total transfers:",
    int(total_transfers)
)

print(
    "Tickets with transfers:",
    tickets_with_transfers
)

print(
    "Transfer rate:",
    round(
        (tickets_with_transfers / len(tickets)) * 100,
        2
    ),
    "%"
)

print(
    "Cost per transfer: ₹",
    COST_PER_TRANSFER
)

print(
    "Transfer cost represented: ₹",
    int(transfer_cost)
)


# ==================================================
# 5. CSAT AUDIT
# ==================================================

tickets["csat_score"] = pd.to_numeric(
    tickets["csat_score"],
    errors="coerce"
)

csat_responses = (
    tickets["csat_score"].notna().sum()
)

csat_missing = (
    tickets["csat_score"].isna().sum()
)

average_csat = tickets["csat_score"].mean()

print("\n--- 5. CSAT AUDIT ---")

print(
    "CSAT responses:",
    csat_responses
)

print(
    "Missing CSAT:",
    csat_missing
)

print(
    "CSAT response rate:",
    round(
        (csat_responses / len(tickets)) * 100,
        2
    ),
    "%"
)

print(
    "Average CSAT excluding blanks:",
    round(average_csat, 2)
)


# ==================================================
# 6. DATA QUALITY AUDIT
# ==================================================

duplicate_counts = (
    tickets["ticket_id"].value_counts()
)

duplicate_ticket_ids = (
    duplicate_counts[
        duplicate_counts > 1
    ]
)

source_counts = (
    tickets.groupby("ticket_id")["source_system"]
    .nunique()
)

multi_source_ids = (
    source_counts[
        source_counts > 1
    ]
)

# Missing order IDs
missing_order_ids = (
    tickets["order_id"].isna().sum()
)

# Refund without reason
refund_without_reason = (
    (tickets["refund_amount_inr"] > 0)
    &
    (
        tickets["refund_reason_code"].isna()
        |
        (
            tickets["refund_reason_code"]
            .astype(str)
            .str.strip()
            == ""
        )
    )
).sum()

# Replacement without notes
replacement_without_notes = (
    (tickets["replacement_issued"] == "Y")
    &
    (
        tickets["agent_notes"].isna()
        |
        (
            tickets["agent_notes"]
            .astype(str)
            .str.strip()
            == ""
        )
    )
).sum()

# Notes mention replacement while field says N
notes = (
    tickets["agent_notes"]
    .fillna("")
    .astype(str)
    .str.lower()
)

notes_say_replacement = notes.str.contains(
    "replacement|replaced|new unit|dispatched",
    regex=True
)

structured_says_no_replacement = (
    tickets["replacement_issued"] == "N"
)

possible_note_conflicts = (
    notes_say_replacement
    & structured_says_no_replacement
).sum()

print("\n--- 6. DATA QUALITY AUDIT ---")

print(
    "Duplicate ticket IDs:",
    len(duplicate_ticket_ids)
)

print(
    "Rows involved in duplicates:",
    tickets["ticket_id"]
    .duplicated(keep=False)
    .sum()
)

print(
    "Ticket IDs in multiple source systems:",
    len(multi_source_ids)
)

print(
    "Missing order IDs:",
    missing_order_ids
)

print(
    "Refunds without refund reason:",
    refund_without_reason
)

print(
    "Replacements without agent notes:",
    replacement_without_notes
)

print(
    "Possible note/field conflicts:",
    possible_note_conflicts
)


# ==================================================
# FINAL SUMMARY
# ==================================================

print("\n==============================================")
print("              FINAL AUDIT SUMMARY")
print("==============================================")

print(
    "SLA violations:",
    sla_violation
)

print(
    "Routing violations:",
    routing_violation
)

print(
    "Potential double compensation:",
    double_compensation
)

print(
    "Total transfers:",
    int(total_transfers)
)

print(
    "Transfer cost represented: ₹",
    int(transfer_cost)
)

print(
    "Average CSAT:",
    round(average_csat, 2)
)

print(
    "Duplicate ticket IDs:",
    len(duplicate_ticket_ids)
)

print(
    "Missing order IDs:",
    missing_order_ids
)

print(
    "Possible note conflicts:",
    possible_note_conflicts
)

print("\n==============================================")
print("             AUDIT COMPLETED")
print("==============================================")


# ==================================================
# 7. VALIDATION SAMPLE
# ==================================================

print("\n==============================================")
print("             VALIDATION SAMPLE")
print("==============================================")

# Select a reproducible sample of up to 30 records
sample_size = min(30, len(tickets))

sample = tickets.sample(
    n=sample_size,
    random_state=42
)

validation_columns = [
    "ticket_id",
    "channel",
    "category",
    "assigned_team",
    "response_minutes",
    "sla_limit",
    "sla_status",
    "routing_status",
    "refund_amount_inr",
    "replacement_issued",
    "agent_notes"
]

print(
    f"\n{sample_size} records selected for manual validation:\n"
)

print(
    sample[validation_columns]
    .to_string(index=False)
)

print("\n==============================================")
print("Validation sample generated.")
print("==============================================")
```
