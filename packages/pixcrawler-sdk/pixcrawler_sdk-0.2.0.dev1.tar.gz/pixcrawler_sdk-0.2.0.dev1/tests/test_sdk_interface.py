"""
Test the SDK interface matches the README specification.
"""

import pytest
from unittest.mock import Mock, patch

import pixcrawler as pix


class TestSDKInterface:
    """Test that the SDK interface matches the README specification."""

    def test_imports(self):
        """Test that all expected functions and classes are importable."""
        # Core classes
        assert hasattr(pix, 'Dataset')
        assert hasattr(pix, 'Project')
        assert hasattr(pix, 'AzureConfig')
        
        # Main functions
        assert hasattr(pix, 'auth')
        assert hasattr(pix, 'dataset')
        assert hasattr(pix, 'datasets')
        assert hasattr(pix, 'project')
        assert hasattr(pix, 'get_dataset_info')
        assert hasattr(pix, 'download_dataset')
        
        # Legacy functions
        assert hasattr(pix, 'load_dataset')
        assert hasattr(pix, 'list_datasets')
        
        # Exceptions
        assert hasattr(pix, 'PixCrawlerError')
        assert hasattr(pix, 'APIError')
        assert hasattr(pix, 'AuthenticationError')
        assert hasattr(pix, 'NotFoundError')
        assert hasattr(pix, 'RateLimitError')

    def test_auth_function(self):
        """Test the auth function sets global authentication."""
        pix.auth(token="test-token", base_url="https://test.api.com", project_id="project-123")
        
        # Verify global state is set
        from pixcrawler.core import _global_auth_token, _global_base_url, _global_project_id
        assert _global_auth_token == "test-token"
        assert _global_base_url == "https://test.api.com"
        assert _global_project_id == "project-123"

    @patch('pixcrawler.core.requests.request')
    def test_dataset_class(self, mock_request):
        """Test Dataset class functionality."""
        # Mock API responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 123,
            "name": "Test Dataset",
            "total_images": 100,
            "size_mb": 25.5,
            "status": "completed"
        }
        mock_request.return_value = mock_response
        
        # Test dataset creation and info
        dataset = pix.dataset("123")
        assert dataset.dataset_id == "123"
        
        info = dataset.info()
        assert info["name"] == "Test Dataset"
        assert dataset.name == "Test Dataset"
        assert dataset.image_count == 100
        assert dataset.size_mb == 25.5

    @patch('pixcrawler.core.requests.request')
    def test_dataset_load(self, mock_request):
        """Test Dataset load functionality."""
        # Mock export JSON response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = [
            {"id": 1, "url": "http://example.com/1.jpg", "label": "cat"},
            {"id": 2, "url": "http://example.com/2.jpg", "label": "dog"}
        ]
        mock_request.return_value = mock_response
        
        dataset = pix.dataset("123")
        loaded_dataset = dataset.load()
        
        # Should return self for chaining
        assert loaded_dataset is dataset
        
        # Should be iterable
        items = list(dataset)
        assert len(items) == 2
        assert items[0]["label"] == "cat"
        assert items[1]["label"] == "dog"

    @patch('pixcrawler.core.requests.request')
    def test_project_class(self, mock_request):
        """Test Project class functionality."""
        # Mock project info response
        def mock_request_side_effect(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            
            if "/projects/" in url:
                response.json.return_value = {
                    "id": 456,
                    "name": "Test Project",
                    "description": "A test project"
                }
            elif "/datasets" in url:
                response.json.return_value = {
                    "items": [
                        {"id": 1, "name": "Dataset 1"},
                        {"id": 2, "name": "Dataset 2"}
                    ]
                }
            return response
        
        mock_request.side_effect = mock_request_side_effect
        
        project = pix.project("456")
        assert project.project_id == "456"
        
        info = project.info()
        assert info["name"] == "Test Project"
        assert project.name == "Test Project"
        assert project.description == "A test project"
        
        datasets_list = project.datasets()
        assert len(datasets_list) == 2
        assert datasets_list[0]["name"] == "Dataset 1"

    @patch('pixcrawler.core.requests.request')
    def test_datasets_function(self, mock_request):
        """Test the datasets function."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"id": 1, "name": "Dataset 1", "total_images": 100},
                {"id": 2, "name": "Dataset 2", "total_images": 200}
            ],
            "total": 2,
            "page": 1,
            "size": 50
        }
        mock_request.return_value = mock_response
        
        pix.auth(token="test-token")
        datasets_list = pix.datasets(page=1, size=10)
        
        assert len(datasets_list) == 2
        assert datasets_list[0]["name"] == "Dataset 1"
        assert datasets_list[1]["total_images"] == 200

    @patch('pixcrawler.core.requests.request')
    def test_get_dataset_info_function(self, mock_request):
        """Test the get_dataset_info function."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 789,
            "name": "Info Dataset",
            "total_images": 500,
            "size_mb": 125.0
        }
        mock_request.return_value = mock_response
        
        info = pix.get_dataset_info("789")
        assert info["name"] == "Info Dataset"
        assert info["total_images"] == 500

    def test_legacy_functions_exist(self):
        """Test that legacy functions exist for backward compatibility."""
        # These should be callable (even if they fail without mocking)
        assert callable(pix.load_dataset)
        assert callable(pix.list_datasets)

    def test_exception_hierarchy(self):
        """Test that exceptions have proper hierarchy."""
        # All custom exceptions should inherit from PixCrawlerError
        assert issubclass(pix.APIError, pix.PixCrawlerError)
        assert issubclass(pix.AuthenticationError, pix.PixCrawlerError)
        assert issubclass(pix.NotFoundError, pix.PixCrawlerError)
        assert issubclass(pix.RateLimitError, pix.PixCrawlerError)
        assert issubclass(pix.ValidationError, pix.PixCrawlerError)

    @patch('pixcrawler.core.requests.request')
    def test_error_handling(self, mock_request):
        """Test that API errors are properly handled."""
        # Test 404 error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        
        with pytest.raises(pix.NotFoundError):
            pix.get_dataset_info("nonexistent")
        
        # Test 401 error
        mock_response.status_code = 401
        with pytest.raises(pix.AuthenticationError):
            pix.datasets()
        
        # Test 429 error
        mock_response.status_code = 429
        with pytest.raises(pix.RateLimitError):
            pix.datasets()

    def test_azure_config_class(self):
        """Test AzureConfig class functionality."""
        # Test basic creation
        azure_config = pix.AzureConfig(
            connection_string="DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test_key==",
            container_name="test-container"
        )
        
        assert azure_config.connection_string is not None
        assert azure_config.container_name == "test-container"
        
        # Test with account name and key
        azure_config2 = pix.AzureConfig(
            account_name="testaccount",
            account_key="testkey==",
            container_name="datasets"
        )
        
        assert azure_config2.account_name == "testaccount"
        assert azure_config2.account_key == "testkey=="

    def test_dataset_with_secret_params(self):
        """Test Dataset creation with secret parameters."""
        # Test with direct URL
        dataset_url = pix.dataset("123", __url="https://example.com/dataset.json")
        assert dataset_url.dataset_id == "123"
        assert dataset_url._Dataset__url == "https://example.com/dataset.json"
        
        # Test with Azure config
        azure_config = pix.AzureConfig(
            connection_string="DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test_key==",
            container_name="datasets"
        )
        dataset_azure = pix.dataset("456", __azure=azure_config)
        assert dataset_azure.dataset_id == "456"
        assert dataset_azure._Dataset__azure == azure_config

    def test_project_with_azure_config(self):
        """Test Project creation with Azure configuration."""
        azure_config = pix.AzureConfig(
            connection_string="DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test_key==",
            container_name="datasets"
        )
        
        project_azure = pix.project("789", __azure=azure_config)
        assert project_azure.project_id == "789"
        assert project_azure._Project__azure == azure_config
        
        # Test that project passes Azure config to datasets
        dataset = project_azure.dataset("123")
        assert dataset._Dataset__azure == azure_config

    def test_project_id_functionality(self):
        """Test project_id parameter in auth function and default project access."""
        # Test auth with project_id
        pix.auth(token="test-token", project_id="default-project-123")
        
        # Verify global project ID is set
        from pixcrawler.core import _global_project_id
        assert _global_project_id == "default-project-123"
        
        # Test project creation without explicit ID (should use global)
        with patch('pixcrawler.core.requests.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": 123,
                "name": "Default Project",
                "description": "Default project from auth"
            }
            mock_request.return_value = mock_response
            
            # Should use project_id from auth()
            default_project = pix.project()
            assert default_project.project_id == "default-project-123"
        
        # Test error when no project_id available
        # Reset global state completely
        from pixcrawler.core import _global_project_id
        import pixcrawler.core
        pixcrawler.core._global_project_id = None
        pix.auth(token="test-token")  # Reset without project_id
        
        with pytest.raises(ValueError, match="No project_id provided"):
            pix.project()

    @patch('pixcrawler.core.requests.request')
    def test_datasets_with_project_id(self, mock_request):
        """Test datasets function with project_id filtering."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"id": 1, "name": "Project Dataset 1"},
                {"id": 2, "name": "Project Dataset 2"}
            ]
        }
        mock_request.return_value = mock_response
        
        # Test with explicit project_id
        pix.auth(token="test-token")
        datasets_list = pix.datasets(project_id="explicit-project")
        
        # Verify project_id was passed in params
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["project_id"] == "explicit-project"
        
        # Test with global project_id
        mock_request.reset_mock()
        pix.auth(token="test-token", project_id="global-project")
        datasets_list = pix.datasets()  # Should use global project_id
        
        # Verify global project_id was used
        call_args = mock_request.call_args
        assert call_args[1]["params"]["project_id"] == "global-project"

    def test_readme_examples_syntax(self):
        """Test that README examples have valid syntax."""
        # This tests the basic syntax of README examples
        
        # Example 1: Basic usage with project_id
        try:
            # This should not raise syntax errors
            code = """
