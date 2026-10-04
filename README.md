# Vireo Support Policy Auditor

A Python-based deterministic audit tool for checking customer support tickets against Vireo Audio's support policies.

## What it does

The auditor reads support-ticket data and checks:

* Response-time SLA compliance
* Team-routing compliance
* Potential refund + replacement double compensation
* Transfer-related planning cost
* CSAT response rate and average score
* Data-quality issues such as duplicate ticket IDs and missing order IDs

## Tech Stack

* Python
* Pandas
* CSV
* Rule-based policy checks

## Key Dataset Findings

The dataset contains:

* **12,528 records**
* **11,875 unique ticket IDs**
* **1,119 potential SLA violations**
* **5,906 tickets matching categories with explicit routing rules**
* **4 potential double-compensation cases requiring human review**
* **1,241 transfers**
* **₹3,78,505 in transfer-related planning cost represented by the dataset**
* **Average CSAT: 2.42**, excluding missing responses
* **653 duplicate ticket IDs**
* **4,218 records with missing order IDs**

## Important Limitations

Some records come from legacy and helpdesk systems, so duplicate ticket IDs may represent migration or reconciliation issues.

The auditor flags potentially problematic cases for review rather than automatically assuming every flagged record is a confirmed policy violation.

Warranty-agent certification cannot be independently verified because certification information is not included in the dataset.

## How to Run

Install pandas:

```bash
pip install pandas
```

Run:

```bash
python auditor.py
```

The program prints the audit results and summary in the terminal.

## AI Usage

AI assistance was used during development for:

* Understanding the assignment requirements
* Designing the audit approach
* Debugging Python code
* Interpreting dataset results
* Improving documentation and presentation

The final audit logic uses deterministic Python rules based on the provided policy and dataset.
