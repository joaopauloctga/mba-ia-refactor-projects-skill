# Skill de Auditoria e Refatoração Arquitetural (`refactor-arch`)

Solução do desafio: uma **Skill do Claude Code** que audita qualquer codebase de
backend e a refatora para o padrão **MVC**, de forma **agnóstica de tecnologia**.
A skill roda em 3 fases sequenciais — **Análise → Auditoria → Refatoração** — e
foi validada nos 3 projetos legados fornecidos (2 Python/Flask e 1 Node/Express).

> O enunciado original do desafio está preservado no histórico do git (commit
> inicial). Este README documenta a **solução**.

## Estrutura do repositório

```
mba-ia-refactor-projects-skill/
├── README.md                          # esta documentação
├── reports/
│   ├── audit-project-1.md             # saída da Fase 2 — code-smells-project
│   ├── audit-project-2.md             # saída da Fase 2 — ecommerce-api-legacy
│   └── audit-project-3.md             # saída da Fase 2 — task-manager-api
│
├── code-smells-project/               # Projeto 1 — Python/Flask (E-commerce), refatorado
│   ├── .claude/skills/refactor-arch/  # A SKILL (SKILL.md + 5 arquivos de referência)
│   └── src/ ...                        # estrutura MVC resultante
├── ecommerce-api-legacy/              # Projeto 2 — Node/Express (LMS+checkout), refatorado
│   ├── .claude/skills/refactor-arch/  # cópia da skill
│   └── src/ ...
└── task-manager-api/                  # Projeto 3 — Python/Flask (Task Manager), refatorado
    ├── .claude/skills/refactor-arch/  # cópia da skill
    └── src/ ...
```

A skill vive em `.claude/skills/refactor-arch/` e é composta por:

| Arquivo | Área de conhecimento |
|---|---|
| `SKILL.md` | Orquestrador — as 3 fases e as regras de ouro |
| `references/project-analysis.md` | Heurísticas de detecção de linguagem/framework/DB/arquitetura |
| `references/anti-patterns.md` | Catálogo de anti-patterns + APIs deprecated (20 entradas) |
| `references/report-template.md` | Formato padronizado do relatório de auditoria |
| `references/mvc-guidelines.md` | Regras do MVC alvo (Models, Views/Routes, Controllers, Services) |
| `references/refactoring-playbook.md` | 13 receitas de transformação com código antes/depois |

---

## A) Análise Manual

Leitura manual do código dos três projetos antes de construir a skill. Para cada
projeto, os achados de maior impacto arquitetural (severidade conforme a escala
CRITICAL/HIGH/MEDIUM/LOW do desafio). As linhas referem-se ao **código original**
(preservado no git).

### Projeto 1 — `code-smells-project` (Python/Flask, E-commerce)

| # | Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|---|
| 1 | **CRITICAL** | SQL Injection generalizado (queries por concatenação) | `models.py:28,47-50,109-111,289-297` | Permite ler/alterar/apagar dados e burlar login com `' OR '1'='1` |
| 2 | **CRITICAL** | `SECRET_KEY` hardcoded (e ecoada no /health) | `app.py:7`, `controllers.py:289` | Segredo versionado; qualquer um assina sessões |
| 3 | **CRITICAL** | God Module com 4 domínios | `models.py:1-314` | Impossível testar/isolar; qualquer mudança afeta tudo |
| 4 | **CRITICAL** | Endpoint de SQL arbitrário `/admin/query` | `app.py:59-78` | Execução remota de qualquer comando no banco |
| 5 | **CRITICAL** | Senhas em texto puro (armazenadas e retornadas) | `database.py:76-78`, `models.py:83` | Vazamento de credenciais em breach e via API |
| 6 | HIGH | Regra de negócio na camada de dados | `models.py:133-169,235-273` | Lógica não reutilizável nem testável |
| 7 | HIGH | Conexão global mutável (`check_same_thread=False`) | `database.py:4,10` | Condições de corrida e acoplamento oculto |
| 8 | HIGH | Debug mode em produção | `app.py:8,88` | Debugger do Werkzeug = RCE + stack traces |
| 9 | MEDIUM | N+1 na listagem de pedidos | `models.py:171-233` | Latência explode com o volume de dados |
| 10 | MEDIUM | Código duplicado (row→dict) | `models.py` (várias funções) | Correções em N lugares divergem |
| 11 | MEDIUM | CORS totalmente aberto | `app.py:9` | Qualquer site chama a API no contexto do usuário |
| 12 | LOW | `print()` como logging | `controllers.py` (vários) | Sem níveis/estrutura em produção |
| 13 | LOW | Magic numbers (faixas de desconto) | `models.py:256-262` | Intenção obscura, difícil de manter |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, LMS + checkout)

| # | Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|---|
| 1 | **CRITICAL** | Segredos hardcoded (senha DB, chave de pagamento viva, SMTP) | `src/utils.js:3-5` | Chave `pk_live_...` de produção exposta no repo |
| 2 | **CRITICAL** | God Class (`AppManager`: DB + rotas + regras) | `src/AppManager.js:1-141` | Acoplamento total; impossível testar |
| 3 | **CRITICAL** | Log de cartão completo + chave de pagamento | `src/AppManager.js:45` | Vazamento de PAN e segredo (violação PCI) |
| 4 | HIGH | Hashing caseiro/reversível (`badCrypto`) | `src/utils.js:17-23` | Senhas efetivamente desprotegidas |
| 5 | HIGH | Estado global mutável | `src/utils.js:9-10` | Estado compartilhado entre requisições |
| 6 | MEDIUM | Callback hell + N+1 no relatório | `src/AppManager.js:80-129` | 4 níveis de callbacks, 1+N+N*M queries |
| 7 | MEDIUM | Integridade quebrada ao deletar usuário | `src/AppManager.js:131-137` | Deixa matrículas/pagamentos órfãos |
| 8 | LOW | `console.log` como logging | `src/utils.js:13`, `AppManager.js:45` | Sem níveis/controle |
| 9 | LOW | Nomes crípticos (`u,e,p,cid,cc`) | `src/AppManager.js:29-33` | Baixa legibilidade |

### Projeto 3 — `task-manager-api` (Python/Flask + SQLAlchemy, Task Manager)

Projeto **parcialmente organizado** (já tem `models/ routes/ services/ utils/`),
mas com problemas reais de segurança, performance e arquitetura.

| # | Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|---|
| 1 | **CRITICAL** | Segredos hardcoded (SECRET_KEY, senha SMTP) | `app.py:13`, `services/notification_service.py:10` | Segredos versionados |
| 2 | **CRITICAL** | Hash de senha retornado pela API | `models/user.py:21` | `/users`, `/login` vazam o hash da senha |
| 3 | HIGH | Hashing fraco/obsoleto (MD5) | `models/user.py:29,32` | MD5 inadequado para senhas |
| 4 | HIGH | Sem camada controller/service (lógica nas rotas) | `routes/*.py` | Rotas gigantes; regra não testável |
| 5 | HIGH | Debug mode em produção | `app.py:34` | Debugger exposto = RCE |
| 6 | MEDIUM | N+1 em `GET /tasks` (user/category por task) | `routes/task_routes.py:42,51` | 1+2N queries |
| 7 | MEDIUM | N+1 nos relatórios / `/users` | `routes/report_routes.py:56`, `routes/user_routes.py:22` | Query por usuário em loop |
| 8 | MEDIUM | Lógica "overdue" duplicada | `task_routes.py:30-39`, `report_routes.py:33-43` | Regra divergente em N lugares |
| 9 | LOW | `except:` engolindo erros | `routes/task_routes.py:62` | Erros silenciados sem log |
| 10 | LOW | Imports mortos + token JWT falso | `app.py:7`, `routes/user_routes.py:210` | Ruído e auth fictícia |

**APIs deprecated detectadas:** `datetime.utcnow()` (Python 3.12+),
`Model.query.get()` (SQLAlchemy 2.0 legado), `hashlib.md5` para senha.

---

## B) Construção da Skill

### Decisões de design

- **SKILL.md como orquestrador, referências como conhecimento.** O `SKILL.md` é
  um prompt enxuto que define as 3 fases, as regras de ouro (behavior-preserving,
  `file:line` obrigatório, validar antes de declarar pronto) e **quando** ler cada
  arquivo de referência. O conhecimento de domínio (heurísticas, catálogo,
  template, guidelines, playbook) fica nos 5 arquivos de referência, carregados
  sob demanda — mantém o prompt principal curto e a skill escalável.
