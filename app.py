from flask import Flask, request, jsonify, render_template
import mysql.connector
import json
from rule_engine import create_rule, combine_rules, evaluate_rule, modify_rule

class Node:
    def __init__(self, type, value=None, left=None, right=None):
        self.type = type
        self.value = value
        self.left = left
        self.right = right

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        node = cls(data['type'], data.get('value'))
        if 'left' in data and data['left']:
            node.left = cls.from_dict(data['left'])
        if 'right' in data and data['right']:
            node.right = cls.from_dict(data['right'])
        return node

app = Flask(__name__)

def get_db_connection():
    conn = mysql.connector.connect(
        database="rule_engine",
        user="root",
        password="password",
        host="localhost"
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_rule', methods=['POST'])
def create_rule_endpoint():
    data = request.json
    rule_string = data.get('rule')
    name = data.get('name')
    description = data.get('description')
    attribute_catalog = data.get('attribute_catalog', [])

    if not attribute_catalog:
        attribute_catalog = None

    try:
        ast = create_rule(rule_string, attribute_catalog)
        conn = get_db_connection()
        cur = conn.cursor()
        
        ast_json = json.dumps(ast, default=lambda o: {
            'type': o.type,
            'value': o.value,
            'left': o.left,
            'right': o.right
        })
        
        cur.execute(
            "INSERT INTO rules (name, description, ast) VALUES (%s, %s, %s)",
            (name, description, ast_json)
        )
        conn.commit()
        rule_id = cur.lastrowid
        
        cur.close()
        conn.close()
        return jsonify({"message": "Rule created successfully", "id": rule_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_endpoint():
    data = request.json
    rule_id = data.get('rule_id')
    user_data = data.get('user_data')

    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT ast FROM rules WHERE id = %s", (rule_id,))
        rule = cur.fetchone()
        cur.close()
        conn.close()

        if not rule:
            return jsonify({"error": "Rule not found"}), 404

        # Parse the JSON string into a dictionary
        ast_dict = json.loads(rule['ast'])
        # Convert the dictionary to a Node object using the from_dict method
        ast = Node.from_dict(ast_dict)

        # Capture debug output
        import io
        import sys
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        result = evaluate_rule(ast, user_data)

        debug_output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        return jsonify({"result": result, "debug_info": debug_output})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/modify_rule', methods=['POST'])
def modify_rule_endpoint():
    data = request.json
    rule_id = data.get('rule_id')
    path = data.get('path')
    new_value = data.get('new_value')

    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT ast FROM rules WHERE id = %s", (rule_id,))
        rule = cur.fetchone()

        if not rule:
            return jsonify({"error": "Rule not found"}), 404

        ast_dict = json.loads(rule['ast'])
        ast = Node.from_dict(ast_dict)
        modified_ast = modify_rule(ast, path, new_value)

        modified_ast_json = json.dumps(modified_ast, default=lambda o: {
            'type': o.type,
            'value': o.value,
            'left': o.left,
            'right': o.right
        })

        cur.execute(
            "UPDATE rules SET ast = %s WHERE id = %s",
            (modified_ast_json, rule_id)
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Rule modified successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)