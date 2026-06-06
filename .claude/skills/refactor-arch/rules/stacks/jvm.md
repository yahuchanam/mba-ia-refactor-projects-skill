# JVM (Java / Kotlin) — operations

Spring Boot, Quarkus, Micronaut, Ktor.

## Detect
Maven → `pom.xml`; Gradle → `build.gradle`(`.kts`); `*.java`/`*.kt`. Wrappers: `./mvnw`, `./gradlew`.

## Dependencies & install
Resolved by the build tool on first run/build:
- Maven: `mvn dependency:resolve` (or just build)
- Gradle: `gradle dependencies` (or just build)

## Run / build / stop
- Spring Boot: `mvn spring-boot:run` · `gradle bootRun`
- Build: `mvn package` · `gradle build` (jar then `java -jar target/<app>.jar` — long-running;
  prefer in-process verify)
- Config via env / `application.properties`; don't prefix env on the CLI.

## Tests (when needed)
`mvn test` · `gradle test` (JUnit 5).

## Lint · format
Spotless: `mvn spotless:check` / `gradle spotlessCheck` · Checkstyle · ktlint.

## Verify the route surface in-process
- Spring MVC → `MockMvc` (`@WebMvcTest` / `@SpringBootTest` + `mockMvc.perform(get("/path"))`)
- Reactive → `WebTestClient`
- Full in-JVM boot → `@SpringBootTest(webEnvironment = RANDOM_PORT)` + `TestRestTemplate`

Run via `mvn test` / `gradle test` — no external server.

## Permission notes
Prefer installed `mvn`/`gradle` (program-name-first). The `./mvnw`/`./gradlew` wrappers are
path-qualified — allow-list `Bash(./mvnw:*)` / `Bash(./gradlew:*)` if you must use them.
