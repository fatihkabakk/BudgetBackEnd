class Result(dict):
    def __init__(self, success, message=None):
        super().__init__()
        self['success'] = success
        self['message'] = message

    def __repr__(self):
        return f"Result(success={self['success']}, message={self['message']})"


class SuccessResult(Result):
    def __init__(self, message=None):
        super(SuccessResult, self).__init__(success=True, message=message)


class ErrorResult(Result):
    def __init__(self, message=None):
        super(ErrorResult, self).__init__(success=False, message=message)


class DataResult(Result):
    def __init__(self, success, data=None, message=None):
        super(DataResult, self).__init__(success=success, message=message)
        self['data'] = data

    def __repr__(self):
        return f"DataResult(success={self['success']}, " \
               f"data={self['data'] if len(self['data']) <= 10 else str(self['data'][:10]) + '...'}, message={self['message']})"


class SuccessDataResult(DataResult):
    def __init__(self, data=None, message=None):
        super(SuccessDataResult, self).__init__(
            success=True, data=data, message=message)


class ErrorDataResult(DataResult):
    def __init__(self, data=None, message=None):
        super(ErrorDataResult, self).__init__(
            success=False, data=data, message=message)
