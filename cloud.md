# Git & GitHub Workflow

This project uses Git for version control with GitHub as the remote repository.

## Commit & Push Protocol

**As work is completed, the following workflow must be followed:**

1. **Regular Commits** — After completing each task or feature, create a commit with a clean, descriptive message
   - Example messages:
     - "Add feature: user authentication"
     - "Fix bug: prevent null pointer exception in parser"
     - "Update: refactor database queries for performance"
     - "Docs: add API documentation"

2. **Push to GitHub** — After each commit, push the changes to GitHub immediately
   - This ensures we never lose work and maintain a complete history
   - Command: `git push origin main`

3. **Clean Commit Messages** — Every commit message should:
   - Start with a verb (Add, Fix, Update, Refactor, Docs, etc.)
   - Be concise but descriptive (50 characters or less for the title)
   - Include context about what changed and why if needed
   - Follow a consistent format

## Why This Matters

- **Safety** — GitHub serves as a backup; work is never lost locally
- **History** — We can review what was done and when
- **Reversibility** — We can easily revert changes if needed
- **Transparency** — Clear history of project progress

## Repository

**GitHub Repository:** https://github.com/mansingka/Claude-NM

## Key Rules

- ✅ Commit after each completed task
- ✅ Push to GitHub immediately after committing
- ✅ Write clear, descriptive commit messages
- ✅ Never go long periods without pushing to GitHub
