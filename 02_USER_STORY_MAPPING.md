# 📖 USER STORY MAPPING - Plateforme d'Apprentissage Web

## 🎭 PERSONAS

### 👨‍🎓 Alex - L'Apprenant Débutant
**Profil :**
- Âge : 22 ans
- Niveau : Débutant complet en programmation
- Motivation : Reconversion professionnelle
- Disponibilité : 2h par jour en soirée
- Caractéristiques : Apprend mieux avec des exemples concrets, besoin de validation régulière

**Objectifs :**
- Apprendre les bases du développement web
- Obtenir un portfolio de projets
- Trouver un premier emploi en développement

**Frustrations :**
- Se sent perdu sans structure claire
- Manque de feedback immédiat
- Peur de prendre du retard

---

### 👨‍🏫 Sophie - La Formatrice
**Profil :**
- Âge : 35 ans
- Expérience : 10 ans en développement, 5 ans en formation
- Contexte : Gère 3 groupes de 20 apprenants simultanément
- Disponibilité : 8h par jour, besoin d'efficacité

**Objectifs :**
- Suivre la progression de chaque apprenant en temps réel
- Identifier rapidement les apprenants en difficulté
- Adapter le rythme selon les besoins du groupe
- Automatiser les corrections simples

**Frustrations :**
- Perte de temps sur les tâches répétitives
- Difficulté à suivre 60 apprenants individuellement
- Manque de visibilité sur l'engagement réel

---

### 👔 Marc - L'Administrateur
**Profil :**
- Âge : 40 ans
- Rôle : Directeur pédagogique du centre de formation
- Responsabilités : Suivi global, qualité, reporting

**Objectifs :**
- Vue d'ensemble des statistiques
- Taux de complétion et satisfaction
- Optimisation du parcours pédagogique

---

## 🗺️ USER STORY MAP

```
BACKBONE (Activités principales)
├─ S'INSCRIRE ET COMMENCER
├─ SUIVRE DES LEÇONS
├─ PRATIQUER
├─ PROGRESSER
└─ COLLABORER

WALKING SKELETON (MVP - Release 1)
└─ Stories prioritaires pour version minimale viable

RELEASES FUTURES
└─ Fonctionnalités additionnelles
```

---

## 📋 ACTIVITÉ 1 : S'INSCRIRE ET COMMENCER

### Release 1 (MVP)

**US-001 : Créer un compte apprenant**
```
En tant qu'apprenant potentiel
Je veux créer un compte avec email et mot de passe
Afin d'accéder à la plateforme
```
**Critères d'acceptation :**
- ✓ Formulaire d'inscription avec email, nom, prénom, mot de passe
- ✓ Validation email unique
- ✓ Mot de passe minimum 8 caractères avec complexité
- ✓ Email de confirmation envoyé
- ✓ Redirection vers dashboard apprenant après confirmation

**Priorité :** Must Have | **Story Points :** 5 | **Sprint :** 1.1

---

**US-002 : Se connecter**
```
En tant qu'utilisateur enregistré
Je veux me connecter avec mes identifiants
Afin d'accéder à mon espace personnel
```
**Critères d'acceptation :**
- ✓ Formulaire login (email + mot de passe)
- ✓ Token JWT retourné après authentification réussie
- ✓ Redirection selon rôle (apprenant → dashboard, formateur → suivi)
- ✓ Message d'erreur clair si échec
- ✓ Option "Mot de passe oublié"

**Priorité :** Must Have | **Story Points :** 3 | **Sprint :** 1.1

---

**US-003 : Gérer les rôles utilisateurs**
```
En tant qu'administrateur
Je veux assigner des rôles (Apprenant, Formateur, Admin)
Afin de contrôler les accès aux fonctionnalités
```
**Critères d'acceptation :**
- ✓ Interface admin Django pour gestion utilisateurs
- ✓ Possibilité d'assigner/modifier rôles
- ✓ Permissions Django configurées par rôle
- ✓ Un utilisateur peut avoir plusieurs rôles

**Priorité :** Must Have | **Story Points :** 5 | **Sprint :** 1.1

