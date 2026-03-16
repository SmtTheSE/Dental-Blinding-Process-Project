import openpyxl
from openpyxl.drawing.image import Image
import pandas as pd
from PIL import Image as PILImage
import os
import uuid

img_path = 'sample_opg.jpg'
if not os.path.exists(img_path):
    img = PILImage.new('RGB', (150, 150), color = 'red')
    img.save(img_path)

wb = openpyxl.Workbook()
ws = wb.active

headers = ["ID", "Name", "Age", "Sex", "OPG", "A code", "D code", "A Age", "D Age", "Actual age"]
ws.append(headers)

# Data row 1
p1_id = str(uuid.uuid4())[:8]
ws.append([f"T1_{p1_id}", "John Doe", 12, "male", "", f"A_{p1_id}", f"D_{p1_id}", 12.5, 12.0, 12])
img = Image(img_path)
ws.add_image(img, "E2") 

# Data row 2
p2_id = str(uuid.uuid4())[:8]
ws.append([f"T2_{p2_id}", "Jane Doe", 14, "female", "", f"A_{p2_id}", f"D_{p2_id}", 14.5, 14.0, 14])
img2 = Image(img_path)
ws.add_image(img2, "E3") 

wb.save("test_with_images.xlsx")

print("Generated new test Excel file test_with_images.xlsx")
