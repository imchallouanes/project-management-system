import sys
import os
import sqlite3
import ctypes
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFrame, QHBoxLayout, 
                             QVBoxLayout, QLabel, QPushButton, QWidget, 
                             QStackedWidget, QGridLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor
import pyqtgraph as pg

# --- FONCTION DE CORRECTION DES CHEMINS D'IMAGES ---
def resource_path(relative_path):
    """ Récupère le chemin absolu vers les ressources, fonctionne pour dev et pour PyInstaller """
    try:
        # PyInstaller crée un dossier temporaire _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Configuration pour afficher l'icône dans la barre des tâches Windows
try:
    myappid = 'nbpower.automation.system.v1' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# Importation de tes modules personnalisés
from style import NBStyle
from facture_window import FactureManager
from project_window import ProjectManager
from archive_window import ArchiveManager
from rh_window import RHManager

class NBMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NB Power & Automation - Système de Gestion")
        self.resize(1350, 900)
        
        # --- CONFIGURATION DE L'ICÔNE DU LOGICIEL (CORRIGÉE) ---
        icon_path = resource_path("images/logo_5_5cm_300dpi.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setStyleSheet(NBStyle.STYLESHEET)
        
        # Filtres pour les graphiques
        self.ca_mode = "mensuel"
        self.rh_mode = "mensuel"

        # Widget Central
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.root_layout = QVBoxLayout(main_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # 1. Barre de Navigation Supérieure
        self.create_navbar()

        # 2. Zone d'affichage des pages
        self.content_area = QVBoxLayout()
        self.content_area.setContentsMargins(15, 15, 15, 15)
        self.root_layout.addLayout(self.content_area)

        self.pages_container = QStackedWidget()
        self.content_area.addWidget(self.pages_container)

        # Initialisation des pages
        self.setup_dashboard_page()
        self.project_page = ProjectManager() 
        self.facture_page = FactureManager()
        self.rh_page = RHManager()
        self.archive_page = ArchiveManager()

        # Ajout au container
        self.pages_container.addWidget(self.dashboard_widget) # 0
        self.pages_container.addWidget(self.project_page)      # 1
        self.pages_container.addWidget(self.facture_page)      # 2
        self.pages_container.addWidget(self.rh_page)           # 3
        self.pages_container.addWidget(self.archive_page)      # 4

        # Connexions
        self.btn_dashboard.clicked.connect(self.show_dashboard)
        self.btn_projets.clicked.connect(self.show_projets)
        self.btn_factures.clicked.connect(self.show_factures)
        self.btn_rh.clicked.connect(self.show_rh)
        self.btn_archives.clicked.connect(self.show_archives)
        
        self.show_dashboard()

    def create_navbar(self):
        self.nav_frame = QFrame()
        self.nav_frame.setObjectName("navbar")
        self.nav_frame.setFixedHeight(80) 
        layout = QHBoxLayout(self.nav_frame)
        layout.setContentsMargins(25, 0, 0, 0)
        
        text_logo = QVBoxLayout()
        self.lbl_company = QLabel("NB Power & Automation")
        self.lbl_company.setStyleSheet("color: white; font-size: 20px; font-weight: bold; background: transparent;")
        self.lbl_slogan = QLabel("Matériels & Maintenance Industrielle")
        self.lbl_slogan.setStyleSheet("color: #b0c4de; font-size: 11px; background: transparent;")
        text_logo.addWidget(self.lbl_company); text_logo.addWidget(self.lbl_slogan)
        layout.addLayout(text_logo)
        layout.addStretch(1)

        # Utilisation de resource_path pour les icônes des boutons
        self.btn_dashboard = self.create_nav_button("Tableau de Bord", resource_path("images/accueil.png"))
        self.btn_projets = self.create_nav_button("Projets", resource_path("images/gestion-de-projet (1).png"))
        self.btn_factures = self.create_nav_button("Devis & Factures", resource_path("images/facture-dachat.png"))
        self.btn_rh = self.create_nav_button("RH", resource_path("images/RHH.png"))
        self.btn_archives = self.create_nav_button("Archives", resource_path("images/archiver.png"))

        self.nav_buttons = [self.btn_dashboard, self.btn_projets, self.btn_factures, self.btn_rh, self.btn_archives]
        for btn in self.nav_buttons: layout.addWidget(btn)
        self.root_layout.addWidget(self.nav_frame)

    def create_nav_button(self, text, icon_path):
        btn = QPushButton(f" {text}")
        btn.setObjectName("nav_btn")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(80); btn.setMinimumWidth(160) 
        if os.path.exists(icon_path):
            btn.setIcon(QIcon(icon_path)); btn.setIconSize(QSize(22, 22))
        return btn

    def set_active_button(self, active_btn):
        for btn in self.nav_buttons: btn.setObjectName("nav_btn")
        active_btn.setObjectName("nav_btn_active")
        self.setStyleSheet(NBStyle.STYLESHEET)

    def show_dashboard(self):
        self.set_active_button(self.btn_dashboard)
        self.refresh_dashboard_data()
        self.pages_container.setCurrentWidget(self.dashboard_widget)

    def show_factures(self): self.set_active_button(self.btn_factures); self.pages_container.setCurrentWidget(self.facture_page)
    def show_projets(self): self.set_active_button(self.btn_projets); self.pages_container.setCurrentWidget(self.project_page); self.project_page.load_projects()
    def show_rh(self): self.set_active_button(self.btn_rh); self.pages_container.setCurrentWidget(self.rh_page); self.rh_page.load_data()
    def show_archives(self): self.set_active_button(self.btn_archives); self.pages_container.setCurrentWidget(self.archive_page); self.archive_page.load_archives()

    def setup_dashboard_page(self):
        self.dashboard_widget = QWidget()
        main_layout = QVBoxLayout(self.dashboard_widget)
        main_layout.setSpacing(20)

        kpi_layout = QHBoxLayout()
        self.kpi_projets = self.create_kpi_card("PROJETS TERMINÉS", "0", "📈", "#2ecc71")
        self.kpi_ca = self.create_kpi_card("CHIFFRE D'AFFAIRES", "0 DZD", "💰", "#1a4a7c")
        self.kpi_rh = self.create_kpi_card("EFFECTIF ACTIF", "0", "👥", "#e67e22")
        kpi_layout.addWidget(self.kpi_projets); kpi_layout.addWidget(self.kpi_ca); kpi_layout.addWidget(self.kpi_rh)
        main_layout.addLayout(kpi_layout)

        grid = QGridLayout()
        grid.setSpacing(20)

        self.plot_status = pg.PlotWidget(title="Statut des Projets")
        grid.addWidget(self.wrap_plot(self.plot_status), 0, 0)

        ca_widget = QWidget()
        ca_v = QVBoxLayout(ca_widget)
        ca_h = QHBoxLayout()
        ca_h.addWidget(QLabel("<b>Chiffre d'Affaires</b>"))
        btn_ca_m = QPushButton("Mensuel"); btn_ca_m.clicked.connect(lambda: self.change_ca_mode("mensuel"))
        btn_ca_a = QPushButton("Annuel"); btn_ca_a.clicked.connect(lambda: self.change_ca_mode("annuel"))
        ca_h.addWidget(btn_ca_m); ca_h.addWidget(btn_ca_a)
        self.plot_ca = pg.PlotWidget(); self.plot_ca.setBackground('w')
        ca_v.addLayout(ca_h); ca_v.addWidget(self.plot_ca)
        grid.addWidget(self.wrap_plot(ca_widget), 0, 1)

        rh_widget = QWidget()
        rh_v = QVBoxLayout(rh_widget)
        rh_h = QHBoxLayout()
        rh_h.addWidget(QLabel("<b>Heures de Travail RH</b>"))
        btn_rh_m = QPushButton("Mensuel"); btn_rh_m.clicked.connect(lambda: self.change_rh_mode("mensuel"))
        btn_rh_a = QPushButton("Annuel"); btn_rh_a.clicked.connect(lambda: self.change_rh_mode("annuel"))
        rh_h.addWidget(btn_rh_m); rh_h.addWidget(btn_rh_a)
        self.plot_rh = pg.PlotWidget(); self.plot_rh.setBackground('w')
        rh_v.addLayout(rh_h); rh_v.addWidget(self.plot_rh)
        grid.addWidget(self.wrap_plot(rh_widget), 1, 0)

        self.plot_clients = pg.PlotWidget(title="Top 5 Clients (Volume CA)")
        grid.addWidget(self.wrap_plot(self.plot_clients), 1, 1)

        main_layout.addLayout(grid)

    def wrap_plot(self, widget):
        f = QFrame(); f.setObjectName("WhiteCard")
        f.setStyleSheet("background: white; border-radius: 12px; padding: 5px;")
        NBStyle.add_shadow(f)
        l = QVBoxLayout(f); l.addWidget(widget)
        return f

    def create_kpi_card(self, title, val, icon, color):
        card = QFrame(); card.setObjectName("WhiteCard"); card.setFixedHeight(110)
        NBStyle.add_shadow(card)
        l = QHBoxLayout(card)
        vbox = QVBoxLayout()
        t = QLabel(title); t.setStyleSheet("font-size: 11px; color: #7f8c8d; font-weight: bold;")
        v = QLabel(val); v.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color};"); v.setObjectName("val")
        vbox.addWidget(t); vbox.addWidget(v)
        i = QLabel(icon); i.setStyleSheet("font-size: 35px; color: #d1d1d1;")
        l.addLayout(vbox); l.addStretch(); l.addWidget(i)
        return card

    def change_ca_mode(self, m): self.ca_mode = m; self.refresh_dashboard_data()
    def change_rh_mode(self, m): self.rh_mode = m; self.refresh_dashboard_data()

    def refresh_dashboard_data(self):
        try:
            # Recherche de la base de données au même endroit que l'exécutable
            if getattr(sys, 'frozen', False):
                db_dir = os.path.dirname(sys.executable)
            else:
                db_dir = os.path.dirname(os.path.abspath(__file__))
            
            db_path = os.path.join(db_dir, "gestion_nb.db")
            
            conn = sqlite3.connect(db_path); cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), SUM(total) FROM projets WHERE statut='Terminé'")
            res = cursor.fetchone()
            self.kpi_projets.findChild(QLabel, "val").setText(str(res[0] or 0))
            self.kpi_ca.findChild(QLabel, "val").setText(f"{res[1] or 0:,.0f} DZD")

            cursor.execute("SELECT COUNT(*) FROM employes")
            self.kpi_rh.findChild(QLabel, "val").setText(str(cursor.fetchone()[0]))

            cursor.execute("SELECT statut, COUNT(*) FROM projets GROUP BY statut")
            st_data = dict(cursor.fetchall())
            self.plot_status.clear(); self.plot_status.setBackground('w')
            bg = pg.BarGraphItem(x=[1, 2], height=[st_data.get('En cours', 0), st_data.get('Terminé', 0)], width=0.5, brushes=['#3498db', '#2ecc71'])
            self.plot_status.addItem(bg)

            self.plot_ca.clear()
            cursor.execute("SELECT substr(date, 4, 7) as m, SUM(total) FROM factures GROUP BY m ORDER BY id DESC LIMIT 6")
            ca_data = [r[1] for r in cursor.fetchall()]
            if self.ca_mode == "annuel" and ca_data: ca_data = [sum(ca_data)]
            self.plot_ca.plot(ca_data, pen=pg.mkPen('#1a4a7c', width=3), symbol='o')

            self.plot_rh.clear()
            cursor.execute("SELECT heure_entree, heure_sortie FROM pointage")
            total_h = 0
            for e, s in cursor.fetchall():
                try:
                    delta = datetime.strptime(s, "%H:%M") - datetime.strptime(e, "%H:%M")
                    total_h += delta.total_seconds() / 3600
                except: pass
            rh_data = [total_h * 0.5, total_h * 0.8, total_h]
            self.plot_rh.plot(rh_data, pen=pg.mkPen('#e67e22', width=3), fillLevel=0, brush=(230, 126, 34, 50))

            cursor.execute("SELECT client, SUM(total) as t FROM factures GROUP BY client ORDER BY t DESC LIMIT 5")
            c_data = cursor.fetchall()
            self.plot_clients.clear(); self.plot_clients.setBackground('w')
            if c_data:
                bg_c = pg.BarGraphItem(x=range(len(c_data)), height=[c[1] for c in c_data], width=0.6, brush='#9b59b6')
                self.plot_clients.addItem(bg_c)
            conn.close()
        except Exception as e: print(f"Erreur DB: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NBMainWindow()
    window.showMaximized() 
    sys.exit(app.exec_())