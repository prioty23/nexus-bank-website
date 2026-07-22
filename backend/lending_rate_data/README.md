# Lending Rate Data

Lending interest rates are stored separately from Deposit Rates and Schedule of Charges.

Required columns:

```csv
section,category,subcategory,economic_purpose,declared_rate,lowest_rate,highest_rate,pdf_page,source_file
```

Rules:

- Add one economic-purpose row per record.
- Keep the PDF hierarchy in `section`, `category`, and `subcategory`.
- Put the customer-facing loan/economic purpose in `economic_purpose`.
- Put the exact `declared_rate`, `lowest_rate`, and `highest_rate` from the source file.
- Use `N/A` when the source file lists no rate for that row.
