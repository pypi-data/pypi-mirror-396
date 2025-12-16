## FocusPro package (overview)

Productivity toolkit with three subpackages (`core`, `planner`, `analytics`) plus demos (`run_demo.py`, `test_code.py`). Model tasks/habits, generate daily plans, and produce weekly focus analytics.

### Subpackages
- `core/` — models and state (`Task`, `Habit`, `FocusSession`, managers, exceptions). See `src/project/core/introduction.md`.
- `planner/` — planners, priority strategies, schedulers, and `generate_daily_plan`. See `src/project/planner/introduction.md`.
- `analytics/` — distraction rates, weekly summaries, focus score/grade, markdown export. See `src/project/analytics/introduction.md`.

#### Subpackage summaries
- Core: `tasks.py` / `task.py` (task model + manager), `habit.py` (habit model + manager + CLI helpers), `focus_session.py` (session lifecycle, distractions, ratings), `exceptions.py` (domain errors).
- Planner: `base_planner.py` (planners, `PlannedBlock`), `priority_strategy.py` (scoring), `schedulers.py` (sequential, Pomodoro), `daily_plan.py` (planner selection + validation).
- Analytics: `distraction.py` (overall/per-task rates), `weekly_report.py` (weekly summary + markdown export), `focuscore.py` (focus score + grade), `exceptions.py` (report export errors).

### Demos
- Interactive: `python src/project/run_demo.py` (uses `tasks.json` / `habits.json` if present; otherwise prompts).
- Non-interactive: `python src/project/test_code.py` (scripted output).

### Quick start (PowerShell, repo root)
```bash
$env:PYTHONPATH="src\project"
python src/project/run_demo.py
```

### Using your own data
Place JSON alongside `run_demo.py`:
- `tasks.json`: `name`, `duration`, `category`, `difficulty`, `priority`, `completed`, `pomodoro`, `planned_distractions`.
- `habits.json`: `name`, `frequency`.

### Tests & coverage
```bash
$env:PYTHONPATH="src\project"
python -m unittest discover -s tests -t .
python -m coverage run -m unittest discover -s tests -t .
python -m coverage report
```
- Planner only: `python -m unittest -v tests.test_planner tests.test_planner_helpers`
- Core/analytics: `python -m unittest -v tests.test_core tests.test_focuscore`

### CI
GitHub Actions runs `coverage run -m unittest discover -s tests -t .` on pushes/PRs (see `.github/workflows/ci.yml`).

### Extensibility notes
- Persistence is JSON + prompts (educational); swap storage as needed.
- Planners/schedulers are swappable; add strategies without breaking callers.
- Analytics handles malformed data defensively and surfaces export errors via custom exceptions.
