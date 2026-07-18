// Tiny centralized logger. Replaces scattered console.log used as logging and
// the fake "console.log notification" side-effects that lived in the God class.
module.exports = {
    info: (...args) => console.log('[INFO]', ...args),
    warn: (...args) => console.warn('[WARN]', ...args),
    error: (...args) => console.error('[ERROR]', ...args),
};
