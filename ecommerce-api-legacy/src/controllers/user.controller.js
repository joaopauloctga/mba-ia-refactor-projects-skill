// User controller — thin.
const userService = require('../services/user.service');

async function deleteUser(req, res, next) {
    try {
        await userService.deleteUser(req.params.id);
        return res.status(200).json({ msg: 'Usuário e dados relacionados removidos' });
    } catch (err) {
        return next(err);
    }
}

module.exports = { deleteUser };