---

### Release 2

**US-030 : Connexion sociale (Google, GitHub)**
```
En tant qu'apprenant
Je veux me connecter via Google ou GitHub
Afin de simplifier l'inscription
```
**Priorité :** Should Have | **Story Points :** 8 | **Sprint :** Futur

---

## 📋 ACTIVITÉ 2 : SUIVRE DES LEÇONS

### Release 1 (MVP)

**US-004 : Voir la liste des chapitres disponibles**
```
En tant qu'apprenant
Je veux voir tous les chapitres du parcours
Afin de comprendre la structure du cours
```
**Critères d'acceptation :**
- ✓ Liste des chapitres avec titre, description, durée estimée
- ✓ Indicateur visuel : débloqué/verrouillé
- ✓ Indicateur de progression (0%, 50%, 100%)
- ✓ Badge "Complété" si chapitre terminé

**Priorité :** Must Have | **Story Points :** 3 | **Sprint :** 1.2

---

**US-005 : Créer et gérer du contenu pédagogique**
```
En tant que formateur
Je veux créer des chapitres, leçons, exercices et QCM
Afin de construire un parcours d'apprentissage
```
**Critères d'acceptation :**
- ✓ Interface admin Django avec éditeur riche (Markdown)
- ✓ Upload d'images et fichiers
- ✓ Prévisualisation du rendu
- ✓ Organisation hiérarchique : Chapitre > Leçon > Contenu
- ✓ Possibilité de réordonner éléments (drag & drop)

**Priorité :** Must Have | **Story Points :** 13 | **Sprint :** 1.2

---

**US-012 : Lire une leçon théorique**
```
En tant qu'apprenant
Je veux lire le contenu d'une leçon
Afin d'apprendre les concepts théoriques
```
**Critères d'acceptation :**
- ✓ Affichage du contenu formaté (Markdown → HTML)
- ✓ Sidebar avec navigation chapitres/leçons
- ✓ Bouton "Leçon suivante"
- ✓ Marquage automatique "Leçon vue"
- ✓ Barre de progression du chapitre

**Priorité :** Must Have | **Story Points :** 8 | **Sprint :** 2.2

---

### Release 2

**US-031 : Rechercher dans le contenu**
```
En tant qu'apprenant
Je veux rechercher un terme dans toutes les leçons
Afin de retrouver rapidement une information
```
**Priorité :** Should Have | **Story Points :** 5 | **Sprint :** Futur

---

**US-032 : Prendre des notes sur les leçons**
```
En tant qu'apprenant
Je veux annoter les leçons avec mes propres notes
Afin de personnaliser mon apprentissage
```
**Priorité :** Could Have | **Story Points :** 8 | **Sprint :** Futur

---

## 📋 ACTIVITÉ 3 : PRATIQUER

### Release 1 (MVP)

**US-013 : Faire un exercice de code**
```
En tant qu'apprenant
Je veux écrire du code dans un éditeur intégré
Afin de mettre en pratique les concepts appris
```
**Critères d'acceptation :**
- ✓ Éditeur de code (Monaco Editor) avec coloration syntaxique
- ✓ Support HTML, CSS, JavaScript
- ✓ Prévisualisation en temps réel (iframe isolée)
- ✓ Bouton "Soumettre" pour validation
- ✓ Sauvegarde automatique toutes les 3 secondes

**Priorité :** Must Have | **Story Points :** 13 | **Sprint :** 2.2

---

**US-014 : Répondre à un QCM**
```
En tant qu'apprenant
Je veux répondre à des questions à choix multiples
Afin de valider ma compréhension
```
**Critères d'acceptation :**
- ✓ Interface QCM avec choix uniques ou multiples
- ✓ Validation immédiate après soumission
- ✓ Affichage bonnes/mauvaises réponses
- ✓ Explications pour chaque réponse
- ✓ Score affiché (X/Y)

**Priorité :** Must Have | **Story Points :** 8 | **Sprint :** 2.2

---

