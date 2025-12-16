# PixCrawler SDK Changelog

## Version 0.2.0.dev1 - Azure Direct Access (January 2025)

### 🚀 Major Changes

#### Azure Direct Access Support (Internal Use)
- **Added `AzureConfig` class**: Configuration for direct Azure Blob Storage access
- **Secret `__url` parameter**: Direct blob URL access for datasets
- **Secret `__azure` parameter**: Azure configuration for blob operations
- **Direct download/load**: Bypass API for internal/demo purposes

#### Updated Dependencies
- **Added `azure-storage-blob>=12.0.0`**: Azure Storage SDK for direct blob access
- **Optional dependency**: Graceful fallback if Azure SDK not installed

### 🔧 New Features

#### 1. AzureConfig Class
```python
from pixcrawler import AzureConfig

# Connection string method
azure_config = AzureConfig(
    connection_string="DefaultEndpointsProtocol=https;AccountName=...",
    container_name="datasets"
)

# Account name + key method
azure_config = AzureConfig(
    account_name="pixcrawler",
    account_key="your_key==",
    container_name="datasets"
)

# Account name + SAS token method
azure_config = AzureConfig(
    account_name="pixcrawler",
    sas_token="sv=2021-06-08&ss=b&srt=sco&sp=r&se=...",
    container_name="datasets"
)
```

#### 2. Direct URL Access
```python
import pixcrawler as pix

# Direct blob URL with SAS token
dataset = pix.dataset(
    "dataset-123", 
    __url="https://storage.blob.core.windows.net/datasets/dataset_123.json?sv=..."
)

# Load directly from Azure
data = dataset.load()
path = dataset.download("./dataset.zip")
```

#### 3. Azure Configuration Access
```python
import pixcrawler as pix
from pixcrawler import AzureConfig

azure_config = AzureConfig(
    connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    container_name="datasets"
)

# Dataset with Azure config
dataset = pix.dataset("dataset-123", __azure=azure_config)

# Project with Azure config (inherited by all datasets)
project = pix.project("project-456", __azure=azure_config)
dataset = project.dataset("dataset-789")  # Inherits Azure config
```

### 📋 Implementation Details

#### Blob Naming Conventions
- **JSON Data**: `dataset_{dataset_id}.json`
- **ZIP Archives**: `dataset_{dataset_id}.zip`
- **Container**: Configurable via `AzureConfig.container_name`

#### Authentication Priority
1. **Connection String**: Complete connection string with credentials
2. **Account Name + Key**: Storage account name and access key
3. **Account Name + SAS Token**: Storage account name and SAS token

#### Error Handling
- **Missing Azure SDK**: Clear error message with installation instructions
- **Incomplete Config**: Validation of required authentication parameters
- **Blob Not Found**: Proper error handling for missing blobs
- **Memory Limits**: 300MB limit enforced for direct access

### 🛡️ Security Features

#### Secure Configuration
- **Environment Variables**: Recommended for all credentials
- **SAS Tokens**: Support for time-limited access tokens
- **HTTPS Only**: All Azure endpoints use HTTPS
- **No Hardcoded Secrets**: Configuration designed for external credential sources

#### Access Control
- **Internal Use Only**: Clearly marked as internal functionality
- **Minimal Permissions**: SAS tokens can be scoped to specific operations
- **Container Isolation**: Separate containers for different environments

### 🧪 Testing & Quality

#### New Test Coverage
- **AzureConfig Class**: Creation and validation tests
- **Secret Parameters**: Dataset and Project creation with `__url` and `__azure`
- **Error Scenarios**: Missing SDK, invalid config, blob not found
- **Syntax Validation**: README examples with Azure functionality

#### Demo Updates
- **Azure Demo Section**: Showcases direct access functionality
- **Configuration Examples**: Multiple authentication methods
- **Error Handling**: Demonstrates proper exception handling

### 📚 Documentation

#### New Documentation Files
- **`AZURE_DIRECT_ACCESS.md`**: Comprehensive guide for internal use
- **Security Best Practices**: Credential management and access control
- **Usage Examples**: Real-world scenarios and configurations
- **Migration Guide**: Moving between API and direct access

#### Updated Examples
- **Demo Script**: Azure functionality demonstration
- **README Updates**: Secret parameter documentation
- **Code Comments**: Clear internal use warnings

### 🔄 API Compatibility

#### Backward Compatibility
- **No Breaking Changes**: All existing functionality preserved
- **Optional Parameters**: Secret parameters are optional and hidden
- **Legacy Support**: All legacy functions continue to work
- **Standard API**: Default behavior unchanged

#### New Function Signatures
```python
# Updated signatures with secret parameters
def dataset(
    dataset_id: Union[str, int], 
    config: Optional[Dict[str, Any]] = None,
    __url: Optional[str] = None,
    __azure: Optional[AzureConfig] = None
) -> Dataset

def project(
    project_id: Union[str, int], 
    config: Optional[Dict[str, Any]] = None,
    __azure: Optional[AzureConfig] = None
) -> Project
```

### ⚠️ Important Notes

#### Internal Use Only
- **Not for Production**: External users should use standard API
- **Demo Purposes**: Designed for internal demos and development
- **Security Implications**: Requires direct Azure Storage access
- **Support Limitations**: Internal support only

#### Performance Considerations
- **Direct Access**: Faster than API for large datasets
- **Memory Limits**: 300MB limit enforced
- **Streaming Downloads**: Efficient handling of large files
- **Parallel Operations**: Multiple datasets can be processed concurrently

### 🚀 Usage Examples

#### Development Environment
```python
import os
import pixcrawler as pix
from pixcrawler import AzureConfig

# Development configuration
azure_config = AzureConfig(
    connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    container_name="dev-datasets"
)

# Load dataset directly
dataset = pix.dataset("dev-001", __azure=azure_config)
data = dataset.load()
```

