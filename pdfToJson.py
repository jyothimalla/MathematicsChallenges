import pdfplumber
import json
import os
from pdf2image import convert_from_path

# Path to the input PDF
pdf_path = "First Mathematics Challenge 2023 Paper.pdf"
output_json = "quiz_questions.json"
output_image_folder = "extracted_images"

# Ensure the image output folder exists
os.makedirs(output_image_folder, exist_ok=True)

# List to store extracted questions
quiz_data = []

def extract_text_questions(pdf_path):
    """Extracts questions and answers from a PDF file"""
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                question_data = {}
                for line in lines:
                    if line.strip().startswith(("A)", "B)", "C)", "D)", "E)")):
                        question_data.setdefault("options", []).append(line.strip())
                    elif "?" in line or ":" in line:  # Simple heuristic for questions
                        question_data["question"] = line.strip()
                if "question" in question_data and "options" in question_data:
                    quiz_data.append(question_data)

def extract_images(pdf_path):
    """Extracts images from a PDF file and saves references in JSON"""
    images = convert_from_path(pdf_path)
    image_list = []
    for i, img in enumerate(images):
        img_path = os.path.join(output_image_folder, f"page_{i + 1}.png")
        img.save(img_path, "PNG")
        image_list.append(img_path)
    return image_list

# Extract text-based questions
extract_text_questions(pdf_path)

# Extract images
extracted_images = extract_images(pdf_path)

# Add image references if found
for i, question in enumerate(quiz_data):
    if i < len(extracted_images):
        question["image"] = extracted_images[i]  # Map images to questions

# Save questions to JSON file
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(quiz_data, f, indent=4)

print(f"✅ Extraction Complete! JSON saved as {output_json}")
print(f"✅ Images saved in {output_image_folder}/")
