# Azure Direct Access (Internal Use)

This document describes the internal Azure Storage direct access functionality in the PixCrawler SDK. This feature is designed for internal use and demo purposes to bypass the API and connect directly to Azure Storage.

## ⚠️ Important Notice

**This functionality is for internal use only and should not be used in production by external users.** It requires direct access to Azure Storage credentials and bypasses the standard API authentication and authorization mechanisms.

## Features

### 1. Direct URL Access (`__url` parameter)

Access datasets directly via Azure Storage URLs with SAS tokens or public access.

```python
import pixcrawler as pix

# Direct URL access (for JSON data)
dataset = pix.dataset(
    "dataset-id-123", 
    __url="https://storage.blob.core.windows.net/datasets/dataset_123.json?sv=2021-06-08&ss=b&srt=sco&sp=r&se=2024-12-31T23:59:59Z&st=2024-01-01T00:00:00Z&spr=https&sig=..."
)

# Load data directly from Azure
data = dataset.load()

# Or download ZIP directly
path = dataset.download("./dataset.zip")
```

### 2. Azure Configuration (`__azure` parameter)

Use Azure Storage SDK for direct blob access with various authentication methods.

```python
import pixcrawler as pix
from pixcrawler import AzureConfig

# Method 1: Connection String
azure_config = AzureConfig(
    connection_string="DefaultEndpointsProtocol=https;AccountName=pixcrawler;AccountKey=your_key==;EndpointSuffix=core.windows.net",
    container_name="datasets"
)

# Method 2: Account Name + Key
azure_config = AzureConfig(
    account_name="pixcrawler",
    account_key="your_account_key==",
    container_name="datasets"
)

# Method 3: Account Name + SAS Token
azure_config = AzureConfig(
    account_name="pixcrawler",
    sas_token="sv=2021-06-08&ss=b&srt=sco&sp=r&se=2024-12-31T23:59:59Z&st=2024-01-01T00:00:00Z&spr=https&sig=...",
    container_name="datasets"
)

# Use with dataset
dataset = pix.dataset("dataset-id-123", __azure=azure_config)
data = dataset.load()

# Use with project (passes config to all datasets)
project = pix.project("project-id-456", __azure=azure_config)
dataset = project.dataset("dataset-id-789")  # Inherits Azure config
```

## Configuration Options

### AzureConfig Class

```python
@dataclass
class AzureConfig:
    """Azure Storage configuration for direct blob access."""
    
    connection_string: Optional[str] = None
    account_name: Optional[str] = None
    account_key: Optional[str] = None
    sas_token: Optional[str] = None
    container_name: str = "datasets"
```

#### Authentication Methods (Priority Order)

1. **Connection String**: Complete connection string with all credentials
2. **Account Name + Key**: Storage account name and access key
3. **Account Name + SAS Token**: Storage account name and SAS token

#### Required Dependencies

```bash
pip install azure-storage-blob>=12.0.0
```

## Blob Naming Conventions

The SDK expects specific blob naming patterns in Azure Storage:

- **JSON Data**: `dataset_{dataset_id}.json`
- **ZIP Archives**: `dataset_{dataset_id}.zip`

Example:
- Dataset ID: `123` → JSON blob: `dataset_123.json`, ZIP blob: `dataset_123.zip`

## Usage Examples

### Example 1: Development Environment

```python
import pixcrawler as pix
from pixcrawler import AzureConfig

# Development Azure Storage
azure_config = AzureConfig(
    connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    container_name="dev-datasets"
)

# Load dataset directly
dataset = pix.dataset("dev-dataset-001", __azure=azure_config)
data = dataset.load()

print(f"Loaded {len(data)} items from Azure Storage")
```

### Example 2: Demo with Direct URLs

```python
import pixcrawler as pix

# Demo URLs with SAS tokens
json_url = "https://demostorage.blob.core.windows.net/datasets/demo_001.json?sv=..."
zip_url = "https://demostorage.blob.core.windows.net/datasets/demo_001.zip?sv=..."

# Load JSON data
dataset = pix.dataset("demo-001", __url=json_url)
data = dataset.load()

# Download ZIP archive
dataset_zip = pix.dataset("demo-001", __url=zip_url)
path = dataset_zip.download("./demo_dataset.zip")
```

