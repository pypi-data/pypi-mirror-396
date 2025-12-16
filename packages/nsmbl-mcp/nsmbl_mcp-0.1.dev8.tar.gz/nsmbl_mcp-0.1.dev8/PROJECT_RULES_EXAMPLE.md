---
description: Centralized development rules for NSMBL API - organized by priority
globs: app/**/*.py, main.py, dev/**/*.py, **/*
alwaysApply: true
---

# NSMBL API Development Rules

## Critical System Rules

```json
{
  "never_create_files": {
    "rule": "Never create files without explicit permission",
    "action": "Always ask before creating any new files in the project",
    "rationale": "Prevents unwanted file proliferation and maintains project structure integrity"
  },
  "mandatory_startup_shutdown": {
    "rule": "ONLY use start.sh and stop.sh for project startup and shutdown",
    "action": "Use ./start.sh & for startup, ./stop.sh for shutdown - NEVER manual uvicorn or celery commands",
    "rationale": "Ensures full stack (API + Celery) runs properly and complete cleanup occurs"
  },
  "conda_environment": {
    "rule": "Always activate nsmbl-api conda environment before Python operations",
    "action": "Prefix ALL Python commands with 'conda activate nsmbl-api &&' (start.sh handles this automatically)",
    "rationale": "Ensures correct dependencies and Python version"
  },
  "fail_fast": {
    "rule": "Abort immediately when anything is invalid or unexpected",
    "action": "Never continue with defaults or guessed values - raise specific errors",
    "rationale": "Prevent silent failures and provide clear feedback"
  },
  "never_run_git_commands": {
    "rule": "NEVER run git commands without explicit user permission",
    "action": "Always ask permission before running ANY git command (git status, git branch, git checkout, git commit, git push, etc.)",
    "rationale": "Git operations can affect version control state and must be controlled by the user",
    "critical": "This includes git commands in terminal, scripts, or any other context"
  }
}
```

## Error Handling

```json
{
  "centralized_errors": {
    "rule": "Use centralized app/errors/handlers.py system only",
    "action": "Call handle_*_error() functions, never create HTTPException directly",
    "rationale": "Single source of truth for error responses across entire API"
  },
  "minimal_error_format": {
    "rule": "Ultra-minimal error format: only 'error' and 'message' fields",
    "action": "No 'fix', 'suggestions', 'field', 'value', 'resource', 'details' fields",
    "rationale": "Clean, actionable error responses without verbose explanations"
  },
  "early_validation": {
    "rule": "Validate everything at the earliest possible point",
    "action": "Fail at request time, not processing time",
    "rationale": "Fail fast with specific error messages"
  },
  "http_status_codes": {
    "rule": "Use specific HTTP status codes consistently",
    "action": "422 for validation, 409 for conflicts, 404 for not found, 500 for processing failures",
    "rationale": "Clear error categorization for API consumers"
  },
  "never_expose_internal_services": {
    "rule": "NEVER expose internal service provider names to users",
    "action": "Use generic terms like 'market data service', 'external data provider', 'data service' instead of specific names like 'Alpaca', 'Alpha Vantage', 'Portfolio Optimizer'",
    "forbidden": ["Alpaca", "Alpha Vantage", "AlphaVantage", "Portfolio Optimizer", "any vendor-specific service names"],
    "applies_to": ["Error messages", "API documentation", "Endpoint descriptions", "User-facing responses", "README.md", "Exception messages"],
    "rationale": "Internal service providers are implementation details that should never be visible to end users",
    "critical": "Service provider names in errors/docs expose internal architecture and create vendor lock-in perception"
  }
}
```

## Terminal Usage

```json
{
  "project_startup_shutdown": {
    "rule": "MANDATORY: Use start.sh and stop.sh scripts ONLY",
    "action": "Always use ./start.sh & for startup, ./stop.sh for shutdown",
    "rationale": "Ensures full stack startup, proper cleanup, and terminal reset"
  },
  "single_line_commands": {
    "rule": "Only run single-line commands from terminal",
    "action": "Create .py scripts in dev/test_scripts/ for complex operations",
    "rationale": "Prevents hanging, complex debugging, and unpredictable behavior"
  },
  "script_based_complexity": {
    "rule": "Create scripts for any multi-step operations",
    "action": "Use TASK_{timestamp}_{description}.py naming pattern",
    "rationale": "Debuggable, reusable, and prevents terminal hanging"
  },
  "safe_command_patterns": {
    "rule": "Use proven, simple command patterns",
    "action": "Avoid complex nested quotes, f-strings with ${}, multi-line commands",
    "rationale": "Prevents syntax errors and shell interpretation conflicts"
  }
}
```

## Database Patterns

```json
{
  "database_functions": {
    "rule": "Use database functions for critical automation",
    "action": "Create touch_timestamp(), init_user() functions with triggers",
    "rationale": "Database functions run even if application crashes"
  },
  "security_definer": {
    "rule": "All database functions must use SECURITY DEFINER",
    "action": "SECURITY DEFINER SET search_path = public",
    "rationale": "Required for Supabase security compliance"
  },
  "unified_tables": {
    "rule": "Use unified tables with type discriminators",
    "action": "Single streams table with stream_type field instead of separate tables",
    "rationale": "Reduces schema complexity, simplifies queries"
  },
  "jsonb_storage": {
    "rule": "Store complex data in JSONB fields",
    "action": "Use JSONB for backtest_config, stream_config, backtest_metrics",
    "rationale": "Schema flexibility and easier evolution"
  },
  "row_level_security": {
    "rule": "Leverage Supabase RLS for data isolation",
    "action": "Use auth.uid() = user_id policies on user-scoped tables",
    "rationale": "Bulletproof data isolation without application-level filtering"
  },
  "no_triggers": {
    "rule": "NEVER create database triggers",
    "action": "Handle all business logic in application code, not database triggers",
    "rationale": "Database triggers are fragile, hard to debug, and cause schema/permission issues. Application code provides better error handling, logging, and flexibility",
    "forbidden": ["CREATE TRIGGER", "trigger functions", "automatic database triggers"],
    "preferred": "Use application endpoints for all business logic and data manipulation"
  }
}
```

## Development Workflow

```json
{
  "initial_version": {
    "rule": "This is an initial version - no backward compatibility needed",
    "action": "Build it right the first time, don't compromise for legacy support",
    "rationale": "Modern, clean, state-of-the-art API design without legacy baggage"
  },
  "edit_over_create": {
    "rule": "Always prefer editing existing files over creating new ones",
    "action": "Modify existing files to add new functionality when appropriate",
    "rationale": "Maintains project structure and reduces file proliferation"
  },
  "LATEST_REWORK.md": {
    "rule": "Use dev/LATEST_REWORK.md for comprehensive feature planning and implementation tracking",
    "structure": {
      "top_section": "DEMONSTRATE YOUR UNDERSTANDING OF THE FEATURE: Current vs Future State Analysis - Map out file-by-file and function-by-function flow of how the project currently operates and how it will operate after implementation. Evaluate codebase thoroughly before writing this section.",
      "mid_section": "Comprehensive File Change List - Every file that would be added/removed/modified, plus any Supabase table fields that would be added/removed/modified if database-related.",
      "bottom_section": "JSON Task List - Task-by-task implementation plan with every change needed to fully implement the feature. Exclude testing tasks but prioritize legacy code removal and cleanup. Include reminders to review endpoint schemas or API documentation before implementing API-related code."
    },
    "purpose": "Ensures thorough planning, prevents scope creep, and provides clear implementation roadmap",
    "critical": "Always complete LATEST_REWORK.md before beginning any significant feature work. NEVER INCLUDE TIMELINES."
  }
}
```

## Environment Configuration

```json
{
  "env_file_reading": {
    "rule": "Use Python scripts for all .env file reading operations",
    "action": "Write .py script in dev/test_scripts/ to read and parse .env file contents",
    "rationale": "Provides controlled access without direct file manipulation"
  },
  "env_file_updates": {
    "rule": "Use Python scripts for all .env file modifications",
    "action": "Write .py script that: 1) reads current .env state, 2) makes necessary changes to complete state, 3) overwrites entire file with new state",
    "rationale": "Ensures consistent formatting and prevents concatenation/corruption issues"
  },
  "env_vs_config": {
    "rule": "Keep sensitive variables in .env files, non-sensitive in config files",
    "action": "API keys, passwords, secrets → .env files; timeouts, URLs, defaults → app/core/config.py",
    "rationale": "Separates security-critical data from application configuration"
  },
  "env_settings_approach": {
    "rule": "ALL environment variable access MUST use settings object",
    "action": "Always use 'from app.core.config import settings' then 'settings.VARIABLE_NAME' - NEVER use os.getenv() or direct file reading",
    "rationale": "Single source of truth with type safety, works with Railway dashboard env vars, and provides consistent patterns"
  },
  "readme_maintenance": {
    "rule": "Keep README.md environment documentation current with .env file",
    "action": "Review and update README.md setup/configuration sections after .env changes",
    "rationale": "Ensures new developers have accurate environment setup instructions"
  },
}
```
---
alwaysApply: true
---
