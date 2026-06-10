const AppError = require("../models/AppError");

class UserController {
  constructor(userService) {
    this.userService = userService;
  }

  async delete(request, response) {
    const id = Number(request.params.id);
    if (!Number.isInteger(id) || id < 1) {
      throw new AppError("Usuário inválido", 400);
    }

    await this.userService.deleteUser(id);
    response.send("Usuário deletado.");
  }
}

module.exports = UserController;
