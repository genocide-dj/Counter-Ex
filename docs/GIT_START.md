# Add this milestone to your repository

Repository identified from the supplied screenshot and confirmed through GitHub:
`https://github.com/genocide-dj/Counter-Ex`

This delivery is a source folder, not a clone. No remote files were changed.
To preserve the existing repository history, clone it first, then copy the
contents of this delivery into the clone. Replace the initial short README with
this milestone README. Copy `.github` and `.gitignore` too. Do not copy a ZIP file
or any `__pycache__` directories into the repository.

```powershell
git clone https://github.com/genocide-dj/Counter-Ex.git
cd Counter-Ex
git switch -c codex/verification-foundation
# Copy the delivered source files into this folder now.
python -m unittest discover -s tests -v
python -m counterex demo
git status --short
git add README.md .gitignore .github counterex examples tests docs evidence
git diff --cached --stat
git commit -m "feat: add CounterEx stress-testing foundation and runnable demos"
git push -u origin codex/verification-foundation
```

Then open a pull request into `main` on GitHub. The repository owner should choose
a license before wider redistribution. This milestone does not assume a license.
