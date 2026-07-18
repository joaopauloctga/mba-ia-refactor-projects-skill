```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express 4.18
Dependencies:  sqlite3 5.1
Domain:        LMS API com checkout — users, courses, enrollments, payments,
               audit_logs
Architecture:  Monolítica em torno de uma God Class (AppManager) que inicializa
               o banco, define todas as rotas e executa a lógica de negócio
Source files:  3 files analyzed
DB tables:     users, courses, enrollments, payments, audit_logs
================================
```

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express
Files:   3 analyzed | ~180 lines of code
Date:    2026-07-18

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 3 | LOW: 3
Total: 12 findings

## Findings

### [CRITICAL] Hardcoded Credentials / Secrets
File: src/utils.js:3-5
Description: `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey:
             "pk_live_1234567890abcdef"` e `smtpUser` fixos no código-fonte.
Impact: Chave de pagamento de produção e senha do banco expostas no repositório
        e no histórico do git.
Recommendation: Mover para módulo de config alimentado por variáveis de
                ambiente. Ver playbook P2.

### [CRITICAL] God Class (AppManager)
File: src/AppManager.js:1-141
Description: Uma única classe inicializa o banco (`initDb`), registra todas as
             rotas (`setupRoutes`) e executa checkout, relatório e deleção.
Impact: Impossível testar isoladamente; toda mudança arrisca o sistema inteiro;
        rotas, regras e persistência totalmente acopladas.
Recommendation: Separar em models (por entidade), services, controllers e
                routes. Ver playbook P4/P3.

### [CRITICAL] Exposição de dados sensíveis em log (cartão + chave de pagamento)
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)`
             registra o número do cartão completo e a chave viva do gateway.
Impact: Vazamento de PAN e de segredo de pagamento nos logs (violação grave de
        segurança/PCI).
Recommendation: Nunca logar cartão ou chave; usar logger centralizado sem dados
                sensíveis. Ver playbook P13.

### [HIGH] Hashing de senha caseiro e inseguro (badCrypto)
File: src/utils.js:17-23
Description: `badCrypto` monta um "hash" concatenando base64 em loop e trunca em
             10 caracteres — criptografia caseira e reversível.
Impact: Senhas efetivamente desprotegidas.
Recommendation: Usar um KDF real (scrypt/bcrypt/argon2). Ver playbook P8.

### [HIGH] Estado global mutável
File: src/utils.js:9-10
Description: `let globalCache = {}` e `let totalRevenue = 0` compartilhados no
             módulo.
Impact: Estado compartilhado entre requisições → condições de corrida e
        acoplamento oculto.
Recommendation: Encapsular estado; injetar dependências. Ver playbook P5.

### [HIGH] Lógica de negócio dentro do handler de rota
File: src/AppManager.js:28-78
Description: Todo o fluxo de checkout (autorização de pagamento, criação de
             usuário, matrícula, pagamento, auditoria) vive dentro do callback da
             rota `POST /api/checkout`.
Impact: Regra não reutilizável nem testável; handler gigante.
Recommendation: Extrair para um checkout_service com async/await. Ver playbook P3/P12.

### [MEDIUM] Callback hell + N+1 no relatório financeiro
File: src/AppManager.js:80-129
Description: `GET /api/admin/financial-report` aninha 4 níveis de callbacks com
             contadores manuais e dispara 1 + N + N*M queries (por curso, por
             matrícula, por usuário e por pagamento).
Impact: Ilegível, propenso a erro (risco de dupla resposta) e lento.
Recommendation: Um único JOIN agrupado em memória, com async/await. Ver playbook P6/P12.

### [MEDIUM] Integridade referencial quebrada ao deletar usuário
File: src/AppManager.js:131-137
Description: `DELETE /api/users/:id` remove só o usuário e deixa matrículas e
             pagamentos órfãos ("ficaram sujos no banco", conforme a própria resposta).
Impact: Dados órfãos corrompem relatórios e contagens.
Recommendation: Deletar em transação (pagamentos → matrículas → usuário). Ver
                user_service.

### [MEDIUM] Validação de input ausente / senha default
File: src/AppManager.js:35,68
Description: Só há checagem de presença (`if (!u || !e ...)`); usuários novos são
             criados com senha default `"123456"` (AppManager.js:68).
Impact: Dados inconsistentes e contas com senha previsível.
Recommendation: Validar entrada e exigir/gerar senha adequada via config.

### [LOW] console.log usado como logging
File: src/utils.js:13, src/AppManager.js:45
Description: Diagnóstico via `console.log("[LOG] ...")` espalhado.
Impact: Sem níveis nem controle em produção.
Recommendation: Logger centralizado. Ver playbook P13.

### [LOW] Nomes de variáveis crípticos
File: src/AppManager.js:29-33
Description: `u`, `e`, `p`, `cid`, `cc` para nome, email, senha, id do curso e
             cartão.
Impact: Baixa legibilidade e manutenção.
Recommendation: Nomes que revelam intenção. Ver playbook (nomeação).

### [LOW] Magic value na regra de pagamento
File: src/AppManager.js:46
Description: `cc.startsWith("4") ? "PAID" : "DENIED"` — regra mágica sem nome.
Impact: Intenção obscura; difícil de manter/testar.
Recommendation: Encapsular em função nomeada (ex.: `authorize(card)`). Ver playbook P9.

## Deprecated APIs
- src/AppManager.js:37-129 — API baseada em callbacks do `sqlite3` aninhada →
  promisificar (async/await) ou migrar para `better-sqlite3` / `node:sqlite`.
- src/AppManager.js:26 — padrão `const self = this` para preservar `this` →
  desnecessário com arrow functions / async-await.

================================
Total: 12 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```
