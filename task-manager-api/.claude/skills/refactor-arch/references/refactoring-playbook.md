# Refactoring Playbook — Before / After Recipes

Use this file in **Phase 3**. Each recipe maps an anti-pattern (from
`anti-patterns.md`) to a concrete transformation with before/after code. Examples
are in Python/Flask and Node/Express, but the *pattern* is language-neutral —
apply the equivalent idiom in the detected stack.

---

## P1 — Parameterize queries (fix C1: SQL Injection)

**Before (Python, raw sqlite3):**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
```
**After:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))  # verify hash in code
```
Dynamic filters: build the `WHERE` with placeholders and a params list.
```python
sql = "SELECT * FROM produtos WHERE 1=1"
params = []
if termo:
    sql += " AND (nome LIKE ? OR descricao LIKE ?)"; params += [f"%{termo}%", f"%{termo}%"]
if categoria:
    sql += " AND categoria = ?"; params.append(categoria)
cursor.execute(sql, params)
```
**Node:** always pass values as the array arg — `db.get("... WHERE id = ?", [id])`
— never concatenate.

---

## P2 — Extract config & secrets to a module fed by env (fix C2, H5, L1)

**Before:**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```
**After — `config/settings.py`:**
```python
import os
class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
settings = Settings()
```
```python
# app.py
from config.settings import settings
app.config["SECRET_KEY"] = settings.SECRET_KEY
app.config["DEBUG"] = settings.DEBUG
```
**Node — `config/index.js`:**
```js
module.exports = { config: {
  port: process.env.PORT || 3000,
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "",
  dbPass: process.env.DB_PASS || "",
}};
```
Add `.env` to `.gitignore`; provide `.env.example` with empty values.

---

## P3 — Extract business logic into a Service (fix H1: fat controller)

**Before (logic inside controller/route):**
```python
def relatorio_vendas():
    ...
    if faturamento > 10000: desconto = faturamento * 0.1
    elif faturamento > 5000: desconto = faturamento * 0.05
    ...
```
**After — `services/relatorio_service.py`:**
```python
DISCOUNT_TIERS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]  # named, testable
def calcular_relatorio(pedido_model):
    faturamento = pedido_model.total_faturamento()
    desconto = next((faturamento * r for limite, r in DISCOUNT_TIERS if faturamento > limite), 0)
    return {"faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2), ...}
```
```python
# controllers/pedido_controller.py  (thin)
def relatorio_vendas():
    return jsonify({"dados": relatorio_service.calcular_relatorio(pedido_model), "sucesso": True}), 200
```

---

## P4 — Split a God module by domain into Models (fix C3, H4)

**Before:** `models.py` with product + user + order + report functions all doing
raw SQL.
**After:** one model per entity, each owning only its table:
```
models/produto_model.py   # get_all, get_by_id, create, update, delete, search
models/usuario_model.py   # get_all, get_by_id, create, authenticate
models/pedido_model.py    # create, list_by_user, list_all, update_status, totals
```
Each model function uses `get_connection()` and parameter binding; controllers
import the model, not the DB.

---

## P5 — Replace global connection singleton (fix H2)

**Before:**
```python
db_connection = None          # module-level mutable global
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
    return db_connection
```
**After — `database/connection.py`:**
```python
import sqlite3
from config.settings import settings
def get_connection():
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_connection()
    # create tables / seed
    conn.close()
```
Models open a connection per operation (or use a request-scoped one) instead of
sharing one mutable global. **Node:** wrap the DB in a small class/module with
promisified methods; inject it, don't reach a shared global.

---

## P6 — Kill N+1 with a JOIN / eager load (fix M1)

**Before:**
```python
for row in pedidos:                      # 1 query
    itens = cursor.execute("... WHERE pedido_id = " + row_id)   # + N
    for item in itens:
        prod = cursor.execute("SELECT nome ... WHERE id = " + pid)  # + N*M
```
**After (single JOIN):**
```python
cursor.execute("""
  SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, p.nome
  FROM itens_pedido ip JOIN produtos p ON p.id = ip.produto_id
  WHERE ip.pedido_id IN ({})
""".format(",".join("?" * len(ids))), ids)
```
Then group in memory by `pedido_id`. **ORM (SQLAlchemy):** use
`joinedload`/`selectinload` instead of `Model.query.get()` inside a loop.

---

## P7 — Centralize error handling (fix H5, L4)

**Before:** every handler wrapped in `try/except` returning `str(e)` (leaks
internals) or bare `except:`.
**After — `middlewares/error_handler.py`:**
```python
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e): return jsonify({"erro": "Recurso não encontrado"}), 404
    @app.errorhandler(Exception)
    def handle(e):
        app.logger.exception(e)                 # log full detail server-side
        return jsonify({"erro": "Erro interno"}), 500   # generic to client
