const AppError = require("../models/AppError");

function errorHandler(error, request, response, next) {
  if (response.headersSent) {
    next(error);
    return;
  }

  if (error instanceof AppError) {
    response.status(error.statusCode).json({ error: error.message });
    return;
  }

  process.stderr.write(
    `${JSON.stringify({
      level: "error",
      message: "Unhandled request error",
      method: request.method,
      path: request.path,
    })}\n`,
  );
  response.status(500).json({ error: "Erro interno" });
}

module.exports = { errorHandler };
