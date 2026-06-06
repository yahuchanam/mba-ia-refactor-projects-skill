const DEFAULT_PAGE_SIZE = 20;
const MAX_PAGE_SIZE = 100;

function positiveInteger(value, fallback) {
  const parsed = Number.parseInt(value, 10);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback;
}

class FinancialReportController {
  constructor(financialReportService) {
    this.financialReportService = financialReportService;
  }

  async index(request, response) {
    const page = positiveInteger(request.query.page, 1);
    const requestedSize = positiveInteger(
      request.query.size,
      DEFAULT_PAGE_SIZE,
    );
    const size = Math.min(requestedSize, MAX_PAGE_SIZE);
    const report = await this.financialReportService.getReport({ page, size });

    response.json(report);
  }
}

module.exports = FinancialReportController;
