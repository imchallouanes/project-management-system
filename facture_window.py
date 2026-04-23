import sqlite3
import os
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QPushButton, QLabel, 
                             QHeaderView, QTabWidget, QMessageBox, QTextEdit, QComboBox)
from PyQt5.QtCore import Qt
from pdf_generator import NBPdfGenerator

class FactureManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_db() # Sécuriser et mettre à jour la base de données au lancement
        
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.tab_ajouter = QWidget()
        self.tab_gestion = QWidget()
        
        self.tabs.addTab(self.tab_ajouter, "Ajouter / Modifier")
        self.tabs.addTab(self.tab_gestion, "Liste / Gestion")
        
        self.setup_tab_ajouter()
        self.setup_tab_gestion()
        self.layout.addWidget(self.tabs)
        self.current_edit_id = None
        self.load_factures()

    def init_db(self):
        """Met à jour la base de données pour supporter les nouveaux types de documents"""
        try:
            conn = sqlite3.connect("gestion_nb.db")
            cursor = conn.cursor()
            # Créer la table si elle n'existe pas du tout
            cursor.execute('''CREATE TABLE IF NOT EXISTS factures 
                              (id INTEGER PRIMARY KEY, client TEXT, conditions TEXT, 
                               date TEXT, total REAL, objet TEXT, proforma TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS lignes_facture 
                              (id INTEGER PRIMARY KEY, facture_id INTEGER, article TEXT, 
                               unite TEXT, quantite REAL, prix_u REAL, total_ligne REAL)''')
            
            # Ajouter les nouvelles colonnes si elles manquent (pour les anciennes bases)
            cursor.execute("PRAGMA table_info(factures)")
            cols = [c[1] for c in cursor.fetchall()]
            if "remise" not in cols: 
                cursor.execute("ALTER TABLE factures ADD COLUMN remise REAL DEFAULT 0")
            if "type_doc" not in cols: 
                cursor.execute("ALTER TABLE factures ADD COLUMN type_doc TEXT DEFAULT 'Facture Proforma'")
            
            conn.commit()
            conn.close()
        except Exception as e:
            print("Erreur Init DB :", e)

    def setup_tab_ajouter(self):
        layout = QVBoxLayout(self.tab_ajouter)
        
        # --- LIGNE 1 : TYPE, CLIENT ET DATE ---
        row1 = QHBoxLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Facture Proforma", "Facture"])
        self.type_combo.setStyleSheet("padding: 5px; font-weight: bold;")
        
        self.client_input = QTextEdit()
        self.client_input.setPlaceholderText("Nom du Client\nAdresse\nContact...")
        self.client_input.setFixedHeight(65)
        
        self.date_input = QLineEdit()
        self.date_input.setText(datetime.now().strftime("%d/%m/%Y"))
        self.date_input.setFixedWidth(120)
        
        row1.addWidget(QLabel("Type :"))
        row1.addWidget(self.type_combo)
        row1.addWidget(QLabel("Infos Client :"))
        row1.addWidget(self.client_input)
        row1.addWidget(QLabel("Date :"))
        row1.addWidget(self.date_input)
        layout.addLayout(row1)

        # --- LIGNE 2 : OBJET ET CONDITIONS ---
        row2 = QHBoxLayout()
        self.objet_input = QLineEdit()
        self.objet_input.setPlaceholderText("Objet de la facture")
        self.cond_input = QLineEdit()
        self.cond_input.setPlaceholderText("Condition + Entrée...")
        self.cond_input.returnPressed.connect(self.ajouter_condition_formatee)
        row2.addWidget(QLabel("Objet :"))
        row2.addWidget(self.objet_input)
        row2.addWidget(QLabel("Conditions :"))
        row2.addWidget(self.cond_input)
        layout.addLayout(row2)

        self.cond_display = QLabel("")
        self.cond_display.setStyleSheet("color: #555; font-style: italic; padding: 5px; background: #f9f9f9; border: 1px solid #ddd;")
        layout.addWidget(self.cond_display)

        # --- TABLEAU ---
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Article", "Unité", "Qté", "Prix U", "Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellChanged.connect(self.calculate_row_total)
        layout.addWidget(self.table)
        
        # --- LIGNE BOUTONS ET REMISE ---
        btns_row = QHBoxLayout()
        btn_add_line = QPushButton("+ Ajouter ligne")
        btn_add_line.clicked.connect(self.add_new_row)
        
        btn_remove_line = QPushButton("- Supprimer ligne")
        btn_remove_line.clicked.connect(self.remove_selected_row)
        
        btn_clear = QPushButton("Vider / Annuler")
        btn_clear.clicked.connect(self.clear_form)
        
        self.remise_input = QLineEdit("0")
        self.remise_input.setFixedWidth(60)
        self.remise_input.textChanged.connect(self.update_grand_total)
        
        btns_row.addWidget(btn_add_line)
        btns_row.addWidget(btn_remove_line)
        btns_row.addWidget(btn_clear)
        btns_row.addStretch()
        btns_row.addWidget(QLabel("Remise (%) :"))
        btns_row.addWidget(self.remise_input)
        layout.addLayout(btns_row)
        
        self.label_total = QLabel("Total Général : 0.00 DZD")
        self.label_total.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a4a7c;")
        layout.addWidget(self.label_total, alignment=Qt.AlignRight)
        
        self.btn_save = QPushButton("Enregistrer le Document")
        self.btn_save.setFixedHeight(45)
        self.btn_save.setStyleSheet("background-color: #1a4a7c; color: white; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_facture)
        layout.addWidget(self.btn_save)

    def ajouter_condition_formatee(self):
        nouvelle_cond = self.cond_input.text().strip()
        if nouvelle_cond:
            texte_actuel = self.cond_display.text().strip()
            num = len(texte_actuel.split('\n')) + 1 if texte_actuel else 1
            self.cond_display.setText(f"{texte_actuel}\n{num}/ {nouvelle_cond}" if texte_actuel else f"{num}/ {nouvelle_cond}")
            self.cond_input.clear()

    def get_next_doc_num(self, client_info, type_doc):
        first_line = client_info.split('\n')[0].strip()
        premiere_lettre = first_line[0].upper() if len(first_line) > 0 else "X"
        mois_actuel = datetime.now().strftime("%m")
        
        # Le préfixe change selon le choix du sélecteur
        prefix = "FP" if type_doc == "Facture Proforma" else "F"
        
        conn = sqlite3.connect("gestion_nb.db")
        cursor = conn.cursor()
        # On compte les documents du même type pour ce client
        cursor.execute("SELECT COUNT(*) FROM factures WHERE client LIKE ? AND type_doc = ?", (f"{first_line}%", type_doc))
        count = cursor.fetchone()[0] + 1
        conn.close()
        
        return f"{prefix}{premiere_lettre}{count:03d}-{mois_actuel}"

    def calculate_row_total(self, row, col):
        if col in [2, 3]:
            self.table.blockSignals(True)
            try:
                q = float(self.table.item(row, 2).text().replace(",", ".")) if self.table.item(row, 2) else 0
                p = float(self.table.item(row, 3).text().replace(",", ".")) if self.table.item(row, 3) else 0
                self.table.setItem(row, 4, QTableWidgetItem(f"{q*p:.2f}"))
            except: pass
            self.table.blockSignals(False)
            self.update_grand_total()

    def update_grand_total(self):
        grand_total_ht = 0.0
        for i in range(self.table.rowCount()):
            try:
                item = self.table.item(i, 4)
                if item: grand_total_ht += float(item.text())
            except: pass
        
        try:
            remise_taux = float(self.remise_input.text().replace(",", "."))
        except: remise_taux = 0.0
            
        remise_val = grand_total_ht * (remise_taux / 100)
        ht_net = grand_total_ht - remise_val
        total_ttc = ht_net * 1.19
        self.label_total.setText(f"Net à Payer : {total_ttc:,.2f} DZD")

    def save_facture(self):
        client = self.client_input.toPlainText().strip()
        if not client:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir les infos client.")
            return
            
        type_doc = self.type_combo.currentText()
        num_doc = self.get_next_doc_num(client, type_doc)
        
        try:
            conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
            
            total_val = 0.0
            for i in range(self.table.rowCount()): 
                try: total_val += float(self.table.item(i,4).text())
                except: pass
                
            remise_taux = float(self.remise_input.text().replace(",", ".") or 0)

            if self.current_edit_id:
                cursor.execute("UPDATE factures SET client=?, conditions=?, date=?, total=?, objet=?, remise=?, type_doc=? WHERE id=?", 
                               (client, self.cond_display.text(), self.date_input.text(), total_val, self.objet_input.text(), remise_taux, type_doc, self.current_edit_id))
                cursor.execute("DELETE FROM lignes_facture WHERE facture_id=?", (self.current_edit_id,))
                f_id = self.current_edit_id
            else:
                cursor.execute("INSERT INTO factures (client, conditions, date, total, objet, proforma, remise, type_doc) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                               (client, self.cond_display.text(), self.date_input.text(), total_val, self.objet_input.text(), num_doc, remise_taux, type_doc))
                f_id = cursor.lastrowid

            for i in range(self.table.rowCount()):
                widget_article = self.table.cellWidget(i, 0)
                texte_article = widget_article.toPlainText().strip() if widget_article else ""
                
                cursor.execute("INSERT INTO lignes_facture (facture_id, article, unite, quantite, prix_u, total_ligne) VALUES (?,?,?,?,?,?)",
                               (f_id, texte_article, 
                                self.table.item(i,1).text() if self.table.item(i,1) else "",
                                self.table.item(i,2).text() if self.table.item(i,2) else "0", 
                                self.table.item(i,3).text() if self.table.item(i,3) else "0", 
                                self.table.item(i,4).text() if self.table.item(i,4) else "0"))
            conn.commit(); conn.close()
            QMessageBox.information(self, "Succès", f"{type_doc} enregistrée avec succès.")
            self.clear_form()
            self.load_factures()
            self.tabs.setCurrentIndex(1) # Basculer automatiquement vers la liste après l'enregistrement
        except Exception as e: 
            QMessageBox.critical(self, "Erreur", str(e))

    def setup_tab_gestion(self):
        layout = QVBoxLayout(self.tab_gestion)
        self.list_table = QTableWidget(0, 6)
        self.list_table.setHorizontalHeaderLabels(["ID", "Type", "N° Doc", "Client", "Total", "Actions"])
        self.list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Ajuster les largeurs des colonnes ID et Actions
        self.list_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.list_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        layout.addWidget(self.list_table)
        
        btn_refresh = QPushButton("Actualiser la liste")
        btn_refresh.clicked.connect(self.load_factures)
        layout.addWidget(btn_refresh)

    def load_factures(self):
        try:
            conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
            # On récupère aussi le type de document
            cursor.execute("SELECT id, proforma, client, total, remise, type_doc FROM factures ORDER BY id DESC")
            rows = cursor.fetchall()
            self.list_table.setRowCount(0)
            for r_data in rows:
                idx = self.list_table.rowCount()
                self.list_table.insertRow(idx)
                
                ht_net = r_data[3] * (1 - (r_data[4]/100))
                ttc = ht_net * 1.19
                
                type_doc_text = str(r_data[5]) if r_data[5] else "Facture Proforma"
                
                self.list_table.setItem(idx, 0, QTableWidgetItem(str(r_data[0])))
                self.list_table.setItem(idx, 1, QTableWidgetItem(type_doc_text))
                self.list_table.setItem(idx, 2, QTableWidgetItem(str(r_data[1] or "---")))
                self.list_table.setItem(idx, 3, QTableWidgetItem(str(r_data[2].split('\n')[0])))
                self.list_table.setItem(idx, 4, QTableWidgetItem(f"{ttc:,.2f} DZD"))
                
                act_w = QWidget(); act_l = QHBoxLayout(act_w); act_l.setContentsMargins(5,2,5,2)
                b_edit = QPushButton("Modif"); b_edit.clicked.connect(lambda ch, r=r_data[0]: self.edit_facture(r))
                b_del = QPushButton("Suppr"); b_del.clicked.connect(lambda ch, r=r_data[0]: self.delete_facture(r))
                b_pdf = QPushButton("PDF"); b_pdf.clicked.connect(lambda ch, r=r_data[0]: self.print_existing(r))
                act_l.addWidget(b_edit); act_l.addWidget(b_del); act_l.addWidget(b_pdf)
                self.list_table.setCellWidget(idx, 5, act_w)
            conn.close()
        except Exception as e: 
            print("Erreur Chargement :", e)

    def edit_facture(self, f_id):
        conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
        cursor.execute("SELECT client, conditions, objet, date, remise, type_doc FROM factures WHERE id=?", (f_id,))
        f = cursor.fetchone()
        if f:
            self.clear_form()
            self.current_edit_id = f_id
            
            self.client_input.setPlainText(f[0])
            self.cond_display.setText(f[1])
            self.objet_input.setText(f[2])
            self.date_input.setText(f[3])
            self.remise_input.setText(str(f[4]))
            
            # Restaurer le bon type de document dans la liste déroulante
            type_doc = str(f[5]) if f[5] else "Facture Proforma"
            index = self.type_combo.findText(type_doc)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
            
            cursor.execute("SELECT article, unite, quantite, prix_u, total_ligne FROM lignes_facture WHERE facture_id=?", (f_id,))
            for r_data in cursor.fetchall():
                r = self.table.rowCount()
                self.table.insertRow(r)
                
                text_edit = QTextEdit()
                text_edit.setPlainText(str(r_data[0]))
                text_edit.setStyleSheet("border: none; background-color: transparent;")
                self.table.setCellWidget(r, 0, text_edit)
                
                for c, v in enumerate(r_data[1:], start=1): 
                    self.table.setItem(r, c, QTableWidgetItem(str(v)))
                self.table.setRowHeight(r, 60)
                
            self.tabs.setCurrentIndex(0)
            self.update_grand_total()
        conn.close()

    def delete_facture(self, f_id):
        if QMessageBox.question(self, "Supprimer", "Confirmer la suppression définitive ?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            try:
                conn = sqlite3.connect("gestion_nb.db"); cur = conn.cursor()
                # CORRECTION : Ajout de (f_id,) ici qui manquait et faisait planter la fonction
                cur.execute("DELETE FROM lignes_facture WHERE facture_id=?", (f_id,))
                cur.execute("DELETE FROM factures WHERE id=?", (f_id,))
                conn.commit(); conn.close()
                
                # Recharger le tableau immédiatement
                self.load_factures()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def print_existing(self, f_id):
        try:
            conn = sqlite3.connect("gestion_nb.db"); cur = conn.cursor()
            # J'ajoute type_doc dans le SELECT
            cur.execute("SELECT client, conditions, total, objet, proforma, date, remise, type_doc FROM factures WHERE id=?", (f_id,))
            f = cur.fetchone()
            cur.execute("SELECT article, unite, quantite, prix_u, total_ligne FROM lignes_facture WHERE facture_id=?", (f_id,))
            lignes = cur.fetchall(); conn.close()
            if f:
                # Je passe f[7] (le type de document) comme nouveau paramètre
                type_document = str(f[7]) if f[7] else "Facture Proforma"
                pdf = NBPdfGenerator(f[0], f[1], f[2], lignes, f[3], f[4], f[5], f[6], type_document)
                pdf.generer()
        except Exception as e: QMessageBox.critical(self, "Erreur PDF", str(e))

    def add_new_row(self):
        r = self.table.rowCount()
        self.table.insertRow(r)
        
        text_edit = QTextEdit()
        text_edit.setStyleSheet("border: none; background-color: transparent;")
        self.table.setCellWidget(r, 0, text_edit)
        
        for c in range(1, 5): 
            self.table.setItem(r, c, QTableWidgetItem("0" if c > 1 else ""))
        self.table.setRowHeight(r, 60)

    def remove_selected_row(self):
        """Supprime la ligne actuellement sélectionnée dans le tableau d'édition"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            self.update_grand_total()
        else:
            QMessageBox.information(self, "Information", "Veuillez sélectionner une cellule de la ligne que vous souhaitez supprimer.")

    def clear_form(self):
        self.type_combo.setCurrentIndex(0)
        self.client_input.clear()
        self.cond_input.clear()
        self.objet_input.clear()
        self.remise_input.setText("0")
        self.cond_display.clear()
        self.table.setRowCount(0)
        self.update_grand_total()
        self.date_input.setText(datetime.now().strftime("%d/%m/%Y"))
        self.current_edit_id = None
        self.btn_save.setText("Enregistrer le Document")