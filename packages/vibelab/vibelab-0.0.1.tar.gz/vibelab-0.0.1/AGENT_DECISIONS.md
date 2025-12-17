# Agent Implementation Decisions

This document records key decisions made during MVP implementation.

## Architecture Decisions

1. **Git Worktree Simplification**: For MVP, the local driver clones GitHub repositories directly to the workdir instead of using git worktrees. This simplifies the implementation while maintaining isolation. Worktrees can be added later if needed for performance.

2. **Sequential Execution**: Executors run sequentially (not in parallel) for MVP. This simplifies error handling and resource management. Parallel execution can be added post-MVP.

3. **Background Tasks**: API runs use FastAPI BackgroundTasks for async execution. This allows immediate response while execution continues. For production, consider a proper task queue (Celery, RQ, etc.).

4. **Database Connection Pattern**: Using generator pattern for database connections (`get_db()`) to ensure proper cleanup. This follows FastAPI best practices.

5. **Patch Generation**: Patches are generated using `git diff HEAD` after execution. This captures all changes made during execution.

## Implementation Simplifications

1. **Error Handling**: Basic error handling implemented. More robust error recovery can be added later.

2. **Logging**: Using Python's standard logging module. Structured logging can be enhanced later.

3. **Type Safety**: Full type hints throughout Python code. TypeScript types are basic but functional.

4. **UI Styling**: Using Tailwind CSS for quick styling. Can be enhanced with a design system later.

5. **API Response Format**: Simple JSON responses. Can add pagination, filtering, etc. later.

## Future Enhancements

- Real-time log streaming via WebSocket
- Docker/Modal drivers
- More robust error handling and retries
- Result comparison UI improvements
- Export/import functionality
- Batch evaluation support
