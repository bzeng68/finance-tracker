from categories_utils import CategoriesUtils
from transaction_manager import TransactionManager
from budget_manager import BudgetManager
from tracker_view import TrackerView

def main():
    categories_utils = CategoriesUtils()
    budget_manager = BudgetManager()
    transaction_manager = TransactionManager(categories_utils.get_categories())
    tracker_view = TrackerView(transaction_manager, categories_utils, budget_manager)
    
    tracker_view.handle_file_upload()
    if transaction_manager.has_transactions():
        tracker_view.show_separated_tabs()
    
main()