# ABRomics Lightweight Python SDK

A lightweight Python SDK for interacting with the ABRomics API, including resumable file uploads via TUS protocol.


## Installation

### From PyPI (Recommended)
```bash
pip install abromics-library
```

### From Source
```bash
git clone https://gitlab.com/ifb-elixirfr/abromics/abromics-library.git
cd abromics-library
pip install -e .
```

### Prerequisites
- Python 3.8+
- ABRomics backend running
- API key with `complete_workflow_upload` scope

## Quick Start

### 1. Get Your API Key
1. Go to your ABRomics web interface
2. Navigate to the API Keys page
3. Create a new API key with scope `complete_workflow_upload`
4. Copy the API key (starts with `abk_`)

### 2. Set Environment Variables (Optional)
```bash
export ABROMICS_API_KEY="abk_your_api_key_here"
export ABROMICS_BASE_URL="http://localhost:8000"  # Your ABRomics backend URL
```

## Usage

### Command Line Interface (CLI)

The ABRomics CLI provides essential commands for managing projects and uploading data:

| Command | Description |
|---------|-------------|
| `project create` | Create a new project |
| `complete-upload-workflow` | Complete workflow: TSV processing + file uploads |

#### Create Project
```bash
# Create a new FASTQ project
abromics --api-key "abk_your_api_key_here" --base-url "https://analysis.abromics.fr" project create \
  --name "My FASTQ Project" \
  --template 1 \
  --description "Optional project description"

# Create a new FASTA project
abromics --api-key "abk_your_api_key_here" --base-url "https://analysis.abromics.fr" project create \
  --name "My FASTA Project" \
  --template 2 \
  --description "Optional project description"
```

**Parameters:**
- `--name` - Project name (required)
- `--template` - Template ID (required): 1 for FASTQ, 2 for FASTA
- `--description` - Project description (optional)

#### Complete Workflow
```bash
# One command does everything: validates TSV, creates samples, uploads files
abromics complete-upload-workflow \
  --metadata-tsv "/path/to/samples_fastq_projects.tsv" \
  --data-dir "/path/to/sequence/files"
```

**What this command does:**
- ✅ Auto-detects file types (FASTQ/FASTA)
- ✅ Creates samples from TSV metadata
- ✅ Uploads sequence files to samples
- ✅ Handles multiple projects automatically

### Python Library

#### Basic Usage
```python
from abromics import AbromicsClient

# Initialize client
client = AbromicsClient(
    api_key="abk_your_api_key_here",
    base_url="http://localhost:8000"
)

# Step 1: Create project (template 1 for FASTQ, 2 for FASTA)
project = client.projects.create(
    name="My FASTQ Project",
    template=1,
    description="Project for FASTQ sequencing data"
)

# Step 2: Complete workflow (auto-detects file types)
result = client.batch.process_tsv_and_upload(
    project_id=project.id,
    tsv_file="samples_metadata.tsv",
    files_directory="/path/to/sequence/files"
)

if result['success']:
    print("✅ Workflow completed successfully!")
```

#### Advanced Usage
```python
# Individual operations
sample = client.samples.create(
    project_id=project.id,
    metadata={
        "Sample ID": "SAMPLE_001",
        "Host species": "Homo sapiens",
        "Microorganism scientific name": "Escherichia coli",
        "Country": "France"
    }
)

# File upload with progress tracking
def progress_callback(message, current, total):
    print(f"{message}: {current}/{total}")

uploader = client.upload.create_uploader()
result = uploader.upload_file(
    file_path="/path/to/sequence.fastq.gz",
    metadata={
        "sample_id": str(sample.id),
        "file_type": "FASTQ_GZ",
        "type": "PAIRED_FORWARD"
    },
    progress_callback=progress_callback
)
```

## TSV File Format

The TSV file should contain sample metadata with these columns:

