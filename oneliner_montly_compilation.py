import os
import re

# Folder containing the source .txt files
source_folder = "./pouet_oneliners"

# Output folder for monthly concatenated files
output_folder = "./monthly_oneliners"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Dictionary to store content grouped by month
monthly_content = {}

# Loop through all files in the source folder
for filename in sorted(os.listdir(source_folder)):
    if filename.lower().endswith(".txt"):
        filepath = os.path.join(source_folder, filename)
        
        # Read the content of the file
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract the first date found in the content (format YYYY-MM-DD)
        match = re.search(r"(\d{4})-(\d{2})-\d{2}", content)
        
        if match:
            year = match.group(1)
            month = match.group(2)
            key = f"{year}-{month}"  # Example: "2003-01"

            # Initialize if this month hasn't been seen before
            if key not in monthly_content:
                monthly_content[key] = ""

            # Append the content of the current file to the corresponding month
            monthly_content[key] += content + "\n"

# Write the grouped content to monthly files
for key, content in monthly_content.items():
    output_path = os.path.join(output_folder, f"{key}.txt")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"Concatenation completed. Monthly files are saved in '{output_folder}'")