#### Demo with SAS URLs
```python
import pixcrawler as pix

# Time-limited SAS URL
sas_url = "https://demostorage.blob.core.windows.net/datasets/demo_001.json?sv=2021-06-08&ss=b&srt=sco&sp=r&se=2024-12-31T23:59:59Z&sig=..."

dataset = pix.dataset("demo-001", __url=sas_url)
data = dataset.load()
```

#### Project-Level Configuration
```python
import pixcrawler as pix
from pixcrawler import AzureConfig

# Configure entire project
azure_config = AzureConfig(
    account_name="pixcrawler",
    account_key=os.getenv("AZURE_ACCOUNT_KEY"),
    container_name="production-datasets"
)

project = pix.project("prod-001", __azure=azure_config)

# All datasets inherit Azure config
dataset1 = project.dataset("dataset-001")
dataset2 = project.dataset("dataset-002")
```

### 📦 Version Information

- **Version**: `0.2.0.dev1`
- **Python Support**: 3.11, 3.12, 3.13
- **Dependencies**: `requests>=2.25.0`, `azure-storage-blob>=12.0.0`
- **Status**: Development release with Azure direct access

### 🔮 Future Enhancements

1. **Additional Storage Providers**: AWS S3, Google Cloud Storage support
2. **Advanced Caching**: Local caching for frequently accessed datasets
3. **Batch Operations**: Bulk dataset operations via direct access
4. **Monitoring**: Usage metrics and performance tracking
5. **Security Enhancements**: Advanced authentication methods

---

## Version 0.2.0 - Updated API Interface (January 2025)

### 🚀 Major Changes

#### New Object-Oriented Interface
- **Added `Dataset` class**: Provides methods for loading, downloading, and getting info
- **Added `Project` class**: Manages project-level operations and dataset access
- **New main functions**: `pix.dataset()`, `pix.project()`, `pix.datasets()`

#### Updated API Endpoints
- **Aligned with backend**: Updated to use actual PixCrawler backend endpoints
- **Export endpoints**: Uses `/datasets/{id}/export/json` and `/datasets/{id}/export/zip`
- **Pagination support**: Proper FastAPI pagination handling
- **Project integration**: Full project-dataset hierarchy support

#### Enhanced Authentication
- **Multiple auth methods**: Programmatic, environment variables, per-request config
- **Updated env vars**: Primary `PIXCRAWLER_SERVICE_KEY`, legacy support maintained
- **Global auth state**: `pix.auth()` sets global authentication for session

### 🔧 API Changes

#### New Interface (Recommended)
```python
import pixcrawler as pix

# Authentication
pix.auth(token="your_api_key")

# Project-based access
project = pix.project("project-id")
datasets = project.datasets()
dataset = project.dataset("dataset-id")

# Direct dataset access
dataset = pix.dataset("dataset-id")
info = dataset.info()
data = dataset.load()
path = dataset.download("./dataset.zip")

# List all datasets
all_datasets = pix.datasets(page=1, size=50)
```

#### Legacy Interface (Backward Compatible)
```python
import pixcrawler as pix

# Legacy functions still work
dataset = pix.load_dataset("dataset-id")
datasets = pix.list_datasets(page=1, size=20)
info = pix.get_dataset_info("dataset-id")
path = pix.download_dataset("dataset-id", "./dataset.zip")
```

### 📋 New Features

1. **Method Chaining**: `dataset.load()` returns self for chaining
2. **Property Access**: `dataset.name`, `dataset.image_count`, `dataset.size_mb`
3. **Memory Safety**: 300MB limit with clear error messages
4. **Better Error Handling**: Specific exceptions for different error types
5. **Streaming Downloads**: Efficient handling of large dataset downloads
6. **Project Management**: Full project-dataset hierarchy support

### 🔄 Backend Endpoint Mapping

| SDK Function | Backend Endpoint | Description |
|--------------|------------------|-------------|
| `pix.datasets()` | `GET /datasets` | List user datasets with pagination |
| `dataset.info()` | `GET /datasets/{id}` | Get dataset metadata |
| `dataset.load()` | `GET /datasets/{id}/export/json` | Load dataset into memory |
| `dataset.download()` | `GET /datasets/{id}/export/zip` | Download dataset archive |
| `project.info()` | `GET /projects/{id}` | Get project metadata |
| `project.datasets()` | `GET /datasets?project_id={id}` | List project datasets |

### 🛡️ Security & Best Practices

1. **Environment Variables**: Primary support for `PIXCRAWLER_SERVICE_KEY`
2. **Token Validation**: Proper Bearer token authentication
3. **Error Handling**: Structured error responses with specific exception types
4. **Memory Limits**: 300MB limit prevents memory exhaustion
5. **Timeout Handling**: Configurable timeouts for different operations

### 🧪 Testing

- **Comprehensive test suite**: 14 test cases covering all major functionality
- **Mock support**: Built-in mocking for development and testing
- **README validation**: Ensures documentation examples work correctly
- **Error scenarios**: Tests for authentication, not found, and rate limiting errors

### 📚 Documentation

- **Updated README**: Complete API reference with examples
- **Demo script**: Interactive demonstration of all features
- **Type hints**: Full type annotation support
- **Docstrings**: Comprehensive documentation for all public methods

### 🔧 Development

- **Updated dependencies**: Modern requests library version
- **Test infrastructure**: pytest-based testing with mocking
- **Code quality**: Type hints, docstrings, and error handling
- **Backward compatibility**: Legacy functions maintained

### 🚨 Breaking Changes

None! All existing code continues to work with legacy function support.

---

**Last Updated**: January 2025  
**Status**: Development Release with Azure Direct Access