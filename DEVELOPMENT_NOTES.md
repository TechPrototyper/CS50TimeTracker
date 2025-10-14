# Development Notes

## Useful Tools

### Database Management
- [SQLiteStudio](https://github.com/pawelsalawa/sqlitestudio) - GUI tool for managing SQLite databases
- Command line: `sqlite3 sitr.db` for direct database access

### API Testing
- FastAPI Swagger UI: `http://127.0.0.1:8000/docs` when server is running
- `curl` or `httpie` for command-line API testing
- Postman for comprehensive API testing

## Development History

This project originated as a CS50 Final Project and went through several iterations:

1. **Initial Design Phase** - Domain modeling and architecture planning
2. **Core Implementation** - Models, repositories, and service layer
3. **CLI Development** - Typer-based command interface with Rich formatting
4. **API Layer** - Complete REST API with FastAPI
5. **Infrastructure** - Server management and configuration system

## Key Design Decisions

### Why SQLModel?
- Single source of truth for DB and API models
- Type safety with Pydantic validation
- Seamless ORM integration
- No impedance mismatch (snake_case throughout)

### Why Separate API?
- Enables future web/mobile clients
- Clean separation of concerns
- Can be deployed independently
- Better for testing

### Why Auto-Start Server?
- Better user experience
- No manual server management needed
- Transparent to end users

## Future Enhancements

### Short Term
- [ ] CSV/JSON export functionality
- [ ] Daily/weekly reports
- [ ] Better timezone handling
- [ ] Command aliases for faster typing

### Medium Term
- [ ] macOS menu bar app
- [ ] Integration with Shortcuts app
- [ ] Alfred/Raycast workflow
- [ ] Analytics dashboard

### Long Term
- [ ] Web UI (React/Vue)
- [ ] Mobile apps (iOS/Android)
- [ ] Multi-user support
- [ ] Cloud sync option

## Performance Notes

### Current Limits
- SQLite handles thousands of entries without issues
- Single user = no concurrency concerns
- Local server = minimal latency
- CLI startup time ~200ms (acceptable)

### Optimization Opportunities
- Add database indexes for common queries
- Cache active project in memory
- Batch database writes for analytics
- Consider PostgreSQL for multi-user deployment

## Testing Strategy

### Current Coverage
- Service layer logic
- Repository CRUD operations
- Basic workflow integration

### Needs More Tests
- API endpoint edge cases
- CLI command parsing
- Error handling paths
- Timezone edge cases

## Known Issues

None currently! 🎉

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)

## Contact & Feedback

For questions or suggestions, open an issue on GitHub.

