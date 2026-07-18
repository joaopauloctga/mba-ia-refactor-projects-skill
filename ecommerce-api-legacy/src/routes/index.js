// Routing layer — URL -> controller mapping only.
const express = require('express');
const checkoutController = require('../controllers/checkout.controller');
const reportController = require('../controllers/report.controller');
const userController = require('../controllers/user.controller');

const router = express.Router();

router.post('/api/checkout', checkoutController.checkout);
router.get('/api/admin/financial-report', reportController.financialReport);
router.delete('/api/users/:id', userController.deleteUser);

module.exports = router;
