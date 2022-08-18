import subprocess
import platform
import sys
import os

# Installing packages
def install_packages():
    subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

print("Installation des dépendances Link.")
input("Appuyer sur n'importe quelle touche pour continuer, ou quitter avec CTRL+C")
install_packages()