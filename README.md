# Rule Engine

A flexible rule engine implementation with a Flask backend and MySQL database.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rule-engine.git
cd rule-engine
```

2. Install the required Python packages:
```bash
pip install flask mysql-connector
```

3. Set up the MySQL database:
```sql
CREATE DATABASE rule_engine;
USE rule_engine;

CREATE TABLE rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    ast JSON
);
```

4. Configure the database connection:
   - Update the database connection settings in `app.py` if necessary

## Running the Application

Start the Flask application:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/create_rule` | POST | Create a new rule |
| `/evaluate_rule` | POST | Evaluate a rule against user data |
| `/modify_rule` | POST | Modify an existing rule |

## Usage

### API Interaction
You can interact with the API using:
- REST clients like Postman
- The provided web interface in `index.html`

### Frontend Usage
1. Open `index.html` in your web browser
2. Use the provided forms to:
   - Create new rules
   - Evaluate rules against data
   - Modify existing rules
