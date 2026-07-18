```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3.12
Framework:     Flask 3.0 + Flask-SQLAlchemy 3.1 (ORM)
Dependencies:  flask-cors, marshmallow, requests, python-dotenv
Domain:        Task Manager API — tasks, users, categories, reports
Architecture:  Parcialmente organizada — já tem models/ routes/ services/ utils/,
               mas as rotas concentram validação + queries + serialização (sem
               camada de controller/service real)
Source files:  15 files analyzed
DB tables:     users, tasks, categories
================================
```

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask + SQLAlchemy
Files:   15 analyzed | ~1160 lines of code
Date:    2026-07-18

## Summary
CRITICAL: 2 | HIGH: 3 | MEDIUM: 4 | LOW: 3
Total: 12 findings

## Findings

### [CRITICAL] Hardcoded Secrets (SECRET_KEY e senha SMTP)
File: app.py:13, services/notification_service.py:10
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` e
             `self.email_password = 'senha123'` fixos no código.
Impact: Segredos versionados no repositório e no histórico do git.
Recommendation: Mover para módulo de config alimentado por variáveis de
                ambiente. Ver playbook P2.

### [CRITICAL] Exposição do hash de senha nas respostas da API
File: models/user.py:21
Description: `User.to_dict()` inclui `'password': self.password`, então `/users`,
             `/users/<id>` e a resposta de `/login` devolvem o hash da senha.
Impact: Vazamento do hash (MD5, reversível por rainbow tables) via tráfego
        normal da API.
Recommendation: Remover o campo `password` da serialização. Ver playbook P10.

### [HIGH] Hashing de senha fraco/obsoleto (MD5)
File: models/user.py:29,32
Description: `set_password`/`check_password` usam `hashlib.md5`.
Impact: MD5 é inadequado para senhas — colisões e quebra por dicionário.
Recommendation: Usar `werkzeug.security.generate_password_hash` /
                `check_password_hash` (ou bcrypt/argon2). Ver playbook P8.

### [HIGH] Ausência de separação de camadas (lógica nas rotas)
File: routes/task_routes.py:11-63, routes/user_routes.py:10-90, routes/report_routes.py:12-101
Description: As rotas fazem validação, montam queries e serializam manualmente —
             não há camada de controller/service; os "services/" existentes estão
             praticamente vazios/sem uso.
Impact: Rotas gigantes, regra de negócio não reutilizável nem testável.
Recommendation: Introduzir controllers (orquestração fina) + services (regra +
                acesso a dados). Ver playbook P3/P4.

### [HIGH] Debug mode ligado em produção
File: app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)`.
Impact: Debugger interativo exposto = RCE + vazamento de stack traces.
Recommendation: Config dirigida por env, `DEBUG` desligado por padrão. Ver playbook P2.

### [MEDIUM] N+1 queries na listagem de tasks
File: routes/task_routes.py:42,51
Description: `get_tasks` faz `User.query.get(t.user_id)` e
             `Category.query.get(t.category_id)` dentro do loop de tasks.
Impact: 1 + 2N queries; latência cresce com o número de tasks.
Recommendation: Eager loading (`joinedload(Task.user, Task.category)`). Ver playbook P6.

### [MEDIUM] N+1 queries nos relatórios e na listagem de usuários
File: routes/report_routes.py:56, routes/user_routes.py:22
Description: `summary_report` roda `Task.query.filter_by(user_id=u.id)` por usuário
             dentro do loop; `get_users` usa `len(u.tasks)` (lazy load por usuário).
Impact: N+1 em ambos os endpoints.
Recommendation: Agregações agrupadas (`group_by(user_id)`). Ver playbook P6.

### [MEDIUM] Lógica de "overdue" duplicada
File: routes/task_routes.py:30-39,71-80, routes/user_routes.py:171-181, routes/report_routes.py:33-43
Description: O mesmo bloco aninhado `if due_date < now and status not in ...` é
             copiado em várias rotas (e existe também em `Task.is_overdue`, sem uso).
Impact: Regra divergente e correções em N lugares.
Recommendation: Fonte única em `Task.is_overdue()`. Ver playbook P11.

### [MEDIUM] CORS totalmente aberto
File: app.py:15
Description: `CORS(app)` libera todas as origens.
Impact: Qualquer site consegue chamar a API no contexto do usuário.
Recommendation: Restringir a uma allowlist vinda de config.

### [LOW] Bare `except:` engolindo erros
File: routes/task_routes.py:62, routes/user_routes.py:130,149
Description: Blocos `except:` sem tipo que retornam 500 genérico sem log.
Impact: Erros silenciados; difícil diagnosticar.
Recommendation: Error handler centralizado + log. Ver playbook P7.

### [LOW] Imports não usados
File: app.py:7, utils/helpers.py:3-7
Description: `import os, sys, json, datetime` (app) e `os, json, sys, math,
             hashlib` (helpers) sem uso real.
Impact: Ruído e falsa impressão de dependências.
Recommendation: Remover imports mortos.

### [LOW] Token de auth falso + print como logging
File: routes/user_routes.py:210, services/notification_service.py:21,24
Description: `/login` devolve `'fake-jwt-token-' + id`; notificação usa `print`.
Impact: Autenticação fictícia e logging sem estrutura.
Recommendation: JWT real (fora do escopo) e logger centralizado. Ver playbook P13.

## Deprecated APIs
- models/task.py:15,16,52, routes/report_routes.py:35,45 — `datetime.utcnow()`
  (deprecado no Python 3.12+) → `datetime.now(timezone.utc)` (aqui preservando
  semântica naive com um helper `utcnow()`).
- routes/task_routes.py:42,51,67, routes/user_routes.py:29,94,
  routes/report_routes.py:105 — `Model.query.get(id)` (legado no SQLAlchemy 2.0)
  → `db.session.get(Model, id)`.
- models/user.py:29,32 — `hashlib.md5` para senha (prática obsoleta) →
  `werkzeug.security` / bcrypt.

================================
Total: 12 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```