- **Fases sequenciais com gate humano.** A Fase 2 **pausa** e imprime
  `Proceed with refactoring (Phase 3)? [y/n]` — nenhum arquivo é modificado sem
  confirmação, como exige o desafio.
- **Severidade padronizada.** O catálogo usa exatamente a escala
  CRITICAL/HIGH/MEDIUM/LOW do enunciado, para relatórios consistentes.

### Anti-patterns incluídos (e por quê)

O catálogo tem **20 entradas** (bem acima do mínimo de 8), distribuídas em todas
as severidades e escolhidas a partir dos problemas reais vistos na análise manual:

- **CRITICAL** — SQL Injection, Hardcoded Secrets, God Class, Endpoint de execução
  arbitrária, Exposição de dados sensíveis/senha em texto puro. *(São as falhas
  que quebram segurança ou destroem a separação de responsabilidades.)*
- **HIGH** — Fat Controller (regra de negócio no handler), Estado global mutável,
  Sem hashing real de senha, Data-access dentro das rotas, Debug em produção.
- **MEDIUM** — N+1, Código duplicado, Validação ausente, CORS aberto, Falta de
  auth, Callback hell.
- **LOW** — Magic numbers, `print`/`console.log` como log, Nomes ruins, `except`
  engolido.
- **Seção dedicada de APIs deprecated** — `datetime.utcnow()`, `Query.get()`,
  MD5 para senha, cripto caseira, API de callback do `sqlite3`, `app.run(debug=True)`
  em produção, `var` em JS. Cada uso vira um finding com o equivalente moderno.

O **playbook** tem **13 receitas** (mínimo 8) com código antes/depois: queries
parametrizadas, extração de config/segredos, extração de service, quebra do God
module, fim do singleton global, eliminação de N+1 com JOIN, error handling
centralizado, hashing com KDF, constantes nomeadas, remoção de segredos da
serialização, de-duplicação, `async/await`, e logger.

### Como garanti que a skill é agnóstica de tecnologia

- A **detecção** (Fase 1) parte do manifesto de dependências e dos imports, com
  uma tabela de sinais que cobre Python/Flask/Django/FastAPI, Node/Express/Nest,
  Java/Spring, Go, Ruby/Rails e PHP/Laravel — não assume stack.
