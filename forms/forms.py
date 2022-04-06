import json


class Form:
    def __init__(self, json_data=None, **kwargs) -> None:
        if json_data:
            self.data = json.loads(json_data)
        if kwargs:
            self.data = kwargs

    def validate(self):
        for field in self.fields:
            if not field in self.data:
                return False
        return True


class LoginForm(Form):
    fields = ('username', 'password')


class RegisterForm(LoginForm):
    pass
