import sqlite3
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QDialog, 
                             QLineEdit, QFormLayout, QFrame, QMessageBox, QProgressBar,
                             QFileDialog, QComboBox, QDateEdit, QScrollArea)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QPixmap, QIcon
from style import NBStyle
from fpdf import FPDF

# --- CLASSE GÉNÉRATRICE DU PDF DE LA FICHE DE PAIE ---
class PayrollPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.logo_path = "images/logo_5_5cm_300dpi.png"

    def add_payslip(self, emp_name, emp_poste, date_entree, month_year, total_hours, taux_horaire, primes, frais, acomptes):
        self.add_page()
        self.set_text_color(0, 0, 0)
        
        # --- EN-TÊTE ENTREPRISE ---
        if os.path.exists(self.logo_path):
            self.image(self.logo_path, x=165, y=8, w=30)
            
        self.set_font("Times", "B", 15)
        self.cell(0, 8, "ENT NB POWER & AUTOMATION", ln=True)
        self.set_font("Times", "", 9)
        self.set_text_color(100, 100, 100)
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
        self.ln(5)
        self.set_draw_color(0, 0, 0)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(10)

        # --- TITRE DU DOCUMENT ---
        self.set_font("Times", "B", 16)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 12, "BULLETIN DE PAIE", border=1, fill=True, align="C", ln=True)
        self.ln(5)

        # --- BLOC INFORMATIONS EMPLOYÉ ---
        self.set_font("Times", "B", 10)
        self.cell(30, 6, "Période :", border=0)
        self.set_font("Times", "", 10)
        self.cell(60, 6, month_year, border=0)
        
        self.set_font("Times", "B", 10)
        self.cell(30, 6, "Employé :", border=0)
        self.set_font("Times", "B", 11)
        self.cell(0, 6, emp_name.upper(), border=0, ln=True)

        self.set_font("Times", "B", 10)
        self.cell(30, 6, "Taux Horaire :", border=0)
        self.set_font("Times", "", 10)
        self.cell(60, 6, f"{taux_horaire:,.2f} DZD", border=0)
        
        self.set_font("Times", "B", 10)
        self.cell(30, 6, "Poste :", border=0)
        self.set_font("Times", "", 10)
        self.cell(0, 6, emp_poste, border=0, ln=True)
        
        self.set_font("Times", "B", 10)
        self.cell(120, 6, "", border=0)
        self.cell(30, 6, "Date d'entrée :", border=0)
        self.set_font("Times", "", 10)
        self.cell(0, 6, str(date_entree), border=0, ln=True)
        self.ln(10)

        # --- TABLEAU DES GAINS ET RETENUES ---
        self.set_font("Times", "B", 10)
        self.set_fill_color(220, 220, 220)
        self.cell(80, 8, "Rubrique", border=1, fill=True, align="C")
        self.cell(25, 8, "Base / Nbr", border=1, fill=True, align="C")
        self.cell(25, 8, "Taux", border=1, fill=True, align="C")
        self.cell(30, 8, "Gains (DZD)", border=1, fill=True, align="C")
        self.cell(30, 8, "Retenues (DZD)", border=1, fill=True, align="C", ln=True)

        self.set_font("Times", "", 10)
        
        # Ligne 1 : Salaire de base (Heures)
        salaire_base = total_hours * taux_horaire
        self.cell(80, 8, " Salaire de base (Heures travaillées)", border=1)
        self.cell(25, 8, f"{total_hours:.2f} h", border=1, align="C")
        self.cell(25, 8, f"{taux_horaire:.2f}", border=1, align="C")
        self.cell(30, 8, f"{salaire_base:,.2f}", border=1, align="R")
        self.cell(30, 8, "", border=1, align="C", ln=True)

        # Ligne 2 : Primes
        self.cell(80, 8, " Primes", border=1)
        self.cell(25, 8, "", border=1, align="C")
        self.cell(25, 8, "", border=1, align="C")
        self.cell(30, 8, f"{primes:,.2f}" if primes > 0 else "-", border=1, align="R")
        self.cell(30, 8, "", border=1, align="C", ln=True)

        # Ligne 3 : Frais de mission
        self.cell(80, 8, " Frais de mission / Remboursements", border=1)
        self.cell(25, 8, "", border=1, align="C")
        self.cell(25, 8, "", border=1, align="C")
        self.cell(30, 8, f"{frais:,.2f}" if frais > 0 else "-", border=1, align="R")
        self.cell(30, 8, "", border=1, align="C", ln=True)

        # Ligne 4 : Acomptes
        self.cell(80, 8, " Acomptes sur salaire", border=1)
        self.cell(25, 8, "", border=1, align="C")
        self.cell(25, 8, "", border=1, align="C")
        self.cell(30, 8, "", border=1, align="C")
        self.cell(30, 8, f"{acomptes:,.2f}" if acomptes > 0 else "-", border=1, align="R", ln=True)

        # Lignes vides pour remplir
        for _ in range(4):
            self.cell(80, 8, "", border=1)
            self.cell(25, 8, "", border=1)
            self.cell(25, 8, "", border=1)
            self.cell(30, 8, "", border=1)
            self.cell(30, 8, "", border=1, ln=True)

        # --- TOTAUX ---
        total_gains = salaire_base + primes + frais
        total_retenues = acomptes
        net_a_payer = total_gains - total_retenues

        self.set_font("Times", "B", 10)
        self.cell(130, 8, "TOTAUX", border=1, align="R")
        self.cell(30, 8, f"{total_gains:,.2f}", border=1, align="R")
        self.cell(30, 8, f"{total_retenues:,.2f}", border=1, align="R", ln=True)

        self.ln(5)
        
        # --- NET A PAYER ---
        self.set_x(120)
        self.set_fill_color(26, 74, 124) # Bleu NB POWER
        self.set_text_color(255, 255, 255)
        self.set_font("Times", "B", 12)
        self.cell(40, 10, "NET A PAYER :", border=1, fill=True, align="C")
        self.set_text_color(0, 0, 0)
        self.cell(40, 10, f"{net_a_payer:,.2f} DZD", border=1, align="C", ln=True)
        self.ln(20)

        # --- SIGNATURES ---
        self.set_font("Times", "BU", 10)
        self.cell(95, 6, "Signature de l'Employé", align="C")
        self.cell(95, 6, "Signature de l'Employeur", align="C", ln=True)

