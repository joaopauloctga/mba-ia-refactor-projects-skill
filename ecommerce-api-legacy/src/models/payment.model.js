// Payment data access.
const { run } = require('../db/connection');

async function create(enrollmentId, amount, status) {
    return run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [
        enrollmentId,
        amount,
        status,
    ]);
}

async function removeByEnrollments(enrollmentIds) {
    if (!enrollmentIds.length) return null;
    const placeholders = enrollmentIds.map(() => '?').join(',');
    return run(`DELETE FROM payments WHERE enrollment_id IN (${placeholders})`, enrollmentIds);
}

module.exports = { create, removeByEnrollments };