### Required Fields (marked with *)
- `Sample ID *` - Unique sample identifier
- `Strain ID *` - Unique strain identifier  
- `Host species *` - Host species name
- `Microorganism scientific name *` - Scientific name of microorganism
- `Country *` - Country where sample was collected
- `Sample type *` - Type of sample
- `Sample source *` - Source of the sample
- `Instrument model *` - Sequencing instrument model
- `Collected date *` - Date when sample was collected
- `Project Name *` - Name of the project

### File Type Fields (one of these)
- `R1 fastq filename *` + `R2 fastq filename *` - For FASTQ files
- `Fasta filename *` - For FASTA files

### Optional Fields
- `Region` - Region where sample was collected
- `Place` - Specific place where sample was collected
- `Travel countries` - Countries visited before collection
- `Accession number` - Public database accession number
- `Sample comment` - Additional comments about the sample

### Example TSV
```tsv
Sample ID *	Strain ID *	R1 fastq filename *	R2 fastq filename *	Host species *	Microorganism scientific name *	Country *	Project Name *
SAMPLE_001	ST-001	sample_R1.fastq.gz	sample_R2.fastq.gz	Homo sapiens	Escherichia coli	France	My Project
```

## Examples

### CLI Examples
```bash
# Create a FASTQ project first
abromics --api-key "abk_your_api_key_here" --base-url "https://analysis.abromics.fr" project create \
  --name "My FASTQ Project" \
  --template 1 \
  --description "Project for FASTQ sequencing data"

# Or create a FASTA project
abromics --api-key "abk_your_api_key_here" --base-url "https://analysis.abromics.fr" project create \
  --name "My FASTA Project" \
  --template 2 \
  --description "Project for FASTA assembly data"

# Complete workflow (TSV + file uploads)
abromics complete-upload-workflow \
  --metadata-tsv "examples/samples_fastq_projects.tsv" \
  --data-dir "examples/sequence_files/"
```

### Python Examples
```bash
# Run the example script
python examples/python_library_example.py
```

## Configuration

### Environment Variables
```bash
export ABROMICS_API_KEY="abk_your_api_key_here"        # Required
export ABROMICS_BASE_URL="http://localhost:8000"       # Optional
```

### Priority Order
1. Command-line arguments (`--api-key`, `--base-url`)
2. Environment variables (`ABROMICS_API_KEY`, `ABROMICS_BASE_URL`)
3. Default values (base URL only)

## API Reference

### Client
```python
client = AbromicsClient(api_key, base_url, timeout)
```

### Projects
```python
# Create FASTQ project
project = client.projects.create(
    name="My FASTQ Project",
    template=1,  # Template 1 for FASTQ, 2 for FASTA
    description="Optional description"
)

# Create FASTA project
project = client.projects.create(
    name="My FASTA Project",
    template=2,  # Template 1 for FASTQ, 2 for FASTA
    description="Optional description"
)

# List projects
projects = client.projects.list()

# Get project
project = client.projects.get(project_id)
```

### Samples
```python
# Create sample
sample = client.samples.create(project_id, metadata)

# List samples
samples = client.samples.list(project_id=1)

# Get sample
sample = client.samples.get(sample_id)
```

### Batch Operations
```python
# Complete workflow
result = client.batch.process_tsv_and_upload(
    project_id, tsv_file, files_directory
)
```

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure you have a valid API key with the correct scope
2. **File Not Found**: Check that TSV file and data directory paths are correct
3. **Connection Error**: Ensure the ABRomics backend is running on the specified URL
4. **Permission Error**: Verify your API key has the `complete_workflow_upload` scope
5. **Mixed File Types**: Don't mix FASTQ and FASTA files in the same directory

### Getting Help

- Check the main library documentation above
- Verify your TSV file structure matches the expected format
- Ensure all required fields are present and non-empty
- Check that sequence files exist in the specified directory

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Run CLI
python -m abromics.cli --help
```

## Publishing

For instructions on how to publish a new version to PyPI, see [HowToPublish.md](HowToPublish.md).
## License

MIT License