const express = require("express");
const { asyncHandler } = require("../middlewares/asyncHandler");
const { requireAdmin } = require("../middlewares/requireAdmin");

function createRoutes({
  checkoutController,
  financialReportController,
  userController,
  adminToken,
}) {
  const router = express.Router();
  const adminOnly = requireAdmin(adminToken);

  router.post(
    "/api/checkout",
    asyncHandler(checkoutController.create.bind(checkoutController)),
  );
  router.get(
    "/api/admin/financial-report",
    adminOnly,
    asyncHandler(
      financialReportController.index.bind(financialReportController),
    ),
  );
  router.delete(
    "/api/users/:id",
    adminOnly,
    asyncHandler(userController.delete.bind(userController)),
  );

  return router;
}

module.exports = { createRoutes };
