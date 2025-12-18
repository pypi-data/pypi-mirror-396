# nushyax/templates.py

from typing import Dict

FRAMEWORK_TEMPLATES: Dict[str, Dict] = {
    "django": {
        "framework": "django",
        "aliases": {
            "s": "run",          # short for server
            "mm": "makemigrations",          # make migrations (already exists)
            "m": "migrate",      # short for migrate
            "sh": "shell",       # django shell
            "csu": "createsuperuser",
        },
        "overrides": {
            "run": "python manage.py runserver 0.0.0.0:8000",  # accessible from network
        },
        "commands": {  # optional: add commonly missing ones
            "shell": {
                "desc": "Open Django shell",
                "exec": "python manage.py shell"
            },
            "createsuperuser": {
                "desc": "Create a superuser",
                "exec": "python manage.py createsuperuser"
            },
        },
        "comment": "# Common Django shortcuts and overrides"
    },
    "flask": {
        "framework": "flask",
        "aliases": {
            "r": "run",
            "d": "run_debug",
        },
        "overrides": {
            "run": "flask run --host=0.0.0.0 --port=5000",
        },
        "commands": {
            "run_debug": {
                "desc": "Run Flask in debug mode",
                "exec": "flask run --host=0.0.0.0 --port=5000 --debug"
            }
        },
        "comment": "# Common Flask shortcuts"
    },
    "nextjs": {
        "framework": "nextjs",
        "aliases": {
            "d": "dev",      # short for dev
            "b": "build",
            "s": "start",
        },
        "overrides": {
            "dev": "npm run dev -- --hostname 0.0.0.0",
        },
        "comment": "# Common Next.js shortcuts"
    },
    "node": {  # generic Node.js / npm / yarn projects
        "framework": "node",
        "aliases": {
            "d": "dev",
            "b": "build",
            "s": "start",
            "t": "test",
        },
        "overrides": {},
        "comment": "# Generic Node.js aliases (customize scripts in package.json)"
    },
    "docker": {
        "framework": "docker",
        "aliases": {
            "u": "up",
            "d": "down",
            "l": "logs",
        },
        "overrides": {
            "up": "docker-compose up -d",  # detached mode by default
        },
        "commands": {
            "down": {
                "desc": "Stop and remove containers",
                "exec": "docker-compose down"
            },
            "logs": {
                "desc": "Follow logs",
                "exec": "docker-compose logs -f"
            }
        },
        "comment": "# Docker Compose shortcuts"
    },
    # Fallback generic template
    "generic": {
        "framework": None,
        "aliases": {
            "s": "start",
            "b": "build",
            "t": "test",
        },
        "overrides": {},
        "comment": "# Customize this file with your project's commands"
    }
}


def get_template(framework: str | None) -> dict:
    """Return the full template dict for a given framework."""
    if framework and framework in FRAMEWORK_TEMPLATES:
        return FRAMEWORK_TEMPLATES[framework].copy()
    return FRAMEWORK_TEMPLATES["generic"].copy()