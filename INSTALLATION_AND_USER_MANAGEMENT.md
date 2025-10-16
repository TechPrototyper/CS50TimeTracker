# SITR Installation & User Management Guide

## Installation Options

### Interactive Installation

```bash
./install.sh
```

The installer will detect if you have an existing database and offer appropriate options:

**With existing database:**
1. Update (keep existing database)
2. Fresh install (backup and reset database)
3. Development mode (keep database, editable install)

**Without existing database:**
1. Regular installation
2. Development installation (editable)

### Command-Line Options

```bash
# Fresh installation (backs up and resets database)
./install.sh --fresh

# Update existing installation (keeps database)
./install.sh --update

# Development mode (editable install, keeps database)
./install.sh --dev

# Uninstall
./install.sh --uninstall

# Show help
./install.sh --help
```

### Database Management

- **Database location:** `~/.sitr/sitr.db`
- **Automatic backup:** Created on every installation with timestamp
- **Backup location:** `~/.sitr/sitr.db.backup.YYYYMMDD_HHMMSS`
- **Demo data:** Optional during fresh installation

## User Management

### Creating Users

```bash
sitr user add -f John -l Doe -e john@example.com
```

### Listing Users

```bash
# List active users only
sitr user list

# List all users (including archived)
sitr user list --all
```

### Archiving Users (Soft Delete)

**Recommended approach** - Preserves all data:

```bash
sitr user archive -e john@example.com
```

**What happens:**
- ✅ User is hidden from normal lists
- ✅ All tracking data is preserved
- ✅ All projects are preserved
- ✅ User cannot be selected for new tracking
- ✅ Can be restored later

**View archived users:**
```bash
sitr user list --all
```

**Restore archived user:**
```bash
sitr user restore -e john@example.com
```

### Deleting Users (Permanent)

⚠️  **WARNING: This is permanent and cannot be undone!**

```bash
sitr user delete -e john@example.com
```

**Interactive process:**
1. Shows what will be deleted:
   - Number of tracking entries
   - Number of projects owned
   - Projects with shared tracking (from other users)

2. Requires double confirmation

3. Deletes:
   - User account
   - All tracking entries by this user
   - All projects owned by this user (unless other users have tracking on them)

**Skip confirmation (dangerous!):**
```bash
sitr user delete -e john@example.com --force
```

### User Deletion Behavior

**When a user has:**
- **Only their own tracking:** All tracking and projects are deleted
- **Projects with other users' tracking:** Projects are kept, but user's tracking is removed
- **Shared projects:** Projects remain if other users have tracked time on them

**Always consider archiving instead of deleting!**

## Database Locations

### Current (v1.0+)
- Database: `~/.sitr/sitr.db`
- Backups: `~/.sitr/sitr.db.backup.*`

### Legacy (pre-v1.0)
- Database: `./sitr.db` (in project directory)
- Automatically migrated to new location on first install

## Troubleshooting

### "NOT NULL constraint failed: project.user_id"

**Problem:** You tried to delete a user with the old delete command.

**Solution:** Use the new archive or delete commands:
```bash
# Recommended: Archive the user
sitr user archive -e user@example.com

# Or: Delete with cascade (WARNING: permanent!)
sitr user delete -e user@example.com
# (follow the prompts)
```

### Database is Locked

**Problem:** Another SITR process is using the database.

**Solution:**
```bash
# Check if server is running
sitr server status

# Stop server if needed
sitr server stop

# Try operation again
```

### Restore from Backup

**Find latest backup:**
```bash
ls -lt ~/.sitr/*.backup.*
```

**Restore:**
```bash
cp ~/.sitr/sitr.db.backup.YYYYMMDD_HHMMSS ~/.sitr/sitr.db
```

## Best Practices

### User Management

1. **Archive instead of delete:** Unless you're sure you never need the data
2. **Regular backups:** Before major operations
3. **Use archived view:** `sitr user list --all` to see all users
4. **Clean up carefully:** Review deletion impact before confirming

### Installation

1. **Update installations:** Use `./install.sh --update` to keep your data
2. **Fresh installs:** Use `./install.sh --fresh` only when starting over
3. **Development:** Use `./install.sh --dev` for editable installs
4. **Check backups:** Backups are created automatically in `~/.sitr/`

### Demo Data

- **Fresh installations:** Can optionally create demo user and projects
- **Production use:** Skip demo data
- **Testing:** Use demo data to explore features

## Migration Guide

### Upgrading from pre-v1.0

**Automatic migration:**
- Old database at `./sitr.db` is automatically migrated to `~/.sitr/sitr.db`
- Original file is left intact as backup

**Manual migration:**
```bash
mkdir -p ~/.sitr
cp ./sitr.db ~/.sitr/sitr.db
```

### Upgrading User Management

If you have existing users and want to clean up:

```bash
# List all users
sitr user list

# Archive inactive users (preserves data)
sitr user archive -e old-user@example.com

# View archived users
sitr user list --all

# Restore if needed
sitr user restore -e old-user@example.com
```

## API Changes

### New Endpoints

```
POST   /api/users/{email}/archive              - Archive user
POST   /api/users/{email}/restore              - Restore user  
GET    /api/users/{email}/deletion-impact      - Check deletion impact
DELETE /api/users/{email}?cascade=true         - Delete with cascade
GET    /api/users?include_archived=true        - List with archived
```

### Changed Endpoints

```
GET    /api/users
  - New parameter: include_archived (default: false)

DELETE /api/users/{email}
  - New parameter: cascade (default: false)
  - Without cascade: fails if user has data
  - With cascade: deletes all related data
```

## Command Reference

### User Commands

```bash
sitr user add -f <first> -l <last> -e <email>   # Create user
sitr user list                                    # List active users
sitr user list --all                              # List all users
sitr user select -e <email>                       # Select user
sitr user archive -e <email>                      # Archive user
sitr user restore -e <email>                      # Restore user
sitr user delete -e <email>                       # Delete user (permanent)
sitr user delete -e <email> --force               # Delete without confirm
```

### Installation Commands

```bash
./install.sh                 # Interactive installation
./install.sh --fresh         # Fresh install
./install.sh --update        # Update keeping database
./install.sh --dev           # Development mode
./install.sh --uninstall     # Remove SITR
./install.sh --help          # Show help
```

---

**Last Updated:** October 16, 2025  
**Version:** 1.0.0
