# Tests bout-en-bout (Playwright)

Ces tests pilotent un **vrai navigateur** contre la stack complète en marche.
Ils ne remplacent pas les tests Vitest (isolés, jsdom) : ils vérifient les
parcours réels, bout à bout.

> Périmètre actuel : **tranche mince** — auth, navigation, pages légales, RGPD.
> Volontairement **hors** soumission d'exercice (qui exige le bac à sable
> celery/docker.sock). Ce sera une tranche ultérieure.

## Prérequis

1. **La stack doit tourner** (front `:5173`, back `:8000`, postgres, redis) :

   ```bash
   docker-compose up -d
   ```

2. **Amorcer les données** (comptes de démo + contenu publié) :

   ```bash
   docker-compose exec backend python manage.py create_demo_users
   docker-compose exec backend python manage.py load_section_1_html --force
   ```

   Seul `navigation.spec.js` dépend du contenu (il ouvre le chapitre
   « Introduction au HTML »). Les autres tests créent leurs propres comptes.

   ⚠️ **Ne pas utiliser `load_demo_content` pour amorcer.** C'est ce qui a
   effacé tout le contenu des cours le 2026-07-22 : la commande supprimait
   *tous* les chapitres, y compris ceux des sections. Elle est désormais bornée
   à ses propres chapitres, mais elle remplace toujours le chapitre HTML riche
   par sa version maigre — `load_section_1_html` fournit le même slug, le même
   titre et la même première leçon, en plus complet et sans rien détruire
   d'autre.

3. **Installer les navigateurs Playwright** (une seule fois) :

   ```bash
   cd frontend
   npx playwright install chromium
   ```

## Lancer

```bash
cd frontend

npm run e2e            # toute la suite, headless
npm run e2e:ui         # mode interactif (débogage pas à pas)
npm run e2e:report     # rouvrir le dernier rapport HTML
```

Cibler un fichier ou un test :

```bash
npx playwright test e2e/auth.spec.js
npx playwright test -g "consentement"
```

## Notes

- Chaque test crée son compte via un **email unique** (`helpers.uniqueEmail`) :
  la suite est ré-exécutable sans purger la base entre deux passages.
- Les tests de suppression de compte n'utilisent **que des comptes jetables**
  qu'ils viennent de créer — jamais les comptes de démo.
- Base URL surchargeable : `E2E_BASE_URL=http://localhost:4173 npm run e2e`.
- La CI ne lance **pas** encore l'E2E (choix assumé : stabiliser en local
  d'abord). Le jour venu, un job devra monter la stack, amorcer, puis lancer
  Playwright headless.
