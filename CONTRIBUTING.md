# Contributing Guide

Thank you for your interest in improving `deepfake-detector`! We welcome contributions that enhance safety, performance, documentation, and usability. Because the project operates in a sensitive domain, we enforce an additional review checklist focused on ethics and compliance.

## Workflow

1. **Discuss first** – open an issue describing the change. For sensitive features (data generation, deployment), include an ethical impact assessment.
2. **Fork & branch** – follow `feature/<topic>` naming.
3. **Install dev deps** – `pip install -r requirements.txt` and `npm install` inside `src/frontend`.
4. **Coding standards**
   - Python: type hints, docstrings, `black`/`ruff` style (pending automation), prefer dependency injection for configurable components.
   - Frontend: functional components, hooks, Tailwind utility classes, accessibility (aria labels).
   - Tests: add or update pytest cases for new behavior. Use mocks/fakes for diffusion pipelines.
5. **Ethics checklist** (include in PR description):
   - [ ] Data sources validated as synthetic or consented.
   - [ ] No automation for scraping or impersonation.
   - [ ] Warn users about legal/ethical constraints in docs or UI where relevant.
6. **Run checks** – ensure `pytest` and `npm run build` succeed. Provide sample outputs when practical.
7. **Pull request** – reference related issues, outline testing, confirm checklist. Two approvals required for high-risk changes.

## Commit Message Guidelines

- Use present tense: `Add`, `Fix`, `Improve`.
- Prefix with module when helpful: `train:`, `backend:`, `docs:`.

## Code of Conduct

Respectful communication is mandatory. Harassment, hate speech, and unethical experimentation are not tolerated. Violations may result in a ban and removal of contributions.

## Security & Responsible Disclosure

If you discover security or misuse vulnerabilities, email the maintainers privately (see `README.md`). Do **not** open a public issue until the concern is mitigated.

Thanks for keeping this project safe and responsible!
