function loadConfig(environment = process.env) {
  const parsedPort = Number.parseInt(environment.PORT || "3000", 10);

  return {
    port: Number.isInteger(parsedPort) ? parsedPort : 3000,
    databaseFilename: environment.DATABASE_FILENAME || ":memory:",
    adminToken: environment.ADMIN_TOKEN || null,
  };
}

module.exports = { loadConfig };
