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