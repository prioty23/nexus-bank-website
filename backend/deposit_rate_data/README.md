# Deposit Rate Data

Deposit interest rates are stored separately from Schedule of Charges.

Required columns:

```csv
business_unit,category,product,condition,rate,note,source_file
```

Rules:

- Add one product condition or tenure per row.
- Use `business_unit` for Retail, SME, Commercial, Corporate, or General.
- Use `category` for the workbook section, such as CASA Products, Term Deposit, Recurring Deposit, or Closed Products.
- Put balance bands, amount bands, tenures, or special conditions in `condition`.
- Put the exact interest rate in `rate`.
- Put closed-product or footnote details in `note`.
