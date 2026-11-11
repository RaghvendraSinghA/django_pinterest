from django.apps import AppConfig


class AccountAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "account_app"

    


# name = "account_app" tells path of application package to whom this config belongs, sometimes application package and config file can belong to different folders/packages.

# The config class is just a Python class. It doesn’t automatically know which package it describes. name is the link between the class and the package.

# A package can define more than one config class (for example, a default one and a variant with different settings). name is the same for both, and INSTALLED_APPS picks which class to use.

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
