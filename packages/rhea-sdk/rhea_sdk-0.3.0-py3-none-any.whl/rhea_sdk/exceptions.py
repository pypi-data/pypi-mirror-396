class AccountInitializationError(Exception):
    pass

class AccountHasNoTokensError(Exception):
    pass

class AccountHasNoStateError(Exception):
    pass

class EmptyStorageBalance(Exception):
    pass

class TransactionError(Exception):
    pass

class TransactionReceiptError(Exception):
    pass

class PoolFeeError(Exception):
    pass