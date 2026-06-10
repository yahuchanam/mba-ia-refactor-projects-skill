# PHP — operations

PHP web backends (Laravel, Symfony, Slim, vanilla).

## Detect
`composer.json`, `composer.lock`, `*.php`; Laravel → `artisan`; Symfony → `bin/console`.

## Dependencies & install
Composer: `composer install`. Run project tools via `composer exec <tool>` or framework CLIs so
the program name is `composer`/`php` (not `./vendor/bin/<tool>`).

## Run / stop environment
- Laravel: `php artisan serve`
- Symfony: `symfony serve` · or built-in `php -S localhost:8000 -t public`
- Config via `.env` (Dotenv) loaded by the framework; don't prefix env on the CLI.
- Prefer in-process verification (below).

## Tests (when needed)
- Laravel: `php artisan test`
- PHPUnit: `composer exec phpunit` (avoid `./vendor/bin/phpunit`)
- Pest: `composer exec pest`

## Lint · static analysis · format
- PHPStan: `composer exec phpstan analyse` · Psalm: `composer exec psalm`
- CS: `composer exec php-cs-fixer fix --dry-run` / `composer exec phpcs`

## Verify the route surface in-process
- Laravel → HTTP tests in `TestCase`: `$this->get('/path')`, `$this->postJson(...)` — no server.
- Symfony → `WebTestCase`: `$client = static::createClient(); $client->request('GET', '/path')`.

Run via `php artisan test` or `composer exec phpunit`.

## Permission notes
Drive everything through `php`/`composer`. `./vendor/bin/<tool>` is path-qualified — use
`composer exec <tool>` instead, or allow-list it explicitly.
