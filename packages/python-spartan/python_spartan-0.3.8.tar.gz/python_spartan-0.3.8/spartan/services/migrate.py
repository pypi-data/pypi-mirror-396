import shutil
from pathlib import Path

from alembic import command


class MigrateService:
    def __init__(self, alembic_cfg):
        self.alembic_cfg = alembic_cfg

    def migrate_initialize(self, db_type: str):
        database_dir = Path.cwd() / "database"
        database_dir.mkdir(exist_ok=True)
        print("Ensured 'database' folder exists in the current directory.")

        db_path = database_dir / "spartan.db"
        if not db_path.exists():
            db_path.touch()
            print("Created 'spartan.db' in the 'database' folder.")
        else:
            print("'spartan.db' already exists in the 'database' folder.")

        destination_path = Path.cwd() / "alembic.ini"

        if destination_path.exists():
            print(
                "alembic.ini already exists in the current directory. Operation aborted to prevent overwriting."
            )
            return

        stub_mapping = {
            "psql": "psql_alembic.stub",
            "mysql": "mysql_alembic.stub",
            "sqlite": "sqlite_alembic.stub",
        }

        stub_file = stub_mapping.get(db_type)
        if not stub_file:
            print(f"Unsupported or unnecessary database type for stub: {db_type}")
            return

        source_path = Path(__file__).parent.parent / "stubs" / "migration" / stub_file

        try:
            shutil.copyfile(source_path, destination_path)
            print("New alembic.ini has been created in the current directory.")
        except Exception as e:
            print(f"Error occurred while copying the file: {e}")

    def migrate_create(self, message=""):
        command.revision(self.alembic_cfg, message=message)
        print("Migration created")

    def migrate_downgrade(self):
        command.downgrade(self.alembic_cfg, "base")
        print("Migration downgraded")

    def migrate_upgrade(self):
        command.upgrade(self.alembic_cfg, "head")
        print("Migration upgraded")

    def migrate_refresh(self):
        command.downgrade(self.alembic_cfg, "base")
        command.upgrade(self.alembic_cfg, "head")
        print("Refresh all tables")
