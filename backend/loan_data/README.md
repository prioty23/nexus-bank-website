# Loan Type Data

This folder stores loan category data used to guide loan-selection flows.

Required columns:

```csv
schedule_type,loan_category,loan_name,source_file
```

Rules:

- Keep one loan product per row.
- Use `schedule_type` for the banking schedule, such as `Retail` or `SME`.
- Use `loan_category` for customer-facing groups, such as `Personal Loan` or `Home Loan`.
- Use `loan_name` for the exact loan/product name.
