const test = require("node:test");
const assert = require("node:assert/strict");
const http = require("node:http");
const request = require("supertest");
const { createApplication } = require("../src/app");

const ADMIN_TOKEN = "test-admin-token";

async function createTestContext(adminToken = ADMIN_TOKEN) {
  const application = await createApplication({
    config: {
      port: 0,
      databaseFilename: ":memory:",
      adminToken,
    },
  });
  const server = http.createServer(application.app);

  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolve);
  });

  return {
    ...application,
    client: request(server),
    async close() {
      await new Promise((resolve, reject) => {
        server.close((error) => {
          if (error) {
            reject(error);
            return;
          }

          resolve();
        });
      });
      await application.database.close();
    },
  };
}

test("POST /api/checkout creates a paid enrollment", async (context) => {
  const { client, database, close } = await createTestContext();
  context.after(close);

  const response = await client.post("/api/checkout").send({
    usr: "Guilherme",
    eml: "gui@fullcycle.com.br",
    pwd: "senhaforte",
    c_id: 2,
    card: "4111222233334444",
  });

  assert.equal(response.status, 200);
  assert.equal(response.body.msg, "Sucesso");
  assert.equal(typeof response.body.enrollment_id, "number");

  const user = await database.get("SELECT pass FROM users WHERE email = ?", [
    "gui@fullcycle.com.br",
  ]);
  assert.match(user.pass, /^scrypt\$/);
  assert.equal(user.pass.includes("senhaforte"), false);
});

test("POST /api/checkout rejects invalid and denied payments", async (context) => {
  const { client, database, close } = await createTestContext();
  context.after(close);

  const invalid = await client.post("/api/checkout").send({
    usr: "Invalid",
    eml: "not-an-email",
    pwd: "123",
    c_id: 1,
    card: "4111222233334444",
  });
  assert.equal(invalid.status, 400);

  const denied = await client.post("/api/checkout").send({
    usr: "João",
    eml: "joao@teste.com",
    pwd: "123",
    c_id: 1,
    card: "5111222233334444",
  });
  assert.equal(denied.status, 400);
  assert.deepEqual(denied.body, { error: "Pagamento recusado" });

  const deniedUser = await database.get(
    "SELECT id FROM users WHERE email = ?",
    ["joao@teste.com"],
  );
  assert.equal(deniedUser, undefined);
});

test("GET /api/admin/financial-report requires admin and avoids sensitive data", async (context) => {
  const { client, close } = await createTestContext();
  context.after(close);

  const unauthorized = await client.get("/api/admin/financial-report");
  assert.equal(unauthorized.status, 401);

  const response = await client
    .get("/api/admin/financial-report?page=1&size=10")
    .set("Authorization", `Bearer ${ADMIN_TOKEN}`);

  assert.equal(response.status, 200);
  assert.equal(Array.isArray(response.body), true);
  assert.equal(response.body[0].course, "Clean Architecture");
  assert.equal(response.body[0].revenue, 997);
  assert.deepEqual(response.body[0].students[0], {
    student: "Leonan",
    paid: 997,
  });
  assert.equal(JSON.stringify(response.body).includes("pass"), false);
  assert.equal(JSON.stringify(response.body).includes("email"), false);
});

test("DELETE /api/users/:id is admin-only and cascades related records", async (context) => {
  const { client, database, close } = await createTestContext();
  context.after(close);

  const unauthorized = await client.delete("/api/users/1");
  assert.equal(unauthorized.status, 401);

  const response = await client
    .delete("/api/users/1")
    .set("Authorization", `Bearer ${ADMIN_TOKEN}`);

  assert.equal(response.status, 200);
  assert.equal(response.text, "Usuário deletado.");

  const enrollments = await database.get(
    "SELECT COUNT(*) AS count FROM enrollments WHERE user_id = ?",
    [1],
  );
  const payments = await database.get("SELECT COUNT(*) AS count FROM payments");
  assert.equal(enrollments.count, 0);
  assert.equal(payments.count, 0);
});

test("admin routes return 503 when ADMIN_TOKEN is not configured", async (context) => {
  const { client, close } = await createTestContext(null);
  context.after(close);

  const response = await client
    .get("/api/admin/financial-report")
    .set("Authorization", "Bearer any-value");

  assert.equal(response.status, 503);
});
