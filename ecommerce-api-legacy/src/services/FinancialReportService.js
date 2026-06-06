class FinancialReportService {
  constructor(financialReports) {
    this.financialReports = financialReports;
  }

  async getReport({ page, size }) {
    const rows = await this.financialReports.findPage(size, (page - 1) * size);
    const courses = new Map();

    for (const row of rows) {
      if (!courses.has(row.course_id)) {
        courses.set(row.course_id, {
          course: row.course_title,
          revenue: 0,
          students: [],
        });
      }

      if (!row.enrollment_id) {
        continue;
      }

      const course = courses.get(row.course_id);
      if (row.payment_status === "PAID") {
        course.revenue += row.payment_amount;
      }

      course.students.push({
        student: row.student_name || "Unknown",
        paid: row.payment_amount || 0,
      });
    }

    return Array.from(courses.values());
  }
}

module.exports = FinancialReportService;
