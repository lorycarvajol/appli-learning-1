# 🏗️ DIAGRAMMES UML - Plateforme d'Apprentissage Web

## 📋 TABLE DES MATIÈRES
1. [Diagramme de Cas d'Utilisation](#use-case)
2. [Diagramme de Classes](#class-diagram)
3. [Diagramme de Séquence - Authentification](#sequence-auth)
4. [Diagramme de Séquence - Exercice avec WebSocket](#sequence-exercise)
5. [Diagramme de Séquence - Déblocage Chapitre](#sequence-unlock)
6. [Diagramme d'Activité - Progression Apprenant](#activity-progress)
7. [Diagramme d'État - Statut Projet](#state-project)
8. [Diagramme de Déploiement](#deployment)
9. [Diagramme de Composants](#component)

---

## <a id="use-case"></a>1. 📊 DIAGRAMME DE CAS D'UTILISATION

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Plateforme d'Apprentissage                        │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐                                        ┌──────────────┐
│              │                                        │              │
│  Apprenant   │                                        │  Formateur   │
│              │                                        │              │
└──────┬───────┘                                        └──────┬───────┘
       │                                                       │
       │                                                       │
       ├─────> (S'inscrire)                                   │
       │                                                       │
       ├─────> (Se connecter) <────────────────────────────────┤
       │                                                       │
       ├─────> (Consulter chapitres)                          │
       │                                                       │
       ├─────> (Lire leçon)                                   │
       │            │                                          │
       │            │ <<include>>                              │
       │            └─────> (Sauvegarder progression)          │
       │                                                       │
       ├─────> (Faire exercice)                               │
       │            │                                          │
       │            │ <<include>>                              │
       │            └─────> (Valider code)                     │
       │                         │                             │
       │                         │ <<extend>>                  │
       │                         └─────> (Obtenir indices)     │
       │                                                       │
       ├─────> (Répondre QCM)                                 │
       │            │                                          │
       │            │ <<include>>                              │
       │            └─────> (Calculer score)                   │
       │                                                       │
       ├─────> (Soumettre projet)                             │
       │                                                       │
       ├─────> (Voir progression)                             │
       │                                                       │
       ├─────> (Consulter badges)                             │
       │                                                       │
       ├─────> (Participer forum)                             │
       │                                                       ├─────> (Créer contenu)
       │                                                       │
       │                                                       ├─────> (Suivre apprenants)
       │                                                       │
       │                                                       ├─────> (Débloquer chapitre)
       │                                                       │
       │                                                       ├─────> (Évaluer projet)
       │                                                       │
       │                                                       ├─────> (Modérer forum)
       │                                                       │
                                                   ┌──────────┴───────┐
                                                   │                  │
                                                   │  Administrateur  │
                                                   │                  │
                                                   └──────────────────┘
                                                               │
                                                               ├─────> (Gérer utilisateurs)
                                                               │
                                                               ├─────> (Configurer système)
                                                               │
                                                               └─────> (Voir statistiques)

┌─────────────────────────────────────────────────────────────────────┐
│                        Système Externe                               │
│                                                                      │
│  (Envoyer email) <──────────────────                                │
│  (Exécuter code sandbox) <──────────                                │
│  (Générer certificat) <─────────────                                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## <a id="class-diagram"></a>2. 🗂️ DIAGRAMME DE CLASSES

```
┌─────────────────────────────────┐
│          User                   │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - email: String                 │
│ - password: String (hashed)     │
│ - first_name: String            │
│ - last_name: String             │
│ - role: Enum[LEARNER,           │
│         TRAINER, ADMIN]         │
│ - is_active: Boolean            │
│ - created_at: DateTime          │
│ - last_login: DateTime          │
├─────────────────────────────────┤
│ + register()                    │
│ + login()                       │
│ + logout()                      │
│ + has_permission(perm): Boolean │
└──────────┬──────────────────────┘
           │ 1
           │
           │ 1..*
┌──────────┴──────────────────────┐
│      UserProfile                │
├─────────────────────────────────┤
│ - user: FK(User)                │
│ - bio: Text                     │
│ - avatar: ImageField            │
│ - total_points: Integer         │
│ - level: Integer                │
│ - timezone: String              │
├─────────────────────────────────┤
│ + update_profile()              │
│ + calculate_level()             │
└─────────────────────────────────┘


┌─────────────────────────────────┐
│          Chapter                │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - title: String                 │
│ - description: Text             │
│ - order: Integer                │
│ - estimated_duration: Integer   │
│ - is_published: Boolean         │
│ - created_by: FK(User)          │
│ - created_at: DateTime          │
├─────────────────────────────────┤
│ + publish()                     │
│ + get_completion_rate(): Float  │
│ + get_lessons(): List[Lesson]   │
└──────────┬──────────────────────┘
           │ 1
           │
           │ 0..*
┌──────────┴──────────────────────┐
│          Lesson                 │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - chapter: FK(Chapter)          │
│ - title: String                 │
│ - content: Text (Markdown)      │
│ - type: Enum[THEORY,            │
│         EXERCISE, QUIZ]         │
│ - order: Integer                │
│ - estimated_time: Integer       │
├─────────────────────────────────┤
│ + render_content(): HTML        │
│ + get_next_lesson(): Lesson     │
└──────────┬──────────────────────┘
           │
           ├────────────────────────────────┐
           │                                │
┌──────────┴──────────────────┐  ┌─────────┴──────────────────┐
│       Exercise              │  │         Quiz               │
├─────────────────────────────┤  ├────────────────────────────┤
│ - lesson: FK(Lesson)        │  │ - lesson: FK(Lesson)       │
│ - instructions: Text        │  │ - questions: JSON          │
│ - starter_code: Text        │  │ - passing_score: Integer   │
│ - solution_code: Text       │  │ - time_limit: Integer      │
│ - tests: JSON               │  ├────────────────────────────┤
│ - max_attempts: Integer     │  │ + calculate_score(): Int   │
│ - points: Integer           │  │ + generate_questions()     │
├─────────────────────────────┤  └────────────────────────────┘
│ + validate_solution(code)   │
│ + get_hint(level): String   │
│ + run_tests(code): Result   │
└─────────────────────────────┘


┌─────────────────────────────────┐
│      UserProgress               │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - user: FK(User)                │
│ - lesson: FK(Lesson)            │
│ - status: Enum[NOT_STARTED,     │
│          IN_PROGRESS,           │
│          COMPLETED]             │
│ - attempts: Integer             │
│ - score: Integer                │
│ - time_spent: Integer (seconds) │
│ - last_code: Text               │
│ - started_at: DateTime          │
│ - completed_at: DateTime        │
├─────────────────────────────────┤
│ + mark_completed()              │
│ + save_progress(data)           │
│ + get_completion_percent()      │
└─────────────────────────────────┘


┌─────────────────────────────────┐
│      ChapterAccess              │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - user: FK(User)                │
│ - chapter: FK(Chapter)          │
│ - is_unlocked: Boolean          │
│ - unlocked_by: FK(User)         │
│ - unlocked_at: DateTime         │
├─────────────────────────────────┤
│ + unlock()                      │
│ + can_access(): Boolean         │
└─────────────────────────────────┘


┌─────────────────────────────────┐
│          Project                │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - chapter: FK(Chapter)          │
│ - user: FK(User)                │
│ - title: String                 │
│ - description: Text             │
│ - files: FileField              │
│ - status: Enum[PENDING,         │
│          REVIEWING,             │
│          APPROVED,              │
│          REJECTED]              │
│ - submitted_at: DateTime        │
│ - reviewed_at: DateTime         │
│ - reviewed_by: FK(User)         │
│ - feedback: Text                │
│ - grade: Integer                │
├─────────────────────────────────┤
│ + submit()                      │
│ + review(grade, feedback)       │
│ + resubmit()                    │
└─────────────────────────────────┘


┌─────────────────────────────────┐
│          Badge                  │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - name: String                  │
│ - description: Text             │
│ - icon: ImageField              │
│ - criteria: JSON                │
│ - points_reward: Integer        │
├─────────────────────────────────┤
│ + check_eligibility(user): Bool │
└──────────┬──────────────────────┘
           │ *
           │
           │ *
┌──────────┴──────────────────────┐
│      UserBadge                  │
├─────────────────────────────────┤
│ - user: FK(User)                │
│ - badge: FK(Badge)              │
│ - earned_at: DateTime           │
├─────────────────────────────────┤
│ + award()                       │
└─────────────────────────────────┘


┌─────────────────────────────────┐
│      PointTransaction           │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - user: FK(User)                │
│ - points: Integer               │
│ - reason: String                │
│ - reference_type: String        │
│ - reference_id: UUID            │
│ - created_at: DateTime          │
├─────────────────────────────────┤
│ + award_points(user, pts)       │
│ + get_user_total(user): Integer │
└─────────────────────────────────┘


┌─────────────────────────────────┐
│          ForumPost              │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - chapter: FK(Chapter)          │
│ - author: FK(User)              │
│ - title: String                 │
│ - content: Text                 │
│ - is_solved: Boolean            │
│ - votes: Integer                │
│ - created_at: DateTime          │
├─────────────────────────────────┤
│ + upvote()                      │
│ + mark_solved()                 │
└──────────┬──────────────────────┘
           │ 1
           │
           │ 0..*
┌──────────┴──────────────────────┐
│      ForumReply                 │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - post: FK(ForumPost)           │
│ - author: FK(User)              │
│ - content: Text                 │
│ - is_solution: Boolean          │
│ - votes: Integer                │
│ - created_at: DateTime          │
├─────────────────────────────────┤
│ + mark_as_solution()            │
└─────────────────────────────────┘


┌─────────────────────────────────┐
│      ActivityLog                │
├─────────────────────────────────┤
│ - id: UUID                      │
│ - user: FK(User)                │
│ - action: String                │
│ - resource_type: String         │
│ - resource_id: UUID             │
│ - metadata: JSON                │
│ - ip_address: String            │
│ - timestamp: DateTime           │
├─────────────────────────────────┤
│ + log_activity(user, action)    │
│ + get_user_activity(user)       │
└─────────────────────────────────┘
```

### Relations principales :
- User `1` ──── `1` UserProfile
- User `1` ──── `*` UserProgress
- User `1` ──── `*` ChapterAccess
- Chapter `1` ──── `*` Lesson
- Lesson `1` ──── `*` UserProgress
- User `*` ──── `*` Badge (via UserBadge)
- Chapter `1` ──── `*` Project
- Chapter `1` ──── `*` ForumPost

---

## <a id="sequence-auth"></a>3. 🔐 DIAGRAMME DE SÉQUENCE - AUTHENTIFICATION

```
┌─────────┐    ┌──────────┐    ┌────────┐    ┌──────────┐    ┌─────────┐
│ Client  │    │ Frontend │    │  API   │    │   Auth   │    │   DB    │
│ Browser │    │  React   │    │ Django │    │  Service │    │ Postgres│
└────┬────┘    └────┬─────┘    └───┬────┘    └────┬─────┘    └────┬────┘
     │              │               │              │               │
     │ 1. Remplir formulaire        │              │               │
     │─────────────>│               │              │               │
     │              │               │              │               │
     │              │ 2. POST /api/auth/login      │               │
     │              │  {email, password}           │               │
     │              │──────────────>│              │               │
     │              │               │              │               │
     │              │               │ 3. Validate credentials       │
     │              │               │─────────────>│               │
     │              │               │              │               │
     │              │               │              │ 4. SELECT user│
     │              │               │              │──────────────>│
     │              │               │              │               │
     │              │               │              │ 5. User data  │
     │              │               │              │<──────────────│
     │              │               │              │               │
     │              │               │ 6. Check password hash        │
     │              │               │<─────────────│               │
     │              │               │              │               │
     │              │               │ 7. Generate JWT token         │
     │              │               │─────────────>│               │
     │              │               │              │               │
     │              │               │              │ 8. UPDATE      │
     │              │               │              │   last_login   │
     │              │               │              │──────────────>│
     │              │               │              │               │
     │              │               │ 9. Token +   │               │
     │              │               │    user data │               │
     │              │               │<─────────────│               │
     │              │               │              │               │
     │              │ 10. Response  │              │               │
     │              │  {token, user}│              │               │
     │              │<──────────────│              │               │
     │              │               │              │               │
     │              │ 11. Store token in localStorage              │
     │              │<──────────────│              │               │
     │              │               │              │               │
     │ 12. Redirect to dashboard    │              │               │
     │<─────────────│               │              │               │
     │              │               │              │               │
     │              │ 13. GET /api/user/me         │               │
     │              │    Header: Authorization Bearer {token}      │
     │              │──────────────>│              │               │
     │              │               │              │               │
     │              │               │ 14. Verify JWT               │
     │              │               │─────────────>│               │
     │              │               │              │               │
     │              │               │ 15. Token valid              │
     │              │               │<─────────────│               │
     │              │               │              │               │
     │              │               │              │ 16. SELECT    │
     │              │               │              │  user profile │
     │              │               │              │──────────────>│
     │              │               │              │               │
     │              │               │              │ 17. Profile   │
     │              │               │              │<──────────────│
     │              │               │              │               │
     │              │ 18. User data │              │               │
     │              │<──────────────│              │               │
     │              │               │              │               │
     │ 19. Display dashboard        │              │               │
     │<─────────────│               │              │               │
     │              │               │              │               │
```

### Gestion des erreurs :
- **Identifiants invalides** → 401 Unauthorized, message "Email ou mot de passe incorrect"
- **Token expiré** → 401 Unauthorized, refresh ou reconnexion
- **User inactif** → 403 Forbidden, message "Compte désactivé"

---

## <a id="sequence-exercise"></a>4. 💻 DIAGRAMME DE SÉQUENCE - EXERCICE AVEC WEBSOCKET

```
┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  ┌────────┐  ┌──────┐
│ Client  │  │  React   │  │ WebSocket│  │ Django  │  │ Celery │  │ Redis│
│ Browser │  │Component │  │ Consumer │  │ Channels│  │ Worker │  │      │
└────┬────┘  └────┬─────┘  └────┬─────┘  └────┬────┘  └───┬────┘  └──┬───┘
     │            │              │             │           │          │
     │ 1. Ouvrir exercice        │             │           │          │
     │───────────>│              │             │           │          │
     │            │              │             │           │          │
     │            │ 2. WS Connect ws://server/progress/{exerciseId} │
     │            │─────────────>│             │           │          │
     │            │              │             │           │          │
     │            │              │ 3. Join room│           │          │
     │            │              │────────────>│           │          │
     │            │              │             │           │          │
     │            │              │             │ 4. SUBSCRIBE channel │
     │            │              │             │──────────────────────>│
     │            │              │             │           │          │
     │            │              │ 5. Connection accepted  │          │
     │            │              │<────────────│           │          │
     │            │              │             │           │          │
     │            │ 6. Connected │             │           │          │
     │            │<─────────────│             │           │          │
     │            │              │             │           │          │
     │ 7. Écrire du code         │             │           │          │
     │───────────>│              │             │           │          │
     │            │              │             │           │          │
     │            │ [Every 3 seconds - Auto save]          │          │
     │            │              │             │           │          │
     │            │ 8. Send      │             │           │          │
     │            │  {type: "save_progress",   │           │          │
     │            │   code: "...",              │           │          │
     │            │   timestamp}│             │           │          │
     │            │─────────────>│             │           │          │
     │            │              │             │           │          │
     │            │              │ 9. Process save        │          │
     │            │              │────────────>│           │          │
     │            │              │             │           │          │
     │            │              │             │ 10. HSET progress:userId │
     │            │              │             │──────────────────────>│
     │            │              │             │           │          │
     │            │              │             │ 11. ACK   │          │
     │            │              │             │<──────────────────────│
     │            │              │             │           │          │
     │            │              │ 12. Saved  │           │          │
     │            │              │<────────────│           │          │
     │            │              │             │           │          │
     │            │ 13. Show "Sauvegardé"     │           │          │
     │<───────────│              │             │           │          │
     │            │              │             │           │          │
     │ 14. Click "Soumettre"     │             │           │          │
     │───────────>│              │             │           │          │
     │            │              │             │           │          │
     │            │ 15. Send     │             │           │          │
     │            │  {type: "validate_code",   │           │          │
     │            │   code: "...",              │           │          │
     │            │   exerciseId}│             │           │          │
     │            │─────────────>│             │           │          │
     │            │              │             │           │          │
     │            │              │ 16. Queue validation task        │
     │            │              │────────────>│           │          │
     │            │              │             │           │          │
     │            │              │             │ 17. LPUSH task_queue │
     │            │              │             │──────────────────────>│
     │            │              │             │           │          │
     │            │              │             │ 18. Task queued      │
     │            │              │             │<──────────────────────│
     │            │              │             │           │          │
     │            │              │ 19. Task ID│           │          │
     │            │              │<────────────│           │          │
     │            │              │             │           │          │
     │            │ 20. "Validation en cours..."          │          │
     │<───────────│              │             │           │          │
     │            │              │             │           │          │
     │            │              │             │ 21. LPOP task        │
     │            │              │             │           │<─────────│
     │            │              │             │           │          │
     │            │              │             │ 22. Execute tests    │
     │            │              │             │           │ [Docker Sandbox]
     │            │              │             │           │          │
     │            │              │             │ 23. Validation result│
     │            │              │             │<──────────│          │
     │            │              │             │           │          │
     │            │              │             │ 24. PUBLISH result   │
     │            │              │             │──────────────────────>│
     │            │              │             │           │          │
     │            │              │ 25. Result │           │          │
     │            │              │<────────────│           │          │
     │            │              │             │           │          │
     │            │ 26. Send result            │           │          │
     │            │  {success: true,           │           │          │
     │            │   tests: [...],            │           │          │
     │            │   points: 50}│             │           │          │
     │            │<─────────────│             │           │          │
     │            │              │             │           │          │
     │ 27. Display result + animation         │           │          │
     │<───────────│              │             │           │          │
     │            │              │             │           │          │
     │            │ 28. Update DB (async)     │           │          │
     │            │              │────────────>│           │          │
     │            │              │             │           │          │
     │            │              │ 29. Award points & badge check   │
     │            │              │────────────>│           │          │
     │            │              │             │           │          │
```

### Cas particuliers :
- **Déconnexion** → Reconnexion automatique avec reprise du dernier état
- **Timeout validation** → Message "La validation prend trop de temps, réessayez"
- **Tests échoués** → Affichage détaillé des erreurs avec hints

---

## <a id="sequence-unlock"></a>5. 🔓 DIAGRAMME DE SÉQUENCE - DÉBLOCAGE CHAPITRE

```
┌───────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────┐
│ Formateur │    │   Frontend   │    │     API     │    │   DB    │
│  (Sophie) │    │    React     │    │   Django    │    │ Postgres│
└─────┬─────┘    └──────┬───────┘    └──────┬──────┘    └────┬────┘
      │                 │                   │                 │
      │ 1. Accéder dashboard formateur      │                 │
      │────────────────>│                   │                 │
      │                 │                   │                 │
      │                 │ 2. GET /api/trainer/students        │
      │                 │──────────────────>│                 │
      │                 │                   │                 │
      │                 │                   │ 3. SELECT students, progress
      │                 │                   │────────────────>│
      │                 │                   │                 │
      │                 │                   │ 4. Student data │
      │                 │                   │<────────────────│
      │                 │                   │                 │
      │                 │ 5. Students list  │                 │
      │                 │<──────────────────│                 │
      │                 │                   │                 │
      │ 6. Affichage liste avec filtres      │                 │
      │<────────────────│                   │                 │
      │                 │                   │                 │
      │ 7. Filtrer "Chapitre 2 complété"    │                 │
      │────────────────>│                   │                 │
      │                 │                   │                 │
      │ 8. Filtrage côté client             │                 │
      │<────────────────│                   │                 │
      │                 │                   │                 │
      │ 9. Sélectionner Alex                │                 │
      │────────────────>│                   │                 │
      │                 │                   │                 │
      │ 10. Voir détails progression        │                 │
      │<────────────────│                   │                 │
      │                 │                   │                 │
      │ 11. Click "Débloquer Chapitre 3"    │                 │
      │────────────────>│                   │                 │
      │                 │                   │                 │
      │                 │ 12. Confirmation modal            │
      │                 │  "Débloquer Ch.3 pour Alex ?"     │
      │<────────────────│                   │                 │
      │                 │                   │                 │
      │ 13. Confirmer   │                   │                 │
      │────────────────>│                   │                 │
      │                 │                   │                 │
      │                 │ 14. POST /api/trainer/unlock      │
      │                 │  {userId: "alex-id",              │
      │                 │   chapterId: 3}   │                 │
      │                 │──────────────────>│                 │
      │                 │                   │                 │
      │                 │                   │ 15. Check permissions
      │                 │                   │  (is_trainer?)  │
      │                 │                   │                 │
      │                 │                   │ 16. BEGIN TRANSACTION
      │                 │                   │────────────────>│
      │                 │                   │                 │
      │                 │                   │ 17. INSERT ChapterAccess
      │                 │                   │  (user, chapter, unlocked_by, timestamp)
      │                 │                   │────────────────>│
      │                 │                   │                 │
      │                 │                   │ 18. INSERT ActivityLog
      │                 │                   │────────────────>│
      │                 │                   │                 │
      │                 │                   │ 19. COMMIT     │
      │                 │                   │────────────────>│
      │                 │                   │                 │
      │                 │                   │ 20. Send notification
      │                 │                   │  to Alex (email + in-app)
      │                 │                   │                 │
      │                 │                   │ 21. Broadcast WebSocket
      │                 │                   │  to Alex's connection
      │                 │                   │                 │
      │                 │ 22. Success      │                 │
      │                 │  {message: "Chapitre débloqué"}   │
      │                 │<──────────────────│                 │
      │                 │                   │                 │
      │ 23. Toast notification "Chapitre débloqué pour Alex"│
      │<────────────────│                   │                 │
      │                 │                   │                 │
      │ 24. Update UI (badge "Débloqué")    │                 │
      │<────────────────│                   │                 │
      │                 │                   │                 │


┌───────────┐    ┌──────────────┐    ┌─────────────┐
│ Apprenant │    │   Frontend   │    │  WebSocket  │
│   (Alex)  │    │    React     │    │   Server    │
└─────┬─────┘    └──────┬───────┘    └──────┬──────┘
      │                 │                   │
      │ [Pendant ce temps, Alex est connecté]
      │                 │                   │
      │                 │ 25. WS Message   │
      │                 │  {type: "chapter_unlocked",
      │                 │   chapterId: 3}  │
      │                 │<──────────────────│
      │                 │                   │
      │ 26. Notification "Nouveau chapitre disponible !"
      │<────────────────│                   │
      │                 │                   │
      │ 27. Redirection auto si sur dashboard
      │<────────────────│                   │
      │                 │                   │
```

### Règles métier :
- **Vérification prérequis** : Chapitre précédent complété à 100%
- **Permission formateur** : Seulement le formateur assigné peut débloquer
- **Traçabilité** : Toute action logguée avec timestamp et auteur
- **Notification multiple** : Email + in-app + WebSocket

---

## <a id="activity-progress"></a>6. 🔄 DIAGRAMME D'ACTIVITÉ - PROGRESSION APPRENANT

```
                        [Début]
                           │
                           ▼
                    ┌─────────────┐
                    │ Se connecter│
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │ Accéder Dashboard│
                    └──────┬──────────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │ Consulter liste │
                    │   chapitres     │
                    └──────┬──────────┘
                           │
                           ▼
                   ╔═══════════════════╗
                   ║ Chapitre débloqué?║
                   ╚═══════╤═══════════╝
                           │
                    ┌──────┴──────┐
                    │              │
                   OUI            NON
                    │              │
                    ▼              ▼
         ┌──────────────────┐  ┌────────────────┐
         │ Ouvrir chapitre  │  │ Afficher badge │
         │                  │  │   "Verrouillé" │
         └────────┬─────────┘  └────────┬───────┘
                  │                     │
                  ▼                     ▼
         ┌──────────────────┐     [Attendre déblocage]
         │ Lire leçon       │           │
         └────────┬─────────┘           │
                  │                     │
                  ▼                     │
         ┌──────────────────┐           │
         │ Sauvegarder auto │           │
         │ toutes les 3s    │           │
         └────────┬─────────┘           │
                  │                     │
                  ▼                     │
         ╔═══════════════════╗          │
         ║ Type de contenu ? ║          │
         ╚═══════╤═══════════╝          │
                  │                     │
        ┌─────────┼─────────┐           │
        │         │         │           │
     THÉORIE   EXERCICE   QCM          │
        │         │         │           │
        ▼         ▼         ▼           │
   ┌────────┐ ┌───────┐ ┌──────┐       │
   │ Lire   │ │Écrire │ │Répon-│       │
   │ contenu│ │ code  │ │dre   │       │
   └───┬────┘ └───┬───┘ └──┬───┘       │
       │          │        │            │
       │          ▼        │            │
       │    ┌──────────┐   │            │
       │    │Soumettre │   │            │
       │    │solution  │   │            │
       │    └────┬─────┘   │            │
       │         │         │            │
       │         ▼         ▼            │
       │   ╔═════════════════╗          │
       │   ║   Validation    ║          │
       │   ║    réussie ?    ║          │
       │   ╚═════╤═══════════╝          │
       │         │                      │
       │    ┌────┴────┐                 │
       │    │         │                 │
       │   OUI       NON                │
       │    │         │                 │
       │    ▼         ▼                 │
       │ ┌─────┐  ┌──────────┐          │
       │ │+pts │  │ Feedback │          │
       │ │Badge│  │ erreurs  │          │
       │ └──┬──┘  └────┬─────┘          │
       │    │          │                │
       │    │          ▼                │
       │    │     ╔═══════════╗         │
       │    │     ║Tentatives ║         │
       │    │     ║ < max ?   ║         │
       │    │     ╚═══╤═══════╝         │
       │    │         │                 │
       │    │    ┌────┴────┐            │
       │    │    │         │            │
       │    │   OUI       NON           │
       │    │    │         │            │
       │    │    │         ▼            │
       │    │    │    ┌────────┐        │
       │    │    │    │Demander│        │
       │    │    │    │ indice │        │
       │    │    │    └───┬────┘        │
       │    │    │        │             │
       │    │    └────────┤             │
       │    │             ▼             │
       └────┴─────> [Réessayer] ────────┘
                         │
                         │
                         ▼
                  ┌─────────────┐
                  │ Marquer     │
                  │ "Complété"  │
                  └──────┬──────┘
                         │
                         ▼
                  ╔══════════════════╗
                  ║ Toutes leçons    ║
                  ║ du chapitre      ║
                  ║ complétées ?     ║
                  ╚════════╤═════════╝
                           │
                    ┌──────┴──────┐
                    │             │
                   OUI           NON
                    │             │
                    ▼             │
           ┌────────────────┐    │
           │ Débloquer      │    │
           │ Projet Final   │    │
           └────────┬───────┘    │
                    │             │
                    ▼             │
           ┌────────────────┐    │
           │ Soumettre      │    │
           │ Projet         │    │
           └────────┬───────┘    │
                    │             │
                    ▼             │
           ╔════════════════╗    │
           ║ Projet validé  ║    │
           ║ par formateur? ║    │
           ╚════════╤═══════╝    │
                    │             │
             ┌──────┴──────┐     │
             │             │     │
            OUI           NON    │
             │             │     │
             ▼             ▼     │
      ┌────────────┐  ┌───────┐ │
      │ Chapitre   │  │Refaire│ │
      │ COMPLÉTÉ   │  │projet │ │
      │ Badge 🏆   │  └───┬───┘ │
      └──────┬─────┘      │     │
             │            │     │
             │            └─────┘
             │
             ▼
      ┌─────────────────┐
      │ Notifier        │
      │ formateur pour  │
      │ déblocage Ch+1  │
      └─────────┬───────┘
                │
                ▼
           [Retour Dashboard]
                │
                │
            [Fin/Boucle]
```

### Points clés :
- **Sauvegarde continue** : Aucune perte de données
- **Validation progressive** : Feedback immédiat
- **Gamification** : Points et badges à chaque étape
- **Blocage contrôlé** : Formateur garde la main

---

## <a id="state-project"></a>7. 🎯 DIAGRAMME D'ÉTAT - STATUT PROJET

```
                        [Création]
                            │
                            │ submit()
                            ▼
                   ┌────────────────┐
           ┌──────>│    PENDING     │<──────┐
           │       │  (En attente)  │       │
           │       └────────┬───────┘       │
           │                │               │
           │                │ assign()      │
           │                │               │
           │                ▼               │ resubmit()
           │       ┌────────────────┐       │
           │       │   REVIEWING    │       │
           │       │(En cours review)│      │
           │       └────────┬───────┘       │
           │                │               │
           │         ┌──────┴──────┐        │
           │         │             │        │
           │      approve()     reject()    │
           │         │             │        │
           │         ▼             ▼        │
           │  ┌────────────┐  ┌──────────┐ │
           │  │  APPROVED  │  │ REJECTED │─┘
           │  │  (Validé)  │  │(À refaire)│
           │  └──────┬─────┘  └──────────┘
           │         │
           │         │ archive()
           │         │
           │         ▼
           │  ┌────────────┐
           └──│  ARCHIVED  │
              │ (Archivé)  │
              └────────────┘

ÉTATS & TRANSITIONS DÉTAILLÉES :

┌─────────────────────────────────────────────────────────────────┐
│ PENDING (En attente de review)                                  │
├─────────────────────────────────────────────────────────────────┤
│ Actions possibles:                                              │
│  • assign(trainer) → REVIEWING                                  │
│  • cancel() → CANCELLED (si apprenant retire)                   │
│                                                                 │
│ Acteurs: Apprenant (soumission), Système (notification)        │
│ Durée typique: 0-48h                                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ REVIEWING (En cours de review par formateur)                    │
├─────────────────────────────────────────────────────────────────┤
│ Actions possibles:                                              │
│  • approve(grade, feedback) → APPROVED                          │
│  • reject(feedback) → REJECTED                                  │
│  • request_changes(comments) → REVIEWING (reste en review)      │
│                                                                 │
│ Acteurs: Formateur                                              │
│ Durée typique: 1-7 jours                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ APPROVED (Validé)                                               │
├─────────────────────────────────────────────────────────────────┤
│ Actions possibles:                                              │
│  • archive() → ARCHIVED (après 30 jours)                        │
│                                                                 │
│ Side effects:                                                   │
│  • Déblocage chapitre suivant                                   │
│  • Attribution badge "Projet complété"                          │
│  • +200 points                                                  │
│  • Notification apprenant                                       │
│                                                                 │
│ État final (pour progression)                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ REJECTED (Refusé - À refaire)                                   │
├─────────────────────────────────────────────────────────────────┤
│ Actions possibles:                                              │
│  • resubmit(new_files) → PENDING                                │
│  • abandon() → CANCELLED                                        │
│                                                                 │
│ Side effects:                                                   │
│  • Notification apprenant avec feedback détaillé                │
│  • Compteur tentatives +1                                       │
│                                                                 │
│ Tentatives max: 3 (configurable)                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ARCHIVED (Archivé)                                              │
├─────────────────────────────────────────────────────────────────┤
│ Actions possibles: Aucune (lecture seule)                       │
│                                                                 │
│ Déclencheurs:                                                   │
│  • Auto après 30 jours si APPROVED                              │
│  • Manuel par admin                                             │
│                                                                 │
│ État final (historique uniquement)                              │
└─────────────────────────────────────────────────────────────────┘
```

### Règles de transition :
- Un projet ne peut être `resubmit` que s'il est `REJECTED`
- Maximum 3 soumissions par projet
- Le formateur ne peut `approve` que s'il a le rôle TRAINER
- Notifications envoyées à chaque transition d'état

---

## <a id="deployment"></a>8. 🌐 DIAGRAMME DE DÉPLOIEMENT

```
┌───────────────────────────────────────────────────────────────────┐
│                          PRODUCTION                               │
└───────────────────────────────────────────────────────────────────┘

┌──────────────────┐                  ┌──────────────────────────────┐
│   Client Tier    │                  │      Application Tier         │
└──────────────────┘                  └──────────────────────────────┘

┌─────────────────┐                   ┌──────────────────────────────┐
│  User Browser   │ HTTPS             │     Railway / Render         │
│                 │──────────────────>│                              │
│ - React App     │   Requests        │  ┌────────────────────────┐  │
│ - WebSocket     │                   │  │  Django Container      │  │
│   Client        │<══════════════════│  │  ┌──────────────────┐  │  │
└─────────────────┘   Responses       │  │  │ Gunicorn WSGI   │  │  │
                                      │  │  │ (Port 8000)     │  │  │
                                      │  │  └────────┬─────────┘  │  │
                                      │  │           │            │  │
┌─────────────────┐                   │  │  ┌────────┴─────────┐  │  │
│  Mobile App     │                   │  │  │ Daphne ASGI     │  │  │
│  (Future)       │                   │  │  │ WebSockets      │  │  │
│                 │                   │  │  │ (Port 8001)     │  │  │
└─────────────────┘                   │  │  └─────────────────┘  │  │
                                      │  │                        │  │
                                      │  │  ENV Variables:        │  │
                                      │  │  - DATABASE_URL        │  │
                                      │  │  - REDIS_URL           │  │
                                      │  │  - SECRET_KEY          │  │
                                      │  └────────────────────────┘  │
                                      │                              │
                                      │  ┌────────────────────────┐  │
                                      │  │  Celery Worker         │  │
                                      │  │  - Task execution      │  │
                                      │  │  - Code validation     │  │
                                      │  └────────────────────────┘  │
                                      │                              │
                                      │  ┌────────────────────────┐  │
                                      │  │  Celery Beat           │  │
                                      │  │  - Scheduled tasks     │  │
                                      │  │  - Cleanup jobs        │  │
                                      │  └────────────────────────┘  │
                                      └──────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                        Data Tier                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┐    ┌───────────────────────────────┐
│  PostgreSQL Database         │    │     Redis Cluster             │
│  (Railway / Supabase)        │    │  (Redis Labs / Railway)       │
│                              │    │                               │
│  - Users, Progress           │    │  ┌─────────────────────────┐  │
│  - Chapters, Lessons         │    │  │  Channel Layer          │  │
│  - Exercises, Quizzes        │    │  │  - WebSocket messages   │  │
│  - Projects, Forum           │    │  └─────────────────────────┘  │
│  - Badges, Points            │    │                               │
│                              │    │  ┌─────────────────────────┐  │
│  Backups: Daily              │    │  │  Cache                  │  │
│  Retention: 30 days          │    │  │  - Lessons content      │  │
│                              │    │  │  - User sessions        │  │
│  Connection Pooling: Yes     │    │  └─────────────────────────┘  │
│  Max Connections: 100        │    │                               │
└──────────────────────────────┘    │  ┌─────────────────────────┐  │
                                    │  │  Task Queue (Celery)    │  │
                                    │  │  - Validation jobs      │  │
                                    │  └─────────────────────────┘  │
                                    └───────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                    External Services                              │
└──────────────────────────────────────────────────────────────────┘

┌───────────────────┐  ┌─────────────────┐  ┌────────────────────┐
│  Email Service    │  │  S3 / Storage   │  │   Monitoring       │
│  (SendGrid)       │  │  (Railway)      │  │   (Sentry)         │
│                   │  │                 │  │                    │
│  - Notifications  │  │  - User uploads │  │  - Error tracking  │
│  - Password reset │  │  - Project files│  │  - Performance     │
└───────────────────┘  │  - Static files │  │  - Alerts          │
                       └─────────────────┘  └────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     CI/CD Pipeline                                │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  GitHub Actions                                                  │
│                                                                  │
│  [Push to main] → [Run Tests] → [Build Images] → [Deploy]       │
│                       │                                          │
│                       ├─ Unit Tests                              │
│                       ├─ Integration Tests                       │
│                       └─ Linting & Security Scan                 │
│                                                                  │
│  Environments:                                                   │
│  - staging (auto-deploy on PR)                                  │
│  - production (manual approval)                                 │
└─────────────────────────────────────────────────────────────────┘

ARCHITECTURE NOTES:
───────────────────

1. SCALABILITY:
   - Horizontal scaling: Multiple Django/Daphne instances
   - Redis: Handles up to 10k concurrent connections
   - PostgreSQL: Connection pooling via PgBouncer
   - CDN: CloudFlare for static assets

2. SECURITY:
   - HTTPS enforced (Let's Encrypt)
   - JWT tokens with refresh mechanism
   - Rate limiting on all endpoints
   - CORS configured for frontend domain only
   - SQL injection prevention (Django ORM)
   - XSS protection (Content Security Policy)

3. MONITORING:
   - Sentry: Real-time error tracking
   - Railway Metrics: Resource usage
   - Custom Prometheus metrics
   - Log aggregation: Railway logs

4. BACKUP STRATEGY:
   - Database: Daily automated backups (30 days retention)
   - Redis: AOF persistence
   - User uploads: S3 versioning enabled

5. DISASTER RECOVERY:
   - RTO (Recovery Time Objective): 1 hour
   - RPO (Recovery Point Objective): 24 hours
   - Multi-region backup storage

NETWORK TOPOLOGY:
─────────────────

Internet
   │
   ▼
[CloudFlare CDN]
   │
   ▼
[Load Balancer]
   │
   ├────> [Django Instance 1] ─┐
   ├────> [Django Instance 2] ─┼──> [PostgreSQL]
   └────> [Django Instance 3] ─┘    [Redis]
```

---

## <a id="component"></a>9. 🧩 DIAGRAMME DE COMPOSANTS

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                           │
└──────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│  ┌────────────────────┐    ┌──────────────────┐                  │
│  │   UI Components    │    │   Redux Store    │                  │
│  │                    │    │                  │                  │
│  │ - ChapterList      │◄───┤ - authSlice      │                  │
│  │ - LessonViewer     │    │ - progressSlice  │                  │
│  │ - CodeEditor       │    │ - gamificationSl │                  │
│  │ - QuizInterface    │    └────────┬─────────┘                  │
│  │ - Dashboard        │             │                            │
│  │ - Forum            │             │                            │
│  └──────────┬─────────┘             │                            │
│             │                       │                            │
│             ▼                       ▼                            │
│  ┌──────────────────────────────────────────┐                   │
│  │         Services Layer                   │                   │
│  ├──────────────────────────────────────────┤                   │
│  │  apiService.js    - REST API calls       │                   │
│  │  wsService.js     - WebSocket management │                   │
│  │  authService.js   - Auth logic           │                   │
│  │  cacheService.js  - Local storage cache  │                   │
│  └──────────────────┬───────────────────────┘                   │
│                     │                                            │
└─────────────────────┼────────────────────────────────────────────┘
                      │
                      │ HTTPS/WSS
                      │
┌─────────────────────┼────────────────────────────────────────────┐
│                     ▼                                            │
│  ┌──────────────────────────────────────────┐                   │
│  │         API Gateway (Django)             │                   │
│  ├──────────────────────────────────────────┤                   │
│  │  - Routing                               │                   │
│  │  - Authentication Middleware             │                   │
│  │  - Rate Limiting                         │                   │
│  │  - CORS                                  │                   │
│  └──────────────────┬───────────────────────┘                   │
│                     │                                            │
│                     │                                            │
│  ┌──────────────────┴───────────────────────┐                   │
│  │         BACKEND (Django)                 │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     Apps Layer                           │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  ┌────────────┐  ┌────────────┐  ┌─────────────┐       │   │
│  │  │  accounts  │  │  courses   │  │ progression │       │   │
│  │  ├────────────┤  ├────────────┤  ├─────────────┤       │   │
│  │  │ - User     │  │ - Chapter  │  │ - Progress  │       │   │
│  │  │ - Profile  │  │ - Lesson   │  │ - Access    │       │   │
│  │  │ - Auth     │  │ - Exercise │  │ - Activity  │       │   │
│  │  └────────────┘  │ - Quiz     │  └─────────────┘       │   │
│  │                  │ - Project  │                        │   │
│  │                  └────────────┘                        │   │
│  │                                                          │   │
│  │  ┌────────────────┐  ┌────────────┐  ┌────────────┐   │   │
│  │  │  gamification  │  │   forum    │  │ validation │   │   │
│  │  ├────────────────┤  ├────────────┤  ├────────────┤   │   │
│  │  │ - Badge        │  │ - Post     │  │ - Runner   │   │   │
│  │  │ - Points       │  │ - Reply    │  │ - Sandbox  │   │   │
│  │  │ - Leaderboard  │  │ - Vote     │  │ - Tests    │   │   │
│  │  └────────────────┘  └────────────┘  └────────────┘   │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Django Channels                         │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  ┌────────────────────────────────────────────────┐     │   │
│  │  │  consumers/                                    │     │   │
│  │  │  ├─ ProgressConsumer  (real-time save)        │     │   │
│  │  │  ├─ ActivityConsumer  (live tracking)         │     │   │
│  │  │  └─ NotificationConsumer (alerts)             │     │   │
│  │  └────────────────────────────────────────────────┘     │   │
│  │                                                          │   │
│  │  ┌────────────────────────────────────────────────┐     │   │
│  │  │  Channel Layer (Redis)                         │     │   │
│  │  │  - Group management                            │     │   │
│  │  │  - Message broadcasting                        │     │   │
│  │  └────────────────────────────────────────────────┘     │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Celery Workers                         │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  tasks/                                                  │   │
│  │  ├─ validation_tasks.py    (code validation)            │   │
│  │  ├─ notification_tasks.py  (email sending)              │   │
│  │  ├─ gamification_tasks.py  (badge checks)               │   │
│  │  └─ cleanup_tasks.py       (old data removal)           │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Core Services                               │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  services/                                               │   │
│  │  ├─ auth_service.py        (JWT, permissions)           │   │
│  │  ├─ progress_service.py    (tracking logic)             │   │
│  │  ├─ gamification_service.py (points/badges)             │   │
│  │  ├─ validation_service.py  (code execution)             │   │
│  │  └─ notification_service.py (multi-channel notify)      │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                   │
└──────────────────────────────────────────────────────────────────┘

┌────────────────────────┐        ┌──────────────────────────────┐
│  PostgreSQL            │        │       Redis                  │
├────────────────────────┤        ├──────────────────────────────┤
│                        │        │                              │
│ - Relational data      │        │  [db0] Channel Layer         │
│ - User accounts        │        │  [db1] Cache                 │
│ - Course content       │        │  [db2] Celery Queue          │
│ - Progress tracking    │        │  [db3] Sessions              │
│ - Forum posts          │        │                              │
│ - Transactions         │        └──────────────────────────────┘
│                        │
└────────────────────────┘        ┌──────────────────────────────┐
                                  │  File Storage (S3)           │
                                  ├──────────────────────────────┤
                                  │                              │
                                  │  /user-uploads/              │
                                  │  /project-submissions/       │
                                  │  /static/                    │
                                  │  /media/                     │
                                  │                              │
                                  └──────────────────────────────┘

COMPONENT INTERACTIONS:
───────────────────────

1. User Authentication Flow:
   React UI → apiService → Django Auth App → PostgreSQL
                                  ↓
                             Generate JWT
                                  ↓
                         Return to Frontend

2. Real-time Progress Save:
   CodeEditor → wsService → Daphne → ProgressConsumer
                                          ↓
                                   Redis (cache)
                                          ↓
                                   PostgreSQL (batch)

3. Exercise Validation:
   Submit Code → API → validation_service → Celery Task
                                               ↓
                                        Docker Sandbox
                                               ↓
                                        Return Result
                                               ↓
                                     WebSocket Notification

4. Gamification:
   Action Completed → gamification_service → Check Criteria
                                                   ↓
                                            Award Badge/Points
                                                   ↓
                                            Notification

DESIGN PATTERNS USED:
─────────────────────

- Repository Pattern: Data access abstraction
- Service Layer: Business logic separation
- Observer Pattern: WebSocket notifications
- Strategy Pattern: Different validation strategies
- Factory Pattern: Task creation in Celery
- Singleton Pattern: Redis connection pool
```

---

## 📝 NOTES FINALES

### Conventions UML utilisées :
- **Cardinalités** : 1 (un), * (plusieurs), 0..* (zéro ou plusieurs)
- **Relations** : → (dépendance), ◄── (association), ═══ (communication)
- **Stéréotypes** : <<include>>, <<extend>>, <<create>>

### Outils recommandés pour éditer ces diagrammes :
- PlantUML (texte → diagrammes)
- Draw.io / Lucidchart (visuel)
- Mermaid (intégration Git)
- Enterprise Architect (professionnel)

### Prochaines étapes :
1. Valider ces diagrammes avec l'équipe
2. Générer le schéma de base de données détaillé
3. Définir les contrats d'API (OpenAPI/Swagger)
4. Créer les wireframes UI
