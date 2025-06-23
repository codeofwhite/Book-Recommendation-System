from app import create_app, db
from app.models import User # Import User model for shell context

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

if __name__ == '__main__':
    app.run(debug=True, port=5001) # Use a different port than default Flask (5000)