from django.urls import path
from . import views

urlpatterns = [
    path('linked_test_cases', views.issue_linked_test_cases, name='issue_linked_test_cases')
]
