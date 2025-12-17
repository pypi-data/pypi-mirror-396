"""
PyX Testing Utilities
Helpers for testing PyX applications with pytest.
"""
from typing import Optional, Dict, Any
import json


class TestClient:
    """
    Test client for PyX applications.
    
    Usage:
        from pyx.testing import TestClient
        from main import app
        
        def test_homepage():
            client = TestClient(app)
            response = client.get("/")
            assert response.status_code == 200
            assert "Welcome" in response.text
        
        def test_login():
            client = TestClient(app)
            response = client.post("/login", data={
                "email": "test@example.com",
                "password": "password123"
            })
            assert response.status_code == 200
    """
    
    def __init__(self, app):
        """
        Initialize test client.
        
        Args:
            app: PyX App instance
        """
        self.app = app
        self._client = None
        self._setup_client()
    
    def _setup_client(self):
        """Setup FastAPI TestClient"""
        try:
            from fastapi.testclient import TestClient as FastAPITestClient
            self._client = FastAPITestClient(self.app.api)
        except ImportError:
            raise ImportError("Please install 'httpx' for testing: pip install httpx")
    
    def get(self, path: str, **kwargs) -> "TestResponse":
        """Send GET request"""
        response = self._client.get(path, **kwargs)
        return TestResponse(response)
    
    def post(self, path: str, data: Dict = None, json_data: Dict = None, **kwargs) -> "TestResponse":
        """Send POST request"""
        if data:
            response = self._client.post(path, data=data, **kwargs)
        elif json_data:
            response = self._client.post(path, json=json_data, **kwargs)
        else:
            response = self._client.post(path, **kwargs)
        return TestResponse(response)
    
    def put(self, path: str, data: Dict = None, json_data: Dict = None, **kwargs) -> "TestResponse":
        """Send PUT request"""
        if data:
            response = self._client.put(path, data=data, **kwargs)
        elif json_data:
            response = self._client.put(path, json=json_data, **kwargs)
        else:
            response = self._client.put(path, **kwargs)
        return TestResponse(response)
    
    def delete(self, path: str, **kwargs) -> "TestResponse":
        """Send DELETE request"""
        response = self._client.delete(path, **kwargs)
        return TestResponse(response)
    
    def patch(self, path: str, data: Dict = None, json_data: Dict = None, **kwargs) -> "TestResponse":
        """Send PATCH request"""
        if data:
            response = self._client.patch(path, data=data, **kwargs)
        elif json_data:
            response = self._client.patch(path, json=json_data, **kwargs)
        else:
            response = self._client.patch(path, **kwargs)
        return TestResponse(response)


class TestResponse:
    """Wrapper for test response with convenient assertions"""
    
    def __init__(self, response):
        self._response = response
    
    @property
    def status_code(self) -> int:
        """Get response status code"""
        return self._response.status_code
    
    @property
    def text(self) -> str:
        """Get response body as text"""
        return self._response.text
    
    @property
    def json(self) -> Dict:
        """Get response body as JSON"""
        return self._response.json()
    
    @property
    def headers(self) -> Dict:
        """Get response headers"""
        return dict(self._response.headers)
    
    @property
    def cookies(self) -> Dict:
        """Get response cookies"""
        return dict(self._response.cookies)
    
    def assert_status(self, status_code: int) -> "TestResponse":
        """Assert response status code"""
        assert self.status_code == status_code, \
            f"Expected status {status_code}, got {self.status_code}"
        return self
    
    def assert_ok(self) -> "TestResponse":
        """Assert status is 200"""
        return self.assert_status(200)
    
    def assert_created(self) -> "TestResponse":
        """Assert status is 201"""
        return self.assert_status(201)
    
    def assert_redirect(self) -> "TestResponse":
        """Assert status is 302 or 301"""
        assert self.status_code in [301, 302], \
            f"Expected redirect, got {self.status_code}"
        return self
    
    def assert_not_found(self) -> "TestResponse":
        """Assert status is 404"""
        return self.assert_status(404)
    
    def assert_forbidden(self) -> "TestResponse":
        """Assert status is 403"""
        return self.assert_status(403)
    
    def assert_unauthorized(self) -> "TestResponse":
        """Assert status is 401"""
        return self.assert_status(401)
    
    def assert_contains(self, text: str) -> "TestResponse":
        """Assert response contains text"""
        assert text in self.text, f"Response does not contain '{text}'"
        return self
    
    def assert_not_contains(self, text: str) -> "TestResponse":
        """Assert response does not contain text"""
        assert text not in self.text, f"Response contains '{text}'"
        return self
    
    def assert_json_has(self, key: str) -> "TestResponse":
        """Assert JSON response has key"""
        data = self.json
        assert key in data, f"JSON does not have key '{key}'"
        return self
    
    def assert_json_equals(self, key: str, value: Any) -> "TestResponse":
        """Assert JSON key equals value"""
        data = self.json
        assert key in data, f"JSON does not have key '{key}'"
        assert data[key] == value, f"Expected {key}={value}, got {data[key]}"
        return self


