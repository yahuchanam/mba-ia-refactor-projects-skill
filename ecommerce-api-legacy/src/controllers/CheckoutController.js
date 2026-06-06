const { parseCheckout } = require("../models/Checkout");

class CheckoutController {
  constructor(checkoutService) {
    this.checkoutService = checkoutService;
  }

  async create(request, response) {
    const input = parseCheckout(request.body);
    const result = await this.checkoutService.checkout(input);
    response.status(200).json(result);
  }
}

module.exports = CheckoutController;
