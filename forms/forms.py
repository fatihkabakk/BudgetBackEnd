from json import loads


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
        """ Uses an exceptional case for boolean values. """
        for i in self.fields:
            data = self.data.get(i)
            setattr(self, i, loads(data)) if data in (
                'false', 'true') else setattr(self, i, data)


class RegisterForm(Form):
    fields = ('username', 'password')


class LoginForm(RegisterForm):
    fields = (*RegisterForm.fields, 'rememberMe')
