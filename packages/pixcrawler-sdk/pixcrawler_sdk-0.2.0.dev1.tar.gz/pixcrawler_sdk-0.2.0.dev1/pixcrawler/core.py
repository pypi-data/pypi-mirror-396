import os
import time
from pathlib import Path
from typing import Optional, Any, Dict, List, Union
from dataclasses import dataclass

import requests

try:
    from azure.storage.blob import BlobServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

# ============================================================================
# Module-Level State for Global Authentication
# ============================================================================

_global_auth_token: Optional[str] = None
_global_base_url: str = "https://api.pixcrawler.com/v1"
_global_project_id: Optional[str] = None


# ============================================================================
# Custom Exceptions
# ============================================================================

class PixCrawlerError(Exception):
    """Base exception for all PixCrawler SDK errors."""
    pass


class APIError(PixCrawlerError):
    """API returned an error response."""
    def __init__(self, status_code: int, message: str, details: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"API Error {status_code}: {message}")


class AuthenticationError(PixCrawlerError):
    """Authentication failed or credentials missing."""
    pass


class ValidationError(PixCrawlerError):
    """Request validation failed."""
    pass


class NotFoundError(PixCrawlerError):
    """Resource not found."""
    pass


class RateLimitError(PixCrawlerError):
    """Rate limit exceeded."""
    pass


# ============================================================================
# Azure Configuration
# ============================================================================

@dataclass
class AzureConfig:
    """
    Azure Storage configuration for direct blob access.
    
    This is used internally for demo and development purposes to bypass
    the API and connect directly to Azure Storage.
    """
    connection_string: Optional[str] = None
    account_name: Optional[str] = None
    account_key: Optional[str] = None
    sas_token: Optional[str] = None
    container_name: str = "datasets"
    
    def get_blob_service_client(self) -> "BlobServiceClient":
        """Get Azure Blob Service Client."""
        if not AZURE_AVAILABLE:
            raise PixCrawlerError(
                "Azure Storage SDK not available. Install with: pip install azure-storage-blob"
            )
        
        if self.connection_string:
            return BlobServiceClient.from_connection_string(self.connection_string)
        elif self.account_name and self.account_key:
            return BlobServiceClient(
                account_url=f"https://{self.account_name}.blob.core.windows.net",
                credential=self.account_key
            )
        elif self.account_name and self.sas_token:
            return BlobServiceClient(
                account_url=f"https://{self.account_name}.blob.core.windows.net",
                credential=self.sas_token
            )
        else:
            raise PixCrawlerError(
                "Azure configuration incomplete. Provide either connection_string or "
                "(account_name + account_key) or (account_name + sas_token)"
            )


# ============================================================================
# Core Classes
# ============================================================================

