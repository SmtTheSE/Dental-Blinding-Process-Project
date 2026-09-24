# Scripts

Developer utilities. **None of these are imported by the running app** — the
deployed application only uses the modules at the repository root, `utils/`,
`templates/` and `static/`.

Run every script **from the repository root** as a module, so `from app import …`
and relative file paths resolve the same way they always have:

```bash
python -m scripts.diagnostics.check_db
```

Scripts that talk to the database need the same `.env` as the app.

| Folder | Purpose |
|---|---|
| `diagnostics/` | Read-only checks against the database and exports (`check_*`, `count_completed`, `verify_excel_content`, …) |
| `dev/` | Manual experiments for uploads, signed URLs and Excel export (`test_*`, `chrome_simulation`, `generate_test_excel`) |
| `data/` | One-off data jobs (`upload_opg_and_build_excel`, `trim_tooth`) |
| `fixtures/` | Sample inputs the dev scripts read (`sample_opg.jpg`, sample import workbooks) |

Anything a script writes goes to `tmp/`, which is git-ignored.

> The `dev/test_*.py` files are manual scripts, not an automated test suite —
> several of them hit the live database or storage when run.