import pixcrawler as pix
pix.auth(token="your_api_key", project_id="project-id-123")
project = pix.project()  # Uses project_id from auth
dataset = project.dataset("dataset-id-123")
"""
            compile(code, '<string>', 'exec')
        except SyntaxError:
            pytest.fail("README example 1 has syntax errors")
        
        # Example 2: Dataset operations
        try:
            code = """
import pixcrawler as pix
dataset = pix.dataset("dataset-id-123")
info = dataset.info()
data = dataset.load()
path = dataset.download("./my_dataset.zip")
"""
            compile(code, '<string>', 'exec')
        except SyntaxError:
            pytest.fail("README example 2 has syntax errors")
        
        # Example 3: Azure direct access
        try:
            code = """
import pixcrawler as pix
from pixcrawler import AzureConfig

azure_config = AzureConfig(
    connection_string="DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test_key==",
    container_name="datasets"
)
dataset = pix.dataset("dataset-id-123", __azure=azure_config)
dataset_url = pix.dataset("dataset-id-456", __url="https://storage.blob.core.windows.net/...")
"""
            compile(code, '<string>', 'exec')
        except SyntaxError:
            pytest.fail("README example 3 (Azure) has syntax errors")
        
        # Example 4: Project ID functionality
        try:
            code = """
import pixcrawler as pix
pix.auth(token="your_api_key", project_id="project-id-123")
project = pix.project()  # Uses project_id from auth()
datasets = pix.datasets()  # Uses project_id from auth()
explicit_datasets = pix.datasets(project_id="other-project")  # Explicit project
"""
            compile(code, '<string>', 'exec')
        except SyntaxError:
            pytest.fail("README example 4 (project_id) has syntax errors")