// Checkout workflow: find course -> ensure user -> authorize payment -> enroll
// -> record payment -> audit. Extracted from the God class; uses async/await
// (no callback pyramid) and never logs card numbers or the gateway key.
const { config } = require('../config');
const logger = require('../utils/logger');
const DomainError = require('../utils/DomainError');
const userModel = require('../models/user.model');
const courseModel = require('../models/course.model');
const enrollmentModel = require('../models/enrollment.model');
const paymentModel = require('../models/payment.model');
const auditModel = require('../models/auditLog.model');

// Mock payment gateway authorization. Kept identical to the legacy rule:
// cards starting with "4" are approved.
function authorize(card) {
    return String(card).startsWith('4') ? 'PAID' : 'DENIED';
}

async function checkout({ name, email, password, courseId, card }) {
    const course = await courseModel.findActiveById(courseId);
    if (!course) throw new DomainError('Curso não encontrado', 404);

    let user = await userModel.findByEmail(email);
    const userId = user ? user.id : await userModel.create(name, email, password || config.defaultUserPassword);

    // Authorize BEFORE enrolling. Do not log the card or the gateway key.
    const status = authorize(card);
    logger.info(`Autorizando pagamento (gateway ${config.paymentGatewayKey ? 'configurado' : 'não configurado'})`);
    if (status === 'DENIED') throw new DomainError('Pagamento recusado', 400);

    const enrollmentId = await enrollmentModel.create(userId, courseId);
    await paymentModel.create(enrollmentId, course.price, status);
    await auditModel.create(`Checkout curso ${courseId} por ${userId}`);

    return { msg: 'Sucesso', enrollment_id: enrollmentId };
}

module.exports = { checkout };
