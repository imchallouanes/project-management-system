import sqlite3
import os
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QLineEdit, QPushButton, QLabel, 
                             QHeaderView, QComboBox, QDialog, QFileDialog, QMessageBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from style import NBStyle

class ProjectManager(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # --- HEADER ---
        header_layout = QHBoxLayout()
        title = QLabel("Gestion des Projets")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a4a7c;")
        
        self.btn_add_project = QPushButton("+ Ajouter Projet")
        self.btn_add_project.setFixedSize(180, 45)
        self.btn_add_project.setStyleSheet("""
            QPushButton { background-color: #e67e22; color: white; border-radius: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #d35400; }
        """)
        self.btn_add_project.clicked.connect(self.open_add_dialog)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add_project)
        self.layout.addLayout(header_layout)

        # --- STATS CARDS ---
        stats_layout = QHBoxLayout()
        self.card_encours = self.create_stat_card("Projets en Cours", "0")
        self.card_termine = self.create_stat_card("Terminés", "0")
        self.card_total_money = self.create_stat_card("Total Projets", "0 DZD")
        
        stats_layout.addWidget(self.card_encours)
        stats_layout.addWidget(self.card_termine)
        stats_layout.addWidget(self.card_total_money)
        self.layout.addLayout(stats_layout)

        # --- TABLEAU (7 colonnes maintenant avec Statut) ---
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Projet", "Client", "Total", "Durée", "Statut", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: white; border-radius: 10px; gridline-color: #f0f0f0;")
        self.table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.table)
        
        self.load_projects()

    def create_stat_card(self, title, value):
        card = QFrame()
        card.setObjectName("WhiteCard")
        card.setFixedHeight(100)
        NBStyle.add_shadow(card)
        l = QVBoxLayout(card)
        t = QLabel(title); t.setStyleSheet("color: #7f8c8d; font-weight: bold;")
        v = QLabel(value); v.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a4a7c;")
        v.setObjectName("stat_value") # Pour le retrouver facilement
        l.addWidget(t); l.addWidget(v)
        return card

    def load_projects(self):
        conn = sqlite3.connect("gestion_nb.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom_projet, client, total, duree, statut FROM projets")
        rows = cursor.fetchall()
        self.table.setRowCount(0)
        
        nb_encours = 0
        nb_termines = 0
        total_dzd = 0

        for row_data in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Calculs KPI
            total_dzd += row_data[3]
            if row_data[5] == "Terminé": nb_termines += 1
            else: nb_encours += 1

            # Remplissage colonnes de base
            for i in range(5):
                text = f"{row_data[i]:,.2f} DZD".replace(",", " ") if i == 3 else str(row_data[i])
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, i, item)

            # Colonne Statut
            status_item = QTableWidgetItem(row_data[5])
            status_item.setTextAlignment(Qt.AlignCenter)
            color = "#27ae60" if row_data[5] == "Terminé" else "#2980b9"
            status_item.setForeground(QColor(color))
            font = QFont(); font.setBold(True)
            status_item.setFont(font)
            self.table.setItem(row, 5, status_item)

            # Colonne Actions
            self.add_action_buttons(row, row_data[0])

        conn.close()
        
        # Update KPI Labels
        self.card_encours.findChild(QLabel, "stat_value").setText(str(nb_encours))
        self.card_termine.findChild(QLabel, "stat_value").setText(str(nb_termines))
        self.card_total_money.findChild(QLabel, "stat_value").setText(f"{total_dzd:,.2f} DZD".replace(",", " "))

    def add_action_buttons(self, row, p_id):
        action_widget = QWidget()
        layout = QHBoxLayout(action_widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)

        btn_view = QPushButton("Voir"); btn_view.setStyleSheet("background:#34495e; color:white; border-radius:3px; padding:4px;")
        btn_edit = QPushButton("Modifier"); btn_edit.setStyleSheet("background:#f39c12; color:white; border-radius:3px; padding:4px;")
        btn_del = QPushButton("Supprimer"); btn_del.setStyleSheet("background:#e74c3c; color:white; border-radius:3px; padding:4px;")

        btn_view.clicked.connect(lambda: self.view_details(p_id))
        btn_edit.clicked.connect(lambda: self.open_edit_dialog(p_id))
        btn_del.clicked.connect(lambda: self.delete_project(p_id))

        layout.addWidget(btn_view); layout.addWidget(btn_edit); layout.addWidget(btn_del)
        self.table.setCellWidget(row, 6, action_widget)

    def view_details(self, p_id):
        conn = sqlite3.connect("gestion_nb.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projets WHERE id=?", (p_id,))
        p = cursor.fetchone()
        conn.close()
        if p:
            msg = f"DÉTAILS DU PROJET\n\nID: {p[0]}\nProjet: {p[2]}\nClient: {p[3]}\nTotal: {p[4]:,.2f} DZD\nDurée: {p[5]}\nStatut: {p[6]}\nDocuments: {p[7]}\nCréé le: {p[8]}"
            QMessageBox.information(self, "Détails Projet", msg)

    def open_add_dialog(self):
        if AddProjectDialog().exec_(): self.load_projects()

    def open_edit_dialog(self, p_id):
        if EditProjectDialog(p_id).exec_(): self.load_projects()

    def delete_project(self, p_id):
        if QMessageBox.question(self, "Confirmer", "Supprimer ce projet ?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            conn = sqlite3.connect("gestion_nb.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projets WHERE id=?", (p_id,))
            conn.commit(); conn.close()
            self.load_projects()

# --- DIALOGUE AJOUT ---
class AddProjectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nouveau Projet")
        self.setFixedSize(450, 480)
        self.layout = QVBoxLayout(self)
        self.selected_docs = []

        self.layout.addWidget(QLabel("Lier à une facture :"))
        self.combo = QComboBox(); self.load_factures()
        self.layout.addWidget(self.combo)

        self.layout.addWidget(QLabel("Durée estimée :"))
        self.input_duree = QLineEdit()
        self.layout.addWidget(self.input_duree)

        self.btn_docs = QPushButton("📁 Joindre Documents"); self.btn_docs.clicked.connect(self.pick_files)
        self.layout.addWidget(self.btn_docs)
        self.lbl_docs = QLabel("Aucun document"); self.layout.addWidget(self.lbl_docs)

        self.btn_save = QPushButton("Créer Projet"); self.btn_save.setFixedHeight(45)
        self.btn_save.setStyleSheet("background:#1a4a7c; color:white; font-weight:bold;")
        self.btn_save.clicked.connect(self.save)
        self.layout.addWidget(self.btn_save)

    def load_factures(self):
        conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
        cursor.execute("SELECT id, client, total FROM factures")
        self.data = cursor.fetchall()
        for f in self.data: self.combo.addItem(f"Facture #{f[0]} - {f[1]} ({f[2]:,.2f} DZD)", f[0])
        conn.close()

    def pick_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Docs", "", "Images/PDF (*.png *.jpg *.pdf)")
        if files: self.selected_docs = files; self.lbl_docs.setText(f"{len(files)} document(s) prêt(s)")

    def save(self):
        idx = self.combo.currentIndex()
        if idx < 0: return
        f_id, f_client, f_total = self.data[idx]
        conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
        cursor.execute("INSERT INTO projets (facture_id, nom_projet, client, total, duree, documents, date_creation) VALUES (?,?,?,?,?,?,?)",
                       (f_id, f"Chantier {f_id}", f_client, f_total, self.input_duree.text(), ";".join(self.selected_docs), datetime.now().strftime("%d/%m/%Y")))
        conn.commit(); conn.close()
        self.accept()

# --- DIALOGUE MODIFIER ---
class EditProjectDialog(QDialog):
    def __init__(self, p_id):
        super().__init__()
        self.p_id = p_id
        self.setWindowTitle("Modifier Projet")
        self.setFixedSize(400, 300)
        self.layout = QVBoxLayout(self)

        self.layout.addWidget(QLabel("Changer le Statut :"))
        self.combo_status = QComboBox()
        self.combo_status.addItems(["En cours", "Terminé"])
        self.layout.addWidget(self.combo_status)

        self.layout.addWidget(QLabel("Modifier Durée :"))
        self.input_duree = QLineEdit()
        self.layout.addWidget(self.input_duree)

        conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
        cursor.execute("SELECT statut, duree FROM projets WHERE id=?", (p_id,))
        res = cursor.fetchone()
        if res:
            self.combo_status.setCurrentText(res[0])
            self.input_duree.setText(res[1])
        conn.close()

        btn_upd = QPushButton("Mettre à jour"); btn_upd.clicked.connect(self.update)
        btn_upd.setStyleSheet("background:#27ae60; color:white; font-weight:bold; height:40px;")
        self.layout.addWidget(btn_upd)

    def update(self):
        conn = sqlite3.connect("gestion_nb.db"); cursor = conn.cursor()
        cursor.execute("UPDATE projets SET statut=?, duree=? WHERE id=?", (self.combo_status.currentText(), self.input_duree.text(), self.p_id))
        conn.commit(); conn.close()
        self.accept()