from django.core.exceptions import PermissionDenied, SuspiciousOperation

def test_400(request):
    raise SuspiciousOperation("Test 400")

def test_403(request):
    raise PermissionDenied("Test 403")

def test_500(request):
    raise Exception("Test 500")