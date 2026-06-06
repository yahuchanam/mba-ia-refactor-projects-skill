const AppError = require("../models/AppError");

const APPROVED_CARD_PREFIX = "4";

class PaymentService {
  authorize(cardNumber) {
    if (!cardNumber.startsWith(APPROVED_CARD_PREFIX)) {
      throw new AppError("Pagamento recusado", 400);
    }

    return "PAID";
  }
}

module.exports = PaymentService;
