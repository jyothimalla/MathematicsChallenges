import pdfplumber
import json
import os
import re
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
        current_question = None
        options = {}
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue  # Skip if page has no text
            
            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect new question (heuristic: ends with ? or starts with number)
                if re.match(r"^\d+\.", line) or "?" in line:
                    if current_question and options:
                        quiz_data.append({
                            "question": current_question,
                            "options": options
                        })
                    current_question = line
                    options = {}
                
                # Detect multiple-choice answers
                match = re.match(r"^(A|B|C|D|E)[).] (.+)", line)
                if match:
                    option_letter, option_text = match.groups()
                    options[option_letter] = option_text
        
        # Append the last question
        if current_question and options:
            quiz_data.append({
                "question": current_question,
                "options": options
            })

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

# Map images to questions (only if applicable)
for i, question in enumerate(quiz_data):
    if i < len(extracted_images):  # If an image exists, map it
        question["image"] = extracted_images[i]

# Save questions to JSON file
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(quiz_data, f, indent=4)

print(f"✅ Extraction Complete! JSON saved as {output_json}")
print(f"✅ Images saved in {output_image_folder}/")
