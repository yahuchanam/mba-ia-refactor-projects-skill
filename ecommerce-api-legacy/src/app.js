const express = require("express");
const { loadConfig } = require("./config");
const SqliteDatabase = require("./database/SqliteDatabase");
const { initializeDatabase } = require("./database/initializeDatabase");
const AppError = require("./models/AppError");
const PasswordHasher = require("./security/PasswordHasher");
const UserRepository = require("./repositories/UserRepository");
const CourseRepository = require("./repositories/CourseRepository");
const EnrollmentRepository = require("./repositories/EnrollmentRepository");
const PaymentRepository = require("./repositories/PaymentRepository");
const AuditLogRepository = require("./repositories/AuditLogRepository");
const FinancialReportRepository = require("./repositories/FinancialReportRepository");
const PaymentService = require("./services/PaymentService");
const CheckoutService = require("./services/CheckoutService");
const FinancialReportService = require("./services/FinancialReportService");
const UserService = require("./services/UserService");
const CheckoutController = require("./controllers/CheckoutController");
const FinancialReportController = require("./controllers/FinancialReportController");
const UserController = require("./controllers/UserController");
const { createRoutes } = require("./routes");
const { errorHandler } = require("./middlewares/errorHandler");

async function createApplication(options = {}) {
  const config = options.config || loadConfig();
  const database =
    options.database || new SqliteDatabase(config.databaseFilename);
  const passwordHasher = options.passwordHasher || new PasswordHasher();

  await initializeDatabase(database, passwordHasher);

  const users = new UserRepository(database);
  const courses = new CourseRepository(database);
  const enrollments = new EnrollmentRepository(database);
  const payments = new PaymentRepository(database);
  const auditLogs = new AuditLogRepository(database);
  const financialReports = new FinancialReportRepository(database);

  const checkoutService = new CheckoutService({
    database,
    users,
    courses,
    enrollments,
    payments,
    auditLogs,
    paymentService: new PaymentService(),
    passwordHasher,
  });
  const financialReportService = new FinancialReportService(financialReports);
  const userService = new UserService(users);

  const app = express();
  app.disable("x-powered-by");
  app.use(express.json({ limit: "32kb" }));
  app.use(
    createRoutes({
      checkoutController: new CheckoutController(checkoutService),
      financialReportController: new FinancialReportController(
        financialReportService,
      ),
      userController: new UserController(userService),
      adminToken: config.adminToken,
    }),
  );
  app.use((request, response, next) => {
    next(new AppError("Rota não encontrada", 404));
  });
  app.use(errorHandler);

  return { app, database, config };
}

async function start(options = {}) {
  const application = await createApplication(options);
  const server = await new Promise((resolve, reject) => {
    const listener = application.app.listen(application.config.port);
    listener.once("listening", () => resolve(listener));
    listener.once("error", reject);
  });

  const address = server.address();
  process.stdout.write(`LMS API rodando na porta ${address.port}\n`);
  return { ...application, server };
}

if (require.main === module) {
  start().catch((error) => {
    process.stderr.write(`Falha ao iniciar a aplicação: ${error.message}\n`);
    process.exitCode = 1;
  });
}

module.exports = { createApplication, start };
