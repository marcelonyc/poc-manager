# POC Manager Documentation

End-user documentation for POC Manager, built with MkDocs Material.

## Setup

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Install dependencies:

```bash
pip install -r docs-requirements.txt
```

## Usage

### Local Development

To serve the documentation locally:

```bash
mkdocs serve
```

Then open http://127.0.0.1:8000 in your browser.

### Building Static Site

To build the static documentation site:

```bash
mkdocs build
```

The built site will be in the `site/` directory.

### Deploying

To deploy to GitHub Pages:

```bash
mkdocs gh-deploy
```

## Documentation Structure

```
docs/
├── index.md                    # Home page
├── getting-started/           # Getting started guides
│   ├── overview.md
│   ├── login.md
│   └── roles.md
├── platform-admin/            # Platform admin guides
│   └── tenants.md
├── tenant-admin/              # Tenant admin guides
│   ├── users.md
│   └── settings.md
├── administrator/             # Administrator guides
│   ├── task-templates.md
│   ├── creating-pocs.md
│   └── managing-pocs.md
├── sales-engineer/            # Sales engineer guides
│   ├── poc-overview.md
│   ├── inviting-customers.md
│   ├── managing-tasks.md
│   ├── adding-resources.md
│   └── tracking-progress.md
├── customer/                  # Customer guides
│   ├── viewing-pocs.md
│   ├── providing-feedback.md
│   └── task-completion.md
└── features/                  # Feature guides
    ├── dashboard.md
    ├── comments.md
    ├── documents.md
    └── resources.md
```

## Contributing

To add or update documentation:

1. Edit the relevant `.md` file in the `docs/` directory
2. Preview changes with `mkdocs serve`
3. Commit and push your changes

## Features

- **Material Design**: Modern, responsive theme
- **Search**: Full-text search across all documentation
- **Dark Mode**: Automatic dark/light mode switching
- **Navigation**: Tabbed navigation with sections
- **Code Highlighting**: Syntax highlighting for code blocks
- **Admonitions**: Call-out boxes for tips, warnings, etc.
- **Tabs**: Tabbed content for alternative information

## Configuration

Documentation is configured in `mkdocs.yml` in the project root.

Key configuration sections:

- `nav`: Navigation structure
- `theme`: Material theme settings
- `plugins`: Enabled plugins
- `markdown_extensions`: Extended markdown features
