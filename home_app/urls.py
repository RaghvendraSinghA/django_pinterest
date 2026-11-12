from django.urls import path
from . import views
from . import tests

urlpatterns = [
    path("", views.home, name="home"),
    # views.home is a function from home_app views.py
    ]


urlpatterns += [
    # ...your existing routes...
    path('test-400/', tests.test_400),
    path('test-403/', tests.test_403),
    path('test-500/', tests.test_500),
]