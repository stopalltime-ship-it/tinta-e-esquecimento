from pathlib import Path
import sys

WIDTH, HEIGHT = 1152, 720
FPS = 60
TITLE = "Tinta e Esquecimento"
# Funciona tanto no fonte quanto na pasta do executável, sem caminhos do autor.
ROOT = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
BG = (17, 24, 34)
PAPER = (239, 224, 192)
MUTED = (155, 167, 168)
GOLD = (222, 175, 98)
TEAL = (102, 205, 186)
RED = (226, 116, 124)
