import sqlite3
import os
import shutil
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QFrame, QGridLayout, QPushButton, 
                             QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from style import NBStyle

class ArchiveManager(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(25, 25, 25, 25)
        
        # --- HEADER ---
        self.header = QLabel("Archives")
        self.header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1a4a7c; margin-bottom: 20px;")
        self.layout.addWidget(self.header)

        # --- ZONE DE GRILLE ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background-color: transparent; border: none;")
        
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(30)
        self.grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)
        
        self.load_archives()

    def load_archives(self):
        for i in reversed(range(self.grid.count())): 
            if self.grid.itemAt(i).widget():
                self.grid.itemAt(i).widget().setParent(None)

        conn = sqlite3.connect("gestion_nb.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nom_projet, client, documents FROM projets")
        projets = cursor.fetchall()
        conn.close()

        col, row = 0, 0
        for p_nom, p_client, p_docs in projets:
            card = self.create_folder_card(p_nom, p_client, p_docs)
            self.grid.addWidget(card, row, col)
            col += 1
            if col > 2: # 3 dossiers par ligne
                col = 0
                row += 1

    def create_folder_card(self, name, client, docs_string):
        card = QFrame()
        card.setObjectName("WhiteCard")
        card.setFixedSize(340, 420) 
        NBStyle.add_shadow(card)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        # 1. EN-TÊTE
        header_layout = QHBoxLayout()
        folder_icon = QLabel("📁")
        folder_icon.setStyleSheet("font-size: 30px; color: #f1c40f;")
        
        title_vbox = QVBoxLayout()
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-size: 15px; font-weight: bold; color: #1a4a7c;")
        lbl_client = QLabel(client)
        lbl_client.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        title_vbox.addWidget(lbl_name)
        title_vbox.addWidget(lbl_client)
        
        header_layout.addWidget(folder_icon)
        header_layout.addLayout(title_vbox)
        layout.addLayout(header_layout)

        paths = [p for p in docs_string.split(";") if p.strip()] if docs_string else []
        count_lbl = QLabel(f"{len(paths)} Documents & Images")
        count_lbl.setStyleSheet("font-weight: bold; color: #34495e; font-size: 11px; margin-top: 5px;")
        layout.addWidget(count_lbl)

        # 2. GRILLE DE PRÉVISUALISATION
        preview_container = QWidget()
        preview_grid = QGridLayout(preview_container)
        preview_grid.setContentsMargins(0, 5, 0, 5)
        preview_grid.setSpacing(8)

        for i in range(4):
            slot = QFrame()
            slot.setFixedSize(145, 90)
            slot.setStyleSheet("background: #fdfdfd; border: 1px solid #eee; border-radius: 5px;")
            slot_layout = QVBoxLayout(slot)
            slot_layout.setContentsMargins(0, 0, 0, 0)
            
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            
            if i < len(paths):
                file_path = paths[i]
                ext = file_path.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png'] and os.path.exists(file_path):
                    pix = QPixmap(file_path).scaled(140, 85, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    img_label.setPixmap(pix)
                else:
                    img_label.setText(f"📄\n{ext.upper()}")
                    img_label.setStyleSheet("color: #95a5a6; font-weight: bold; font-size: 9px;")
                
                btn_mini = QPushButton("↓", slot) # Changé img_label -> slot pour une meilleure gestion
                btn_mini.setFixedSize(20, 20)
                btn_mini.move(120, 65)
                btn_mini.setStyleSheet("background: #3498db; color: white; border-radius: 10px; font-size: 10px;")
                # Fix du lambda avec l'argument par défaut file_path=file_path
                btn_mini.clicked.connect(lambda checked, p=file_path: self.download_file(p))
            
            slot_layout.addWidget(img_label)
            preview_grid.addWidget(slot, i // 2, i % 2)

        layout.addWidget(preview_container)

        # 3. FOOTER
        footer_layout = QHBoxLayout()
        btn_full_dl = QPushButton(" Télécharger tout le dossier")
        btn_full_dl.setFixedHeight(30)
        btn_full_dl.setStyleSheet("""
            QPushButton { background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; color: #555; font-size: 10px; }
            QPushButton:hover { background: #e9ecef; }
        """)
        # Connexion pour télécharger tous les fichiers
        btn_full_dl.clicked.connect(lambda checked, ps=paths: self.download_folder(ps))
        
        btn_icon = QPushButton("↓")
        btn_icon.setFixedSize(30, 30)
        btn_icon.setStyleSheet("background: #3498db; color: white; border-radius: 4px; font-weight: bold;")
        btn_icon.clicked.connect(lambda checked, ps=paths: self.download_folder(ps))

        footer_layout.addWidget(btn_full_dl)
        footer_layout.addStretch()
        footer_layout.addWidget(btn_icon)
        layout.addLayout(footer_layout)
        
        return card

    def download_file(self, source):
        if not os.path.exists(source):
            QMessageBox.warning(self, "Erreur", "Fichier introuvable.")
            return
        dest, _ = QFileDialog.getSaveFileName(self, "Enregistrer le fichier", os.path.basename(source))
        if dest:
            shutil.copy2(source, dest)
            QMessageBox.information(self, "Succès", "Fichier sauvegardé !")

    def download_folder(self, sources):
        if not sources:
            QMessageBox.warning(self, "Erreur", "Aucun fichier à télécharger.")
            return
        
        folder_dest = QFileDialog.getExistingDirectory(self, "Sélectionner le dossier de destination")
        if folder_dest:
            for source in sources:
                if os.path.exists(source):
                    shutil.copy2(source, os.path.join(folder_dest, os.path.basename(source)))
            QMessageBox.information(self, "Succès", "Tous les fichiers ont été copiés !")