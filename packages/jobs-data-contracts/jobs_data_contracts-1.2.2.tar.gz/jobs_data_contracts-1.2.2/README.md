# Jobs Data Contracts

Canonical data contracts and schemas for the CS Jobs Board solution. This repository serves as the single source of truth for all data structures used across the Jobs Board ecosystem.

## Overview

This repository contains OpenAPI/JSON Schema definitions that are used to generate:
- **TypeScript types** for Next.js and Node.js applications
- **Python Pydantic models** for FastAPI applications

The generated exports ensure consistency across all applications in the Jobs Board platform.

## Repository Structure

```
.
├── schemas/                    # OpenAPI and JSON Schema definitions
│   ├── jobs/                  # Jobs API service schemas
│   │   └── openapi.yaml
│   └── search/                # Search API service schemas
│       └── openapi.yaml
├── generated/                 # Auto-generated code (do not edit manually)
│   ├── typescript/            # TypeScript types
│   │   ├── jobs.ts           # Generated from jobs/openapi.yaml
│   │   ├── search.ts         # Generated from search/openapi.yaml
│   │   └── src/              # Auto-generated TypeScript entry points
│   └── python/               # Python Pydantic models
│       ├── jobs/
│       └── search/
├── scripts/                   # Generation scripts
│   ├── generate_pydantic.sh  # Generate Pydantic models
│   └── generate-src-files.js # Auto-generate TypeScript src/ files
└── dist/                      # Compiled TypeScript output (excluded from git)
```

---

## TypeScript/JavaScript Usage

### Installation

Install the package from npm:

```bash
npm install jobs-data-contracts
```

Or with yarn:

```bash
yarn add jobs-data-contracts
```

### Usage

Import commonly used types directly:

```typescript
import { 
  Job, 
  JobResultItem, 
  JobSearchResponse, 
  Approach, 
  Grade, 
  Profession,
  Salary,
  FixedLocation,
  OverseasLocation 
} from 'jobs-data-contracts';
```

For more granular imports:

```typescript
// Search API types
import { SearchComponents, SearchPaths, SearchOperations } from 'jobs-data-contracts/search';

// Jobs API types
import { JobsComponents, JobsPaths, JobsOperations } from 'jobs-data-contracts/jobs';
```

### Available Type Exports

| Export | Description |
|--------|-------------|
| `Job` | Full job object for indexing |
| `JobResultItem` | Compact job result in search responses |
| `JobSearchResponse` | Search API response with pagination |
| `FixedLocation` | UK location with address details |
| `OverseasLocation` | International location |
| `Salary` | Salary range and currency |
| `Contacts` | Contact information |
| `Approach` | Enum: Internal, Across Government, External |
| `Assignments` | Enum: Apprentice, FTA, Loan, Secondment, Permanent |
| `Grade` | Enum: Civil Service grades |
| `Profession` | Enum: Civil Service professions |
| `Error` | Error response type |

---

## Python/Pydantic Usage

### Installation

```bash
pip install jobs-data-contracts
```

### Usage

Import and use Pydantic models in your FastAPI application:

```python
from fastapi import FastAPI
from jobs_data_contracts import Job, JobSearchResponse

app = FastAPI()

@app.post("/jobs", response_model=Job)
async def create_job(job: Job):
    return job  # Automatic validation

@app.get("/search", response_model=JobSearchResponse)
async def search_jobs():
    return JobSearchResponse(results=[], total=0, page=1, pageSize=10, totalPages=0)
```

All models provide automatic validation, type safety, and serialization via Pydantic v2.

---

## Development

### Prerequisites

- **For TypeScript**: Node.js >= 18
- **For Python**: Python >= 3.8

### Setup

```bash
npm install
```

### Generating Types

**TypeScript:**

The TypeScript generation process is fully automated. When you modify schemas, simply run:

```bash
npm run generate:typescript
```

This command will:
1. Generate TypeScript types from OpenAPI schemas (`jobs.ts`, `search.ts`)
2. Automatically create re-export files in `generated/typescript/src/`
3. Export all schema types for convenient use in your applications

You can also run individual steps:
```bash
npm run generate:jobs      # Generate types from jobs/openapi.yaml
npm run generate:search    # Generate types from search/openapi.yaml
npm run generate:src       # Auto-generate src/ re-export files
```

**Python:**
```bash
npm run generate:python
# Or: ./scripts/generate_pydantic.sh
```

Generated models are placed in `generated/` directory.

**Note:** The `generated/typescript/src/` files are now auto-generated. You no longer need to manually edit these files when schemas change!

### Building

**TypeScript:**
```bash
npm run build
```

**Python:**
```bash
npm run generate:python
python -m build
```

### Testing

```bash
npm test  # TypeScript type checking
```

---

## Publishing

### TypeScript to npm

```bash
npm run build
npm publish
```

### Python to PyPI

```bash
npm run generate:python
pip install build twine
python -m build
python -m twine upload dist/*.whl dist/*.tar.gz
```

**Note:** Use the specific file patterns (`dist/*.whl dist/*.tar.gz`) to avoid uploading TypeScript files that may be present in the `dist/` directory.

## Versioning

This repository follows [Semantic Versioning](https://semver.org/):

- **Major**: Breaking changes to schemas or generated types
- **Minor**: New schemas or backward-compatible additions
- **Patch**: Documentation updates, bug fixes in generation scripts

## Contributing

1. **Schema Changes**: All schema modifications should be made in the `schemas/` directory
2. **Generation**: After schema changes, run generation scripts to update types
3. **Testing**: Run `npm test` to verify types compile correctly
4. **Documentation**: Update this README if adding new types or changing usage

### Schema Guidelines

- Use clear, descriptive property names
- Include descriptions for all schemas and properties
- Define validation rules (min/max, patterns, required fields)
- Use appropriate data types and formats
- Leverage `$ref` for reusable components
- Follow OpenAPI 3.x best practices

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions or issues, please open a GitHub issue.