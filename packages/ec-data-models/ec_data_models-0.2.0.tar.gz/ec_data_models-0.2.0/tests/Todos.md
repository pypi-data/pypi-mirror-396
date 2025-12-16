- Proof of concept tests
- Refactor test helper functions like setting up a tmp test DB and loading environment variables into common file
- Good opportunity to learn / use fancy pytest features, test coverage reporting with badges etc (of course thats overengineering)

## Test to implement

- Simple CRUD for each table; can be vibe coded after robust initial setup
- Integration test with alembic, migrating test DB from scratch
- Test that are intendet to fail, e.g. because they violate some integrity constraints
- Test simple on cascade and on update logic
