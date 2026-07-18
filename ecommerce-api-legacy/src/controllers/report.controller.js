// Financial report controller — thin.
const reportService = require('../services/report.service');

async function financialReport(req, res, next) {
    try {
        const report = await reportService.financialReport();
        return res.status(200).json(report);
    } catch (err) {
        return next(err);
    }
}

module.exports = { financialReport };
