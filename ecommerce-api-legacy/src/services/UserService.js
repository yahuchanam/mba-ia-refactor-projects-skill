const AppError = require("../models/AppError");

class UserService {
  constructor(users) {
    this.users = users;
  }

  async deleteUser(id) {
    const result = await this.users.deleteById(id);
    if (result.changes === 0) {
      throw new AppError("Usuário não encontrado", 404);
    }
  }
}

module.exports = UserService;
