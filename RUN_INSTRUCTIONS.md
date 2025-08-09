# How to Run the Application

### 1. Set Up the Virtual Environment
First, create and activate a virtual environment. This will keep your project dependencies isolated.
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
**With the virtual environment activated**, install all the necessary packages by running:
```bash
pip install -r attendance_app/requirements.txt
```

### 3. Reset the Database
Since the database schema has changed, you need to delete the old database file to apply the updates.
```bash
rm attendance_app/instance/attendance.db
```
Next, create the database tables:
```bash
python attendance_app/scripts/create_tables.py
```

### 4. Create the Admin User
After creating the database, create the initial admin user by running:
```bash
python attendance_app/create_admin.py
```
The default credentials are:
- **Username:** admin
- **Password:** admin123

### 5. Run the Application

Finally, you can run the application in development mode (from the project root):
```bash
python -m attendance_app.app
```
The application will be available at `http://127.0.0.1:5000`.

### Running in Production
For a production environment, it is recommended to use a WSGI server like Gunicorn.

1.  **Set the environment to production:**
    ```bash
    export FLASK_ENV=production
    ```

2.  **Run with Gunicorn:**
    ```bash
    gunicorn -w 4 "attendance_app.app:app"