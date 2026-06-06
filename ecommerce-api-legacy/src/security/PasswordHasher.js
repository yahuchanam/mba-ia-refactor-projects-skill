const crypto = require("node:crypto");
const { promisify } = require("node:util");

const scrypt = promisify(crypto.scrypt);
const KEY_LENGTH = 64;

class PasswordHasher {
  async hash(password) {
    const salt = crypto.randomBytes(16).toString("hex");
    const derivedKey = await scrypt(password, salt, KEY_LENGTH);
    return `scrypt$${salt}$${derivedKey.toString("hex")}`;
  }

  async verify(storedPassword, candidate) {
    const [algorithm, salt, storedKey] = storedPassword.split("$");
    if (algorithm !== "scrypt" || !salt || !storedKey) {
      return false;
    }

    const derivedKey = await scrypt(candidate, salt, KEY_LENGTH);
    const storedBuffer = Buffer.from(storedKey, "hex");
    return (
      storedBuffer.length === derivedKey.length &&
      crypto.timingSafeEqual(storedBuffer, derivedKey)
    );
  }
}

module.exports = PasswordHasher;
