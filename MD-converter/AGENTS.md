# AGENTS.md

Keep guidance short, concrete, and easy to follow.

## Working rules
- Make the smallest change that solves the task.
- Preserve existing architecture, naming, and style unless the task says otherwise.
- Prefer simple, readable code over clever code.
- Do not add new dependencies unless they are clearly justified.
- Ask for clarification only when the request is genuinely ambiguous or conflicting.

## When changing code
- Read the relevant files before editing.
- Follow the established patterns in the codebase.
- Keep unrelated refactors out of the same change.
- Update tests, types, docs, and examples when behavior changes.

## Quality bar
- Verify changes with the most relevant automated checks available: tests, linting, type-checking, build, or targeted scripts.
- Do not claim something works unless you have checked it.
- Prefer incremental, reviewable commits or patches.

## Security and safety
- Never expose secrets, tokens, private keys, or credentials.
- Treat user data and environment variables as sensitive.
- Avoid introducing unsafe code paths, shell injection risks, or insecure defaults.
- Flag security-sensitive changes explicitly in your summary.

## Communication
- State assumptions clearly.
- Summarize what changed, what was verified, and any remaining risks.
- If a task is large, propose a short plan before making broad edits.
