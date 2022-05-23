from json import loads
from core.validation import ErrorResponse, SuccessResponse, run_checks


class Form:
    def __init__(self, json_data=None, **kwargs) -> None:
        self.data = json_data or kwargs

    def validate(self):
        print(self.fields, self.data)
        for field in self.fields:
            if not field in self.data:
                return False
        self.set_attributes()
        return True

    def set_attributes(self):
        """ Embeds attributes to the object. 
        ! Note: Uses an exceptional case for boolean values.
        """
        for i in self.fields:
            data = self.data.get(i)
            setattr(self, i, loads(data)) if data in (
                'false', 'true') else setattr(self, i, data)


class RegisterForm(Form):
    fields = ('username', 'password')

    def validate(self):
        result = super().validate()
        validation = run_checks(check_username(self.username), check_password(self.password))
        if not result or validation: return False
        return True


class LoginForm(RegisterForm):
    fields = (*RegisterForm.fields, 'rememberMe')


def check_username(username):
    if len(username) >= 2:
        return SuccessResponse()
    return ErrorResponse('Username must be at least 2 characters.')


def check_password(password):
    if len(password) >= 6:
        return SuccessResponse()
    return ErrorResponse('Password must be at least 6 characters.')