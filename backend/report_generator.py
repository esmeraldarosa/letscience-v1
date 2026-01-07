
from fpdf import FPDF
from datetime import datetime
import textwrap

class ProductDossier(FPDF):
    def __init__(self, product_name):
        super().__init__()
        self.product_name = product_name
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("Arial", "", "Arial.ttf", uni=True) if 0 else None # Use standard fonts
        
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

    def add_card(self, title, detail, link=None):
        self.set_fill_color(248, 250, 252) # Slate 50
        self.set_draw_color(226, 232, 240)
        
        # Calculate height based on detail length
        self.set_font("Helvetica", "", 9)
        # Mock calculation of height
        num_lines = len(textwrap.wrap(detail, width=90))
        height = 12 + (num_lines * 5)
        
        # Check if page break needed
        if self.get_y() + height > 270:
            self.add_page()
            
        start_x = self.get_x()
        start_y = self.get_y()
        
        self.rect(start_x, start_y, 190, height, 'DF')
        
        self.set_xy(start_x + 4, start_y + 4)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(15, 23, 42)
        self.cell(0, 5, title, 0, 1)
        
        self.set_x(start_x + 4)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(71, 85, 105)
        self.multi_cell(180, 5, detail)
        
        if link:
            self.set_xy(start_x + 160, start_y + 4)
            self.set_font("Helvetica", "U", 8)
            self.set_text_color(37, 99, 235) # Blue
            self.cell(25, 5, "View Source", 0, 0, link=link)
            
        self.set_xy(start_x, start_y + height + 5)

def create_dossier(product, trials, patents, articles, milestones, synthesis_schemes, indications):
    pdf = ProductDossier(product.name)
    pdf.add_page()
    
    # Title Page
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 20, product.name, 0, 1, "C")
    
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 10, "Comprehensive Intelligence Report", 0, 1, "C")
    
    pdf.ln(10)
    
    # Metadata Box
    pdf.set_fill_color(241, 245, 249)
    pdf.rect(60, pdf.get_y(), 90, 40, 'F')
    pdf.set_y(pdf.get_y() + 5)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, f"Phase: {product.development_phase}", 0, 1, "C")
    pdf.cell(0, 6, f"Indication: {product.target_indication}", 0, 1, "C")
    pdf.cell(0, 6, f"Date: {datetime.now().strftime('%B %d, %Y')}", 0, 1, "C")
    
    pdf.ln(25)
    
    # 1. Executive Summary
    pdf.chapter_title("1. Executive Summary")
    pdf.chapter_body(f"{product.name} is a pharmaceutical asset currently in {product.development_phase}. "
                     f"This report aggregates real-time intelligence including {len(trials)} clinical trials, {len(patents)} patents, "
                     f"{len(articles)} scientific articles, and {len(synthesis_schemes)} synthesis pathways.")
    
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(40, 10, "Description & Mechanism:", 0, 1)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, product.description or "No detailed description available.")
    
    if indications:
        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(40, 10, "Approved Indications:", 0, 1)
        pdf.set_font("Helvetica", "", 10)
        for ind in indications:
            pdf.cell(5, 7, "-", 0, 0)
            pdf.multi_cell(0, 7, f"{ind.disease_name} ({ind.approval_status})")

    pdf.add_page()

    # 2. Timeline & Milestones
    if milestones:
        pdf.chapter_title("2. Development Timeline")
        # Sort milestones
        sorted_milestones = sorted(milestones, key=lambda x: x.date)
        
        pdf.set_font("Helvetica", "", 10)
        for m in sorted_milestones:
            date_str = m.date.strftime('%Y-%m-%d')
            pdf.cell(30, 8, date_str, 0, 0)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(40, 8, m.phase, 0, 0)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 8, m.event)
            pdf.ln(2)
        pdf.ln(10)

    # 3. Clinical Development
    pdf.chapter_title("3. Clinical Development")
    pdf.chapter_body(f"Total Trials Found: {len(trials)}")
    
    if trials:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(226, 232, 240)
        pdf.cell(20, 8, "Phase", 1, 0, 'C', True)
        pdf.cell(25, 8, "Status", 1, 0, 'C', True)
        pdf.cell(145, 8, "Title", 1, 1, 'C', True)
        
        pdf.set_font("Helvetica", "", 8)
        for t in trials[:25]: # Limit rows
            pdf.cell(20, 8, t.phase[:8], 1)
            pdf.cell(25, 8, t.status[:12], 1)
            # Truncate title
            title = t.title[:85] + "..." if len(t.title)>85 else t.title
            pdf.cell(145, 8, title, 1)
            pdf.ln()
    
    pdf.add_page()

    # 4. Scientific Literature
    pdf.chapter_title("4. Scientific Literature")
    if articles:
        for a in articles[:10]:
            pdf.add_card(
                title=a.title,
                detail=f"Authors: {a.authors[:100]}...\nPublished: {a.publication_date.strftime('%Y-%m-%d') if a.publication_date else 'N/A'}",
                link=a.url
            )
    else:
         pdf.chapter_body("No specific scientific articles found in database.")

    # 5. Review of Synthesis
    if synthesis_schemes:
        pdf.add_page()
        pdf.chapter_title("5. Chemical Synthesis")
        for s in synthesis_schemes:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 10, s.scheme_name, 0, 1)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, s.scheme_description)
            pdf.ln(5)
            
            # Attempt to check if image_url is valid/accessible?
            # For now, just print the link as we can't easily download external images blindly in this environment without requests overhead logic
            # If we had local path, we would use pdf.image(path)
            if s.source_url:
                pdf.set_text_color(37, 99, 235)
                pdf.cell(0, 6, "View Source Scheme", 0, 1, link=s.source_url)
            
            pdf.set_text_color(0, 0, 0)
            pdf.ln(10)

    # 6. Intellectual Property
    pdf.add_page()
    pdf.chapter_title("6. Intellectual Property (Patents)")
    if patents:
        for p in patents[:15]:
            expiry = p.publication_date.year + 20 if p.publication_date else 'Unknown'
            pdf.add_card(
                title=f"{p.source_id}: {p.title[:90]}...",
                detail=f"Type: {p.patent_type} | Status: {p.status} | Est. Expiry: {expiry}\nAssignee: {p.assignee}",
                link=p.url
            )
    else:
        pdf.chapter_body("No patent data available.")

    return pdf

