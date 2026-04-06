# ERD (схема сущностей БД)

Диаграмма построена по ORM-моделям в `app/models`.

```mermaid
erDiagram
  USERS {
    int id PK
    string email "unique"
    string hashed_password
    string full_name
    datetime created_at
  }

  SKILLS {
    int id PK
    string name "unique"
    datetime created_at
  }

  PROJECTS {
    int id PK
    string title
    string description
    datetime created_at
    datetime nullable deadline
    int owner_id FK
  }

  TEAMS {
    int id PK
    string name
    datetime created_at
    int project_id FK
  }

  PROJECT_TASKS {
    int id PK
    string title
    string status
    datetime created_at
    datetime nullable due_date
    int team_id FK
    int sort_order
  }

  USER_SKILLS {
    int user_id PK, FK
    int skill_id PK, FK
    int proficiency
    datetime created_at
  }

  TEAM_MEMBERSHIPS {
    int team_id PK, FK
    int user_id PK, FK
    string role
    datetime joined_at
  }

  USERS ||--o{ PROJECTS : "owner_id"
  PROJECTS ||--o{ TEAMS : "project_id"
  TEAMS ||--o{ PROJECT_TASKS : "team_id"

  USERS ||--o{ USER_SKILLS : "user_id"
  SKILLS ||--o{ USER_SKILLS : "skill_id"

  TEAMS ||--o{ TEAM_MEMBERSHIPS : "team_id"
  USERS ||--o{ TEAM_MEMBERSHIPS : "user_id"
```

