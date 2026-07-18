// Password hashing with a real KDF (Node's built-in scrypt).
// Replaces `badCrypto` — a home-grown, insecure base64 loop (fixes: weak/broken
// password hashing). No native dependency needed; `crypto` is built in.
const crypto = require('crypto');

function hashPassword(plain) {
    const salt = crypto.randomBytes(16).toString('hex');
    const derived = crypto.scryptSync(String(plain), salt, 32).toString('hex');
    return `${salt}:${derived}`;
}

function verifyPassword(plain, stored) {
    if (!stored || !stored.includes(':')) return false;
    const [salt, key] = stored.split(':');
    const derived = crypto.scryptSync(String(plain), salt, 32).toString('hex');
    const a = Buffer.from(key, 'hex');
    const b = Buffer.from(derived, 'hex');
    return a.length === b.length && crypto.timingSafeEqual(a, b);
}

module.exports = { hashPassword, verifyPassword };
