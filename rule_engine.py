import re
from typing import List, Dict, Any

class Node:
    def __init__(self, type, value=None, left=None, right=None):
        self.type = type
        self.value = value
        self.left = left
        self.right = right

def create_rule(rule_string: str, attribute_catalog: List[str] = None) -> Node:
    tokens = tokenize(rule_string)
    validate_rule(tokens, attribute_catalog)
    return parse_expression(tokens)

def combine_rules(rules: List[str]) -> Node:
    if not rules:
        return None
    if len(rules) == 1:
        return create_rule(rules[0])
    
    # Combine rules with OR operator
    combined = Node("operator", "OR")
    combined.left = create_rule(rules[0])
    combined.right = combine_rules(rules[1:])
    return combined

def evaluate_rule(root: Node, data: Dict[str, Any]) -> bool:
    if root.type == "operand":
        result = evaluate_condition(root.value, data)
        print(f"Evaluating condition: {root.value} -> {result}")  # Debug print
        return result
    elif root.type == "operator":
        if root.value == "AND":
            left_result = evaluate_rule(root.left, data)
            right_result = evaluate_rule(root.right, data)
            print(f"AND operation: {left_result} AND {right_result}")  # Debug print
            return left_result and right_result
        elif root.value == "OR":
            left_result = evaluate_rule(root.left, data)
            right_result = evaluate_rule(root.right, data)
            print(f"OR operation: {left_result} OR {right_result}")  # Debug print
            return left_result or right_result
    return False

def tokenize(rule_string: str) -> List[str]:
    return re.findall(r'\(|\)|AND|OR|[^()\s]+', rule_string)

def parse_expression(tokens: List[str]) -> Node:
    if not tokens:
        return None
    
    if tokens[0] == '(':
        count = 1
        for i, token in enumerate(tokens[1:], 1):
            if token == '(':
                count += 1
            elif token == ')':
                count -= 1
            if count == 0:
                break
        
        left = parse_expression(tokens[1:i])
        if i + 1 < len(tokens) and tokens[i+1] in ['AND', 'OR']:
            node = Node("operator", tokens[i+1])
            node.left = left
            node.right = parse_expression(tokens[i+2:])
            return node
        return left
    
    if 'AND' in tokens:
        i = tokens.index('AND')
        node = Node("operator", "AND")
        node.left = parse_expression(tokens[:i])
        node.right = parse_expression(tokens[i+1:])
        return node
    
    if 'OR' in tokens:
        i = tokens.index('OR')
        node = Node("operator", "OR")
        node.left = parse_expression(tokens[:i])
        node.right = parse_expression(tokens[i+1:])
        return node
    
    # Single condition
    return Node("operand", ' '.join(tokens))

def evaluate_condition(condition: str, data: Dict[str, Any]) -> bool:
    print(f"Evaluating condition: {condition}")  # Debug print
    print(f"Data: {data}")  # Debug print
    parts = condition.split()
    if len(parts) != 3:
        raise ValueError(f"Invalid condition: {condition}")
    
    attr, op, value = parts
    if attr not in data:
        print(f"Attribute {attr} not found in data")  # Debug print
        return False
    
    if op == '=':
        result = str(data[attr]) == value.strip("'")  # Remove quotes from string values
    elif op == '>':
        result = float(data[attr]) > float(value)
    elif op == '<':
        result = float(data[attr]) < float(value)
    else:
        raise ValueError(f"Unsupported operator: {op}")
    
    print(f"Condition result: {result}")  # Debug print
    return result

def validate_rule(tokens: List[str], attribute_catalog: List[str] = None) -> bool:
    parentheses_count = 0
    expect_attribute = True
    expect_operator = False
    expect_value = False

    for token in tokens:
        if token == '(':
            parentheses_count += 1
            expect_attribute = True
        elif token == ')':
            parentheses_count -= 1
            expect_attribute = False
        elif token in ['AND', 'OR']:
            expect_attribute = True
            expect_operator = False
            expect_value = False
        elif token in ['=', '>', '<']:
            if not expect_operator:
                raise ValueError(f"Unexpected operator: {token}")
            expect_operator = False
            expect_value = True
        else:
            if expect_attribute:
                if attribute_catalog and token not in attribute_catalog:
                    raise ValueError(f"Invalid attribute: {token}")
                expect_attribute = False
                expect_operator = True
            elif expect_value:
                expect_value = False
                expect_attribute = False
            else:
                raise ValueError(f"Unexpected token: {token}")

    if parentheses_count != 0:
        raise ValueError("Unbalanced parentheses in the rule")
    
    return True

def modify_rule(root: Node, path: List[str], new_value: str) -> Node:
    if not path:
        return Node("operand", new_value)
    
    current = root
    for i, direction in enumerate(path[:-1]):
        if direction == 'left':
            current = current.left
        elif direction == 'right':
            current = current.right
        else:
            raise ValueError(f"Invalid path direction: {direction}")
    
    if path[-1] == 'left':
        current.left = Node("operand", new_value)
    elif path[-1] == 'right':
        current.right = Node("operand", new_value)
    else:
        raise ValueError(f"Invalid path direction: {path[-1]}")
    
    return root