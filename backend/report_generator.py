
from fpdf import FPDF
from datetime import datetime

class ProductDossier(FPDF):
    def __init__(self, product_name):
        super().__init__()
        self.product_name = product_name
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("Arial", "", "Arial.ttf", uni=True) if 0 else None # Use standard fonts for now

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"LetScience Intelligence Dossier: {self.product_name}", 0, 1, "R")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d')} | Page {self.page_no()}", 0, 0, "C")

    def chapter_title(self, title):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(30, 41, 59) # Slate 900
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(4)
        self.set_draw_color(226, 232, 240) # Slate 200
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def chapter_body(self, text):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(51, 65, 85) # Slate 700
        self.multi_cell(0, 7, text)
        self.ln()

    def add_card(self, title, detail):
        self.set_fill_color(248, 250, 252) # Slate 50
        self.set_draw_color(226, 232, 240)
        self.rect(self.get_x(), self.get_y(), 190, 20, 'DF')
        
        self.set_xy(self.get_x() + 2, self.get_y() + 2)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, title, 0, 1)
        self.set_x(self.get_x() + 2)
        self.set_font("Helvetica", "", 9)
        self.cell(0, 5, detail, 0, 1)
        self.ln(12)

def create_dossier(product, trials, patents, articles):
    pdf = ProductDossier(product.name)
    pdf.add_page()
    
    # Title Page content (Simulated)
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 20, product.name, 0, 1, "C")
    
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 10, "Comprehensive Intelligence Report", 0, 1, "C")
    pdf.ln(20)
    
    # 1. Executive Summary
    pdf.chapter_title("1. Executive Summary")
    pdf.chapter_body(f"{product.name} is a key asset in the current competitive landscape. "
                     f"This report aggregates data from {len(trials)} clinical trials, {len(patents)} patents, "
                     f"and {len(articles)} scientific articles to provide a 360-degree view of its development status and exclusivity profile.")
    
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(40, 10, "Description:", 0, 1)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, product.description or "No description available.")
    
    pdf.ln(10)
    pdf.add_page()

    # 2. Clinical Development
    pdf.chapter_title("2. Clinical Development")
    pdf.chapter_body(f"Total Trials Found: {len(trials)}")
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(241, 245, 249) # Slate 100
    pdf.cell(20, 8, "Phase", 1, 0, 'C', True)
    pdf.cell(30, 8, "Status", 1, 0, 'C', True)
    pdf.cell(140, 8, "Title", 1, 1, 'C', True)
    
    pdf.set_font("Helvetica", "", 9)
    for t in trials[:20]: # Limit rows
        pdf.cell(20, 8, t.phase[:8], 1)
        pdf.cell(30, 8, t.status[:12], 1)
        pdf.cell(140, 8, t.title[:80] + "..." if len(t.title)>80 else t.title, 1)
        pdf.ln()
        
    pdf.ln(10)
    
    # 3. Intellectual Property
    pdf.chapter_title("3. Intellectual Property (Patents)")
    for p in patents[:10]:
        pdf.add_card(f"Patent: {p.source_id}", f"Expires: {p.publication_date.year + 20 if p.publication_date else 'Unknown'} | {p.title}")

    return pdf
