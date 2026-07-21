# Account Type Data

This folder stores account category data used to guide account-selection flows.

Required columns:

```csv
schedule_type,account_category,account_name,source_file
```

Rules:

- Keep one account product per row.
- Use `schedule_type` for the banking schedule, such as `Retail`, `SME`, or `Corporate`.
- Use `account_category` for customer-facing groups, such as `Savings Deposits` or `Fixed Deposit`.
- Use `account_name` for the exact account/product name.