class LandscapeDossier(FPDF):
    def __init__(self, title, subtitle):
        super().__init__()
        self.report_title = title
        self.report_subtitle = subtitle
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("Arial", "", "Arial.ttf", uni=True) if 0 else None
        
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"LetScience Landscape: {self.report_title}", 0, 1, "R")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d')} | Page {self.page_no()}", 0, 0, "C")

    def chapter_title(self, title):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(30, 41, 59)
        self.cell(0, 10, title, 0, 1, "L")
        self.ln(4)
        self.set_draw_color(226, 232, 240)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def comparison_table(self, headers, rows, col_widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(241, 245, 249)
        
        # Header
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, h, 1, 0, 'C', True)
        self.ln()
        
        # Rows
        self.set_font("Helvetica", "", 8)
        self.set_fill_color(255, 255, 255)
        
        for row in rows:
            max_lines = 1
            # Calculate max height needed
            for i, cell_text in enumerate(row):
                # Rough estimate of lines needed
                lines = len(textwrap.wrap(str(cell_text), width=int(col_widths[i]/2)))  
                if lines > max_lines: max_lines = lines
            
            height = max_lines * 5 + 4
            
            # Check page break
            if self.get_y() + height > 270:
                self.add_page()
                # Re-print header
                self.set_font("Helvetica", "B", 9)
                self.set_fill_color(241, 245, 249)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 8, h, 1, 0, 'C', True)
                self.ln()
                self.set_font("Helvetica", "", 8)
                self.set_fill_color(255, 255, 255)
            
            # Draw cells
            x_start = self.get_x()
            y_start = self.get_y()
            
            for i, cell_text in enumerate(row):
                self.set_xy(x_start + sum(col_widths[:i]), y_start)
                self.multi_cell(col_widths[i], 5, str(cell_text), border=1)
                
            self.set_xy(x_start, y_start + height) # However, multi_cell moves cursor. 
            # FPDF MultiCell logic is tricky for tables. 
            # Simplified approach: Use generic cell for single lines, truncate if too long for now to avoid layout complexity in MVP
            
                
            # Move to next row
            self.set_xy(x_start, y_start + height)
            self.ln(0) # Ensure we are on a new line logical flow if needed, but set_xy handles it.