- Os **anti-patterns** são descritos por **princípio** (ex.: "SQL montado por
  concatenação", "query dentro de loop") com exemplos em mais de uma linguagem,
  não por API específica.
- O **playbook** e as **guidelines** trazem o layout MVC alvo para cada stack
  (Flask raw SQL, Flask+ORM, Node/Express) e mandam "aplicar o idioma equivalente
  na stack detectada".
- **Prova prática:** a mesma skill produziu refatorações corretas em Python (raw
  sqlite3), Python (SQLAlchemy ORM) e Node (Express + sqlite3 callbacks).

### Desafios encontrados e como resolvi

- **Preservar comportamento vs. corrigir vulnerabilidades.** Alguns "fixes"
  mudam o contrato (parar de retornar senha, remover `/admin/query`). Resolvi
  mantendo rotas/métodos/status e documentando explicitamente as mudanças de
  segurança intencionais.
- **Deprecated `datetime.utcnow()` vs. datetimes naive no SQLite (Projeto 3).**
  Trocar por `datetime.now(timezone.utc)` (aware) quebraria as comparações com as
  colunas naive. Criei um helper `utcnow()` que retorna UTC **naive**, removendo o
  uso deprecado sem quebrar as comparações.
- **Projeto parcialmente organizado (Projeto 3).** A skill não reconstrói do
  zero: mantém os models ORM corretos e introduz as camadas ausentes
  (controllers + services), ataca segurança (MD5→werkzeug, segredos) e N+1.
- **Node 24 + `sqlite3` nativo.** Confirmei que o driver carrega e promisifiquei
  a API de callbacks para permitir `async/await` (fim do callback hell).
- **Porta 5000 ocupada no macOS (AirPlay).** A config passou a ler `PORT` do
  ambiente; a validação usou portas livres.

---

## C) Resultados

### Resumo dos relatórios de auditoria

| Projeto | Stack | Arquivos | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python/Flask | 4 | 5 | 4 | 4 | 3 | **16** |
| 2 — ecommerce-api-legacy | Node/Express | 3 | 3 | 3 | 3 | 3 | **12** |
| 3 — task-manager-api | Python/Flask+SQLAlchemy | 15 | 2 | 3 | 4 | 3 | **12** |

Todos ≥ 5 findings e ≥ 1 CRITICAL/HIGH. Relatórios completos em `reports/`.

### Comparação antes/depois (estrutura)

**Projeto 1 — code-smells-project**
```
ANTES (monolito plano)          DEPOIS (MVC + services)
app.py                          app.py                     (entry point fino)
controllers.py                  src/config/settings.py     (config via env, sem hardcoded)
models.py   (God module)        src/database/connection.py (factory, sem singleton global)
database.py (conn global)       src/models/{produto,usuario,pedido}_model.py  (queries parametrizadas)
                                src/services/{pedido,relatorio,notification}_service.py
                                src/controllers/{produto,usuario,pedido,system}_controller.py
                                src/views/routes.py        (blueprint fino)
                                src/middlewares/error_handler.py
                                src/app.py                 (composition root / factory)
```

**Projeto 2 — ecommerce-api-legacy**
```
ANTES                           DEPOIS
src/app.js                      src/app.js                 (composition root, async)
src/AppManager.js (God Class)   src/config/index.js        (segredos via env)
src/utils.js (segredos+crypto)  src/db/connection.js       (sqlite3 promisificado)
                                src/models/{user,course,enrollment,payment,auditLog}.model.js
                                src/services/{checkout,report,user}.service.js  (async/await, JOIN)
                                src/controllers/{checkout,report,user}.controller.js
                                src/routes/index.js
                                src/middlewares/errorHandler.js
                                src/utils/{security,logger,DomainError}.js  (scrypt no lugar do badCrypto)
```

**Projeto 3 — task-manager-api**
```
ANTES (parcialmente organizado) DEPOIS (camadas completas)
app.py (SECRET_KEY hardcoded)   app.py + src/app.py        (factory, config via env)
database.py                     src/extensions.py
models/ (MD5, vaza senha)       src/models/ (werkzeug, sem senha no to_dict, utcnow helper)
routes/ (lógica+queries)        src/routes/ (blueprints finos)  +  src/controllers/ (NOVO)
services/ (quase vazio)         src/services/ (NOVO: task, user, report, category, notification — sem N+1)
utils/                          src/utils/ (helpers + timeutils)
                                src/middlewares/error_handler.py
```

### Logs das aplicações rodando após a refatoração

```
# Projeto 1 (Flask) — boot real em porta livre
$ PORT=5055 python app.py
==================================================
SERVIDOR INICIADO
Rodando em http://localhost:5055
==================================================
 * Serving Flask app 'src.app'  |  * Debug mode: off
$ curl /health   -> {"counts":{"pedidos":0,"produtos":10,"usuarios":3},"database":"connected","status":"ok"}
$ curl /login    -> {"dados":{"email":"joao@email.com","id":2,"nome":"João Silva","tipo":"cliente"},"mensagem":"Login OK"}
  (senha NÃO aparece em /usuarios; secret_key NÃO aparece em /health; /admin/query -> 404)

# Projeto 2 (Express) — boot real em porta livre
$ PORT=3011 node src/app.js   ->  [INFO] LMS API rodando na porta 3011...
$ POST /api/checkout (card 4...) -> 200 {"msg":"Sucesso","enrollment_id":2}
$ POST /api/checkout (card 5...) -> 400 {"error":"Pagamento recusado"}
$ GET  /api/admin/financial-report -> 200 [{"course":"Clean Architecture","revenue":997,...},{"course":"Docker",...}]
$ DELETE /api/users/1 -> 200 (matrículas/pagamentos removidos junto — integridade corrigida)

# Projeto 3 (Flask+SQLAlchemy) — boot real em porta livre
$ PORT=5066 python app.py  ->  * Running on http://127.0.0.1:5066  |  Debug mode: off
$ curl /health      -> {"status":"ok","timestamp":"..."}
$ curl /tasks/stats -> {"total":10,"done":1,"pending":6,"overdue":2,"completion_rate":10.0,...}  (idêntico ao baseline)
$ POST /login       -> {"message":"Login realizado com sucesso","token":"...","user":{...}}  (sem campo password)
```

### Checklist de validação (preenchido para os 3 projetos)

| Item | P1 | P2 | P3 |
|---|:--:|:--:|:--:|
| **Fase 1** — Linguagem detectada corretamente | ✅ | ✅ | ✅ |
| **Fase 1** — Framework detectado corretamente | ✅ | ✅ | ✅ |
| **Fase 1** — Domínio descrito corretamente | ✅ | ✅ | ✅ |
| **Fase 1** — Nº de arquivos condiz com a realidade | ✅ | ✅ | ✅ |
| **Fase 2** — Relatório segue o template | ✅ | ✅ | ✅ |
| **Fase 2** — Cada finding com arquivo e linhas | ✅ | ✅ | ✅ |
| **Fase 2** — Findings ordenados por severidade | ✅ | ✅ | ✅ |
| **Fase 2** — Mínimo de 5 findings | ✅ (16) | ✅ (12) | ✅ (12) |
| **Fase 2** — Detecção de APIs deprecated | ✅ | ✅ | ✅ |
| **Fase 2** — Pausa/confirmação antes da Fase 3 | ✅ | ✅ | ✅ |
| **Fase 3** — Estrutura de diretórios MVC | ✅ | ✅ | ✅ |
| **Fase 3** — Config extraída (sem hardcoded) | ✅ | ✅ | ✅ |
| **Fase 3** — Models abstraindo dados | ✅ | ✅ | ✅ |
| **Fase 3** — Views/Routes separadas | ✅ | ✅ | ✅ |
| **Fase 3** — Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| **Fase 3** — Error handling centralizado | ✅ | ✅ | ✅ |
| **Fase 3** — Entry point claro | ✅ | ✅ | ✅ |
| **Fase 3** — Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| **Fase 3** — Endpoints originais respondem | ✅ | ✅ | ✅ |

### Como a skill se comportou em stacks diferentes

- **Python raw SQL (P1):** foco em parametrização, quebra do God module e
  extração de services — a maior transformação estrutural.
- **Node/Express (P2):** foco em promisificar o driver, matar o callback hell/N+1
  e substituir cripto caseira por `scrypt` (built-in, sem dependência nativa nova).
- **Python + ORM parcialmente organizado (P3):** aproveitou os models ORM, apenas
  corrigindo-os (MD5→werkzeug, sem senha no `to_dict`, `utcnow` helper), e
  **adicionou** as camadas ausentes (controllers + services), sem reconstruir do zero.

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado.
- **Python 3.12+** (Projetos 1 e 3) e **Node.js 18+** (Projeto 2).

### Invocar a skill em cada projeto

A skill já está copiada em `.claude/skills/refactor-arch/` nos três projetos.

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A skill executa Fase 1 (análise) → Fase 2 (auditoria + relatório, **pausa para
confirmação**) → responda `y` → Fase 3 (refatoração + validação).

### Rodar e validar as aplicações refatoradas

> No macOS a porta 5000 costuma estar ocupada pelo AirPlay Receiver; use `PORT`.

```bash
# Projeto 1 — Flask (E-commerce)
cd code-smells-project
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
PORT=5055 .venv/bin/python app.py
# valida: curl http://localhost:5055/health  |  curl http://localhost:5055/produtos

# Projeto 2 — Node/Express (LMS)
cd ../ecommerce-api-legacy
npm install
PORT=3011 npm start
# valida: curl -X POST http://localhost:3011/api/checkout -H 'Content-Type: application/json' \
#   -d '{"usr":"Ana","eml":"ana@x.com","pwd":"s3nha","c_id":2,"card":"4111222233334444"}'
#         curl http://localhost:3011/api/admin/financial-report

# Projeto 3 — Flask + SQLAlchemy (Task Manager)
cd ../task-manager-api
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py        # popular o banco (rode antes do 1º boot)
PORT=5066 .venv/bin/python app.py
# valida: curl http://localhost:5066/tasks  |  curl http://localhost:5066/tasks/stats
```

**Critério de "funciona":** a API inicia sem erros e todos os endpoints originais
continuam respondendo com os status esperados — verificado nos três projetos.

### Variáveis de ambiente

Cada projeto tem um `.env.example` com as chaves esperadas (`SECRET_KEY`, `PORT`,
credenciais de DB/SMTP/gateway, `CORS_ORIGINS`). Nenhum segredo fica hardcoded no
código — copie para `.env` e preencha conforme o ambiente.
