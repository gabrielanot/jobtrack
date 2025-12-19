from app import Base, engine  # adjust import based on your codebase

def setup_module(module):
    Base.metadata.create_all(bind=engine)  # creates tables