# Feature Request: PhysioNet Dataset Validator

## Overview
Add a pre-submission validation tool (`physionet validate`) that helps contributors verify their datasets before uploading to PhysioNet. This tool would catch common issues early, reduce submission rejections, and improve overall data quality.

## Motivation
- Contributors currently don't have a way to validate their data locally before submission
- Many submissions are rejected for preventable issues (missing files, PHI, formatting problems)
- Early detection of issues saves time for both contributors and PhysioNet reviewers
- Improves consistency and quality of submitted datasets

## Proposed Functionality

### Core Validation Checks

#### 1. File System & Organization
- [ ] Verify required files exist (README.md at minimum)
- [ ] Check for valid file naming conventions (no special characters, reasonable path lengths)
- [ ] Detect version control artifacts (.git, .DS_Store, .pyc, __pycache__, etc.)
- [ ] Flag unexpected file sizes (very large or zero-byte files)
- [ ] Calculate and report total dataset size
- [ ] Warn if excessive number of small files (suggest consolidation)
- [ ] Identify compression opportunities

#### 2. Documentation & Metadata
- [ ] Check README has recommended sections (background, methods, data description, usage notes, references)
- [ ] Validate citation.txt format if present
- [ ] Verify completeness of required metadata fields
- [ ] Check for proper acknowledgements and conflict of interest statements

#### 3. Data Integrity & Format Validation
- [ ] Validate file formats (CSV structure, WFDB signal integrity, DICOM headers, etc.)
- [ ] Verify subject/record ID consistency across files
- [ ] Check referential integrity between related files (IDs referenced in one file exist in another)
- [ ] Detect character encoding issues
- [ ] Validate CSV headers and column consistency
- [ ] Check domain-specific standards compliance (WFDB, DICOM, HL7 where applicable)

#### 4. Data Quality & Plausibility
- [ ] Detect excessive missing values (by column/file)
- [ ] Check data type consistency within columns
- [ ] Verify temporal consistency (monotonic timestamps, valid date ranges)
- [ ] Flag biologically/clinically implausible values (configurable ranges, e.g., heart rate >300, negative ages)
- [ ] Identify outliers or anomalous distributions
- [ ] Check for duplicate records

#### 5. Privacy & De-identification
- [ ] Scan for PHI patterns (full dates, potential MRNs, email addresses, phone numbers, zip codes)
- [ ] Verify ages >89 are de-identified per HIPAA requirements
- [ ] Flag suspicious date patterns that might not be properly shifted
- [ ] Detect potential names or common identifiers
- [ ] Warn about free-text fields that may contain identifiable information
- [ ] Check for IP addresses or device identifiers

## Proposed API

### Command Line Interface
```bash
# Validate a dataset directory
physionet validate /path/to/dataset

# Generate detailed report
physionet validate /path/to/dataset --report report.json

# Run specific check categories only
physionet validate /path/to/dataset --checks phi,integrity

# Set severity threshold
physionet validate /path/to/dataset --level error  # only show errors, not warnings

# Specify dataset type for specialized checks
physionet validate /path/to/dataset --type waveform  # applies WFDB-specific checks
```

### Python API
```python
from physionet.validate import validate_dataset, ValidationConfig

# Basic validation
results = validate_dataset('/path/to/dataset')
print(results.summary())

# Custom configuration
config = ValidationConfig(
    check_phi=True,
    phi_patterns=['custom_pattern'],
    allowed_age_max=89,
    value_ranges={'heart_rate': (20, 300), 'temperature': (32, 43)}
)
results = validate_dataset('/path/to/dataset', config=config)

# Programmatic access to results
for issue in results.errors:
    print(f"{issue.file}:{issue.line} - {issue.message}")
```

## Output Format

### Console Output
```
PhysioNet Dataset Validation Report
===================================
Dataset: /path/to/my-dataset
Total size: 2.3 GB (142 files)

✓ File System & Organization (1 warning)
  ⚠ Found version control files: .git/

✓ Documentation & Metadata (2 warnings)
  ⚠ README.md missing 'Conflicts of Interest' section
  ⚠ No citation.txt file found

✓ Data Integrity & Format (0 issues)

✓ Data Quality & Plausibility (1 warning)
  ⚠ data/vitals.csv:234 - Heart rate value 312 exceeds typical maximum (300)

✗ Privacy & De-identification (1 error, 1 warning)
  ✗ data/patients.csv:45 - Potential full date found: 2023-05-15
  ⚠ data/notes.txt contains free-text fields - manual review recommended

Summary: 1 error, 5 warnings
⚠ Dataset has issues that should be addressed before submission
```

### JSON Report
```json
{
  "dataset_path": "/path/to/my-dataset",
  "timestamp": "2025-12-05T10:30:00Z",
  "version": "0.2.0",
  "dataset_stats": {
    "total_size_bytes": 2469606195,
    "file_count": 142,
    "directory_count": 8
  },
  "summary": {
    "total_errors": 1,
    "total_warnings": 5,
    "total_info": 2,
    "status": "warn"
  },
  "checks": {
    "filesystem": {
      "status": "warn",
      "issues": [
        {
          "severity": "warning",
          "category": "filesystem",
          "message": "Found version control files: .git/",
          "suggestion": "Remove .git directory before submission"
        }
      ]
    },
    "phi": {
      "status": "error",
      "issues": [
        {
          "severity": "error",
          "category": "phi",
          "file": "data/patients.csv",
          "line": 45,
          "column": "admission_date",
          "value": "2023-05-15",
          "message": "Potential full date found",
          "suggestion": "Use year-only or date-shifted values"
        }
      ]
    }
  }
}
```

## Implementation Approach

### Phase 1: Core Framework & File System
- Set up basic validation framework and reporting structure
- Implement CLI with `physionet validate` subcommand
- Add file system checks (required files, naming conventions, size analysis)
- Basic CSV parsing and format validation

### Phase 2: Data Integrity & Quality
- Implement subject/record ID consistency checks
- Add referential integrity validation
- Missing value detection
- Data type consistency checks
- Configurable value range validation

### Phase 3: Privacy & PHI Detection
- Implement PHI pattern detection (regex-based initially)
- Add age de-identification checks
- Date pattern scanning
- Free-text field warnings

### Phase 4: Advanced Features & Domain-Specific
- WFDB signal validation
- DICOM header checks
- Configurable custom checks and plugins
- Dataset type profiles (clinical, waveform, imaging)
- Integration with CI/CD workflows

## Open Questions
1. Should we provide auto-fix suggestions or scripts for common issues?
2. What should the default PHI patterns include? How aggressive should detection be?
3. Should we support custom validation plugins or configuration files?
4. Do we need dataset-type-specific profiles (clinical, waveform, imaging)?
5. Should validation rules be configurable via a .physionet-validation.yml file?

## Success Metrics
- Reduction in submission rejection rate due to preventable issues
- User adoption (package downloads, CLI usage analytics)
- Community feedback and contributions
- Coverage of common submission issues identified by PhysioNet reviewers
