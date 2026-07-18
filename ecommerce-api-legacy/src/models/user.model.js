// User data access. Parameterized queries + hashed passwords.
const { get, run } = require('../db/connection');
const { hashPassword } = require('../utils/security');

async function findByEmail(email) {
    return get('SELECT * FROM users WHERE email = ?', [email]);
}

async function create(name, email, plainPassword) {
    const result = await run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
        name,
        email,
        hashPassword(plainPassword),
    ]);
    return result.lastID;
}

async function remove(id) {
    return run('DELETE FROM users WHERE id = ?', [id]);
}

module.exports = { findByEmail, create, remove };
