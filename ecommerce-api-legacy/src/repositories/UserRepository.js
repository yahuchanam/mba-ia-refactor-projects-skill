class UserRepository {
  constructor(database) {
    this.database = database;
  }

  findByEmail(email) {
    return this.database.get(
      "SELECT id, name, email FROM users WHERE email = ?",
      [email],
    );
  }

  create({ name, email, passwordHash }) {
    return this.database.run(
      "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
      [name, email, passwordHash],
    );
  }

  deleteById(id) {
    return this.database.run("DELETE FROM users WHERE id = ?", [id]);
  }
}

module.exports = UserRepository;
