import openpyxl

wb2 = openpyxl.load_workbook("test_with_images.xlsx")
ws2 = wb2.active

for i, img in enumerate(ws2._images):
    # Get raw image data
    image_data = img._data()
    # Or maybe it's in img.ref
    
    with open(f"extracted_{i}.jpg", "wb") as f:
        f.write(image_data)
        
    print(f"Saved image {i}")
