class CourseRepository {
  constructor(database) {
    this.database = database;
  }

  findActiveById(id) {
    return this.database.get(
      "SELECT id, title, price FROM courses WHERE id = ? AND active = 1",
      [id],
    );
  }
}

module.exports = CourseRepository;
