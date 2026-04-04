import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db.database import engine
from db.models import Base

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
