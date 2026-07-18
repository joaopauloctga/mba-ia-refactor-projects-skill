// Enrollment data access.
const { run, all } = require('../db/connection');

async function create(userId, courseId) {
    const result = await run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [
        userId,
        courseId,
    ]);
    return result.lastID;
}

async function idsByUser(userId) {
    const rows = await all('SELECT id FROM enrollments WHERE user_id = ?', [userId]);
    return rows.map((r) => r.id);
}

async function removeByUser(userId) {
    return run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
}

module.exports = { create, idsByUser, removeByUser };