**US-022 : Valider automatiquement les exercices**
```
En tant que système
Je veux exécuter des tests unitaires sur le code soumis
Afin de valider la solution de l'apprenant
```
**Critères d'acceptation :**
- ✓ Suite de tests prédéfinis par exercice
- ✓ Exécution dans un environnement sandboxé
- ✓ Retour détaillé : tests passés/échoués
- ✓ Messages d'erreur clairs
- ✓ Timeout si exécution > 5 secondes

**Priorité :** Must Have | **Story Points :** 13 | **Sprint :** 3.2

---

**US-023 : Obtenir des indices progressifs**
```
En tant qu'apprenant bloqué
Je veux demander des indices
Afin de débloquer ma progression sans voir la solution
```
**Critères d'acceptation :**
- ✓ Bouton "Indice" (max 3 par exercice)
- ✓ Indices révélés progressivement
- ✓ Pénalité de points si indices utilisés
- ✓ Option "Voir la solution" après 3 indices

**Priorité :** Should Have | **Story Points :** 5 | **Sprint :** 3.2

---

### Release 2

**US-033 : Déboguer avec console JavaScript**
```
En tant qu'apprenant
Je veux accéder à une console JavaScript
Afin de déboguer mon code
```
**Priorité :** Should Have | **Story Points :** 8 | **Sprint :** Futur

---

## 📋 ACTIVITÉ 4 : PROGRESSER

### Release 1 (MVP)

**US-006 : Suivre ma progression globale**
```
En tant qu'apprenant
Je veux voir un tableau de bord de ma progression
Afin de visualiser mon avancement
```
**Critères d'acceptation :**
- ✓ Pourcentage global de complétion
- ✓ Chapitres complétés / total
- ✓ Temps passé sur la plateforme
- ✓ Dernière activité
- ✓ Prochaine leçon suggérée

**Priorité :** Must Have | **Story Points :** 8 | **Sprint :** 1.3

---

**US-007 : Débloquer un chapitre pour un apprenant**
```
En tant que formateur
Je veux débloquer l'accès au chapitre suivant pour un apprenant
Afin de contrôler sa progression
```
**Critères d'acceptation :**
- ✓ Liste des apprenants avec statut par chapitre
- ✓ Bouton "Débloquer chapitre X" par apprenant
- ✓ Confirmation avant déblocage
- ✓ Notification envoyée à l'apprenant
- ✓ Log de l'action avec timestamp

**Priorité :** Must Have | **Story Points :** 8 | **Sprint :** 1.3

---

**US-008 : Sauvegarde automatique de ma progression**
```
En tant qu'apprenant
Je veux que mon travail soit sauvegardé automatiquement
Afin de ne jamais perdre mon avancement
```
**Critères d'acceptation :**
- ✓ Sauvegarde toutes les 3 secondes via WebSocket
- ✓ Indicateur visuel "Sauvegardé" / "Sauvegarde en cours"
- ✓ Reprise exacte au dernier point en cas de reconnexion
- ✓ Versioning (dernières 10 versions)

**Priorité :** Must Have | **Story Points :** 13 | **Sprint :** 2.1

---

**US-009 : Voir l'activité en temps réel des apprenants**
```
En tant que formateur
Je veux voir qui est actif et sur quel contenu
Afin de suivre l'engagement en temps réel
```
**Critères d'acceptation :**
- ✓ Liste apprenants avec statut : actif/inactif
- ✓ Indication du contenu actuellement consulté
- ✓ Durée sur le contenu actuel
- ✓ Rafraîchissement automatique (WebSocket)
- ✓ Filtre par chapitre

**Priorité :** Must Have | **Story Points :** 13 | **Sprint :** 2.1

---

**US-019 : Gagner des points**
```
En tant qu'apprenant
Je veux gagner des points pour chaque action
Afin d'être motivé et gamifié
```
**Critères d'acceptation :**
- ✓ Points attribués : leçon vue (+10), exercice réussi (+50), QCM parfait (+30)
- ✓ Bonus vitesse : exercice en < 5min (+20)
- ✓ Affichage total points sur dashboard
- ✓ Animation lors du gain de points
- ✓ Historique des gains

