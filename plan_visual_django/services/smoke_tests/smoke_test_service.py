import os
import time
from django.db import connections
from django.db.utils import OperationalError
from django.conf import settings
from django.test import Client
from django.urls import reverse

def check_database():
    """Verifies that the database connection is operational."""
    try:
        connection = connections['default']
        start_time = time.time()
        connection.cursor().execute("SELECT 1")
        duration = (time.time() - start_time) * 1000
        return {"status": "PASS", "message": f"Database is reachable ({duration:.2f}ms)"}
    except Exception as e:
        return {"status": "FAIL", "message": f"Database error: {str(e)}"}

def check_static_files():
    """Verifies that key static files exist on disk."""
    # We check for the webpack bundle which is critical for the UI
    bundle_path = os.path.join(settings.BASE_DIR, 'plan_visual_django', 'static', 'dist', 'bundle.js')
    if os.path.exists(bundle_path):
        size_kb = os.path.getsize(bundle_path) / 1024
        return {"status": "PASS", "message": f"Static bundle found ({size_kb:.1f} KB)"}
    else:
        return {"status": "FAIL", "message": f"Critical static bundle missing at {bundle_path}"}

def check_dependencies():
    """Verifies that critical third-party libraries are installed and importable."""
    deps = [
        ('pptx', 'python-pptx'),
        ('openpyxl', 'openpyxl'),
        ('PIL', 'Pillow'),
    ]
    missing = []
    for module_name, pkg_name in deps:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pkg_name)
    
    if not missing:
        return {"status": "PASS", "message": "All critical dependencies are present"}
    else:
        return {"status": "FAIL", "message": f"Missing dependencies: {', '.join(missing)}"}

def check_environment_vars():
    """Verifies that essential environment variables are configured."""
    required = ['SECRET_KEY', 'DJANGO_ENVIRONMENT']
    missing = [var for var in required if not os.getenv(var) and not getattr(settings, var, None)]
    
    # Special check for SECRET_KEY as it might have a dummy value in base_settings
    if getattr(settings, 'SECRET_KEY', None) == 'dummy-secret-key-for-dev' and os.getenv('DJANGO_ENVIRONMENT') == 'production':
        return {"status": "FAIL", "message": "Production detected but using dummy SECRET_KEY"}

    if not missing:
        env = os.getenv('DJANGO_ENVIRONMENT', 'Not Set')
        return {"status": "PASS", "message": f"Environment configured (Env: {env})"}
    else:
        return {"status": "FAIL", "message": f"Missing critical settings: {', '.join(missing)}"}

def check_api_health():
    """Performs a basic internal request to ensure the URL routing and middleware are working."""
    try:
        from django.test.utils import override_settings
        with override_settings(ALLOWED_HOSTS=['testserver']):
            client = Client()
            # Landing page redirect check
            response = client.get('/', follow=True)
            if response.status_code == 200:
                return {"status": "PASS", "message": f"Web server responding (Status: {response.status_code})"}
            else:
                return {"status": "FAIL", "message": f"Web server returned unexpected status: {response.status_code}"}
    except Exception as e:
        return {"status": "FAIL", "message": f"API health check failed: {str(e)}"}

def run_all_smoke_tests():
    """Runs all registered smoke tests and returns a summary."""
    results = {
        "Database": check_database(),
        "Static Files": check_static_files(),
        "Dependencies": check_dependencies(),
        "Environment": check_environment_vars(),
        "API Health": check_api_health(),
    }
    return results
