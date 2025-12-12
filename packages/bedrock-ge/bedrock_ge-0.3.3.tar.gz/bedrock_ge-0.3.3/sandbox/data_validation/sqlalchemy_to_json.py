import json

from sqlalchemy import Column, Integer, MetaData, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {"id": self.id, "name": self.name, "email": self.email}


def get_schema_json(metadata):
    """Convert SQLAlchemy MetaData object to JSON serializable format."""
    schema = {}
    for table in metadata.tables.values():
        schema[table.name] = {
            "columns": [
                {
                    "name": column.name,
                    "type": str(column.type),
                    "primary_key": column.primary_key,
                    "nullable": column.nullable,
                    "default": str(column.default) if column.default else None,
                }
                for column in table.columns
            ],
            "foreign_keys": [
                {
                    "column": fk.column.name,
                    "ref_table": fk.column.table.name,
                    "ref_column": fk.column.name,
                }
                for fk in table.foreign_keys
            ],
        }
    return schema


# Setup database
engine = create_engine("sqlite:///example.db")
metadata = MetaData()
metadata.reflect(bind=engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Add sample data (optional)
session.add(User(name="Alice", email="alice@example.com"))
session.add(User(name="Bob", email="bob@example.com"))
session.commit()

# Query the User table
users = session.query(User).all()

# Convert each user to a dictionary and then to JSON
users_json = json.dumps([user.to_dict() for user in users], indent=4)

print(users_json)


# Get the schema as a JSON-serializable dictionary
schema_dict = get_schema_json(metadata)

# Convert to JSON
schema_json = json.dumps(schema_dict, indent=4)

# Output the schema
print(schema_json)