**Priorité :** Should Have | **Story Points :** 8 | **Sprint :** 3.1

---

**US-020 : Débloquer des badges**
```
En tant qu'apprenant
Je veux obtenir des badges pour mes accomplissements
Afin de célébrer mes succès
```
**Critères d'acceptation :**
- ✓ Badges définis : "Premier pas", "Marathonien" (5h continu), "Perfectionniste" (100% QCM)
- ✓ Notification popup à l'obtention
- ✓ Galerie de badges sur profil
- ✓ Badges verrouillés visibles (grayed out)
- ✓ Description de comment les obtenir

**Priorité :** Should Have | **Story Points :** 8 | **Sprint :** 3.1

---

**US-021 : Voir le classement général**
```
En tant qu'apprenant
Je veux voir ma position dans le classement
Afin de me comparer aux autres
```
**Critères d'acceptation :**
- ✓ Leaderboard : Top 10 + ma position
- ✓ Tri par points totaux
- ✓ Anonymisation optionnelle
- ✓ Réinitialisation hebdomadaire optionnelle
- ✓ Badge pour Top 3

**Priorité :** Could Have | **Story Points :** 5 | **Sprint :** 3.1

---

## 📋 ACTIVITÉ 5 : COLLABORER

### Release 1 (MVP)

**US-025 : Soumettre un projet final**
```
En tant qu'apprenant
Je veux uploader mon projet de fin de chapitre
Afin qu'il soit évalué par le formateur
```
**Critères d'acceptation :**
- ✓ Upload fichiers (ZIP < 50MB)
- ✓ Champ description/commentaires
- ✓ Confirmation de soumission
- ✓ Status : "En attente", "En cours de review", "Validé", "À refaire"
- ✓ Possibilité de re-soumettre

**Priorité :** Must Have | **Story Points :** 8 | **Sprint :** 4.1

---

**US-026 : Évaluer un projet**
```
En tant que formateur
Je veux consulter et noter les projets soumis
Afin de valider la fin de chapitre
```
**Critères d'acceptation :**
- ✓ Liste projets à évaluer
- ✓ Visualisation fichiers (code viewer)
- ✓ Formulaire notation + commentaires
- ✓ Action : Valider / Refuser avec feedback
- ✓ Notification envoyée à l'apprenant

**Priorité :** Must Have | **Story Points :** 13 | **Sprint :** 4.1

---

### Release 2

**US-028 : Poser une question sur le forum**
```
En tant qu'apprenant
Je veux poser une question sur un chapitre spécifique
Afin d'obtenir de l'aide
```
**Critères d'acceptation :**
- ✓ Forum organisé par chapitre
- ✓ Formulaire question : titre, description, code snippet
- ✓ Tagging automatique du chapitre
- ✓ Notification formateur + apprenants du chapitre

**Priorité :** Should Have | **Story Points :** 13 | **Sprint :** 4.2

---

**US-029 : Répondre et aider les autres**
```
En tant qu'apprenant avancé
Je veux répondre aux questions des autres
Afin d'aider la communauté
```
**Critères d'acceptation :**
- ✓ Interface réponse avec éditeur Markdown
- ✓ Système de votes (upvote/downvote)
- ✓ Marquer réponse comme "Solution"
- ✓ Points bonus si réponse marquée solution (+50)
- ✓ Badge "Helpful" après 10 solutions

**Priorité :** Should Have | **Story Points :** 8 | **Sprint :** 4.2

---

## 📋 TECHNICAL STORIES

**TS-001 : Optimiser les performances DB**
```
En tant que développeur
Je veux optimiser les requêtes N+1
Afin d'améliorer les temps de réponse
```
**Critères d'acceptation :**
- ✓ Utilisation select_related / prefetch_related
- ✓ Indexes sur colonnes fréquemment filtrées
- ✓ Temps requête API < 300ms (p95)

**Priorité :** Must Have | **Story Points :** 5 | **Sprint :** 5.1

---

