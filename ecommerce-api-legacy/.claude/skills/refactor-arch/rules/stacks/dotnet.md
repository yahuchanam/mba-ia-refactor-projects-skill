# .NET — operations

ASP.NET Core web APIs (C#).

## Detect
`*.csproj`, `*.sln`, `Program.cs`, `*.cs`.

## Dependencies & install
`dotnet restore` (NuGet). Often implicit in `build`/`run`.

## Run / build / stop
- Run: `dotnet run` (in the project dir) · `dotnet run --project src/Api`
- Build: `dotnet build`
- Config via env / `appsettings.json` / user-secrets; don't prefix env on the CLI.
- Prefer in-process verification (below).

## Tests (when needed)
`dotnet test` (xUnit / NUnit / MSTest).

## Lint · format
`dotnet format` (style + analyzers).

## Verify the route surface in-process
ASP.NET Core integration tests: `WebApplicationFactory<Program>` →
`var client = factory.CreateClient();` then `await client.GetAsync("/path")` — the app runs
in-memory, no real socket. Place in an xUnit project and run `dotnet test`.

## Permission notes
Everything is program-name-first under `dotnet`. Single commands only.
