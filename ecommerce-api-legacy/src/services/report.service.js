// Financial report. The legacy version nested 4 levels of callbacks with manual
// counters and issued 1 + N + N*M queries (callback hell + N+1). This version is
// a single JOIN grouped in memory (fixes: N+1, callback hell). Output shape is
// preserved: [{ course, revenue, students: [{ student, paid }] }].
const { all } = require('../db/connection');

async function financialReport() {
    const rows = await all(`
        SELECT c.id          AS course_id,
               c.title       AS title,
               e.id          AS enrollment_id,
               u.name        AS student_name,
               p.amount      AS amount,
               p.status      AS status
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u       ON u.id = e.user_id
        LEFT JOIN payments p    ON p.enrollment_id = e.id
        ORDER BY c.id, e.id
    `);

    const byCourse = new Map();
    for (const row of rows) {
        if (!byCourse.has(row.course_id)) {
            byCourse.set(row.course_id, { course: row.title, revenue: 0, students: [] });
        }
        const courseData = byCourse.get(row.course_id);
        if (row.enrollment_id != null) {
            if (row.status === 'PAID') courseData.revenue += row.amount;
            courseData.students.push({
                student: row.student_name || 'Unknown',
                paid: row.amount != null ? row.amount : 0,
            });
        }
    }

    return [...byCourse.values()];
}

module.exports = { financialReport };
