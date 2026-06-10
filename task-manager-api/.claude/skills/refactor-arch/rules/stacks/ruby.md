# Ruby — operations

Ruby web backends (Rails, Sinatra, Rack, Hanami).

## Detect
`Gemfile`, `Gemfile.lock`, `config.ru`, `*.rb`; Rails → `bin/rails`, `config/application.rb`.

## Dependencies & install
Bundler: `bundle install`. Run project bins via `bundle exec <tool>` (program-name = `bundle`),
not `./bin/<tool>` paths where avoidable.

## Run / stop environment
- Rails: `bundle exec rails server` (or `bin/rails server` — path-qualified, allow-list
  `Bash(bin/rails:*)` if used)
- Rack/Sinatra: `bundle exec rackup` · plain `ruby app.rb`
- Config via env (`ENV[...]`) set inside the script/test, not a CLI prefix.
- Prefer in-process verification (below).

## Tests (when needed)
RSpec: `bundle exec rspec` · Minitest/Rails: `bin/rails test` (or `bundle exec rake test`).

## Lint · format
RuboCop: `bundle exec rubocop` (autocorrect `bundle exec rubocop -a`).

## Verify the route surface in-process
- Rack apps → `rack-test`: `include Rack::Test::Methods`; `get '/path'` against `app`.
- Rails → request/integration specs (`ActionDispatch::IntegrationTest`) drive routes without a
  booted server.

Run via `bundle exec rspec` or `bin/rails test`.

## Permission notes
Prefer `bundle exec <tool>` so the program name is `bundle`. Path-qualified `bin/*` wrappers need
their own allow-list entry.
