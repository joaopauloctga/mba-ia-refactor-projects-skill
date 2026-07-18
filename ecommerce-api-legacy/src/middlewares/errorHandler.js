// Centralized error handler (registered last). Business errors (DomainError)
// return their status + message; anything unexpected is logged server-side and
// returned as a generic 500 (fixes: hand-rolled res.status(500) everywhere and
// leaking internal error strings).
const logger = require('../utils/logger');

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
    if (err && err.expose) {
        return res.status(err.status || 400).json({ error: err.message });
    }
    logger.error('Erro não tratado:', err);
    return res.status(500).json({ error: 'Erro interno' });
}

module.exports = errorHandler;
