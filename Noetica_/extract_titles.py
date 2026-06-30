import pypdf
import glob
import os

pdf_files = glob.glob('Noetica Master Blueprint Part *.pdf')
pdf_files.sort(key=lambda x: int(x.split('Part ')[1].split('.pdf')[0]))

out_text = ''
for f in pdf_files:
    try:
        reader = pypdf.PdfReader(f)
        text = ''
        for page in reader.pages[:2]: # Just read the first two pages to get the intro
            text += page.extract_text() + '\n'
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Grab first 15 lines to capture titles and purpose
        title_lines = lines[:15]
        out_text += "=== " + f + " ===\n" + "\n".join(title_lines) + "\n\n"
    except Exception as e:
        out_text += "Error reading " + f + ": " + str(e) + "\n\n"

with open('blueprint_titles.txt', 'w', encoding='utf-8') as out:
    out.write(out_text)
print('Titles extracted.')
