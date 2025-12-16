"""Akron CLI for schema management and migrations."""
import argparse
import sys
import json
import os
from akron import Akron
from akron.migrations import MigrationManager
from akron.schema import SchemaManager, AkronSchema, create_default_schema


def create_parser():
    """Create the argument parser with subcommands."""
    parser = argparse.ArgumentParser(description="Akron ORM CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Legacy commands (for backward compatibility)
    legacy_parser = subparsers.add_parser("legacy", help="Legacy command format")
    legacy_parser.add_argument("action", choices=[
        "makemigrations", "migrate", "showmigrations",
        "create-table", "drop-table", "inspect-schema", "seed", "raw-sql"
    ], help="Action")
    legacy_parser.add_argument("table", nargs="?", help="Table name (if applicable)")
    legacy_parser.add_argument("--db", required=True, help="Database URL")
    legacy_parser.add_argument("--schema", help="Schema as JSON string")
    legacy_parser.add_argument("--data", help="Seed data as JSON string")
    legacy_parser.add_argument("--sql", help="Raw SQL to execute")
    
    # New db commands (Prisma-like)
    db_parser = subparsers.add_parser("db", help="Database schema management")
    db_subparsers = db_parser.add_subparsers(dest="db_action", help="Database actions")
    
    # db init
    init_parser = db_subparsers.add_parser("init", help="Initialize a new Akron project")
    init_parser.add_argument("--provider", choices=["sqlite", "mysql", "postgresql", "mongodb"], 
                           default="sqlite", help="Database provider")
    init_parser.add_argument("--url", help="Database URL")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing akron.json")
    
    # db makemigrations
    makemigrations_parser = db_subparsers.add_parser("makemigrations", 
                                                   help="Generate migrations from schema changes")
    makemigrations_parser.add_argument("--name", help="Migration name")
    
    # db migrate
    migrate_parser = db_subparsers.add_parser("migrate", help="Apply pending migrations")
    migrate_parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated")
    
    # db status
    status_parser = db_subparsers.add_parser("status", help="Show migration status")
    
    # db reset
    reset_parser = db_subparsers.add_parser("reset", help="Reset database and apply all migrations")
    reset_parser.add_argument("--force", action="store_true", help="Don't ask for confirmation")
    
    return parser


def handle_db_init(args):
    """Handle 'akron db init' command."""
    if os.path.exists("akron.json") and not args.force:
        print("❌ akron.json already exists. Use --force to overwrite.")
        return
    
    # Determine database URL
    if args.url:
        database_url = args.url
    else:
        if args.provider == "sqlite":
            database_url = "sqlite://app.db"
        elif args.provider == "mysql":
            database_url = "mysql://user:password@localhost:3306/database"
        elif args.provider == "postgresql":
            database_url = "postgres://user:password@localhost:5432/database"
        elif args.provider == "mongodb":
            database_url = "mongodb://localhost:27017/database"
    
    # Create default schema
    schema_dict = create_default_schema(args.provider, database_url)
    
    # Save to akron.json
    with open("akron.json", "w") as f:
        json.dump(schema_dict, f, indent=2)
    
    # Create .akron directory
    os.makedirs(".akron", exist_ok=True)
    
    print("✅ Initialized Akron project")
    print(f"   Provider: {args.provider}")
    print(f"   Database: {database_url}")
    print("   Schema file: akron.json")
    print("\n📝 Next steps:")
    print("   1. Edit akron.json to define your schema")
    print("   2. Run 'akron db makemigrations' to generate migrations")
    print("   3. Run 'akron db migrate' to apply migrations")


def handle_db_makemigrations(args):
    """Handle 'akron db makemigrations' command."""
    if not os.path.exists("akron.json"):
        print("❌ No akron.json found. Run 'akron db init' first.")
        return
    
    schema_manager = SchemaManager()
    
    if not schema_manager.has_schema_changed():
        print("✅ No changes detected in schema.")
        return
    
    # Load current schema
    try:
        current_schema = schema_manager.load_schema()
    except Exception as e:
        print(f"❌ Error loading schema: {e}")
        return
    
    # Generate migration steps
    steps = schema_manager.generate_migration_steps()
    
    if not steps:
        print("✅ No changes detected in schema.")
        return
    
    # Create migration file
    migration_name = args.name or f"migration_{len(os.listdir('.akron')) if os.path.exists('.akron') else 0:04d}"
    migration_file = f".akron/{migration_name}.json"
    
    migration_data = {
        "name": migration_name,
        "timestamp": schema_manager._get_timestamp(),
        "steps": steps,
        "checksum": current_schema.get_checksum()
    }
    
    with open(migration_file, "w") as f:
        json.dump(migration_data, f, indent=2)
    
    # Save snapshot
    schema_manager.save_snapshot(current_schema, f"Migration: {migration_name}")
    
    print(f"✅ Generated migration: {migration_name}")
    print(f"   File: {migration_file}")
    print(f"   Steps: {len(steps)}")
    
    # Show preview
    print("\n📋 Migration preview:")
    for i, step in enumerate(steps, 1):
        action = step["action"]
        if action == "create_table":
            print(f"   {i}. Create table '{step['table']}'")
        elif action == "drop_table":
            print(f"   {i}. Drop table '{step['table']}'")
        elif action == "add_column":
            print(f"   {i}. Add column '{step['column']}' to '{step['table']}'")
        elif action == "drop_column":
            print(f"   {i}. Drop column '{step['column']}' from '{step['table']}'")
        elif action == "modify_column":
            print(f"   {i}. Modify column '{step['column']}' in '{step['table']}'")


def handle_db_migrate(args):
    """Handle 'akron db migrate' command."""
    if not os.path.exists("akron.json"):
        print("❌ No akron.json found. Run 'akron db init' first.")
        return
    
    # Load schema to get database connection
    try:
        schema = AkronSchema.from_file("akron.json")
        db = Akron(schema.database.url)
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return
    
    # Find pending migrations
    applied_migrations = get_applied_migrations(db)
    all_migrations = get_all_migrations()
    pending_migrations = [m for m in all_migrations if m not in applied_migrations]
    
    if not pending_migrations:
        print("✅ No pending migrations.")
        return
    
    if args.dry_run:
        print("🔍 Dry run - showing pending migrations:")
        for migration in pending_migrations:
            print(f"   • {migration}")
        return
    
    print(f"📦 Applying {len(pending_migrations)} migration(s)...")
    
    try:
        for migration_file in pending_migrations:
            print(f"   Applying {migration_file}...")
            
            with open(f".akron/{migration_file}") as f:
                migration_data = json.load(f)
            
            # Apply each step
            for step in migration_data["steps"]:
                apply_migration_step(db, step)
            
            # Mark as applied
            mark_migration_applied(db, migration_file, migration_data["checksum"])
            
            print(f"   ✅ Applied {migration_file}")
        
        print("✅ All migrations applied successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        db.close()


def handle_db_status(args):
    """Handle 'akron db status' command."""
    if not os.path.exists("akron.json"):
        print("❌ No akron.json found. Run 'akron db init' first.")
        return
    
    schema_manager = SchemaManager()
    
    # Check if schema has changes
    has_changes = schema_manager.has_schema_changed()
    
    # Get migration info
    try:
        schema = AkronSchema.from_file("akron.json")
        db = Akron(schema.database.url)
        applied_migrations = get_applied_migrations(db)
        all_migrations = get_all_migrations()
        pending_migrations = [m for m in all_migrations if m not in applied_migrations]
        db.close()
    except Exception as e:
        print(f"❌ Error checking migration status: {e}")
        return
    
    print("📊 Akron Status")
    print("=" * 50)
    print(f"Schema file: akron.json")
    print(f"Database: {schema.database.provider}")
    print(f"URL: {schema.database.url}")
    print(f"Tables: {len(schema.tables)}")
    print()
    
    if has_changes:
        print("⚠️  Schema has uncommitted changes")
        print("   Run 'akron db makemigrations' to generate migration")
    else:
        print("✅ Schema is up to date")
    
    print()
    print(f"Applied migrations: {len(applied_migrations)}")
    print(f"Pending migrations: {len(pending_migrations)}")
    
    if pending_migrations:
        print("\n📋 Pending migrations:")
        for migration in pending_migrations:
            print(f"   • {migration}")


def get_applied_migrations(db) -> list:
    """Get list of applied migrations from database."""
    try:
        driver = db.driver
        if hasattr(driver, "conn") and hasattr(driver, "cur"):
            # Create migrations table if it doesn't exist
            driver.cur.execute("""
                CREATE TABLE IF NOT EXISTS _akron_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_name TEXT UNIQUE NOT NULL,
                    checksum TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            driver.conn.commit()
            
            driver.cur.execute("SELECT migration_name FROM _akron_migrations ORDER BY applied_at")
            return [row[0] for row in driver.cur.fetchall()]
        else:
            # MongoDB - use collections
            return []
    except Exception:
        return []


def get_all_migrations() -> list:
    """Get list of all migration files."""
    if not os.path.exists(".akron"):
        return []
    
    migrations = []
    for file in os.listdir(".akron"):
        if file.endswith(".json") and file != "schema_snapshots.json":
            migrations.append(file)
    
    return sorted(migrations)


def apply_migration_step(db, step):
    """Apply a single migration step."""
    action = step["action"]
    
    if action == "create_table":
        db.create_table(step["table"], step["schema"])
    elif action == "drop_table":
        # This would need to be implemented in the drivers
        driver = db.driver
        if hasattr(driver, "conn") and hasattr(driver, "cur"):
            driver.cur.execute(f"DROP TABLE IF EXISTS {step['table']}")
            driver.conn.commit()
    elif action == "add_column":
        # This would need to be implemented in the drivers
        driver = db.driver
        if hasattr(driver, "conn") and hasattr(driver, "cur"):
            sql_type = step["definition"].upper()
            if "->" not in sql_type:  # Not a foreign key
                driver.cur.execute(f"ALTER TABLE {step['table']} ADD COLUMN {step['column']} {sql_type}")
                driver.conn.commit()
    elif action == "drop_column":
        print(f"⚠️  Column drop not fully supported: {step['table']}.{step['column']}")
    elif action == "modify_column":
        print(f"⚠️  Column modification not fully supported: {step['table']}.{step['column']}")


def mark_migration_applied(db, migration_name, checksum):
    """Mark a migration as applied in the database."""
    driver = db.driver
    if hasattr(driver, "conn") and hasattr(driver, "cur"):
        driver.cur.execute(
            "INSERT INTO _akron_migrations (migration_name, checksum) VALUES (?, ?)",
            (migration_name, checksum)
        )
        driver.conn.commit()


def handle_legacy_commands(args):
    """Handle legacy command format for backward compatibility."""
    db = Akron(args.db)
    mgr = MigrationManager(db)
    
    if args.action == "makemigrations":
        if not args.schema:
            print("--schema required for makemigrations")
            sys.exit(1)
        schema = json.loads(args.schema)
        mgr.makemigrations(args.table, schema)
    elif args.action == "migrate":
        mgr.migrate(args.table)
    elif args.action == "showmigrations":
        driver = db.driver
        if hasattr(driver, "conn") and hasattr(driver, "cur"):
            driver.cur.execute("SELECT * FROM _akron_migrations WHERE table_name=?", (args.table,))
            for row in driver.cur.fetchall():
                print(row)
        else:
            print("Migration history not supported for this backend.")
    elif args.action == "create-table":
        if not args.schema:
            print("--schema required for create-table")
            sys.exit(1)
        schema = json.loads(args.schema)
        db.create_table(args.table, schema)
        print(f"Table {args.table} created.")
    elif args.action == "drop-table":
        driver = db.driver
        if hasattr(driver, "conn") and hasattr(driver, "cur"):
            driver.cur.execute(f"DROP TABLE IF EXISTS {args.table}")
            driver.conn.commit()
            print(f"Table {args.table} dropped.")
        elif hasattr(driver, "db"):
            driver.db.drop_collection(args.table)
            print(f"Collection {args.table} dropped.")
    elif args.action == "inspect-schema":
        driver = db.driver
        if hasattr(driver, "conn") and hasattr(driver, "cur"):
            driver.cur.execute(f"PRAGMA table_info({args.table})")
            for row in driver.cur.fetchall():
                print(row)
        elif hasattr(driver, "db"):
            doc = driver.db[args.table].find_one()
            print(doc if doc else "No documents found.")
    elif args.action == "seed":
        if not args.data:
            print("--data required for seed")
            sys.exit(1)
        data = json.loads(args.data)
        db.insert(args.table, data)
        print(f"Seeded data into {args.table}.")
    elif args.action == "raw-sql":
        if not args.sql:
            print("--sql required for raw-sql")
            sys.exit(1)
        driver = db.driver
        if hasattr(driver, "conn") and hasattr(driver, "cur"):
            driver.cur.execute(args.sql)
            if driver.cur.description:
                for row in driver.cur.fetchall():
                    print(row)
            driver.conn.commit()
            print("SQL executed.")
        else:
            print("Raw SQL not supported for this backend.")
    
    db.close()


def main():
    parser = create_parser()
    
    # Handle the case where no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Check for legacy command format (no subcommand)
    if len(sys.argv) > 1 and sys.argv[1] not in ['db', 'legacy', '--help', '-h']:
        # Convert to legacy format
        args = argparse.Namespace()
        args.action = sys.argv[1]
        args.table = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
        
        # Parse remaining arguments
        remaining_args = sys.argv[2:] if args.table is None else sys.argv[3:]
        legacy_parser = argparse.ArgumentParser()
        legacy_parser.add_argument("--db", required=True)
        legacy_parser.add_argument("--schema")
        legacy_parser.add_argument("--data")
        legacy_parser.add_argument("--sql")
        
        try:
            legacy_args = legacy_parser.parse_args(remaining_args)
            args.db = legacy_args.db
            args.schema = legacy_args.schema
            args.data = legacy_args.data
            args.sql = legacy_args.sql
            
            handle_legacy_commands(args)
            return
        except SystemExit:
            parser.print_help()
            return
    
    args = parser.parse_args()
    
    if args.command == "db":
        if args.db_action == "init":
            handle_db_init(args)
        elif args.db_action == "makemigrations":
            handle_db_makemigrations(args)
        elif args.db_action == "migrate":
            handle_db_migrate(args)
        elif args.db_action == "status":
            handle_db_status(args)
        elif args.db_action == "reset":
            print("Reset functionality not yet implemented.")
        else:
            parser.print_help()
    elif args.command == "legacy":
        handle_legacy_commands(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
