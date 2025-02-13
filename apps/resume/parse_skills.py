from pathlib import Path

import fitz
import re


# Function to read PDF line by line and record size and boldness in correct sequence


def extract_text_size_and_boldness(pdf_path):
    doc = fitz.open(pdf_path)  # Open the PDF file
    text_info = []  # List to store text, size, and boldness information

    # Iterate through each page of the document
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Load the page
        blocks = page.get_text("dict")["blocks"]  # Extract text blocks

        # Iterate through each block
        for block in blocks:
            if block['type'] == 0:  # Text block
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text']
                        font = span['font']
                        size = span['size']
                        x0, y0, x1, y1 = span['bbox']  # Get the bounding box coordinates of the span

                        # Check if the font is bold by checking the font name
                        is_bold = 'bold' in font.lower()

                        # Record the text, size, boldness, and position information
                        text_info.append({
                            'text': text.strip(),
                            'size': size,
                            'bold': is_bold,
                            'x0': x0,
                            'y0': y0,
                            'x1': x1,
                            'y1': y1
                        })

        # Sort text based on the Y-coordinate first, then by X-coordinate (to maintain left-to-right sequence)
        text_info.sort(key=lambda x: (x['y0'], x['x0']))  # Sort by vertical position (top to bottom) and horizontal (left to right)

    return text_info

# Function to filter and extract titles with size between 14.5 and 16 and boldness True


def extract_titles(text_info, min_size=14.5, max_size=16, bold=True):
    titles = []  # List to store titles

    # Iterate through the extracted text information
    for entry in text_info:
        # Check if the size is between 14.5 and 16 and boldness is True
        if min_size <= entry['size'] <= max_size and entry['bold'] == bold:
            titles.append(entry['text'])  # Add title text to the list

    return titles

# Function to list skills under a title, using regex for flexible matching


def list_skills_under_title(text_info, title_keywords=None, min_size=14.5, max_size=16, bold=True):
    if title_keywords is None:
        title_keywords = [
            "KEY COMPETENCIES", "SKILLS", "CORE COMPETENCIES", "EXPERTISE", "AREAS OF EXPERTISE", "PROFESSIONAL SKILLS"
        ]

    skills = []
    listing_skills = False
    title_pattern = re.compile(r'|'.join([re.escape(keyword) for keyword in title_keywords]), re.IGNORECASE)

    # Iterate through the extracted text information
    for entry in text_info:
        # Start listing skills once we find a title that matches any of the keywords
        if title_pattern.search(entry['text']):  # Found the title (matches any of the keywords)
            listing_skills = True
            continue  # Skip the title itself

        # Stop listing skills when another title with the desired size and boldness is encountered
        if min_size <= entry['size'] <= max_size and entry['bold'] == bold:
            if listing_skills:  # If we were listing skills, stop now
                break

        # If we are listing skills and the text is smaller and not bold, add to skills list
        if listing_skills and entry['size'] < max_size and not entry['bold']:
            # Split the text by commas and treat each part as a separate skill
            individual_skills = [skill.strip() for skill in entry['text'].split(',')]
            skills.extend(individual_skills)

    return skills

# Function to reuse the skills list


def reuse_skills(skills):
    # Example: Print out all skills
    for skill in skills:
        print(f"Skill: {skill}")

# Usage
pdf_path = "/src/ats/media/uploads/sushant-cvs.pdf"  # Replace with your PDF file path
text_info = extract_text_size_and_boldness(pdf_path)

# List skills under any of the common keywords (like "KEY COMPETENCIES", "SKILLS", etc.)
skills = list_skills_under_title(text_info, title_keywords=[
    "KEY COMPETENCIES", "SKILLS", "CORE COMPETENCIES", "EXPERTISE", "AREAS OF EXPERTISE", "PROFESSIONAL SKILLS"
], min_size=14.5, max_size=16, bold=True)

# Now you have the 'skills' list stored and ready for reuse
reuse_skills(skills)  # Example of how to reuse the skills list

BASE_DIR = Path(__file__).resolve().parent.parent.parent


print(BASE_DIR)
