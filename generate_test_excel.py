import pandas as pd

# Columns based on the full format spec in routes.py:
# Format 2 (Full): ID, Name, Age, Sex, OPG, A code, D code, A Age, D Age, Actual age (10 columns)
# 0: ID
# 1: Name
# 2: Age
# 3: Sex
# 4: OPG
# 5: A code
# 6: D code
# 7: A Age
# 8: D Age
# 9: Actual age

data = {
    "ID": ["TEST-1", "TEST-2", "TEST-3"],
    "Name": ["Test One", "Test Two", "Test Three"],
    "Age": ["12", "14", "15"],
    "Sex": ["male", "female", "male"],
    "OPG": ["test_opg_image.jpg", "test_opg_image.jpg", "test_opg_image.jpg"],
    "A code": ["A111", "A222", "A333"],
    "D code": ["D111", "D222", "D333"],
    "A Age": ["12.5", "14.2", "15.1"],
    "D Age": ["12.0", "14.5", "14.9"],
    "Actual age": ["12", "14", "15"]
}

df = pd.DataFrame(data)

file_path = "test_bulk_import_opg.xlsx"
df.to_excel(file_path, index=False)
print(f"Excel file created at: {file_path}")
