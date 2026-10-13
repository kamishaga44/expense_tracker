# Expense Tracker

A simple personal expense tracking web application built with Python and Flask.

## Features

- Add expenses with a title, amount, category, and date
- View all recorded expenses
- Edit and delete expenses
- Calculate the total amount of expenses automatically
- Filter expenses by date range
- Visualize expenses by category with a bar chart
- Validate user input
- Protect forms against CSRF attacks
- Store expense data in an SQLite database
- Run automated tests with pytest

## Technologies

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Flask-WTF
- HTML
- CSS
- pytest
- python-dotenv

## Installation

1. Clone this repository:

   ```bash
git clone https://github.com/kamishaga44/expense_tracker.git
cd expense_tracker
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

3. Activate the environment:

   ```bash
   source .venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the application:

   ```bash
   python app.py
   ```

6. Open http://127.0.0.1:5000 in your browser.

## Running Tests

Run the automated test suite:

```bash
pytest -v
```

The test suite covers the main application features, input validation, date filtering, and error handling.

## Project Structure

```text
expense_tracker/
├── app.py
├── test_app.py
├── requirements.txt
├── templates/
│   ├── index.html
│   └── edit_expense.html
└── static/
    └── style.css
```

## Database

Expense records are stored locally in an SQLite database.

## Security Notes

The application loads its secret key from the `SECRET_KEY` environment variable. For local development, create a `.env` file with your own secret key. The `.env` file is excluded from Git.

For deployment, configure `SECRET_KEY` separately on the hosting platform. Never commit secret keys to the repository.

## Testing

All 11 automated tests passed during local testing.

## Author

Personal portfolio project.