class TestDatabase:
    """
    Test database utilities.
    
    Usage:
        from pyx.testing import TestDatabase
        
        def test_user_creation():
            with TestDatabase() as db:
                user = User(email="test@example.com")
                db.save(user)
                
                found = db.find_by(User, email="test@example.com")
                assert found is not None
            # Database is automatically cleaned up
    """
    
    def __init__(self, url: str = "sqlite:///:memory:"):
        """
        Initialize test database.
        
        Args:
            url: Database URL (default: in-memory SQLite)
        """
        self.url = url
        self._original_engine = None
    
    def __enter__(self):
        from ..data.database import db
        
        # Save original engine
        self._original_engine = db._engine
        
        # Connect to test database
        db.connect(self.url)
        db.init()
        
        return db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        from ..data.database import db
        
        # Restore original engine
        db._engine = self._original_engine


def mock_auth_user(email: str = "test@example.com", role: str = "user"):
    """
    Mock an authenticated user for testing.
    
    Usage:
        from pyx.testing import mock_auth_user
        
        def test_protected_route():
            with mock_auth_user("admin@example.com", "admin"):
                # auth.current_user() will return mocked user
                response = client.get("/admin")
                assert response.status_code == 200
    """
    from ..lib.auth import auth, User
    
    class MockAuthContext:
        def __init__(self, email: str, role: str):
            self.email = email
            self.role = role
            self._original_user = None
        
        def __enter__(self):
            self._original_user = auth._current_user
            
            # Create mock user
            mock_user = User(
                id=1,
                email=self.email,
                full_name="Test User",
                role=self.role,
                is_active=True
            )
            mock_user.password_hash = ""
            
            auth._current_user = mock_user
            return mock_user
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            auth._current_user = self._original_user
    
    return MockAuthContext(email, role)


# Assertion helpers
def assert_validation_fails(data: Dict, rules: Dict, expected_fields: list = None):
    """
    Assert that validation fails for given data.
    
    Usage:
        assert_validation_fails(
            {"email": "invalid"},
            {"email": ["required", "email"]},
            expected_fields=["email"]
        )
    """
    from ..lib.validation import validate
    
    errors = validate(data, rules)
    assert len(errors) > 0, "Validation should have failed but passed"
    
    if expected_fields:
        for field in expected_fields:
            assert field in errors, f"Expected validation error for '{field}'"


def assert_validation_passes(data: Dict, rules: Dict):
    """
    Assert that validation passes for given data.
    
    Usage:
        assert_validation_passes(
            {"email": "valid@example.com"},
            {"email": ["required", "email"]}
        )
    """
    from ..lib.validation import validate
    
    errors = validate(data, rules)
    assert len(errors) == 0, f"Validation should have passed but failed: {errors}"


