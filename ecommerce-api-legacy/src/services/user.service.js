// User workflow. Deleting a user now also removes their enrollments and
// payments, instead of leaving orphaned rows "dirty" in the database (fixes:
// broken referential integrity on delete).
const userModel = require('../models/user.model');
const enrollmentModel = require('../models/enrollment.model');
const paymentModel = require('../models/payment.model');

async function deleteUser(userId) {
    const enrollmentIds = await enrollmentModel.idsByUser(userId);
    await paymentModel.removeByEnrollments(enrollmentIds);
    await enrollmentModel.removeByUser(userId);
    await userModel.remove(userId);
}

module.exports = { deleteUser };
