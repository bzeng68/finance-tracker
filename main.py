from transaction_manager import TransactionManager
from categories_utils import CategoriesUtils
from tracker_view import TrackerView

def main():
    transaction_manager = TransactionManager()
    categories_utils = CategoriesUtils()
    tracker_view = TrackerView(transaction_manager, categories_utils)
    
    tracker_view.handle_file_upload()
    if transaction_manager.has_transactions():
        tracker_view.show_separated_tabs()
    
main()