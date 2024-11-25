#!/bin/bash

# Activer l'environnement virtuel si nécessaire
# source /chemin/vers/votre/environnement/virtuel/bin/activate

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null
then
    echo "Python3 n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Vérifier si les dépendances sont installées
pip3 install -r requirements.txt

# Lancer le bot
python3 main.py