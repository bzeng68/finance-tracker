import json
import os

class BudgetManager:
    def __init__(self, storage_dir="budgets"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def save_budget(self, name, budget):
        filename = os.path.join(self.storage_dir, f"{name}.json")
        
        problems_with_budget = self.validate_budget(name, budget)

        if problems_with_budget:
            with open(filename, "w") as f:
                json.dump(budget, f, indent=2)
        return problems_with_budget
            
    def validate_budget(self, name, budget):
        problems = []

        if not name:
            problems.append("Budget name cannot be empty.")

        for i, (key, value) in enumerate(budget.items()):
            actual_index = i + 1
            if not key:
                problems.append(f"Category {actual_index} cannot be empty.")
            
            if not value:
                problems.append(f"Value {actual_index} cannot be empty.")
            else:  
                try:
                    float_value = float(value)
                    if float_value < 0:
                        problems.append(f"Value {actual_index} must be a non-negative.")
                except Exception:
                    problems.append(f"Value {actual_index} must be a number.")

        if len(budget) != len(set(budget.keys())):
            problems.append("Duplicate category names are not allowed.")

        return problems

    def load_budget(self, name):
        filename = os.path.join(self.storage_dir, f"{name}.json")
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return json.load(f)
        return None

    def list_budgets(self):
        return [f.replace(".json", "") for f in os.listdir(self.storage_dir)]