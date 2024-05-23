Here's a markdown file that provides a detailed explanation of setting up and using this FastAPI project with PostgreSQL.

```markdown
# FastAPI Authentication Project

This project uses FastAPI with a PostgreSQL database to provide user signup, login, and landing page functionality. Passwords are securely hashed using `bcrypt`.

## Prerequisites

- Python 3.8 or later
- PostgreSQL Server

## Project Setup

1. **Install Required Python Libraries:**

   Run the following command to install the necessary Python libraries:
    ```bash
   pip install fastapi uvicorn psycopg2-binary bcrypt python-dotenv jinja2
    ```
   or

    ```bash
   pip install -r requirements.txt
    ```

2. **Set Up PostgreSQL Database:**

   - Start by installing PostgreSQL on your local machine. Follow the instructions for your operating system [here](https://www.postgresql.org/download/).
   - Start the PostgreSQL service:
     - **Ubuntu:**
       ```bash
       sudo service postgresql start
       ```
     - **macOS (Homebrew):**
       ```bash
       brew services start postgresql
       ```
     - **Windows:**
       Start via the PostgreSQL service in Control Panel.
   
   - Access the PostgreSQL interactive terminal `psql`:
     ```bash
     psql -U postgres
     ```
   
   - Create a new database user with a secure password and a new database:
     ```sql
     CREATE USER your_username WITH PASSWORD 'your_secure_password';
     GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_username;
     CREATE DATABASE your_database_name;
     ```

3. **Set Up Environment Variables:**

   - Create a `.env` file in the root of the project with the following content:
   ```env
   DATABASE_URL=postgresql://your_username:your_secure_password@localhost:5432/your_database_name
   SECRET_KEY=your_secure_secret_key
   ```

   Make sure to replace the placeholders with your actual database credentials and a secure secret key.

4. **Prepare the FastAPI Project:**

   - Create a project directory with the following structure:
   ```
   fastapi_project/
     ├── main.py
     ├── models.py
     ├── templates/
     │   ├── signup.html
     │   ├── login.html
     │   └── landing.html
     └── .env
   ```
   - Place your Python files in the main directory and your HTML templates in the `templates` directory.

5. **Run the FastAPI Server:**

   Start the FastAPI server with Uvicorn using the command below. Make sure to adjust paths if necessary.
   ```bash
   uvicorn main:app --reload
   ```

6. **Access the Web Application:**

   - Visit `http://127.0.0.1:8000/signup` to sign up for a new account.
   - Use the credentials to log in via `http://127.0.0.1:8000/login`.
   - After successful login, you will be redirected to the landing page.

7. **Logout Functionality:**

   - Click the "Logout" button on the landing page to sign out and return to the login page.

### Notes
- Passwords are securely hashed using `bcrypt`.
- Ensure that the `.env` file is stored securely and never exposed to the public.
- Remember to stop and restart the PostgreSQL service when necessary, especially after system reboots.