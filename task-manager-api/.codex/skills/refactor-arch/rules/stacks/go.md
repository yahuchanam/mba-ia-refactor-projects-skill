# Go — operations

Go web backends (net/http, Gin, Echo, Fiber, Chi).

## Detect
`go.mod`, `go.sum`, `*.go`. Entry is the `main` package (often `./cmd/<svc>` or the root).

## Dependencies & install
`go mod download` (fetch) · `go mod tidy` (reconcile). Modules are cached; no venv.

## Run / build / stop
- Run: `go run .` or `go run ./cmd/server`
- Build: `go build ./...` (binary then `./<bin>` — long-running; prefer in-process verify)
- Config via env read in code (`os.Getenv`), set inside the test, not as a CLI prefix.

## Tests (when needed)
`go test ./...` (Go's test tool also drives HTTP handlers in-process — see below).

## Lint · format
- Format check: `gofmt -l .`
- Vet: `go vet ./...`
- Lint: `golangci-lint run` (if configured)

## Verify the route surface in-process
Use `net/http/httptest` — no socket needed:
- `httptest.NewRecorder()` + `handler.ServeHTTP(rec, req)` for a handler/mux, or
- `httptest.NewServer(handler)` for an ephemeral in-memory server.

Put route assertions in a `_test.go` and run `go test ./...`, or a small `verify_routes.go` run
with `go run verify_routes.go`.

## Permission notes
Everything is program-name-first under `go`/`gofmt`/`golangci-lint`. Single commands only.
