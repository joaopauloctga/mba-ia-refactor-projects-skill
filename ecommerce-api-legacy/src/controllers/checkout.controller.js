// Checkout controller — parse/validate the request, call the service, respond.
// Thin: no SQL, no business rules. Maps the terse legacy field names to clear
// ones (fixes: cryptic variable names u/e/p/cid/cc).
const checkoutService = require('../services/checkout.service');

async function checkout(req, res, next) {
    try {
        const { usr: name, eml: email, pwd: password, c_id: courseId, card } = req.body;

        if (!name || !email || !courseId || !card) {
            return res.status(400).json({ error: 'Bad Request: usr, eml, c_id e card são obrigatórios' });
        }

        const result = await checkoutService.checkout({ name, email, password, courseId, card });
        return res.status(200).json(result);
    } catch (err) {
        return next(err);
    }
}

module.exports = { checkout };
