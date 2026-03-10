import openpyxl
import os

def verify_excel(filename):
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return

    try:
        wb = openpyxl.load_workbook(filename)
        ws = wb.active
        print(f"Successfully loaded {filename}")
        print(f"Sheet title: {ws.title}")
        
        # Check headers
        headers = [ws.cell(row=1, column=i).value for i in range(1, 11)]
        print(f"Headers: {headers}")
        
        # Check row count
        rows = list(ws.rows)
        print(f"Total rows (including header): {len(rows)}")
        
        if len(rows) > 1:
            print(f"First data row: {[cell.value for cell in rows[1]]}")
            
        # Check for images
        print(f"Number of images in sheet: {len(ws._images)}")
        
    except Exception as e:
        print(f"Failed to verify Excel: {e}")

if __name__ == "__main__":
    verify_excel('debug_export.xlsx')