**TS-002 : Implémenter le cache**
```
En tant que développeur
Je veux mettre en cache le contenu statique
Afin de réduire la charge DB
```
**Critères d'acceptation :**
- ✓ Cache Redis pour leçons/chapitres
- ✓ Invalidation cache à la modification
- ✓ TTL configuré par type de contenu

**Priorité :** Should Have | **Story Points :** 5 | **Sprint :** 5.1

---

**TS-003 : Tests de charge**
```
En tant que développeur
Je veux tester la plateforme avec 50 utilisateurs simultanés
Afin de valider la scalabilité
```
**Critères d'acceptation :**
- ✓ Tests Locust avec scénarios réalistes
- ✓ 50 connexions WebSocket simultanées
- ✓ Temps réponse < 500ms sous charge
- ✓ Pas de memory leak après 1h

**Priorité :** Must Have | **Story Points :** 8 | **Sprint :** 5.1

---

## 📊 STORY MAPPING VISUEL

```
┌──────────────────────────────────────────────────────────────────────┐
│                         BACKBONE (Activités)                          │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┤
│ S'inscrire│  Leçons │ Pratiquer│Progresser│Collaborer│  Admin       │
│  Commencer│          │          │          │          │              │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────────┘

═══════════════════════════════════════════════════════════════════════
RELEASE 1 (MVP) - 8 semaines
───────────────────────────────────────────────────────────────────────

[US-001]    [US-004]    [US-013]    [US-006]    [US-025]
Créer       Liste       Exercice    Dashboard   Soumettre
compte      chapitres   code        progression projet

[US-002]    [US-005]    [US-014]    [US-007]    [US-026]
Login       Créer       QCM         Débloquer   Évaluer
            contenu                 chapitre    projet

[US-003]    [US-012]    [US-022]    [US-008]
Gérer       Lire        Validation  Sauvegarde
rôles       leçon       auto        temps réel

                        [US-023]    [US-009]
                        Indices     Activité
                                   temps réel

                                   [US-019]
                                   Points

                                   [US-020]
                                   Badges

═══════════════════════════════════════════════════════════════════════
RELEASE 2 - Fonctionnalités additionnelles
───────────────────────────────────────────────────────────────────────

[US-030]    [US-031]    [US-033]    [US-021]    [US-028]
OAuth       Recherche   Console JS  Leaderboard Forum

            [US-032]                            [US-029]
            Notes                               Réponses

═══════════════════════════════════════════════════════════════════════
TECHNICAL STORIES (Transversales)
───────────────────────────────────────────────────────────────────────

[TS-001] Optimisation DB
[TS-002] Cache Redis
[TS-003] Tests de charge
[TS-004] CI/CD
[TS-005] Documentation
```

---

## 🎯 PRIORISATION MOSCOW

### Must Have (29 stories)
- US-001 à US-009
- US-012 à US-014
- US-016 à US-018
- US-022, US-025, US-026
- TS-001, TS-003

### Should Have (10 stories)
- US-019, US-020, US-023
- US-028, US-029
- TS-002

### Could Have (5 stories)
- US-021
- US-031 à US-033

### Won't Have (Release 1)
- US-030 (OAuth)
- Fonctionnalités avancées forum
- Certificats
- Export PDF

---

## 📈 VÉLOCITÉ ESTIMÉE

**Capacité équipe :** 30 story points / sprint (2 semaines)

**Total story points MVP :** ~200

**Durée estimée :** 12-14 sprints (24-28 semaines)

**Note :** Vélocité à ajuster après les 2 premiers sprints

---

## 🔄 DÉFINITION OF DONE

Une story est "Done" quand :
- [ ] Code developed & peer reviewed
- [ ] Tests unitaires écrits (couverture > 80%)
- [ ] Tests d'intégration passés
- [ ] Documentation API mise à jour (Swagger)
- [ ] Accepté par le Product Owner
- [ ] Déployé sur environnement staging
- [ ] Pas de bugs critiques ouverts

---

## 📝 NOTES

- User stories écrites en collaboration avec formateurs réels
- Priorisation basée sur valeur métier + dépendances techniques
- Révision du backlog tous les 2 sprints
- Feedback utilisateurs intégré en continu
