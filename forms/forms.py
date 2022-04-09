class Form:
    def __init__(self, json_data=None, **kwargs) -> None:
        self.data = json_data or kwargs

    def validate(self):
        for field in self.fields:
            if not field in self.data:
                return False
        self.set_attributes()
        return True

    def set_attributes(self):
        for i in self.fields:
            setattr(self, i, self.data.get(i))


class RegisterForm(Form):
    fields = ('username', 'password')


class LoginForm(RegisterForm):
    fields = (*RegisterForm.fields, 'rememberMe')
