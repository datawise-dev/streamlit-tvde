from utils.base_service import BaseService

class RevenueService(BaseService):
    """
    Service for managing revenue data.
    Inherits common CRUD operations from BaseService.
    """
    table_name = 'revenue'
    primary_key = 'id'
    default_order_by = 'created_at DESC'
