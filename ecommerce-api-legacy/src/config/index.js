// Centralized, environment-driven configuration.
// All secrets come from environment variables (fixes: hardcoded credentials /
// payment key / SMTP password that used to live as literals in utils.js).
const config = {
    port: process.env.PORT || 3000,
    // Secrets — provide via environment (.env). Never hardcode.
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    dbUser: process.env.DB_USER || '',
    dbPass: process.env.DB_PASS || '',
    smtpUser: process.env.SMTP_USER || '',
    // Default password for auto-created users at checkout (override via env).
    defaultUserPassword: process.env.DEFAULT_USER_PASSWORD || 'change-me',
};

module.exports = { config };