class Dataset:
    """
    A class representing a dataset that can be loaded into memory or downloaded.
    """
    def __init__(
        self, 
        dataset_id: Union[str, int], 
        config: Optional[Dict[str, Any]] = None,
        __url: Optional[str] = None,
        __azure: Optional[AzureConfig] = None
    ):
        """
        Initialize the Dataset with ID and configuration.

        Args:
            dataset_id: The ID of the dataset
            config: Optional configuration dictionary
            __url: Secret parameter for direct Azure Storage URL (internal use)
            __azure: Azure configuration for direct blob access (internal use)
        """
        self.dataset_id = str(dataset_id)
        self.config = config or {}
        self._data: Optional[List[Any]] = None
        self._info: Optional[Dict[str, Any]] = None
        
        # Secret parameters for internal/demo use
        self.__url = __url
        self.__azure = __azure
        
        # Validate Azure configuration if provided
        if self.__azure and not AZURE_AVAILABLE:
            raise PixCrawlerError(
                "Azure Storage SDK not available. Install with: pip install azure-storage-blob"
            )

    def load(self) -> "Dataset":
        """
        Load dataset into memory for iteration.
        
        Returns:
            Self for method chaining
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If dataset not found
            RuntimeError: If dataset exceeds memory limit (300MB)
        """
        if self._data is None:
            # Check for direct Azure access first
            if self.__azure or self.__url:
                self._load_direct()
            else:
                # Standard API load
                response = _make_request(
                    "GET",
                    f"/datasets/{self.dataset_id}/export/json",
                    config=self.config,
                    timeout=300  # 5 minutes for large datasets
                )
                
                # Check memory guardrail before loading
                content_length = response.headers.get('Content-Length')
                max_memory_bytes = 300 * 1024 * 1024  # 300MB limit
                
                if content_length and int(content_length) > max_memory_bytes:
                    raise RuntimeError(
                        f"Dataset size ({int(content_length) / (1024*1024):.2f}MB) exceeds "
                        f"memory limit ({max_memory_bytes / (1024*1024):.0f}MB)"
                    )
                
                # Parse JSON response
                try:
                    data = response.json()
                    if isinstance(data, list):
                        self._data = data
                    elif isinstance(data, dict) and "items" in data:
                        self._data = data["items"]
                    else:
                        self._data = [data] if data else []
                except ValueError:
                    raise PixCrawlerError("Failed to parse dataset response as JSON")
        
        return self

    def _load_direct(self) -> None:
        """
        Load dataset directly from Azure Storage (internal use).
        """
        max_memory_bytes = 300 * 1024 * 1024  # 300MB limit
        
        try:
            if self.__url:
                # Direct URL load
                response = requests.get(self.__url, timeout=300)
                response.raise_for_status()
                
                # Check memory guardrail
                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > max_memory_bytes:
                    raise RuntimeError(
                        f"Dataset size ({int(content_length) / (1024*1024):.2f}MB) exceeds "
                        f"memory limit ({max_memory_bytes / (1024*1024):.0f}MB)"
                    )
                
                data = response.json()
            
            elif self.__azure:
                # Azure Blob Storage load
                blob_service_client = self.__azure.get_blob_service_client()
                blob_name = f"dataset_{self.dataset_id}.json"
                
                blob_client = blob_service_client.get_blob_client(
                    container=self.__azure.container_name,
                    blob=blob_name
                )
                
                # Download and check size
                blob_properties = blob_client.get_blob_properties()
                if blob_properties.size > max_memory_bytes:
                    raise RuntimeError(
                        f"Dataset size ({blob_properties.size / (1024*1024):.2f}MB) exceeds "
                        f"memory limit ({max_memory_bytes / (1024*1024):.0f}MB)"
                    )
                
                download_stream = blob_client.download_blob()
                content = download_stream.readall().decode('utf-8')
                
                import json
                data = json.loads(content)
            
            # Process data
            if isinstance(data, list):
                self._data = data
            elif isinstance(data, dict) and "items" in data:
                self._data = data["items"]
            else:
                self._data = [data] if data else []
                
        except Exception as e:
            raise PixCrawlerError(f"Direct load failed: {str(e)}")

    def download(self, output_path: str) -> str:
        """
        Download dataset archive to local file.
        
        Args:
            output_path: Local file path to save the dataset
            
        Returns:
            Absolute path to downloaded file
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If dataset not found
            PixCrawlerError: If download fails
        """
        # Check for direct Azure access first
        if self.__azure or self.__url:
            return self._download_direct(output_path)
        
        # Standard API download
        response = _make_request(
            "GET",
            f"/datasets/{self.dataset_id}/export/zip",
            config=self.config,
            timeout=300,  # 5 minutes for large downloads
            stream=True
        )
        
        # Create output directory if it doesn't exist
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Download with progress
        try:
            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return str(output_file.absolute())
            
        except Exception as e:
            # Clean up partial download
            if output_file.exists():
                output_file.unlink()
            raise PixCrawlerError(f"Download failed: {str(e)}")

    def _download_direct(self, output_path: str) -> str:
        """
        Download dataset directly from Azure Storage (internal use).
        
        Args:
            output_path: Local file path to save the dataset
            
        Returns:
            Absolute path to downloaded file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if self.__url:
                # Direct URL download
                response = requests.get(self.__url, stream=True, timeout=300)
                response.raise_for_status()
                
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            
            elif self.__azure:
                # Azure Blob Storage download
                blob_service_client = self.__azure.get_blob_service_client()
                blob_name = f"dataset_{self.dataset_id}.zip"
                
                blob_client = blob_service_client.get_blob_client(
                    container=self.__azure.container_name,
                    blob=blob_name
                )
                
                with open(output_file, 'wb') as f:
                    download_stream = blob_client.download_blob()
                    f.write(download_stream.readall())
            
            return str(output_file.absolute())
            
        except Exception as e:
            # Clean up partial download
            if output_file.exists():
                output_file.unlink()
            raise PixCrawlerError(f"Direct download failed: {str(e)}")

    def info(self) -> Dict[str, Any]:
        """
        Get dataset metadata without downloading.
        
        Returns:
            Dictionary with dataset metadata
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If dataset not found
        """
        if self._info is None:
            response = _make_request(
                "GET",
                f"/datasets/{self.dataset_id}",
                config=self.config,
                timeout=30
            )
            self._info = response.json()
        
        return self._info

    @property
    def name(self) -> str:
        """Get dataset name."""
        return self.info().get("name", "")

    @property
    def image_count(self) -> int:
        """Get total image count."""
        return self.info().get("total_images", 0)

    @property
    def size_mb(self) -> float:
        """Get dataset size in MB."""
        return self.info().get("size_mb", 0.0)

    def __iter__(self):
        """
        Iterate over the dataset items.
        
        Note: This requires the dataset to be loaded first.
        """
        if self._data is None:
            self.load()
        
        for item in self._data:
            yield item

    def __len__(self) -> int:
        """Get number of items in loaded dataset."""
        if self._data is None:
            return self.image_count
        return len(self._data)


class Project:
    """
    A class representing a project that contains datasets.
    """
    def __init__(
        self, 
        project_id: Union[str, int], 
        config: Optional[Dict[str, Any]] = None,
        __azure: Optional[AzureConfig] = None
    ):
        """
        Initialize the Project with ID and configuration.

        Args:
            project_id: The ID of the project
            config: Optional configuration dictionary
            __azure: Azure configuration for direct blob access (internal use)
        """
        self.project_id = str(project_id)
        self.config = config or {}
        self._info: Optional[Dict[str, Any]] = None
        self.__azure = __azure

    def datasets(self, page: int = 1, size: int = 50) -> List[Dict[str, Any]]:
        """
        List datasets in this project.
        
        Args:
            page: Page number (default: 1)
            size: Items per page (default: 50, max: 100)
            
        Returns:
            List of dataset metadata dictionaries
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If API request fails
        """
        response = _make_request(
            "GET",
            "/datasets",
            config=self.config,
            params={"project_id": self.project_id, "page": page, "size": size},
            timeout=30
        )
        
        data = response.json()
        
        # Handle fastapi-pagination format
        if isinstance(data, dict) and "items" in data:
            return data["items"]
        elif isinstance(data, list):
            return data
        else:
            return [data] if data else []

    def dataset(self, dataset_id: Union[str, int], __url: Optional[str] = None) -> Dataset:
        """
        Get a dataset from this project.
        
        Args:
            dataset_id: Dataset ID
            __url: Secret parameter for direct Azure Storage URL (internal use)
            
        Returns:
            Dataset instance
        """
        return Dataset(dataset_id, self.config, __url, self.__azure)

    def info(self) -> Dict[str, Any]:
        """
        Get project metadata.
        
        Returns:
            Dictionary with project metadata
            
        Raises:
            AuthenticationError: If authentication fails
            NotFoundError: If project not found
        """
        if self._info is None:
            response = _make_request(
                "GET",
                f"/projects/{self.project_id}",
                config=self.config,
                timeout=30
            )
            self._info = response.json()
        
        return self._info

    @property
    def name(self) -> str:
        """Get project name."""
        return self.info().get("name", "")

    @property
    def description(self) -> str:
        """Get project description."""
        return self.info().get("description", "")

# ============================================================================
# Main API Functions
# ============================================================================

def dataset(
    dataset_id: Union[str, int], 
    config: Optional[Dict[str, Any]] = None,
    __url: Optional[str] = None,
    __azure: Optional[AzureConfig] = None
) -> Dataset:
    """
    Create a Dataset instance for loading or downloading.

    Args:
        dataset_id: UUID or ID of the dataset
        config: Optional configuration with 'api_key' and 'base_url'
        __url: Secret parameter for direct Azure Storage URL (internal use)
        __azure: Azure configuration for direct blob access (internal use)

    Returns:
        Dataset instance

    Example:
        >>> import pixcrawler as pix
        >>> dataset = pix.dataset("dataset-id-123")
        >>> data = dataset.load()  # Load into memory
        >>> # or
        >>> path = dataset.download("./my_dataset.zip")  # Download to file
        
        # Internal/Demo usage with direct Azure access:
        >>> from pixcrawler.core import AzureConfig
        >>> azure_config = AzureConfig(
        ...     connection_string="DefaultEndpointsProtocol=https;AccountName=...",
        ...     container_name="datasets"
        ... )
        >>> dataset = pix.dataset("dataset-id-123", __azure=azure_config)
        >>> # or with direct URL
        >>> dataset = pix.dataset("dataset-id-123", __url="https://storage.blob.core.windows.net/...")
    """
    return Dataset(dataset_id, config, __url, __azure)


def project(
    project_id: Optional[Union[str, int]] = None, 
    config: Optional[Dict[str, Any]] = None,
    __azure: Optional[AzureConfig] = None
) -> Project:
    """
    Create a Project instance for accessing datasets.

    Args:
        project_id: UUID or ID of the project (optional if set via auth())
        config: Optional configuration with 'api_key' and 'base_url'
        __azure: Azure configuration for direct blob access (internal use)

    Returns:
        Project instance

    Raises:
        ValueError: If no project_id provided and none set globally

    Example:
        >>> import pixcrawler as pix
        >>> pix.auth(token="your_api_key", project_id="project-id-123")
        >>> proj = pix.project()  # Uses project_id from auth()
        >>> # or
        >>> proj = pix.project("project-id-456")  # Explicit project_id
        >>> datasets = proj.datasets()  # List datasets in project
        >>> dataset = proj.dataset("dataset-id-789")  # Get specific dataset
        
        # Internal/Demo usage with Azure config:
        >>> from pixcrawler.core import AzureConfig
        >>> azure_config = AzureConfig(
        ...     connection_string="DefaultEndpointsProtocol=https;AccountName=...",
        ...     container_name="datasets"
        ... )
        >>> proj = pix.project("project-id-123", __azure=azure_config)
    """
    # Use provided project_id or get from global state/config
    if project_id is None:
        project_id = _get_project_id(config)
        if project_id is None:
            raise ValueError(
                "No project_id provided. Either pass project_id parameter or "
                "set it globally with pix.auth(token='...', project_id='...')"
            )
    
    return Project(project_id, config, __azure)


def datasets(
    page: int = 1, 
    size: int = 50, 
    config: Optional[Dict[str, Any]] = None,
    project_id: Optional[Union[str, int]] = None
) -> List[Dict[str, Any]]:
    """
    List user's datasets with pagination.
    
    Retrieves a paginated list of datasets owned by the authenticated user.
    
    Args:
        page: Page number (default: 1)
        size: Items per page (default: 50, max: 100)
        config: Optional configuration with 'api_key' and 'base_url'
        project_id: Optional project ID to filter datasets (uses global if not provided)
    
    Returns:
        List of dataset metadata dictionaries
    
    Raises:
        AuthenticationError: If authentication fails
        APIError: If API request fails
    
    Example:
        >>> import pixcrawler as pix
        >>> pix.auth(token="your_api_key", project_id="project-123")
        >>> datasets = pix.datasets(page=1, size=10)  # Uses project from auth()
        >>> # or
        >>> datasets = pix.datasets(project_id="other-project")  # Explicit project
        >>> for dataset in datasets:
        ...     print(f"{dataset['id']}: {dataset['name']}")
    """
    # Build query parameters
    params = {"page": page, "size": size}
    
    # Add project_id if provided or available globally
    if project_id is not None:
        params["project_id"] = str(project_id)
    else:
        global_project_id = _get_project_id(config)
        if global_project_id:
            params["project_id"] = global_project_id
    
    response = _make_request(
        "GET",
        "/datasets",
        config=config,
        params=params,
        timeout=30
    )
    
    data = response.json()
    
    # Handle fastapi-pagination format
    if isinstance(data, dict) and "items" in data:
        return data["items"]
    elif isinstance(data, list):
        return data
    else:
        return [data] if data else []


# ============================================================================
# Legacy Functions (for backward compatibility)
# ============================================================================

def load_dataset(dataset_id: str, config: Optional[Dict[str, Any]] = None) -> Dataset:
    """
    Load a dataset from the PixCrawler service (legacy function).

    Args:
        dataset_id: The ID of the dataset to load.
        config: Optional configuration dictionary. Can contain 'api_key' and 'base_url'.

    Returns:
        A Dataset object containing the loaded data.

    Raises:
        AuthenticationError: If authentication credentials are missing.
        NotFoundError: If dataset not found.
        RuntimeError: If dataset exceeds memory limit (300MB).
        
    Note:
        This is a legacy function. Use pix.dataset(id).load() instead.
    """
    return dataset(dataset_id, config).load()


def list_datasets(page: int = 1, size: int = 20, config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    List user's datasets with pagination (legacy function).
    
    Args:
        page: Page number (default: 1)
        size: Items per page (default: 20, max: 100)
        config: Optional configuration with 'api_key' and 'base_url'
    
    Returns:
        List of dataset metadata dictionaries
    
    Note:
        This is a legacy function. Use pix.datasets() instead.
    """
    return datasets(page, size, config)


