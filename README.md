# Bot de Trading Crypto Avancé

Ce bot de trading crypto automatisé utilise des stratégies avancées, incluant l'analyse technique, l'analyse de sentiment, et l'apprentissage automatique pour prendre des décisions de trading.

## Prérequis

- Python 3.7+
- pip (gestionnaire de paquets Python)
- Compte sur un exchange crypto supporté (par exemple, Binance)

## Installation

1. Clonez ce dépôt :
   ```
   git clone https://github.com/votre-nom/crypto-trading-bot.git
   cd crypto-trading-bot
   ```

2. Installez les dépendances :
   ```
   pip install -r requirements.txt
   ```

3. Configurez vos variables d'environnement :
   Copiez le fichier `.env.example` en `.env` et remplissez-le avec vos informations :
   ```
   cp .env.example .env
   ```
   Ouvrez le fichier `.env` et remplacez les valeurs par défaut par vos propres informations.

## Configuration

Vous pouvez ajuster les paramètres du bot dans le fichier `config.py`. Assurez-vous de bien comprendre chaque paramètre avant de le modifier.

## Utilisation

1. Pour lancer le bot en mode paper trading (simulation) :
   ```
   bash start_bot.sh
   ```

2. Pour lancer le bot en trading réel, modifiez la ligne suivante dans `main.py` :
   ```python
   trading_loop(..., paper_trade=False)
   ```
   Puis lancez le bot avec la commande ci-dessus.

## Avertissement

Le trading de crypto-monnaies comporte des risques importants. N'investissez que l'argent que vous pouvez vous permettre de perdre. Les performances passées ne garantissent pas les résultats futurs.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.