def create_landscape_dossier(report_type, query, products, all_trials, all_patents, all_milestones):
    pdf = LandscapeDossier(f"{report_type} Analysis", query)
    pdf.add_page()
    
    # Title Page
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 20, "Comparative Landscape Report", 0, 1, "C")
    
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 10, f"{report_type}: {query}", 0, 1, "C")
    
    pdf.ln(10)
    
    # Metadata
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Products Analyzed: {len(products)}", 0, 1, "C")
    pdf.cell(0, 6, f"Total Patents: {len(all_patents)}", 0, 1, "C")
    pdf.cell(0, 6, f"Total Clinical Trials: {len(all_trials)}", 0, 1, "C")
    
    pdf.ln(20)
    
    # 1. Product Portfolio
    pdf.chapter_title("1. Portfolio Overview")
    
    headers = ["Product Name", "Phase", "Target Indication", "Description"]
    widths = [40, 30, 40, 80]
    rows = []
    
    for p in products:
        rows.append([
            p.name,
            p.development_phase,
            p.target_indication,
            p.description
        ])
        
    pdf.comparison_table(headers, rows, widths)
    pdf.ln(10)
    
    # 2. Development Comparison (Milestones)
    if all_milestones:
        pdf.add_page()
        pdf.chapter_title("2. Key Development Milestones")
        # Merged timeline
        sorted_milestones = sorted(all_milestones, key=lambda x: x.date)
        
        pdf.set_font("Helvetica", "", 9)
        for m in sorted_milestones:
            # Find product name
            p_name = next((p.name for p in products if p.id == m.product_id), "Unknown")
            
            date_str = m.date.strftime('%Y-%m')
            pdf.cell(25, 6, date_str, 0, 0)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(40, 6, p_name, 0, 0)
            pdf.set_font("Helvetica", "", 9)
            pdf.multi_cell(0, 6, f"{m.phase}: {m.event}")
            pdf.ln(2)
            
    # 3. Clinical Landscape
    pdf.add_page()
    pdf.chapter_title("3. Comparitive Clinical Status")
    
    # Group by Phase
    phases = ["Phase 3", "Phase 2", "Phase 1", "Preclinical"]
    
    for phase in phases:
        phase_trials = [t for t in all_trials if phase in t.phase]
        if phase_trials:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, phase, 0, 1)
            
            headers = ["Product", "Status", "Trial Title"]
            widths = [40, 30, 120]
            rows = []
            for t in phase_trials[:10]: # Top 10 per phase
                p_name = next((p.name for p in products if p.id == t.product_id), "Unknown")
                rows.append([p_name, t.status, t.title])
            
            pdf.comparison_table(headers, rows, widths)
            pdf.ln(5)

    return pdf

class CombinationBrief(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, "LetScience Combination Analysis Brief", 0, 1, "R")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d')}", 0, 0, "C")

def create_combination_brief(result):
    pdf = CombinationBrief()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, "Interaction Analysis Report", 0, 1, "C")
    pdf.ln(10)
    
    # Comparison Header
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(241, 245, 249)
    # Header Row
    pdf.cell(90, 12, "Drug A", 1, 0, 'C', fill=True) 
    pdf.cell(10, 12, "", 0, 0, 'C') 
    pdf.cell(90, 12, "Drug B", 1, 1, 'C', fill=True)
    
    # Names
    name_a = result['drug_a']['name']
    name_b = result['drug_b']['name']
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(90, 12, name_a, 1, 0, 'C')
    pdf.cell(10, 12, "+", 0, 0, 'C') 
    pdf.cell(90, 12, name_b, 1, 1, 'C')
    
    # Types
    type_a = result['drug_a']['mechanism_type']
    type_b = result['drug_b']['mechanism_type']
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(90, 8, type_a if type_a != 'Unknown' else '', 0, 0, 'C')
    pdf.cell(10, 8, "", 0, 0, 'C') 
    pdf.cell(90, 8, type_b if type_b != 'Unknown' else '', 0, 1, 'C')
    pdf.ln(5)
    
    # Synergy Score
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, "SYNERGY SCORE", 0, 1, "C")
    
    pdf.set_font("Helvetica", "B", 40)
    score = result['synergy_score']
    if score >= 7: pdf.set_text_color(34, 197, 94) # Green
    elif score >= 4: pdf.set_text_color(245, 158, 11) # Amber
    else: pdf.set_text_color(239, 68, 68) # Red
        
    pdf.cell(0, 15, f"{score}/10", 0, 1, "C")
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 8, result['interaction_type'], 0, 1, "C")
    pdf.ln(10)
    
    # Analysis Section
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, "Interaction & Mechanism Profile", 0, 1, "L")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "", 11)
    if result['analysis']:
        for item in result['analysis']:
            pdf.multi_cell(0, 8, f"- {item}")
    else:
        pdf.cell(0, 8, "No specific mechanistic interactions detected.", 0, 1)
    pdf.ln(8)
    
    # Safety Section
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(185, 28, 28) # Dark Red
    pdf.cell(0, 10, "Safety Warnings", 0, 1, "L")
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(127, 29, 29)
    if result['safety_warnings']:
        for w in result['safety_warnings']:
            pdf.multi_cell(0, 8, f"(!) {w}")
    else:
        pdf.set_text_color(22, 163, 74)
        pdf.cell(0, 8, "No critical overlapping toxicities detected with current data.", 0, 1)
        
    return bytes(pdf.output(dest='S'))