def get_dataset_info(dataset_id: Union[str, int], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get dataset metadata without downloading.
    
    Retrieves metadata about a dataset including image count, size,
    labels, and other information without downloading the actual data.
    
    Args:
        dataset_id: UUID or ID of the dataset
        config: Optional configuration with 'api_key' and 'base_url'
    
    Returns:
        Dictionary with dataset metadata
    
    Raises:
        AuthenticationError: If authentication fails
        NotFoundError: If dataset not found
        APIError: If API request fails
    
    Example:
        >>> import pixcrawler as pix
        >>> info = pix.get_dataset_info("dataset-id-123")
        >>> print(f"Images: {info['image_count']}, Size: {info['size_mb']}MB")
    """
    return dataset(dataset_id, config).info()


def download_dataset(
    dataset_id: Union[str, int],
    output_path: str,
    config: Optional[Dict[str, Any]] = None
) -> str:
    """
    Download dataset archive to local file.
    
    Downloads the dataset as a ZIP archive to the specified path.
    Does NOT load the dataset into memory, making it suitable for large datasets.
    
    Args:
        dataset_id: UUID or ID of the dataset
        output_path: Local file path to save the dataset (e.g., "./wildlife.zip")
        config: Optional configuration with 'api_key' and 'base_url'
    
    Returns:
        Path to the downloaded file
    
    Raises:
        AuthenticationError: If authentication fails
        NotFoundError: If dataset not found
        APIError: If API request fails
        PixCrawlerError: If download or file write fails
    
    Example:
        >>> import pixcrawler as pix
        >>> pix.auth(token="your_api_key")
        >>> path = pix.download_dataset("dataset-id-123", "./my_dataset.zip")
        >>> print(f"Downloaded to: {path}")
    """
    return dataset(dataset_id, config).download(output_path)


# ============================================================================
# Global Authentication Function
# ============================================================================

def auth(token: str, base_url: Optional[str] = None, project_id: Optional[str] = None) -> None:
    """
    Set global authentication token for the session.
    
    This function sets the authentication token that will be used for all
    subsequent API calls. The token is stored in module-level state.
    
    Args:
        token: API token or JWT token from Supabase Auth
        base_url: Optional base URL override (default: https://api.pixcrawler.com/v1)
        project_id: Optional default project ID for subsequent operations
    
    Example:
        >>> import pixcrawler as pix
        >>> pix.auth(token="your_api_key", project_id="project-id-123")
        >>> datasets = pix.datasets()
    
    Note:
        - Token is stored in memory for the current Python session
        - Use environment variables (PIXCRAWLER_SERVICE_KEY) for production
        - This function is optional if using environment variables
        - project_id can be used as default for project operations
    """
    global _global_auth_token, _global_base_url, _global_project_id
    _global_auth_token = token
    if base_url:
        _global_base_url = base_url
    if project_id:
        _global_project_id = project_id


# ============================================================================
# Helper Functions
# ============================================================================

def _get_auth_token(config: Optional[Dict[str, Any]] = None) -> str:
    """
    Get authentication token from config, global state, or environment.
    
    Priority:
        1. config["api_key"]
        2. Global auth token (set via auth())
        3. PIXCRAWLER_SERVICE_KEY environment variable
        4. SERVICE_API_KEY environment variable (legacy)
        5. SERVICE_API_TOKEN environment variable (legacy)
    
    Args:
        config: Optional configuration dictionary
    
    Returns:
        Authentication token
    
    Raises:
        AuthenticationError: If no token is found
    """
    config = config or {}
    
    # Priority 1: config parameter
    token = config.get("api_key")
    if token:
        return token
    
    # Priority 2: global auth token
    if _global_auth_token:
        return _global_auth_token
    
    # Priority 3-5: environment variables
    token = (
        os.getenv("PIXCRAWLER_SERVICE_KEY") or 
        os.getenv("SERVICE_API_KEY") or 
        os.getenv("SERVICE_API_TOKEN")
    )
    if token:
        return token
    
    raise AuthenticationError(
        "Authentication failed: No API key found. "
        "Use pix.auth(token='...') or set PIXCRAWLER_SERVICE_KEY environment variable."
    )


def _get_base_url(config: Optional[Dict[str, Any]] = None) -> str:
    """
    Get base URL from config, global state, or environment.
    
    Args:
        config: Optional configuration dictionary
    
    Returns:
        Base URL for API requests
    """
    config = config or {}
    
    # Priority 1: config parameter
    if "base_url" in config:
        return config["base_url"]
    
    # Priority 2: global base URL
    if _global_base_url != "https://api.pixcrawler.com/v1":
        return _global_base_url
    
    # Priority 3: environment variable
    return os.getenv("PIXCRAWLER_API_URL", _global_base_url)


def _get_project_id(config: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Get project ID from config, global state, or environment.
    
    Priority:
        1. config["project_id"]
        2. Global project ID (set via auth())
        3. PIXCRAWLER_PROJECT_ID environment variable
    
    Args:
        config: Optional configuration dictionary
    
    Returns:
        Project ID if available, None otherwise
    """
    config = config or {}
    
    # Priority 1: config parameter
    project_id = config.get("project_id")
    if project_id:
        return str(project_id)
    
    # Priority 2: global project ID
    if _global_project_id:
        return _global_project_id
    
    # Priority 3: environment variable
    env_project_id = os.getenv("PIXCRAWLER_PROJECT_ID")
    if env_project_id:
        return env_project_id
    
    return None


def _make_request(
    method: str,
    endpoint: str,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> requests.Response:
    """
    Make authenticated API request with error handling.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path (e.g., "/datasets")
        config: Optional configuration dictionary
        **kwargs: Additional arguments for requests
    
    Returns:
        Response object
    
    Raises:
        AuthenticationError: If authentication fails
        APIError: If API returns an error
        RateLimitError: If rate limit is exceeded
        NotFoundError: If resource is not found
    """
    token = _get_auth_token(config)
    base_url = _get_base_url(config)
    url = f"{base_url}{endpoint}"
    
    headers = kwargs.pop("headers", {})
    headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    })
    
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        
        # Handle specific status codes
        if response.status_code == 401:
            raise AuthenticationError("Authentication failed: Invalid or expired token")
        elif response.status_code == 404:
            raise NotFoundError(f"Resource not found: {endpoint}")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded. Please try again later.")
        elif response.status_code == 422:
            try:
                error_data = response.json()
                raise ValidationError(f"Validation failed: {error_data.get('detail', response.text)}")
            except ValueError:
                raise ValidationError(f"Validation failed: {response.text}")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                raise APIError(
                    status_code=response.status_code,
                    message=error_data.get("message", error_data.get("detail", response.text)),
                    details=error_data.get("details", {})
                )
            except ValueError:
                raise APIError(
                    status_code=response.status_code,
                    message=response.text,
                    details={}
                )
        
        return response
        
    except requests.exceptions.Timeout:
        raise PixCrawlerError("Request timeout: Connection took too long")
    except requests.exceptions.ConnectionError:
        raise PixCrawlerError("Connection error: Could not connect to API")
    except (AuthenticationError, APIError, RateLimitError, NotFoundError, ValidationError):
        raise
    except Exception as e:
        raise PixCrawlerError(f"Unexpected error: {str(e)}")
