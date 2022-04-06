from .results import ErrorResult, SuccessResult
from . import messages


def luhn_checksum(card_number: str) -> bool:
    """ Credit Card Number Validator.

    Args:
        card_number (str): Credit Card Number

    Returns:
        Result: Success if valid else Error
    """
    def digits_of(n: "str | int"):
        if not isinstance(n, str):
            n = str(n)
        return [int(i) for i in n]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)

    for j in even_digits:
        checksum += sum(digits_of(j * 2))
    if checksum % 10:
        return ErrorResult(message=messages.INVALID_CARD_NUMBER)
    return SuccessResult()


def check_card(card_data):
    """ Check if card info has all fields filled.

    Args:
        card_data (dict): Card informations

    Returns:
        Result: Success if valid else Error 
    """
    requirements = ["cardNumber", "expireYear",
                    "expireMonth", "cvc", "cardHolderName"]

    for requirement in requirements:
        if not requirement in card_data:
            return ErrorResult(message=messages.INVALID_PAYMENT_CARD)
    return luhn_checksum(card_data.get('cardNumber'))


def check_identity(data):
    """ Check identity number of the buyer.

    Args:
        data (dict): Buyer informations

    Returns:
        Result: Success if valid else Error 
    """
    if not 'identityNumber' in data:
        return ErrorResult(message=messages.INVALID_IDENTITY_NUMBER)
    return SuccessResult()


def check_product(data):
    """ Check if any products exist in data.

    Args:
        data (dict): Buyer informations

    Returns:
        Result: Success if valid else Error 
    """
    if not 'product' in data:
        return ErrorResult(message=messages.INVALID_PRODUCT_NUMBER)
    return SuccessResult()


def check_user_address(user_meta):
    """ Check if user's meta data is valid.

    Args:
        user_meta (UserMeta): User's meta data

    Returns:
        Result: Success if valid else Error 
    """
    keys = ('city', 'country', 'details')
    if user_meta.address is None:
        return ErrorResult(message=messages.INVALID_ADDRESS)
    if any([i for i in keys if i not in user_meta.address]):
        return ErrorResult(message=messages.MISSING_ADDRESS_DETAIL)
    return SuccessResult()


def check_lat_long_addr(user_meta):
    """ Checks lat, long and general address.

    Args:
        user_meta (UserMeta): User's meta data

    Returns:
        Result: Success if valid else Error 
    """
    result = check_user_address(user_meta)
    if any([i for i in ('lat', 'long') if i not in user_meta.address]):
        return result if not result.success else ErrorResult(message=messages.MISSING_ADDRESS_DETAIL)
    return result if not result.success else SuccessResult()


def check_credits(user_meta):
    """ Check if is dog sitter and user credits more than 0

    Args:
        user_meta (UserMeta): User's meta data

    Returns:
        Result: Success if valid else Error 
    """
    if user_meta.user_status == "dog_sitter" and user_meta.credit_amount <= 0:
        return ErrorResult(message=messages.INSUFFICIENT_CREDITS)
    return SuccessResult()


def check_job_owner(user, job):
    """ Check if user is owner of job

    Args:
        user (User): User data

    Returns:
        Result: Success if valid else Error 
    """
    if user == job.owner:
        return ErrorResult(message=messages.YOU_ARE_JOB_OWNER)
    return SuccessResult()


def run_checks(*logics):
    """ Checks if any faulty logic exists. 

    Returns:
        Result | None: ErrorResult if any faulty logics else None 
    """
    for logic in logics:
        if not logic.get('success'):
            return logic
