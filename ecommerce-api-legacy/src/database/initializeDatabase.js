const crypto = require("node:crypto");

async function initializeDatabase(database, passwordHasher) {
  await database.run("PRAGMA foreign_keys = ON");
  await database.run(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            pass TEXT NOT NULL
        )
    `);
  await database.run(`
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        )
    `);
  await database.run(`
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE
        )
    `);
  await database.run(`
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            enrollment_id INTEGER NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
            amount REAL NOT NULL,
            status TEXT NOT NULL
        )
    `);
  await database.run(`
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY,
            action TEXT NOT NULL,
            created_at DATETIME NOT NULL
        )
    `);

  const existingCourse = await database.get("SELECT id FROM courses LIMIT 1");
  if (existingCourse) {
    return;
  }

  const seedPassword = await passwordHasher.hash(
    crypto.randomBytes(32).toString("hex"),
  );

  await database.transaction(async () => {
    const user = await database.run(
      "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
      ["Leonan", "leonan@fullcycle.com.br", seedPassword],
    );
    const firstCourse = await database.run(
      "INSERT INTO courses (title, price, active) VALUES (?, ?, ?)",
      ["Clean Architecture", 997, 1],
    );
    await database.run(
      "INSERT INTO courses (title, price, active) VALUES (?, ?, ?)",
      ["Docker", 497, 1],
    );
    const enrollment = await database.run(
      "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
      [user.id, firstCourse.id],
    );
    await database.run(
      "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
      [enrollment.id, 997, "PAID"],
    );
  });
}

module.exports = { initializeDatabase };
