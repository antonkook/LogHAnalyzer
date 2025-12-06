# LogHAnalyzer - AI Agent Instructions

## Project Overview
LogHAnalyzer is a Flask-based web application for log analysis with a Jinja2-templated frontend. The architecture is straightforward: a single Flask app instance with SQLAlchemy ORM integration and server-side template rendering.

## Architecture & Key Components

### Stack
- **Backend**: Flask with SQLAlchemy ORM (`app.py` is the single entry point)
- **Database**: SQLite at `sqlite:///test.db`
- **Frontend**: Jinja2 templates with vanilla CSS/JS

### Data Model
- `Todo` model in `app.py` with fields: `id`, `content`, `completed` (flag), `date_created`
- Direct model definition in main app file (no separate models module)

### Routing & Templating
- Root route `/` renders `templates/index.html` (extends `templates/base.html`)
- Base template includes static CSS and JS via `url_for()` helpers
- No blueprints currently in use (commented-out scaffold code in `__init__.py`)

## Developer Workflows

### Running the Application
```bash
python app.py  # Runs on default Flask dev server with debug=True
```

### Database Operations
- Instantiate `db` object from `app.py`: `from app import db`
- Create tables: `db.create_all()` in Python REPL or within app context
- No migrations framework (Alembic) configured; schema changes are manual

### Static Files
- CSS in `static/styles/style.css` (linked in base template)
- JavaScript in `static/js/main.js` (currently empty; to be implemented)

## Project Conventions & Patterns

### Code Organization
- **Single file app**: All Flask config, models, and routes in `app.py` (not factory pattern)
- **Minimal structure**: No separate blueprints or application factory despite scaffold comments
- **Template hierarchy**: Base template in `templates/base.html` with blocks for `head` and `body`

### SQLAlchemy Conventions
- Model defined inline with Flask app initialization
- Direct column definitions using SQLAlchemy Column types
- `__repr__` method returns task ID for debugging

### Frontend Integration
- Jinja2 `{% extends %}` and `{% block %}` for template inheritance
- `url_for()` function for static file references (prevents hardcoded paths)
- Empty `main.js` ready for event handlers and AJAX calls

## Critical Patterns to Preserve

1. **Flask app singleton**: `app` is globally instantiated in `app.py`, avoid factory pattern changes without refactoring views
2. **Direct SQLAlchemy initialization**: `db = SQLAlchemy(app)` couples database to app instance
3. **Inline models**: Keep model definitions in `app.py` unless migrating to blueprints/factory
4. **Template block inheritance**: Use consistent block names (`head`, `body`) across templates

## Common Tasks

### Adding a New Route
```python
@app.route("/path")
def view_name():
    return render_template("template.html", data=data)
```

### Querying the Database
```python
tasks = Todo.query.all()  # Fetch all
task = Todo.query.get(id)  # By ID
filtered = Todo.query.filter_by(completed=0).all()  # Filter
```

### Extending Templates
Use the block pattern in `index.html`:
```jinja2
{% extends 'base.html' %}
{% block body %}
  <!-- Your content here -->
{% endblock %}
```

## Known Limitations & Debt

- No error handling on routes (missing try-catch, 404 handlers)
- No test suite or fixtures
- Minimal CSS (base selector instead of classes)
- `main.js` is empty stub
- Database URI hardcoded (no environment config)
- Comments indicate abandoned Flaskr tutorial code; clean up when possible
