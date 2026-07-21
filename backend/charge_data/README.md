# Charge Data

Each schedule PDF should be converted into one CSV file in this folder.

Required columns:

```csv
schedule,category,product,charge_name,condition,amount,vat_note,source_file
```

Rules:

- Add one charge or condition per row.
- Keep `charge_name` consistent across files, such as `Account closing charge`, `Processing fee`, or `Cheque book issue charge`.
- Put ranges, tiers, locations, card types, or account-balance rules in `condition`.
- Put the exact payable value in `amount`.
- Put VAT details in `vat_note`.
- Do not combine multiple unrelated charges into one row.
