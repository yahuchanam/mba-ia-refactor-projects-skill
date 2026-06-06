const sqlite3 = require("sqlite3").verbose();

class SqliteDatabase {
  constructor(filename) {
    this.connection = new sqlite3.Database(filename);
    this.transactionTail = Promise.resolve();
  }

  run(sql, parameters = []) {
    return new Promise((resolve, reject) => {
      this.connection.run(sql, parameters, function onRun(error) {
        if (error) {
          reject(error);
          return;
        }

        resolve({ id: this.lastID, changes: this.changes });
      });
    });
  }

  get(sql, parameters = []) {
    return new Promise((resolve, reject) => {
      this.connection.get(sql, parameters, (error, row) => {
        if (error) {
          reject(error);
          return;
        }

        resolve(row);
      });
    });
  }

  all(sql, parameters = []) {
    return new Promise((resolve, reject) => {
      this.connection.all(sql, parameters, (error, rows) => {
        if (error) {
          reject(error);
          return;
        }

        resolve(rows);
      });
    });
  }

  async transaction(work) {
    const execute = async () => {
      await this.run("BEGIN IMMEDIATE");

      try {
        const result = await work();
        await this.run("COMMIT");
        return result;
      } catch (error) {
        await this.run("ROLLBACK");
        throw error;
      }
    };

    const result = this.transactionTail.then(execute, execute);
    this.transactionTail = result.catch(() => undefined);
    return result;
  }

  close() {
    return new Promise((resolve, reject) => {
      this.connection.close((error) => {
        if (error) {
          reject(error);
          return;
        }

        resolve();
      });
    });
  }
}

module.exports = SqliteDatabase;
