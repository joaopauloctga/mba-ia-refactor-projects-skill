// A business-rule error that carries an HTTP status and is safe to expose to
// the client (message is a controlled, user-facing string).
class DomainError extends Error {
    constructor(message, status = 400) {
        super(message);
        this.name = 'DomainError';
        this.status = status;
        this.expose = true;
    }
}

module.exports = DomainError;
