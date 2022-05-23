class Response(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, success, message=None):
        super().__init__()
        self['success'] = success
        self['message'] = message

    def __repr__(self):
        return f"Response(success={self['success']}, message={self['message']})"


class SuccessResponse(Response):
    def __init__(self, message=None):
        super().__init__(success=True, message=message)


class ErrorResponse(Response):
    def __init__(self, message=None):
        super().__init__(success=False, message=message)


class DataResponse(Response):
    def __init__(self, success, data=None, message=None):
        super().__init__(success=success, message=message)
        self['data'] = data
        if hasattr(data, 'to_json'):
            self['data'] = data.to_json()

    def __repr__(self):
        return f"DataResponse(success={self['success']}, " \
               f"data={self['data'] if len(self['data']) <= 10 else str(self['data'][:10]) + '...'}, message={self['message']})"


class SuccessDataResponse(DataResponse):
    def __init__(self, data=None, message=None):
        super().__init__(
            success=True, data=data, message=message)


class ErrorDataResponse(DataResponse):
    def __init__(self, data=None, message=None):
        super().__init__(
            success=False, data=data, message=message)
