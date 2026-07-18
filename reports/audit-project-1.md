```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3.12
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Domain:        E-commerce API — produtos, usuários, pedidos, itens_pedido
Architecture:  Monolítica — 4 arquivos, sem separação de camadas (models.py
               concentra dados + regras + SQL de 4 domínios)
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code
Date:    2026-07-18

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 4 | LOW: 3
Total: 16 findings

## Findings

### [CRITICAL] SQL Injection (queries montadas por concatenação)
File: models.py:28,47-50,109-111,289-297
Description: Praticamente todas as queries são montadas concatenando input do
             usuário na string SQL. `get_produto_por_id` faz `"... WHERE id = " + str(id)`,
             `login_usuario` interpola email/senha, `buscar_produtos` concatena o termo.
Impact: Um atacante pode ler/alterar/apagar qualquer dado e burlar o login
        (`' OR '1'='1`). Comprometimento total do banco.
Recommendation: Usar queries parametrizadas (placeholders `?`) em todos os
                models. Ver playbook P1.

### [CRITICAL] Hardcoded Credentials / Secrets
File: app.py:7
Description: `SECRET_KEY = "minha-chave-super-secreta-123"` fixo no código (e ainda
             ecoado pelo endpoint /health em controllers.py:289).
Impact: Qualquer pessoa com acesso ao repositório assina sessões/tokens; o
        segredo vaza pelo histórico do git.
Recommendation: Mover para módulo de config alimentado por variáveis de
                ambiente. Ver playbook P2.

### [CRITICAL] God Module (models.py)
File: models.py:1-314
Description: Um único arquivo concentra acesso a dados, regras de negócio,
             validação e formatação para produtos, usuários, pedidos e relatórios.
Impact: Impossível testar em isolamento; qualquer mudança afeta tudo.
Recommendation: Separar em models por domínio + camada de services. Ver
                playbook P4/P3.

### [CRITICAL] Endpoint de execução arbitrária de SQL
File: app.py:59-78
Description: `POST /admin/query` recebe SQL cru do corpo da requisição e executa
             (`cursor.execute(query)`), sem autenticação.
Impact: Execução remota de qualquer comando no banco — leitura/escrita/drop.
Recommendation: Remover o endpoint. Substituir por operações específicas,
                autorizadas e parametrizadas.

### [CRITICAL] Exposição de dados sensíveis / senhas em texto puro
File: database.py:76-78, models.py:83,122-131, controllers.py:287-289
Description: Senhas são armazenadas em texto puro (seed e `criar_usuario`),
             retornadas pelo endpoint `/usuarios` (`senha` no dict) e o /health
             expõe a SECRET_KEY.
Impact: Vazamento de credenciais em qualquer breach e pelo tráfego normal da API.
Recommendation: Hashear senhas (KDF), remover `senha` da serialização e do
                /health. Ver playbook P8/P10.

### [HIGH] Regra de negócio presa na camada de dados
File: models.py:133-169,235-273
Description: `criar_pedido` faz todo o fluxo de estoque/total dentro do model e
             `relatorio_vendas` calcula faixas de desconto no model.
Impact: Lógica não reutilizável nem testável isoladamente; models inchados.
Recommendation: Extrair para uma camada de services (pedido_service,
                relatorio_service). Ver playbook P3.

### [HIGH] Estado global mutável / conexão singleton
File: database.py:4,7-10
Description: `db_connection = None` global reaproveitado em toda a aplicação com
             `check_same_thread=False`.
Impact: Condições de corrida e acoplamento oculto; impossível isolar.
Recommendation: Factory de conexão por operação (ou request-scoped). Ver
                playbook P5.

### [HIGH] Autenticação sem hashing de senha
File: models.py:105-120
Description: `login_usuario` compara a senha em texto puro dentro do SQL.
Impact: Senhas trivialmente comprometidas; login vulnerável a injeção.
Recommendation: Buscar por email e verificar hash em código
                (`check_password_hash`). Ver playbook P8.

### [HIGH] Debug mode ligado em produção
File: app.py:8,88
Description: `app.config["DEBUG"] = True` e `app.run(debug=True)`.
Impact: Debugger interativo do Werkzeug exposto = RCE + vazamento de stack traces.
Recommendation: Config dirigida por env, `DEBUG` desligado por padrão; WSGI em
                produção. Ver playbook P2/P7.

### [MEDIUM] N+1 queries na listagem de pedidos
File: models.py:171-201,203-233
Description: `get_pedidos_usuario`/`get_todos_pedidos` fazem 1 query da lista e
             depois 1 query por pedido e 1 por item (loops aninhados).
Impact: Latência explode conforme cresce o número de pedidos/itens.
Recommendation: Substituir por um único JOIN e agrupar em memória. Ver playbook P6.

### [MEDIUM] Código duplicado (mapeamento row->dict)
File: models.py:12-21,31-40,304-313
Description: O mesmo bloco de mapeamento de linha para dicionário é copiado em
             quase todas as funções de produto.
Impact: Correções precisam ser feitas em N lugares; tendem a divergir.
Recommendation: Extrair um serializer único. Ver playbook P11.

### [MEDIUM] CORS totalmente aberto
File: app.py:9
Description: `CORS(app)` libera todas as origens em uma API autenticada.
Impact: Qualquer site consegue chamar a API no contexto do usuário.
Recommendation: Restringir a uma allowlist vinda de config.

### [MEDIUM] Efeitos colaterais (notificações) dentro do controller
File: controllers.py:208-210,247-250
Description: `print("ENVIANDO EMAIL/SMS/PUSH ...")` misturado no fluxo do controller.
Impact: Controller acoplado a responsabilidade de notificação; não testável.
Recommendation: Extrair para um notification_service. Ver playbook P13.

### [LOW] print() usado como logging
File: controllers.py:8,11,57,61,161,179
Description: Diagnóstico via `print(...)` espalhado pelos controllers.
Impact: Sem níveis, sem estrutura, impossível controlar em produção.
Recommendation: Usar o logger do framework. Ver playbook P13.

### [LOW] Magic numbers nas faixas de desconto
File: models.py:256-262
Description: Limiares `10000/5000/1000` e taxas `0.1/0.05/0.02` soltos no código.
Impact: Difícil de entender e alterar com segurança.
Recommendation: Constantes nomeadas em config (`DISCOUNT_TIERS`). Ver playbook P9.

### [LOW] Erros vazando detalhes internos ao cliente
File: controllers.py:12,22,96,126
Description: Handlers retornam `str(e)` diretamente ao cliente em blocos try/except.
Impact: Vazamento de mensagens internas; sem log centralizado.
Recommendation: Error handler centralizado com mensagem genérica + log. Ver playbook P7.

## Deprecated APIs
- app.py:88 — `app.run(debug=True)` como servidor de produção → usar WSGI
  (gunicorn/uwsgi) com DEBUG desligado.

================================
Total: 16 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```
