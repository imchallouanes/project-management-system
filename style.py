from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

class NBStyle:
    # Couleurs basées sur ton image
    BLUE_NB = "#1a4a7c"        # Bleu foncé de la barre
    BLUE_HOVER = "#2a5a8c"     # Bleu un peu plus clair pour le survol
    BLUE_ACTIVE = "#3a6a9c"    # Bleu pour l'onglet sélectionné
    BG_LIGHT = "#f0f2f5"      # Gris clair du fond
    WHITE = "#ffffff"
    TEXT_DARK = "#333333"

    STYLESHEET = f"""
        QMainWindow {{
            background-color: {BG_LIGHT};
        }}

        /* Barre de navigation supérieure */
        QFrame#navbar {{
            background-color: {BLUE_NB};
            border-bottom: 2px solid #143a62;
            min-height: 70px;
            max-height: 70px;
        }}

        /* Nom de l'entreprise dans la barre */
        QLabel#nav_title {{
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding-left: 10px;
        }}
        
        QLabel#nav_subtitle {{
            color: #d1d1d1;
            font-size: 11px;
            padding-left: 10px;
        }}

        /* Boutons de navigation (Design de l'image) */
        QPushButton#nav_btn {{
            background-color: transparent;
            color: white;
            border: none;
            border-right: 1px solid rgba(255, 255, 255, 0.1); /* Séparateur vertical */
            font-weight: bold;
            font-size: 13px;
            padding: 10px 20px;
            text-align: center;
        }}

        QPushButton#nav_btn:hover {{
            background-color: {BLUE_HOVER};
        }}

        /* Style pour le bouton actif (onglet sélectionné) */
        QPushButton#nav_btn_active {{
            background-color: {BLUE_ACTIVE};
            color: white;
            border: none;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            font-weight: bold;
            font-size: 13px;
            padding: 10px 20px;
        }}

        /* Tableau et entrées */
        QTableWidget {{
            background-color: white;
            border: 1px solid #ddd;
            gridline-color: #f0f0f0;
            border-radius: 5px;
        }}

        QHeaderView::section {{
            background-color: {BLUE_NB};
            color: white;
            padding: 5px;
            font-weight: bold;
            border: none;
        }}

        QLineEdit, QTextEdit {{
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 5px;
        }}

        /* Cartes du Tableau de bord */
        QFrame#BlueCard {{
            background-color: {BLUE_NB};
            border-radius: 10px;
        }}

        QFrame#WhiteCard {{
            background-color: {WHITE};
            border-radius: 10px;
            border: 1px solid #e0e0e0;
        }}

        QLabel#BigNumber {{
            color: white;
            font-size: 40px;
            font-weight: bold;
        }}
    """

    @staticmethod
    def add_shadow(widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        widget.setGraphicsEffect(shadow)