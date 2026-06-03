# AGENTS.md

Guidance for AI coding agents and contributors working on this Django shared expense tracking project.

## Project Context

This is a Django, Bootstrap, and SQLite web application for shared expense tracking and payment verification. Core features include user accounts, expense groups, equal split calculation, payment proof uploads, receiver verification, notifications, payment history, and reports.

The project is intended to be deployable to AWS later, so all changes should keep production readiness, security, and maintainability in mind.

## Software Best Practices

- Keep code simple, readable, and consistent with existing Django patterns.
- Prefer Django built-in features before adding custom abstractions or third-party packages.
- Keep business logic close to the domain it belongs to:
  - group membership rules in the `groups` app
  - expense and split logic in the `expenses` app
  - payment proof and verification logic in the `payments` app
  - notification creation in the `notifications` app
  - reporting queries in the `reports` app
- Avoid large views. Move repeated business logic into helper functions or model/query utilities when needed.
- Use clear model, form, view, and template names.
- Do not duplicate query logic across multiple views if it affects permissions or money calculations.
- Use database transactions for workflows that create or update multiple related records, especially expense creation and payment verification.
- Store money values with `DecimalField`, never floats.
- Keep templates focused on presentation. Do not place complex business rules in templates.
- Do not commit local-only files such as `.env`, `db.sqlite3`, uploaded media, caches, or virtual environments.

## Clean Code Standards

- Write small functions with one clear responsibility.
- Use meaningful variable names, especially for money, users, groups, and payment status.
- Keep comments rare and useful. Add comments only when the reason is not obvious from the code.
- Remove dead code, unused imports, and temporary debugging output before finishing.
- Prefer explicit permission checks over clever shortcuts.
- Use Django URL names consistently instead of hard-coded paths.
- Keep forms responsible for input validation.
- Keep views responsible for request flow, permissions, messages, and redirects.
- Keep tests readable and named after the behavior being verified.

## Security Best Practices

- Never commit secrets, API keys, AWS credentials, database passwords, or production `.env` files.
- Never commit Google OAuth client secrets or Gmail app passwords.
- Use environment variables for production settings:
  - `SECRET_KEY`
  - `DEBUG`
  - `ALLOWED_HOSTS`
  - database credentials
  - AWS storage credentials
- Set `DEBUG=False` in production.
- Set strict `ALLOWED_HOSTS` in production.
- Require login for all private pages.
- Always filter records by the logged-in user’s group membership before showing or updating data.
- Do not trust hidden form fields for ownership, payer, receiver, amount, or group permissions.
- Validate uploaded payment proof files by extension and preferably by content type before production launch.
- Restrict upload types to JPG, PNG, and PDF unless the product requirements change.
- Store uploaded files outside the code directory in production.
- Use HTTPS in production.
- Enable secure cookie settings in production:
  - `SESSION_COOKIE_SECURE=True`
  - `CSRF_COOKIE_SECURE=True`
  - `SECURE_SSL_REDIRECT=True`
  - `SECURE_HSTS_SECONDS` with an appropriate value after HTTPS is confirmed
- Keep CSRF protection enabled.
- Avoid exposing stack traces or raw exception messages to users.
- Use Django admin only for trusted staff accounts.
- Apply least privilege for AWS IAM users, roles, S3 buckets, and database access.

## Test Coverage Best Practices

- Add or update tests for every behavior change that affects:
  - authentication
  - group membership access
  - expense split calculations
  - payment status transitions
  - proof upload validation
  - notification creation
  - report totals
- Test permission boundaries:
  - users cannot view groups they do not belong to
  - non-admin members cannot add group members
  - payers can upload proof only for their own payments
  - receivers can verify only payments owed to them
- Test money calculations with `Decimal` values.
- Test important edge cases:
  - uneven split amounts
  - payer included in participants
  - payer excluded from participants
  - rejected payment resubmission
  - empty reports
- Keep tests deterministic. Avoid depending on the real current date unless the test explicitly controls it.
- Run before finishing changes:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

## AWS Deployment Best Practices

- Use environment variables or AWS Secrets Manager for all secrets.
- Store Google OAuth credentials and Gmail/AWS email credentials in environment variables or AWS Secrets Manager.
- Do not use SQLite for production if multiple users will use the app. Prefer Amazon RDS PostgreSQL for production.
- Use Amazon S3 for uploaded payment proofs and static/media files.
- Use CloudFront in front of S3 for static assets when appropriate.
- Use HTTPS with AWS Certificate Manager.
- Recommended deployment options:
  - AWS Elastic Beanstalk for a simpler Django deployment
  - ECS/Fargate for containerized deployment
  - EC2 only if manual server management is required
- Use a production WSGI server such as Gunicorn behind a reverse proxy/load balancer.
- Run migrations during deployment in a controlled step.
- Configure logging for production and send logs to CloudWatch.
- Set up automated backups for the production database.
- Apply S3 bucket policies carefully so payment proofs are not publicly accessible unless explicitly intended.
- Use separate environments for local, staging, and production.
- Keep production settings separate from development defaults.

## Required Quality Bar

Before considering work complete:

- The app starts without Django system check errors.
- Relevant tests pass.
- New or changed pages enforce login and ownership rules.
- Money calculations are covered by tests when changed.
- User-facing forms show clear validation errors.
- No secrets or local files are committed.
- Code remains clean, focused, and consistent with the current project structure.
