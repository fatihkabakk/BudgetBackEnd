from .responses import ErrorResponse, SuccessResponse
from . import messages


def run_checks(*logics):
    """ Checks if any faulty logic exists. 

    Returns:
        Response | None: ErrorResponse if any faulty logics else None 
    """
    for logic in logics:
        if not logic.get('success'):
            return logic
