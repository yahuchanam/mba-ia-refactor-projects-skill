const AppError = require("./AppError");

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const CARD_PATTERN = /^\d{12,19}$/;

function parseCheckout(body) {
  const name = typeof body.usr === "string" ? body.usr.trim() : "";
  const email =
    typeof body.eml === "string" ? body.eml.trim().toLowerCase() : "";
  const password = typeof body.pwd === "string" ? body.pwd : "";
  const courseId = Number(body.c_id);
  const cardNumber =
    typeof body.card === "string" ? body.card.replace(/\s/g, "") : "";

  if (!name || !EMAIL_PATTERN.test(email)) {
    throw new AppError("Nome e email válidos são obrigatórios", 400);
  }

  if (password.length < 3) {
    throw new AppError("A senha deve ter ao menos 3 caracteres", 400);
  }

  if (!Number.isInteger(courseId) || courseId < 1) {
    throw new AppError("Curso inválido", 400);
  }

  if (!CARD_PATTERN.test(cardNumber)) {
    throw new AppError("Cartão inválido", 400);
  }

  return { name, email, password, courseId, cardNumber };
}

module.exports = { parseCheckout };
