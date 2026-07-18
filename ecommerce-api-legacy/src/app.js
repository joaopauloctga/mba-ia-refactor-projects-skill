// Composition root. Assembles the app: init DB, wire middleware, mount routes,
// register the centralized error handler, start the server. No business logic.
const express = require('express');
const { config } = require('./config');
const { initDb } = require('./db/connection');
const routes = require('./routes');
const errorHandler = require('./middlewares/errorHandler');
const logger = require('./utils/logger');

async function main() {
    await initDb();

    const app = express();
    app.use(express.json());
    app.use(routes);
    app.use(errorHandler); // must be last

    app.listen(config.port, () => {
        logger.info(`LMS API rodando na porta ${config.port}...`);
    });
}

main().catch((err) => {
    logger.error('Falha ao iniciar a aplicação:', err);
    process.exit(1);
});