# --- 1. FENÊTRE PROFIL EMPLOYÉ (L'OEIL) ---
class EmployeeProfileDialog(QDialog):
    def __init__(self, emp_id, month_year, taux_horaire):
        super().__init__()
        self.setWindowTitle("Fiche Profil Employé")
        self.setFixedSize(500, 600)
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(self)
        conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
        cursor.execute("SELECT nom, poste, photo, date_entree FROM employes WHERE id=?", (emp_id,))
        emp = cursor.fetchone()
        
        header = QHBoxLayout()
        photo_lbl = QLabel()
        photo_lbl.setFixedSize(100, 100)
        if emp[2] and os.path.exists(emp[2]):
            photo_lbl.setPixmap(QPixmap(emp[2]).scaled(100, 100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        else: photo_lbl.setText("👤")
        photo_lbl.setStyleSheet("border-radius: 50px; border: 2px solid #3498db; background: #f8f9fa;")
        photo_lbl.setAlignment(Qt.AlignCenter)
        
        info_vbox = QVBoxLayout()
        name_lbl = QLabel(emp[0]); name_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a4a7c;")
        poste_lbl = QLabel(f"{emp[1]} | Entré le : {emp[3]}"); poste_lbl.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        info_vbox.addWidget(name_lbl); info_vbox.addWidget(poste_lbl)
        header.addWidget(photo_lbl); header.addLayout(info_vbox)
        layout.addLayout(header)

        layout.addWidget(QLabel(f"<b>Historique de Pointage : {month_year}</b>"))
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        hist_table = QTableWidget(0, 4); hist_table.setHorizontalHeaderLabels(["Date", "Entrée", "Sortie", "Total Jour"])
        hist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        cursor.execute("SELECT date, heure_entree, heure_sortie, prime, frais_mission, acompte FROM pointage WHERE employe_id=? AND date LIKE ?", (emp_id, f"%{month_year}"))
        total_mois = 0
        for p in cursor.fetchall():
            row = hist_table.rowCount(); hist_table.insertRow(row)
            hist_table.setItem(row, 0, QTableWidgetItem(p[0]))
            hist_table.setItem(row, 1, QTableWidgetItem(p[1]))
            hist_table.setItem(row, 2, QTableWidgetItem(p[2]))
            try:
                delta = datetime.strptime(p[2], "%H:%M") - datetime.strptime(p[1], "%H:%M")
                tj = (delta.total_seconds() / 3600 * taux_horaire) + p[3] + p[4] - p[5]
            except: tj = 0
            total_mois += tj
            hist_table.setItem(row, 3, QTableWidgetItem(f"{tj:,.2f} DZD"))

        scroll.setWidget(hist_table); layout.addWidget(scroll)
        footer = QLabel(f"TOTAL CUMULÉ DU MOIS : {total_mois:,.2f} DZD")
        footer.setStyleSheet("font-size: 16px; font-weight: bold; color: #2e7d32; padding: 10px; background: #e8f5e9; border-radius: 5px;")
        footer.setAlignment(Qt.AlignCenter); layout.addWidget(footer)
        conn.close()

# --- 2. FENÊTRE IMPRESSION FICHE DE PAIE ---
class PrintPayrollDialog(QDialog):
    def __init__(self, taux_horaire):
        super().__init__()
        self.taux_horaire = taux_horaire
        self.setWindowTitle("Imprimer Fiches de Paie")
        self.setFixedSize(400, 350); self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 20, 30, 20)

        layout.addWidget(QLabel("<b>Paramètres d'impression</b>"), alignment=Qt.AlignCenter)

        form = QFormLayout(); form.setSpacing(15)
        self.combo_emp = QComboBox(); self.combo_emp.addItem("Tous les employés", 0)
        self.load_employes_list()
        
        self.combo_mois = QComboBox()
        self.combo_mois.addItems(["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])
        self.combo_mois.setCurrentIndex(datetime.now().month - 1)
        
        self.combo_annee = QComboBox()
        cur_y = datetime.now().year
        self.combo_annee.addItems([str(y) for y in range(cur_y-1, cur_y+2)]); self.combo_annee.setCurrentText(str(cur_y))

        form.addRow("Employé :", self.combo_emp); form.addRow("Mois :", self.combo_mois); form.addRow("Année :", self.combo_annee)
        layout.addLayout(form)

        btn_print = QPushButton(" ⎙ Générer & Imprimer"); btn_print.setFixedHeight(45)
        btn_print.setStyleSheet("background: #e67e22; color: white; font-weight: bold; border-radius: 5px;")
        btn_print.clicked.connect(self.generate_batch_pdf); layout.addWidget(btn_print)

    def load_employes_list(self):
        conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
        cursor.execute("SELECT id, nom FROM employes")
        for eid, nom in cursor.fetchall(): self.combo_emp.addItem(nom, eid)
        conn.close()

    def generate_batch_pdf(self):
        emp_id = self.combo_emp.currentData()
        mois_str = f"{self.combo_mois.currentIndex() + 1:02d}"
        annee_str = self.combo_annee.currentText()
        filter_date = f"{mois_str}/{annee_str}"
        
        pdf = PayrollPDF()
        conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
        
        if emp_id == 0:
            cursor.execute("SELECT id FROM employes")
            employes = cursor.fetchall()
        else:
            employes = [(emp_id,)]
            
        lignes_ajoutees = 0
            
        for (eid,) in employes:
            cursor.execute("SELECT nom, poste, date_entree FROM employes WHERE id=?", (eid,))
            emp = cursor.fetchone()
            if not emp: continue
            
            cursor.execute("SELECT heure_entree, heure_sortie, prime, frais_mission, acompte FROM pointage WHERE employe_id=? AND date LIKE ?", (eid, f"%{filter_date}"))
            pointages = cursor.fetchall()
            
            if not pointages: continue # Ne pas imprimer de fiche vide si l'employé n'a pas travaillé
            
            t_heures = t_prime = t_frais = t_acompte = 0
            for e, s, p, f, a in pointages:
                try:
                    delta = datetime.strptime(s, "%H:%M") - datetime.strptime(e, "%H:%M")
                    t_heures += delta.total_seconds() / 3600
                except: pass
                t_prime += (p or 0); t_frais += (f or 0); t_acompte += (a or 0)
                
            pdf.add_payslip(emp[0], emp[1], emp[2], filter_date, t_heures, self.taux_horaire, t_prime, t_frais, t_acompte)
            lignes_ajoutees += 1
            
        conn.close()
        
        if lignes_ajoutees > 0:
            filename = f"Fiches_Paie_{filter_date.replace('/', '_')}.pdf"
            pdf.output(filename)
            os.startfile(filename)
            self.accept()
        else:
            QMessageBox.information(self, "Information", "Aucun pointage trouvé pour cette période.")

# --- 3. FENÊTRE AJOUT EMPLOYÉ ---
class AddEmployeeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nouveau Collaborateur")
        self.setFixedSize(450, 580)
        self.setStyleSheet("background-color: white;")
        self.image_path = ""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        self.lbl_photo = QLabel("Pas de\nphoto")
        self.lbl_photo.setFixedSize(110, 110)
        self.lbl_photo.setAlignment(Qt.AlignCenter) 
        self.lbl_photo.setStyleSheet("""
            QLabel {
                border: 2px dashed #d5d8dc; 
                border-radius: 55px; 
                background: #f8f9fa; 
                color: #7f8c8d; 
                font-weight: bold;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.lbl_photo, alignment=Qt.AlignCenter)
        
        btn_browse = QPushButton("Choisir une Photo")
        btn_browse.setCursor(Qt.PointingHandCursor)
        btn_browse.setFixedSize(160, 35)
        btn_browse.clicked.connect(self.select_photo)
        btn_browse.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                border-radius: 5px; 
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(btn_browse, alignment=Qt.AlignCenter)

        form = QFormLayout()
        form.setSpacing(15)
        self.in_nom = QLineEdit()
        self.in_nom.setPlaceholderText("Nom et Prénom de l'employé")
        
        self.cb_poste = QComboBox()
        self.cb_poste.addItems(["Technicien", "Ingénieur", "Electricien", "Aid Electricien"])
        
        self.in_date = QLineEdit(datetime.now().strftime("%d/%m/%Y"))
        
        form.addRow("Nom & Prénom:", self.in_nom)
        form.addRow("Poste:", self.cb_poste)
        form.addRow("Date d'entrée:", self.in_date)
        layout.addLayout(form)
        
        layout.addStretch() 

        btn_save = QPushButton("Enregistrer le Collaborateur")
        btn_save.setFixedHeight(45)
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.save)
        btn_save.setStyleSheet("""
            QPushButton {
                background: #1a4a7c; 
                color: white; 
                font-weight: bold; 
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #143a62;
            }
        """)
        layout.addWidget(btn_save)

    def select_photo(self):
        file, _ = QFileDialog.getOpenFileName(self, "Choisir une Image", "", "Images (*.png *.jpg *.jpeg)")
        if file:
            self.image_path = file
            pixmap = QPixmap(file)
            self.lbl_photo.setPixmap(pixmap.scaled(110, 110, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            self.lbl_photo.setStyleSheet("border: 2px solid #3498db; border-radius: 55px; background: #f8f9fa;")

    def save(self):
        if not self.in_nom.text().strip():
            return
        
        try:
            conn = sqlite3.connect("gestion_nb.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO employes (nom, poste, photo, date_entree) VALUES (?,?,?,?)",
                           (self.in_nom.text().strip(), self.cb_poste.currentText(), self.image_path, self.in_date.text()))
            conn.commit()
            conn.close()
            self.accept()
        except Exception as e:
            print(f"Erreur lors de l'enregistrement : {e}")

# --- 4. FENÊTRE POINTAGE ---
class PointageDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nouveau Pointage"); self.setFixedSize(450, 520); self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(self); layout.setContentsMargins(30, 20, 30, 20)
        
        form = QFormLayout()
        self.date_input = QDateEdit(QDate.currentDate()); self.date_input.setCalendarPopup(True)
        self.combo_emp = QComboBox(); self.load_emps_combo()
        self.in_ent = QLineEdit("08:00"); self.in_sor = QLineEdit("17:00")
        self.in_p = QLineEdit("0"); self.in_f = QLineEdit("0"); self.in_a = QLineEdit("0")
        form.addRow("Date:", self.date_input); form.addRow("Employé:", self.combo_emp); form.addRow("Entrée:", self.in_ent); form.addRow("Sortie:", self.in_sor)
        form.addRow("Prime:", self.in_p); form.addRow("Frais:", self.in_f); form.addRow("Acompte:", self.in_a)
        layout.addLayout(form)
        
        btn = QPushButton("Enregistrer"); btn.clicked.connect(self.save)
        btn.setStyleSheet("background: #1a4a7c; color: white; font-weight: bold; height: 40px;"); layout.addWidget(btn)

    def load_emps_combo(self):
        conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
        cursor.execute("SELECT id, nom FROM employes")
        for eid, nom in cursor.fetchall(): self.combo_emp.addItem(nom, eid)
        conn.close()

    def save(self):
        try:
            conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
            cursor.execute("INSERT INTO pointage (employe_id, date, heure_entree, heure_sortie, prime, frais_mission, acompte, etat) VALUES (?,?,?,?,?,?,?,?)",
                           (self.combo_emp.currentData(), self.date_input.date().toString("dd/MM/yyyy"), self.in_ent.text(), self.in_sor.text(), 
                            float(self.in_p.text() or 0), float(self.in_f.text() or 0), float(self.in_a.text() or 0), "Pointé"))
            conn.commit(); conn.close(); self.accept()
        except: QMessageBox.critical(self, "Erreur", "Données invalides")

# --- 5. CLASSE PRINCIPALE RH ---
class RHManager(QWidget):
    def __init__(self):
        super().__init__()
        self.TAUX_HORAIRE = 216.345
        self.current_view_date = datetime.now().replace(day=1)
        self.layout = QVBoxLayout(self); self.layout.setContentsMargins(20, 20, 20, 20); self.layout.setSpacing(10)
        
        header = QHBoxLayout(); title = QLabel("Gestion des Employés"); title.setStyleSheet("font-size: 26px; font-weight: bold; color: #1a4a7c;")
        btn_vbox = QVBoxLayout()
        self.btn_add = QPushButton(" + Ajouter un Employé"); self.btn_add.setFixedSize(200, 40); self.btn_add.setStyleSheet("background: #e67e22; color: white; border-radius: 8px; font-weight: bold;")
        self.btn_add.clicked.connect(self.open_add_emp)
        self.btn_del_emp = QPushButton(" 🗑 Supprimer un Employé"); self.btn_del_emp.setFixedSize(200, 35); self.btn_del_emp.setStyleSheet("background: #c0392b; color: white; border-radius: 8px; font-size: 11px;")
        self.btn_del_emp.clicked.connect(self.delete_employee_permanent)
        btn_vbox.addWidget(self.btn_add); btn_vbox.addWidget(self.btn_del_emp)
        header.addWidget(title); header.addStretch(); header.addLayout(btn_vbox); self.layout.addLayout(header)

        stats_layout = QHBoxLayout()
        self.card_actifs = self.create_rh_card("Employés Actifs", "0", "👤", "#3498db")
        self.card_pres = self.create_progress_card("Pointés ce mois", 0, 1) 
        stats_layout.addWidget(self.card_actifs); stats_layout.addWidget(self.card_pres); stats_layout.addStretch(); self.layout.addLayout(stats_layout)

        nav_layout = QHBoxLayout()
        self.btn_pt = QPushButton("⚙ Effectuer Pointage"); self.btn_pt.setFixedSize(170, 38); self.btn_pt.setStyleSheet("background: #546e7a; color: white; font-weight: bold; border-radius: 5px;")
        self.btn_pt.clicked.connect(self.open_pointage_dialog)
        self.btn_print_p = QPushButton("⎙ Imprimer Fiches de Paie"); self.btn_print_p.setFixedSize(190, 38); self.btn_print_p.setStyleSheet("background: #f8f9fa; color: #2c3e50; border: 1px solid #cfd8dc; border-radius: 5px;")
        # Modification ici pour envoyer le Taux Horaire à la boite de dialogue
        self.btn_print_p.clicked.connect(lambda: PrintPayrollDialog(self.TAUX_HORAIRE).exec_())
        nav_layout.addWidget(self.btn_pt); nav_layout.addWidget(self.btn_print_p); nav_layout.addStretch()

        month_nav = QFrame(); month_nav.setStyleSheet("background: white; border-radius: 5px; border: 1px solid #cfd8dc;")
        mn_l = QHBoxLayout(month_nav); mn_l.setContentsMargins(5, 2, 5, 2)
        self.btn_p = QPushButton("<"); self.btn_p.setFixedSize(30, 30); self.btn_p.clicked.connect(self.prev_month)
        self.lbl_m = QLabel(""); self.lbl_m.setStyleSheet("font-weight: bold; min-width: 120px;"); self.lbl_m.setAlignment(Qt.AlignCenter)
        self.btn_n = QPushButton(">"); self.btn_n.setFixedSize(30, 30); self.btn_n.clicked.connect(self.next_month)
        mn_l.addWidget(self.btn_p); mn_l.addWidget(self.lbl_m); mn_l.addWidget(self.btn_n); nav_layout.addWidget(month_nav)
        self.layout.addLayout(nav_layout)

        self.table = QTableWidget(0, 6); self.table.setHorizontalHeaderLabels(["Employé", "Entrée", "Sortie", "État", "💰 Total Mois", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("background: white; border-radius: 8px;"); self.layout.addWidget(self.table)
        self.update_month_display()

    def create_rh_card(self, title, value, icon, color):
        card = QFrame(); card.setFixedSize(280, 90); NBStyle.add_shadow(card)
        l = QHBoxLayout(card); icon_lbl = QLabel(icon); icon_lbl.setStyleSheet(f"font-size: 26px; color: {color}; background: #f5f7f9; border-radius: 25px; padding: 10px;")
        vbox = QVBoxLayout(); v = QLabel(value); v.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a4a7c;"); v.setObjectName("val")
        t = QLabel(title); t.setStyleSheet("color: #90a4ae; font-size: 11px;"); vbox.addWidget(v); vbox.addWidget(t)
        l.addWidget(icon_lbl); l.addLayout(vbox); return card

    def create_progress_card(self, title, current, total):
        card = QFrame(); card.setFixedSize(280, 90); NBStyle.add_shadow(card)
        l = QHBoxLayout(card); icon_lbl = QLabel("📅"); icon_lbl.setStyleSheet("font-size: 26px; background: #f5f7f9; border-radius: 25px; padding: 10px;")
        vbox = QVBoxLayout(); val_lbl = QLabel(""); val_lbl.setStyleSheet("font-size: 13px; font-weight: bold;"); val_lbl.setObjectName("progress_val")
        pbar = QProgressBar(); pbar.setObjectName("pbar"); pbar.setFixedHeight(6); pbar.setTextVisible(False)
        pbar.setStyleSheet("QProgressBar::chunk { background: #3498db; }")
        vbox.addWidget(val_lbl); vbox.addWidget(pbar); l.addWidget(icon_lbl); l.addLayout(vbox); return card

    def update_month_display(self):
        fr = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
        self.lbl_m.setText(f"{fr[self.current_view_date.month-1]} {self.current_view_date.year}"); self.load_data()

    def prev_month(self): self.current_view_date = (self.current_view_date.replace(day=1) - timedelta(days=1)).replace(day=1); self.update_month_display()
    def next_month(self):
        m, y = self.current_view_date.month, self.current_view_date.year
        self.current_view_date = self.current_view_date.replace(year=y+(m==12), month=(m%12)+1, day=1); self.update_month_display()

    def open_add_emp(self): 
        if AddEmployeeDialog().exec_(): self.load_data()
    def open_pointage_dialog(self): 
        if PointageDialog().exec_(): self.load_data()

    def delete_employee_permanent(self):
        dialog = QDialog(self); dialog.setWindowTitle("Supprimer un Employé"); dialog.setFixedSize(350, 200)
        l = QVBoxLayout(dialog); l.addWidget(QLabel("<b>Sélectionner l'employé :</b>"))
        combo = QComboBox(); conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
        cursor.execute("SELECT id, nom FROM employes"); emps = cursor.fetchall()
        for eid, nom in emps: combo.addItem(nom, eid)
        l.addWidget(combo); l.addStretch(); btn = QPushButton("Confirmer"); btn.setStyleSheet("background: #c0392b; color: white; font-weight: bold; height: 35px;"); l.addWidget(btn)
        def do_del():
            if QMessageBox.critical(self, "Attention", f"Supprimer {combo.currentText()} ?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                cursor.execute("DELETE FROM pointage WHERE employe_id=?", (combo.currentData(),))
                cursor.execute("DELETE FROM employes WHERE id=?", (combo.currentData(),))
                conn.commit(); dialog.accept(); self.load_data()
        btn.clicked.connect(do_del); dialog.exec_(); conn.close()

    def generate_single_payslip(self, emp_id, filter_date):
        try:
            pdf = PayrollPDF()
            conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
            
            cursor.execute("SELECT nom, poste, date_entree FROM employes WHERE id=?", (emp_id,))
            emp = cursor.fetchone()
            if not emp: return
            
            cursor.execute("SELECT heure_entree, heure_sortie, prime, frais_mission, acompte FROM pointage WHERE employe_id=? AND date LIKE ?", (emp_id, f"%{filter_date}"))
            pointages = cursor.fetchall()
            
            if not pointages:
                QMessageBox.warning(self, "Attention", "Aucun pointage trouvé pour cet employé ce mois-ci.")
                return
            
            t_heures = t_prime = t_frais = t_acompte = 0
            for e, s, p, f, a in pointages:
                try:
                    delta = datetime.strptime(s, "%H:%M") - datetime.strptime(e, "%H:%M")
                    t_heures += delta.total_seconds() / 3600
                except: pass
                t_prime += (p or 0); t_frais += (f or 0); t_acompte += (a or 0)
                
            pdf.add_payslip(emp[0], emp[1], emp[2], filter_date, t_heures, self.TAUX_HORAIRE, t_prime, t_frais, t_acompte)
            conn.close()
            
            filename = f"Fiche_Paie_{emp[0].replace(' ', '_')}_{filter_date.replace('/', '_')}.pdf"
            pdf.output(filename)
            os.startfile(filename)
        except Exception as e:
            QMessageBox.critical(self, "Erreur PDF", str(e))

    def load_data(self):
        filter_date = self.current_view_date.strftime("%m/%Y")
        conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
        cursor.execute("SELECT id, nom, photo FROM employes"); employes = cursor.fetchall()
        self.table.setRowCount(0); pres_count = 0
        for eid, nom, photo in employes:
            cursor.execute("SELECT heure_entree, heure_sortie, prime, frais_mission, acompte FROM pointage WHERE employe_id=? AND date LIKE ?", (eid, f"%{filter_date}"))
            total, ent, sor, etat = 0, "--:--", "--:--", "Absent"
            for e, s, p, f, a in cursor.fetchall():
                try:
                    delta = datetime.strptime(s, "%H:%M") - datetime.strptime(e, "%H:%M")
                    total += (delta.total_seconds()/3600 * self.TAUX_HORAIRE) + (p or 0) + (f or 0) - (a or 0)
                except: pass
                ent, sor, etat = e, s, "Pointé"
            row = self.table.rowCount(); self.table.insertRow(row); item = QTableWidgetItem(f" 👤 {nom}")
            if photo and os.path.exists(photo): item.setIcon(QIcon(photo))
            self.table.setItem(row,0,item); self.table.setItem(row,1,QTableWidgetItem(ent)); self.table.setItem(row,2,QTableWidgetItem(sor))
            badge = QLabel(etat); badge.setAlignment(Qt.AlignCenter); badge.setStyleSheet(f"background: {'#e8f5e9' if etat == 'Pointé' else '#ffebee'}; color: {'#2e7d32' if etat == 'Pointé' else '#c62828'}; border-radius: 5px; font-weight: bold;")
            if etat == "Pointé": pres_count += 1
            self.table.setCellWidget(row,3,badge); self.table.setItem(row,4,QTableWidgetItem(f"{total:,.2f} DZD"))
            
            actions = QWidget(); al = QHBoxLayout(actions); al.setContentsMargins(0,0,0,0)
            btn_eye = QPushButton("👁"); btn_eye.clicked.connect(lambda ch, id=eid: EmployeeProfileDialog(id, filter_date, self.TAUX_HORAIRE).exec_())
            
            # --- MODIFICATION ICI : BOUTON IMPRIMER ⎙ ---
            btn_prnt = QPushButton("⎙")
            btn_prnt.setToolTip("Imprimer Fiche de Paie")
            btn_prnt.clicked.connect(lambda ch, id=eid: self.generate_single_payslip(id, filter_date))
            
            btn_del = QPushButton("🗑")
            btn_del.setToolTip("Vider les pointages du mois")
            btn_del.clicked.connect(lambda ch, id=eid: self.delete_monthly_points(id, filter_date))
            
            for b in [btn_eye, btn_prnt, btn_del]: 
                b.setFixedSize(28,28); al.addWidget(b)
            self.table.setCellWidget(row,5,actions)
        
        self.card_actifs.findChild(QLabel, "val").setText(str(len(employes)))
        self.card_pres.findChild(QLabel, "progress_val").setText(f"{pres_count} Pointés en {self.lbl_m.text()}")
        p = self.card_pres.findChild(QProgressBar, "pbar")
        p.setMaximum(len(employes) if employes else 1); p.setValue(pres_count)
        conn.close()

    def delete_monthly_points(self, emp_id, month_year):
        if QMessageBox.question(self, "Confirmation", f"Vider le mois {month_year} pour cet employé ?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
            cursor.execute("DELETE FROM pointage WHERE employe_id=? AND date LIKE ?", (emp_id, f"%{month_year}"))
            conn.commit(); conn.close(); self.load_data()