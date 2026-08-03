import os
import subprocess

def parse_checklist(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    sections = []
    current_section = None
    
    for line in lines:
        raw_line = line.strip()
        if not raw_line:
            continue
        
        if raw_line.endswith(":") and not raw_line.startswith("->"):
            if current_section and current_section["items"]:
                sections.append(current_section)
            current_section = {
                "title": raw_line,
                "type": "header",
                "items": []
            }
        elif not raw_line.startswith("->"):
            if current_section and current_section["items"]:
                sections.append(current_section)
            current_section = {
                "title": raw_line,
                "type": "phrase",
                "items": []
            }
        else:
            content = raw_line[2:].strip()
            if "=" in content:
                parts = content.split("=", 1)
                symptom = parts[0].strip()
                solution = parts[1].strip()
            else:
                symptom = content
                solution = ""
            
            if current_section:
                current_section["items"].append({
                    "symptom": symptom,
                    "solution": solution
                })
    
    if current_section and (current_section["items"] or current_section["type"] == "header"):
        sections.append(current_section)
        
    return sections

def generate_html(sections):
    html = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Reflexes & Catchphrases Cheat Sheet (1-Page)</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fira+Code:wght@500;600&display=swap');

  @page {
    size: A4 portrait;
    margin: 4mm 6mm 4mm 6mm;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #0f172a;
    background-color: #ffffff;
    font-size: 9.5px;
    line-height: 1.25;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  /* HEADER BANNER */
  .header {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
    color: #ffffff;
    padding: 8px 14px;
    border-radius: 6px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .header-left h1 {
    font-size: 15px;
    font-weight: 800;
    letter-spacing: -0.3px;
    color: #ffffff;
  }

  .header-left p {
    font-size: 9px;
    color: #cbd5e1;
  }

  .header-badge {
    background: rgba(99, 102, 241, 0.3);
    border: 1px solid #818cf8;
    color: #e0e7ff;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  /* MAIN 3-COLUMN MASONRY */
  .columns-wrap {
    column-count: 3;
    column-gap: 7px;
  }

  .col-break {
    column-span: all;
    background: #0f172a;
    color: #ffffff;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.4px;
    display: flex;
    align-items: center;
    gap: 5px;
    margin: 6px 0 4px 0;
  }

  /* CARD */
  .card {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 5px;
    padding: 6px 8px;
    margin-bottom: 7px;
    break-inside: avoid;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    display: flex;
    flex-direction: column;
  }

  .card-phrase {
    font-size: 9.5px;
    font-weight: 700;
    color: #1e1b4b;
    background: #f1f5f9;
    padding: 3.5px 6px;
    border-left: 3px solid #4f46e5;
    border-radius: 3px;
    margin-bottom: 5px;
    font-style: italic;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .item-list {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .item-row {
    display: flex;
    flex-direction: column;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 3px;
    padding: 3.5px 6px;
  }

  .symptom {
    font-size: 8.5px;
    font-weight: 600;
    color: #b91c1c;
    display: flex;
    align-items: center;
    gap: 3px;
    margin-bottom: 2px;
    line-height: 1.2;
  }

  .symptom::before {
    content: "🔍";
    font-size: 6.5px;
  }

  .solution {
    font-size: 8.5px;
    font-weight: 600;
    color: #15803d;
    background: #f0fdf4;
    border-left: 1.5px solid #22c55e;
    padding: 2px 5px;
    border-radius: 2px;
    font-family: 'Fira Code', monospace;
    line-height: 1.2;
  }

  .footer {
    margin-top: 8px;
    text-align: center;
    font-size: 8px;
    color: #94a3b8;
    border-top: 1px solid #e2e8f0;
    padding-top: 2px;
    grid-column: 1 / -1;
  }
</style>
</head>
<body>

  <div class="header">
    <div class="header-left">
      <h1>⚡ Code Review & Oral Checklist (Fiche 1-Page)</h1>
      <p>Phrases d'Accroche & Réflexes Systématiques (Master Checklist)</p>
    </div>
    <div class="header-badge">1 PAGE ULTIME</div>
  </div>

  <div class="columns-wrap">
"""
    
    for sec in sections:
        if sec["type"] == "header":
            html += f"""
    <div class="col-break">
      🚀 {sec['title']}
    </div>
"""
        else:
            html += f"""
    <div class="card">
      <div class="card-phrase" title="{sec['title']}">"{sec['title']}"</div>
      <div class="item-list">
"""
            for item in sec["items"]:
                html += f"""
        <div class="item-row">
          <div class="symptom">{item['symptom']}</div>
          <div class="solution">➔ {item['solution']}</div>
        </div>
"""
            html += """
      </div>
    </div>
"""

    html += """
  </div>
  <div class="footer">
    Code Review Patterns & Reflexes • Antigravity AI Engineering • Single Page Cheat Sheet
  </div>

</body>
</html>
"""
    return html

txt_path = os.path.abspath("patterns_checklist.txt")
html_path = os.path.abspath("patterns_checklist.html")
pdf_path = os.path.abspath("patterns_checklist.pdf")

sections = parse_checklist(txt_path)
html_content = generate_html(sections)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(edge_path):
    edge_path = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'

file_url = 'file:///' + html_path.replace('\\', '/')

subprocess.run([edge_path, '--headless', '--disable-gpu', '--no-pdf-header-footer', f'--print-to-pdf={pdf_path}', file_url], check=True)
print("PDF created successfully:", os.path.exists(pdf_path), "Size:", os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0)
