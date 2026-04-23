from fpdf import FPDF
import os
from num2words import num2words

class NBPdfGenerator(FPDF):
    # Ajout du paramètre type_doc avec une valeur par défaut pour éviter les erreurs
    def __init__(self, client, conditions, total, lignes, objet, proforma, date, remise=0, type_doc="Facture Proforma"):
        super().__init__()
        self.client_name = client
        self.cond_text = conditions
        self.total_val = total 
        self.data_lignes = lignes
        self.objet_fact = objet
        self.proforma_num = proforma
        self.date_fact = date
        self.remise_taux = remise
        self.type_doc = type_doc # On stocke le type de document
        self.logo_path = "images/logo_5_5cm_300dpi.png"

    def header(self):
        if os.path.exists(self.logo_path):
            self.image(self.logo_path, x=165, y=8, w=30)
            
        self.set_font("Times", "B", 15)
        self.set_text_color(0, 0, 0) 
        self.cell(0, 8, "ENT NB POWER & AUTOMATION", ln=True)
        
        self.set_font("Times", "", 9)
        self.set_text_color(50, 50, 50)
        self.cell(0, 4, "Materiels et Equipements Electriques, Instalations et Maintenance Industrielle", ln=True)
        
        self.set_text_color(0, 0, 0)
        self.set_font("Times", "B", 8)
        self.cell(7, 4, "RC: ") 
        self.set_font("Times", "", 8)
        self.cell(55, 4, "06/00/-5827993 A 26") 
        self.cell(5, 4, " | ") 
        self.set_font("Times", "B", 8)
        self.cell(8, 4, "NIF: ") 
        self.set_font("Times", "", 8)
        self.cell(0, 4, "196193000043017800680", ln=True)
        
        self.set_font("Times", "B", 8)
        self.cell(8, 4, "RIB: ")
        self.set_font("Times", "", 8)
        self.cell(54, 4, "00021005030310000388-83")
        self.cell(5, 4, " | ")
        self.set_font("Times", "B", 8)
        self.cell(8, 4, "NIS: ")
        self.set_font("Times", "", 8)
        self.cell(0, 4, "196193000043017800680", ln=True)

        self.ln(5)
        self.set_draw_color(0, 0, 0)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
        
        # --- MODIFICATION ICI : Le titre s'adapte au type de document ---
        titre_doc = "FACTURE CLIENT :" if self.type_doc == "Facture" else "PROFORMA CLIENT :"
        
        self.set_font("Times", "B", 11)
        self.cell(120, 7, f"{titre_doc} {self.proforma_num}", ln=0)
        self.set_font("Times", "", 10)
        self.cell(0, 7, f"Bejaia le : {self.date_fact}", ln=1, align="R")
        
        curr_y = self.get_y()
        self.set_font("Times", "B", 9)
        self.cell(100, 5, "Condition de vente :", ln=1)
        self.set_font("Times", "", 8)
        self.multi_cell(100, 4, self.cond_text)
        
        self.rect(130, curr_y, 70, 25)
        self.set_xy(132, curr_y + 2)
        self.set_font("Times", "", 11) 
        self.multi_cell(65, 5, self.client_name)
        
        obj_text = str(self.objet_fact).upper() if self.objet_fact else "NON DEFINI"
        self.set_xy(10, curr_y + 28)
        self.set_font("Times", "B", 10)
        self.write(5, "OBJET : ")
        self.set_font("Times", "", 10)
        self.write(5, obj_text)
        self.ln(7)
        
        self.set_fill_color(230, 230, 230); self.set_text_color(0, 0, 0)
        self.set_font("Times", "B", 9)
        self.cell(10, 8, "N", border=1, fill=True, align="C")
        self.cell(90, 8, "DESIGNATION ARTICLE", border=1, fill=True, align="C")
        self.cell(10, 8, "U", border=1, fill=True, align="C")
        self.cell(10, 8, "QNT", border=1, fill=True, align="C")
        self.cell(35, 8, "PRIX U ", border=1, fill=True, align="C")
        self.cell(35, 8, "TOTAL ", border=1, fill=True, align="C")
        self.ln()

    def footer(self):
        self.set_y(-25)
        self.set_draw_color(0, 0, 0)
        self.line(10, self.get_y(), 200, self.get_y())
        
        self.set_font("Times", "B", 10)
        self.set_text_color(0, 0, 0) 
        self.cell(0, 5, "NB POWER... L'ASSURANCE D'UNE TECHNOLOGIE DE POINTE.", ln=True, align="C")
        
        self.set_text_color(0, 0, 0)
        self.set_font("Times", "", 8)
        
        adresse_email = "Tizi ighil ouzoug Bejaia 06000 | "
        email_val = "Nbpower.contact@gmail.com"
        
        total_w = self.get_string_width(adresse_email) + self.get_string_width("Email: ") + self.get_string_width(email_val) + 10
        start_x = (210 - total_w) / 2
        
        self.set_x(start_x)
        self.set_font("Times", "", 8)
        self.cell(self.get_string_width(adresse_email), 4, adresse_email)
        self.set_font("Times", "B", 8) 
        self.cell(self.get_string_width("Email: "), 4, "Email: ")
        self.set_font("Times", "", 8) 
        self.cell(0, 4, email_val, ln=True)

        tel_val = "0550555257 / 0770259829"
        total_w_tel = self.get_string_width("Tel: ") + self.get_string_width(tel_val)
        start_x_tel = (210 - total_w_tel) / 2
        
        self.set_x(start_x_tel)
        self.set_font("Times", "B", 8) 
        self.cell(self.get_string_width("Tel: "), 4, "Tel: ")
        self.set_font("Times", "", 8) 
        self.cell(0, 4, tel_val, ln=True, align="L")

    def draw_table_lines(self, start_y, end_y, cols_x):
        """Dessine les lignes verticales continues du tableau."""
        for x in cols_x:
            self.line(x, start_y, x, end_y)

    def generer(self):
        self.add_page()
        self.set_text_color(0, 0, 0)
        count = 1
        cols_x = [10, 20, 110, 120, 130, 165, 200]
        limit_y = 185 # Limite de hauteur du tableau avant les totaux
        
        start_table_y = self.get_y() 
        
        for lig in self.data_lignes:
            text = f" {lig[0]}"
            
            lines = text.split('\n')
            total_lines = 0
            for line in lines:
                width = self.get_string_width(line)
                total_lines += max(1, int(width / 85) + 1)
            row_h = total_lines * 5 
            
            if self.get_y() + row_h > limit_y:
                self.draw_table_lines(start_table_y, limit_y, cols_x)
                self.line(10, limit_y, 200, limit_y)
                
                self.add_page()
                start_table_y = self.get_y() 
                
            curr_y = self.get_y()
            
            self.set_font("Times", "", 9) 
            self.set_xy(cols_x[0], curr_y); self.cell(10, 5, str(count), align="C")
            self.set_xy(cols_x[2], curr_y); self.cell(10, 5, str(lig[1]), align="C")
            
            try: qnt = int(float(str(lig[2]).replace(",", ".")))
            except: qnt = lig[2]
            self.set_xy(cols_x[3], curr_y); self.cell(10, 5, str(qnt), align="C")
            
            try: px_u = float(str(lig[3]).replace(" ", "").replace("DZD", "").replace(",", "."))
            except: px_u = 0.0
            self.set_xy(cols_x[4], curr_y); self.cell(35, 5, f"{px_u:,.2f}".replace(",", " "), align="C")
            
            try: tot_l = float(str(lig[4]).replace(" ", "").replace("DZD", "").replace(",", "."))
            except: tot_l = 0.0
            self.set_xy(cols_x[5], curr_y); self.cell(35, 5, f"{tot_l:,.2f}".replace(",", " "), align="C")
            
            self.set_font("Times", "B", 9)
            self.set_xy(cols_x[1], curr_y)
            self.multi_cell(90, 5, text, align="L") 
            
            self.set_y(self.get_y() + 2)
            count += 1

        current_y = self.get_y()
        if current_y < limit_y:
            self.draw_table_lines(start_table_y, limit_y, cols_x)
            self.set_y(limit_y) 
            
        self.line(10, limit_y, 200, limit_y) 
        
        # --- CALCULS FINANCIERS ---
        total_ht_brut = self.total_val
        val_remise = total_ht_brut * (self.remise_taux / 100)
        ht_net = total_ht_brut - val_remise
        tva_val = ht_net * 0.19
        total_ttc = ht_net + tva_val

        y_blocks = self.get_y() + 5

        self.set_y(y_blocks)
        self.set_x(10)
        self.set_font("Times", "U", 10)
        
        # --- MODIFICATION ICI : La phrase d'arrêt s'adapte au type de document ---
        mot_facture = "facture" if self.type_doc == "Facture" else "facture proforma"
        self.cell(0, 6, f"Arrêtée la présente {mot_facture} a la somme de :", ln=True)
        
        dinars = int(total_ttc)
        centimes = int(round((total_ttc - dinars) * 100))
        ttc_lettres = num2words(dinars, lang='fr').upper() + " DINARS"
        if centimes > 0:
            ttc_lettres += " ET " + num2words(centimes, lang='fr').upper() + " CENTIMES"
        else:
            ttc_lettres += " PILE"
            
        self.set_x(15)
        self.set_font("Times", "B", 10)
        self.multi_cell(110, 6, ttc_lettres)

        # --- BLOC TOTAUX MODIFIÉ ---
        self.set_y(y_blocks)
        self.set_font("Times", "", 10) 
        
        self.set_x(130)
        self.cell(35, 7, "TOTAL HT", border=1)
        self.cell(35, 7, f"{total_ht_brut:,.2f}".replace(",", " ") + " DZD", border=1, align="C", ln=1)
        
        self.set_x(130)
        self.cell(35, 7, f"REMISE ", border=1)
        self.cell(35, 7, f"{val_remise:,.2f}".replace(",", " ") + " DZD", border=1, align="C", ln=1)
        
        self.set_x(130)
        self.cell(35, 7, "HT-NET", border=1)
        self.cell(35, 7, f"{ht_net:,.2f}".replace(",", " ") + " DZD", border=1, align="C", ln=1)
        
        self.set_x(130)
        self.cell(35, 7, "TVA (19%)", border=1)
        self.cell(35, 7, f"{tva_val:,.2f}".replace(",", " ") + " DZD", border=1, align="C", ln=1)
        
        self.set_x(130)
        self.cell(35, 7, "TOTAL TTC", border=1)
        self.cell(35, 7, f"{total_ttc:,.2f}".replace(",", " ") + " DZD", border=1, align="C", ln=1)
        
        self.set_x(130)
        self.set_fill_color(230, 230, 230)
        self.set_font("Times", "B", 11)
        self.cell(35, 8, "NET A PAYER", border=1, fill=True)
        self.cell(35, 8, f"{total_ttc:,.2f}".replace(",", " ") + " DZD", border=1, fill=True, align="C", ln=1)
        
        name = f"Facture_{self.proforma_num.replace(' ', '_')}.pdf"
        self.output(name)
        os.startfile(name)