```
**Node:** an `(err, req, res, next)` middleware registered last; controllers call
`next(err)` instead of hand-rolling `res.status(500)`.

---

## P8 — Hash passwords with a real KDF (fix C5, H3, deprecated MD5)

**Before:**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()      # deprecated for pws
# or
cursor.execute("... WHERE senha = '" + senha + "'")        # plaintext compare
```
**After:**
```python
from werkzeug.security import generate_password_hash, check_password_hash
def set_password(self, pwd): self.password = generate_password_hash(pwd)
def check_password(self, pwd): return check_password_hash(self.password, pwd)
```
**Node:** replace `badCrypto` with `bcrypt.hash(pwd, 10)` / `bcrypt.compare(...)`.
Login fetches the user by email, then verifies the hash in code — never in SQL.

---

## P9 — Replace magic numbers with named constants (fix L1)

**Before:** `if priority < 1 or priority > 5`, `faturamento > 10000`.
**After:** `MIN_PRIORITY, MAX_PRIORITY = 1, 5`; `DISCOUNT_TIERS = [...]` in config
or a constants module; reference the names.

---

## P10 — Strip secrets from serialization (fix C5)

**Before:**
```python
def to_dict(self):
    return {"id": self.id, "email": self.email, "password": self.password, ...}
```
**After:** never include the password/hash in API output.
```python
def to_dict(self):
    return {"id": self.id, "name": self.name, "email": self.email, "role": self.role, ...}
```
Also remove any secret echoed by health/debug endpoints.

---

## P11 — De-duplicate with a shared serializer/helper (fix M2)

**Before:** the same `row → dict` mapping copied into every function; the same
"overdue" block repeated across routes.
**After:** one function:
```python
def produto_to_dict(row):
    return {"id": row["id"], "nome": row["nome"], "preco": row["preco"], ...}
```
and a single `Task.is_overdue()` reused everywhere. One source of truth.

---

## P12 — Flatten callback hell with async/await (fix M6, deprecated callback API)

**Before (Node, pyramid + manual counters):**
```js
this.db.all("SELECT * FROM courses", [], (err, courses) => {
  courses.forEach(c => this.db.all("... enrollments ...", [c.id], (err, enr) => {
    enr.forEach(e => this.db.get("... users ...", [e.user_id], (err, u) => { ... }))
  }))
});
```
**After — promisified DB + `async/await` in a service:**
```js
const all = (sql, p=[]) => new Promise((res, rej) => db.all(sql, p, (e, r) => e ? rej(e) : res(r)));
async function financialReport() {
  const courses = await all("SELECT * FROM courses");
  return Promise.all(courses.map(async c => {
    const enrollments = await all("SELECT * FROM enrollments WHERE course_id = ?", [c.id]);
    // ... await per-enrollment, or better: one JOIN (see P6)
  }));
}
```
Controller: `try { res.json(await reportService.financialReport()); } catch (e) { next(e); }`.

---

## P13 — Replace print/console.log with a logger (fix L2)

**Before:** `print("ERRO: " + str(e))`, `console.log("[LOG] ...")`, and fake
"ENVIANDO EMAIL/SMS" prints inside handlers.
**After:** use the framework logger (`app.logger.info/error`, or `winston`/
`pino` in Node). Move "send notification" side-effects into a notification
service with a clear (even if stubbed) interface — not a `print` in the
controller.

---

## Sequencing

Resolve findings in severity order: **CRITICAL → HIGH → MEDIUM → LOW**. Land the
structural moves first (P4/P5 create the layers), then security (P1/P2/P8/P10),
then performance (P6), then quality (P7/P11/P12/P13/P9). Re-run the app after each
big move so a break is caught early.
