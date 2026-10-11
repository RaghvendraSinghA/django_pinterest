from django.apps import AppConfig


class AccountAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "account_app"

    def ready(self):
        import account_app.signals


# What is AppConfig?
# Django needs information about each application.
# For example:
# account_app
#     ↓
# Where is this app?
# What should its name be?
# What default primary key should models use?
# Does the app have startup configuration?

# AppConfig provides a place to tell Django these things.


# INSTALLED_APPS = [
#     ...
#     'account_app',
# ]
