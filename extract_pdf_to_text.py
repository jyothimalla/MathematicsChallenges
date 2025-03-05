import fitz  # PyMuPDF
import json
import re
import os
from datetime import datetime

def extract_text_from_pdf(pdf_path):
    """Extracts text while maintaining structure from a given PDF file."""
    doc = fitz.open(pdf_path)
    text_data = []
    
    for page in doc:
        blocks = page.get_text("blocks")  # Get text blocks
        sorted_blocks = sorted(blocks, key=lambda b: (b[1], b[0]))  # Sort based on y, then x positions
        
        page_text = "\n".join([b[4] for b in sorted_blocks])
        text_data.append(page_text)
    
    return "\n".join(text_data)

def clean_text(text):
    """Cleans the extracted text, removes unwanted characters, and formats fractions."""
    text = re.sub(r"©.*", "", text)  # Remove copyright info
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
    
    # Convert standalone numbers into proper fractions
    text = re.sub(r"(\d+)\s+(\d+)", r"\1/\2", text)  # Converts "1 6" → "1/6"
    
    return text

def process_text(text):
    """Processes extracted text to correctly format questions & options."""
    lines = text.split("\n")
    questions = []
    current_question = None
    options_pattern = re.compile(r"^([A-E])\s+(.*)")  # Match options (A, B, C, D, E)

    for line in lines:
        line = clean_text(line)

        if not line:
            continue  # Skip empty lines

        # Match Question Numbers (e.g., "20. ")
        if re.match(r"^\d+\.", line):  
            if current_question:
                questions.append(current_question)  # Save previous question
            
            current_question = {"question": line, "options": {}, "answer": None}

        # Match Answer Options (A, B, C, D, E) and store as dictionary
        elif options_pattern.match(line):
            if current_question:
                match = options_pattern.match(line)
                option_letter = match.group(1)
                option_text = match.group(2).strip()
                
                current_question["options"][option_letter] = option_text

        # Match Answer (if available)
        elif re.match(r"^Answer:\s*[A-E]", line):  
            if current_question:
                current_question["answer"] = line.split(":")[1].strip()

        else:
            if current_question:
                current_question["question"] += " " + line  # Append multi-line questions

    if current_question:
        questions.append(current_question)  # Add last question
    
    return questions

def save_questions_to_json(questions, output_folder="output"):
    """Saves questions to a JSON file with a timestamped name."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"{output_folder}/questions_{timestamp}.json"

    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=4, ensure_ascii=False)

    print(f"✅ Questions saved to: {json_filename}")

# 📌 **Step 1: Specify the PDF File**
pdf_path = "questions_2020.pdf"  # Replace with your actual PDF filename

# 📌 **Step 2: Extract & Process Text**
raw_text = extract_text_from_pdf(pdf_path)
filtered_questions = process_text(raw_text)

# 📌 **Step 3: Save Extracted Questions**
save_questions_to_json(filtered_questions)
