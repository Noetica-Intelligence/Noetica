import glob
from pypdf import PdfWriter
import os

pdf_files = glob.glob('Noetica Master Blueprint Part *.pdf')
# Sort files by their part number to ensure correct order
pdf_files.sort(key=lambda x: int(x.split('Part ')[1].split('.pdf')[0]))

merger = PdfWriter()

for pdf in pdf_files:
    print(f"Appending {pdf}")
    merger.append(pdf)

output_filename = "Noetica_Master_Blueprint_Complete.pdf"
merger.write(output_filename)
merger.close()

print(f"Successfully merged {len(pdf_files)} PDFs into {output_filename}")