class ZenTest:
    """
    Zen Mode Testing - Access all testing utilities via test.*
    
    Usage:
        from pyx import test
        
        # Create test client
        client = test.client(app)
        response = client.get("/")
        response.assert_ok()
        
        # Test database
        with test.database() as db:
            user = User(name="Test")
            db.save(user)
            assert db.exists(User, name="Test")
        
        # Mock auth
        with test.mock_user("admin@test.com", "admin"):
            response = client.get("/admin")
            response.assert_ok()
        
        # Run tests
        test.run()
        test.run("tests/test_users.py")
    """
    
    # Re-export classes
    Client = TestClient
    Response = TestResponse
    Database = TestDatabase
    
    @staticmethod
    def client(app) -> TestClient:
        """Create test client for app"""
        return TestClient(app)
    
    @staticmethod
    def database(url: str = "sqlite:///:memory:") -> TestDatabase:
        """Create test database context"""
        return TestDatabase(url)
    
    @staticmethod
    def mock_user(email: str = "test@example.com", role: str = "user"):
        """Mock authenticated user"""
        return mock_auth_user(email, role)
    
    @staticmethod
    def assert_valid(data: Dict, rules: Dict):
        """Assert data passes validation"""
        assert_validation_passes(data, rules)
    
    @staticmethod
    def assert_invalid(data: Dict, rules: Dict, expected_fields: list = None):
        """Assert data fails validation"""
        assert_validation_fails(data, rules, expected_fields)
    
    @staticmethod
    def run(path: str = "tests", verbose: bool = True, coverage: bool = False):
        """
        Run tests using pytest.
        
        Usage:
            test.run()                    # Run all tests in tests/
            test.run("tests/test_api.py") # Run specific file
            test.run(coverage=True)       # With coverage report
        """
        import subprocess
        import sys
        
        cmd = [sys.executable, "-m", "pytest", path]
        
        if verbose:
            cmd.append("-v")
        
        if coverage:
            cmd.extend(["--cov=.", "--cov-report=html"])
        
        result = subprocess.run(cmd)
        return result.returncode == 0
    
    @staticmethod
    def case(func):
        """
        Decorator to mark a function as a test case.
        
        Usage:
            @test.case
            def test_user_creation():
                user = User(name="John")
                assert user.name == "John"
        """
        # Simply return the function, pytest will discover it
        # by the test_ prefix
        func.__test__ = True
        return func
    
    @staticmethod  
    def fixture(func):
        """
        Decorator to create a test fixture.
        
        Usage:
            @test.fixture
            def sample_user():
                return User(name="Test", email="test@test.com")
        """
        import pytest
        return pytest.fixture(func)
    
    @staticmethod
    def parametrize(params: list):
        """
        Decorator for parameterized tests.
        
        Usage:
            @test.parametrize([
                ("test@example.com", True),
                ("invalid-email", False),
            ])
            def test_email_validation(email, expected):
                result = validate_email(email)
                assert result == expected
        """
        import pytest
        # Extract parameter names from first item
        if params and isinstance(params[0], (list, tuple)):
            num_params = len(params[0])
            if num_params == 2:
                return pytest.mark.parametrize("input,expected", params)
            elif num_params == 3:
                return pytest.mark.parametrize("a,b,expected", params)
        return pytest.mark.parametrize("data", params)
    
    @staticmethod
    def skip(reason: str = ""):
        """Skip a test"""
        import pytest
        return pytest.mark.skip(reason=reason)
    
    @staticmethod
    def xfail(reason: str = ""):
        """Mark test as expected to fail"""
        import pytest
        return pytest.mark.xfail(reason=reason)
    
    @staticmethod
    def describe(description: str):
        """
        Describe a group of tests (for documentation).
        
        Usage:
            @test.describe("User Authentication")
            class TestUserAuth:
                def test_login(self):
                    pass
        """
        def decorator(cls):
            cls.__doc__ = description
            return cls
        return decorator


# Zen Mode instance
test = ZenTest()

