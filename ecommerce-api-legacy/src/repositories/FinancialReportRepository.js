class FinancialReportRepository {
  constructor(database) {
    this.database = database;
  }

  findPage(limit, offset) {
    return this.database.all(
      `
                WITH paged_courses AS (
                    SELECT id, title
                    FROM courses
                    ORDER BY id
                    LIMIT ? OFFSET ?
                )
                SELECT
                    courses.id AS course_id,
                    courses.title AS course_title,
                    enrollments.id AS enrollment_id,
                    users.name AS student_name,
                    payments.amount AS payment_amount,
                    payments.status AS payment_status
                FROM paged_courses AS courses
                LEFT JOIN enrollments ON enrollments.course_id = courses.id
                LEFT JOIN users ON users.id = enrollments.user_id
                LEFT JOIN payments ON payments.enrollment_id = enrollments.id
                ORDER BY courses.id, enrollments.id
            `,
      [limit, offset],
    );
  }
}

module.exports = FinancialReportRepository;
