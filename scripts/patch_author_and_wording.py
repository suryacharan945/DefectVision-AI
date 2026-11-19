import os

# --- 1. PATCH generate_jeas_docx.py ---
with open('scripts/generate_jeas_docx.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Update Affiliation
text = text.replace(
    'affil_run = affil_p.add_run("Department of Computer Science and Engineering, Independent Research Group\\nEmail: suryacharan945@gmail.com\\n*Corresponding author")',
    'affil_run = affil_p.add_run("[Affiliation: AUTHOR CONFIRMATION REQUIRED]\\nEmail: suryacharan945@gmail.com\\n*Corresponding author")'
)

# Update Cover Letter Sign-off
text = text.replace(
    'sop.add_run("Sincerely,\\n\\nSurya Charan\\nIndependent Computer Vision Researcher\\nDepartment of Computer Science and Engineering\\nEmail: suryacharan945@gmail.com")',
    'sop.add_run("Sincerely,\\n\\nSurya Charan\\n[Affiliation: AUTHOR CONFIRMATION REQUIRED]\\nEmail: suryacharan945@gmail.com")'
)

# Update "deterministic" in intro
old_intro_det = 'with deterministic per-image inference latencies of 392.5 ms median (p95: 438.1 ms)'
new_intro_det = 'with measured per-image inference latencies of 392.5 ms median (p95: 438.1 ms, mean 398.4 ms)'
text = text.replace(old_intro_det, new_intro_det)

old_intro_det2 = 'memory-bank adaptation and deterministic inference are achievable'
new_intro_det2 = 'memory-bank adaptation and CPU inference are achievable'
text = text.replace(old_intro_det2, new_intro_det2)

# Update "deterministic" in cover letter
old_cl_det = 'demonstrated deterministic PatchCore inference of 392.5 ms (median)'
new_cl_det = 'demonstrated measured PatchCore inference of 392.5 ms (median; p95 438.1 ms)'
text = text.replace(old_cl_det, new_cl_det)

with open('scripts/generate_jeas_docx.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched generate_jeas_docx.py!')

# --- 2. PATCH generate_jeas_pdf.py ---
with open('scripts/generate_jeas_pdf.py', 'r', encoding='utf-8') as f:
    pdf_text = f.read()

pdf_text = pdf_text.replace(
    'story.append(Paragraph("Department of Computer Science and Engineering, Independent Research Group<br/>Email: suryacharan945@gmail.com | *Corresponding author", affil_style))',
    'story.append(Paragraph("<b>[Affiliation: AUTHOR CONFIRMATION REQUIRED]</b><br/>Email: suryacharan945@gmail.com | *Corresponding author", affil_style))'
)

old_pdf_det = 'demonstrated deterministic inference of 392.5 ms'
new_pdf_det = 'demonstrated measured median inference latency of 392.5 ms (p95: 438.1 ms)'
pdf_text = pdf_text.replace(old_pdf_det, new_pdf_det)

with open('scripts/generate_jeas_pdf.py', 'w', encoding='utf-8') as f:
    f.write(pdf_text)
print('Patched generate_jeas_pdf.py!')
