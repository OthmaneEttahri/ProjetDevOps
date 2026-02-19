Pixel Detective
Projet DevOps – Conteneurisation & Industrialisation (M2)

---

Objectif du projet
Ce projet a pour objectif d’industrialiser le déploiement d’une application web Python en appliquant les bonnes pratiques DevOps suivantes :

Conteneurisation complète des composants
Séparation des responsabilités
Orchestration multi-services avec Docker Compose
Mise en place d’un reverse proxy
Ajout d’un endpoint de healthcheck
Gestion d’un worker batch
Préparation à l’intégration CI/CD
Introduction aux problématiques de sécurité supply chain (SBOM, scan de vulnérabilités)

---

Architecture générale
L’application est composée de trois services :

API Flask
Worker batch
Reverse proxy Nginx

Schéma logique
Client HTTP
→ Nginx (reverse proxy)
→ API Flask
↘ Worker (exécution batch indépendante)

Réseaux Docker
Deux réseaux sont définis :

frontend-net : exposition externe via Nginx
backend-net : communication interne API / Worker

Cette séparation permet de limiter la surface d’exposition réseau.

---

Description des services
3.1 API (Flask)
Responsabilités :

Exposition de l’endpoint /
Exposition de l’endpoint /health
Logique applicative du jeu
Gestion des fichiers temporaires

#### Endpoint /health

L’endpoint réalise les vérifications suivantes :

Présence du dossier images
Permission d’écriture dans le dossier temporaire
Espace disque disponible (> 100 MB)

Retour :

HTTP 200 si tous les checks sont valides
HTTP 500 sinon

3.2 Worker batch
Le worker est un composant autonome qui :

Supprime les fichiers temporaires obsolètes
Réalise un audit simple des noms d’images
Génère un rapport JSON (catalog.json)
Gère correctement les signaux SIGTERM et SIGINT
Retourne un code d’erreur non nul en cas d’échec

Il s’exécute puis se termine proprement.

---

3.3 Reverse Proxy (Nginx)
Rôle :

Recevoir les requêtes HTTP externes
Router vers l’API Flask
Servir les fichiers statiques temporaires

Le proxy dépend du healthcheck de l’API avant démarrage.

---

Conteneurisation
Chaque composant possède son propre Dockerfile :

Dockerfile.api
Dockerfile.worker
Dockerfile.proxy

Bonnes pratiques appliquées
Pas d’utilisation du tag latest
Images légères (Alpine lorsque possible)
Exécution en utilisateur non-root
Isolation des volumes
Healthcheck défini pour l’API
Politique de redémarrage adaptée selon le service

---

Orchestration avec Docker Compose
Le fichier docker-compose.yml permet de :

Construire les images
Définir les réseaux
Définir les volumes
Externaliser la configuration via .env
Gérer les dépendances entre services
Appliquer des politiques de redémarrage

Lancement
Build et démarrage :

```bash
docker compose up --build -d