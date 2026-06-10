const crypto = require("node:crypto");

function secureEqual(left, right) {
  const leftBuffer = Buffer.from(left);
  const rightBuffer = Buffer.from(right);

  return (
    leftBuffer.length === rightBuffer.length &&
    crypto.timingSafeEqual(leftBuffer, rightBuffer)
  );
}

function requireAdmin(adminToken) {
  return (request, response, next) => {
    if (!adminToken) {
      response.status(503).json({ error: "Administração não configurada" });
      return;
    }

    const authorization = request.get("authorization") || "";
    const [scheme, token] = authorization.split(" ");

    if (scheme !== "Bearer" || !token || !secureEqual(token, adminToken)) {
      response.status(401).json({ error: "Não autorizado" });
      return;
    }

    next();
  };
}

module.exports = { requireAdmin };