### Example 3: Project-Level Configuration

```python
import pixcrawler as pix
from pixcrawler import AzureConfig

# Configure Azure for entire project
azure_config = AzureConfig(
    account_name="pixcrawler",
    account_key=os.getenv("AZURE_ACCOUNT_KEY"),
    container_name="production-datasets"
)

# All datasets in project use Azure config
project = pix.project("prod-project-001", __azure=azure_config)

# These datasets inherit the Azure configuration
dataset1 = project.dataset("dataset-001")
dataset2 = project.dataset("dataset-002")

# Load data directly from Azure
data1 = dataset1.load()
data2 = dataset2.load()
```

## Error Handling

### Common Errors

1. **Missing Azure SDK**:
   ```python
   PixCrawlerError: Azure Storage SDK not available. Install with: pip install azure-storage-blob
   ```

2. **Incomplete Configuration**:
   ```python
   PixCrawlerError: Azure configuration incomplete. Provide either connection_string or (account_name + account_key) or (account_name + sas_token)
   ```

3. **Blob Not Found**:
   ```python
   PixCrawlerError: Direct load failed: The specified blob does not exist.
   ```

4. **Memory Limit Exceeded**:
   ```python
   RuntimeError: Dataset size (450.2MB) exceeds memory limit (300MB)
   ```

### Error Handling Example

```python
import pixcrawler as pix
from pixcrawler import AzureConfig, PixCrawlerError

try:
    azure_config = AzureConfig(
        connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
        container_name="datasets"
    )
    
    dataset = pix.dataset("dataset-123", __azure=azure_config)
    data = dataset.load()
    
except PixCrawlerError as e:
    print(f"SDK Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Security Considerations

### 🔒 Security Best Practices

1. **Environment Variables**: Store credentials in environment variables, never in code
2. **SAS Tokens**: Use time-limited SAS tokens with minimal permissions
3. **Network Security**: Use HTTPS endpoints only
4. **Access Control**: Limit blob access to specific IP ranges when possible

### Example Secure Configuration

```python
import os
from pixcrawler import AzureConfig

# ✅ SECURE: Use environment variables
azure_config = AzureConfig(
    connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    container_name=os.getenv("AZURE_CONTAINER_NAME", "datasets")
)

# ❌ INSECURE: Hardcoded credentials
azure_config = AzureConfig(
    connection_string="DefaultEndpointsProtocol=https;AccountName=pixcrawler;AccountKey=hardcoded_key==",
    container_name="datasets"
)
```

## Performance Considerations

### Memory Management

- **300MB Limit**: Enforced for in-memory loading to prevent memory exhaustion
- **Streaming Downloads**: Large files are downloaded in chunks
- **Blob Properties**: Size is checked before download when possible

### Network Optimization

- **Direct Access**: Bypasses API server for faster downloads
- **Azure CDN**: Can be used with direct URLs for global distribution
- **Parallel Downloads**: Multiple datasets can be downloaded concurrently

## Limitations

1. **Internal Use Only**: Not intended for external production use
2. **Azure Storage Only**: Only works with Azure Blob Storage
3. **Naming Convention**: Requires specific blob naming patterns
4. **Memory Limits**: 300MB limit for in-memory operations
5. **No API Features**: Bypasses API-level features like rate limiting, analytics, etc.

## Migration Path

If you need to migrate from direct Azure access to standard API:

```python
# Before (direct Azure access)
azure_config = AzureConfig(connection_string="...")
dataset = pix.dataset("dataset-123", __azure=azure_config)

# After (standard API)
pix.auth(token="your_api_key")
dataset = pix.dataset("dataset-123")
```

## Support

For internal support with Azure direct access:
- Check Azure Storage connection and permissions
- Verify blob naming conventions
- Ensure Azure SDK is installed and up to date
- Review security configurations and SAS token expiration

---

**Version**: 0.2.0.dev1  
**Last Updated**: January 2025  
**Status**: Internal Use Only