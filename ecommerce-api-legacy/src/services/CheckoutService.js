const AppError = require("../models/AppError");

class CheckoutService {
  constructor({
    database,
    users,
    courses,
    enrollments,
    payments,
    auditLogs,
    paymentService,
    passwordHasher,
  }) {
    this.database = database;
    this.users = users;
    this.courses = courses;
    this.enrollments = enrollments;
    this.payments = payments;
    this.auditLogs = auditLogs;
    this.paymentService = paymentService;
    this.passwordHasher = passwordHasher;
  }

  async checkout(input) {
    const course = await this.courses.findActiveById(input.courseId);
    if (!course) {
      throw new AppError("Curso não encontrado", 404);
    }

    const paymentStatus = this.paymentService.authorize(input.cardNumber);

    return this.database.transaction(async () => {
      const userId = await this.findOrCreateUser(input);
      const enrollment = await this.enrollments.create(userId, course.id);

      await this.payments.create(enrollment.id, course.price, paymentStatus);
      await this.auditLogs.record(`Checkout curso ${course.id} por ${userId}`);

      return { msg: "Sucesso", enrollment_id: enrollment.id };
    });
  }

  async findOrCreateUser(input) {
    const existingUser = await this.users.findByEmail(input.email);
    if (existingUser) {
      return existingUser.id;
    }

    const passwordHash = await this.passwordHasher.hash(input.password);
    const user = await this.users.create({
      name: input.name,
      email: input.email,
      passwordHash,
    });
    return user.id;
  }
}

module.exports = CheckoutService;
