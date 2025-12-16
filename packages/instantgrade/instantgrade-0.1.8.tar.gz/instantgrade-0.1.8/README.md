<div align="center">
  <img src="https://raw.githubusercontent.com/chandraveshchaudhari/personal-information/bf3d602dbbf0b7d0bbe6461351c163144b617d24/logos/my%20github%20logo%20template-python%20project%20template%20small.png" width="640" height="320">
</div>

# InstantGrade
> An automated evaluation framework for Python notebooks and Excel assignments

[![PyPI version](https://badge.fury.io/py/instantgrade.svg)](https://pypi.org/project/instantgrade/)
[![Python](https://img.shields.io/pypi/pyversions/instantgrade.svg)](https://pypi.org/project/instantgrade/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://chandraveshchaudhari.github.io/instantgrade/)
[![CI](https://github.com/chandraveshchaudhari/instantgrade/workflows/Test%20Package%20Build/badge.svg)](https://github.com/chandraveshchaudhari/instantgrade/actions)
[![codecov](https://codecov.io/gh/chandraveshchaudhari/instantgrade/branch/master/graph/badge.svg)](https://codecov.io/gh/chandraveshchaudhari/instantgrade)

---

## 📚 Documentation

**[Read the full documentation →](https://chandraveshchaudhari.github.io/instantgrade/)**

- **[Installation Guide](https://chandraveshchaudhari.github.io/instantgrade/installation.html)** - Get started in minutes
- **[Quick Start](https://chandraveshchaudhari.github.io/instantgrade/quickstart.html)** - Your first evaluation
- **[Usage Guide](https://chandraveshchaudhari.github.io/instantgrade/usage.html)** - Comprehensive features
- **[API Reference](https://chandraveshchaudhari.github.io/instantgrade/api.html)** - Complete API documentation
- **[Examples](https://chandraveshchaudhari.github.io/instantgrade/examples.html)** - Real-world use cases

---

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Supported File Types](#supported-file-types)
- [Contribution](#contribution)
- [Future Improvements](#future-improvements)

## Introduction
InstantGrade is a comprehensive, extensible evaluation framework designed to automatically grade student submissions against instructor solution files. It supports multiple file formats including Python Jupyter notebooks and Excel files, making it ideal for educational institutions and online learning platforms.

The framework was created to streamline the grading process for programming and data analysis assignments, reducing manual effort while providing detailed, actionable feedback to students. The vision is to expand support to additional file types and programming languages, creating a universal evaluation platform for technical education. 


## 👩‍🏫 About the Maintainer

**Dr. Chandravesh Chaudhari**

📧 [chandraveshchaudhari@gmail.com](mailto:chandraveshchaudhari@gmail.com)
🌐 [Website](https://chandraveshchaudhari.github.io/website/)
🔗 [LinkedIn](https://www.linkedin.com/in/chandraveshchaudhari)


## Features
- **Automated Evaluation**: Compare student submissions against instructor solutions automatically
- **Multiple File Format Support**: Currently supports Python Jupyter notebooks (.ipynb) and Excel files (.xlsx, .xls)
- **Comprehensive Reporting**: Generate detailed HTML reports with visual feedback and scoring
- **AST Analysis**: Deep code comparison using Abstract Syntax Tree analysis for Python code
- **Flexible Configuration**: Customizable evaluation criteria through JSON configuration
- **Batch Processing**: Evaluate multiple student submissions in one run
- **Extensible Architecture**: Easy to add support for new file types and evaluation strategies

#### Significance
- **Time-Saving**: Reduces manual grading effort by 90% for programming assignments
- **Consistency**: Ensures uniform evaluation criteria across all student submissions
- **Detailed Feedback**: Provides students with specific areas of improvement
- **Scalability**: Handles large classes with hundreds of submissions efficiently
- **Educational Focus**: Allows instructors to focus on teaching rather than repetitive grading tasks

## Installation 
This project is available at [PyPI](https://pypi.org/project/instantgrade/). For help in installation check 
[instructions](https://packaging.python.org/tutorials/installing-packages/#installing-from-pypi)
```bash
python3 -m pip install instantgrade  
```

For development installation:
```bash
git clone https://github.com/chandraveshchaudhari/instantgrade.git
cd evaluator
python3 -m pip install -e .
```

### Dependencies
##### Required
- [pandas](https://pandas.pydata.org/) - Data manipulation and analysis for comparison results
- [openpyxl](https://openpyxl.readthedocs.io/) - Reading and writing Excel files
- [nbformat](https://nbformat.readthedocs.io/) - Working with Jupyter notebook files
- [nbclient](https://nbclient.readthedocs.io/) - Executing Jupyter notebooks programmatically
- [click](https://click.palletsprojects.com/) - Creating command-line interfaces

##### Optional
- [xlwings](https://www.xlwings.org/) - Advanced Excel automation capabilities (Windows/macOS only)

## Usage

### Basic Usage

#### Python API
```python
from instantgrade import Evaluator

# Initialize evaluator with solution and submissions folder
evaluator = Evaluator(
    solution_file_path="path/to/solution.ipynb",
    submission_folder_path="path/to/submissions/"
)

# Run complete evaluation pipeline
report = evaluator.run()
```

#### Command Line Interface
```bash
# Evaluate Python notebook submissions
instantgrade --solution sample_solutions.ipynb --submissions ./submissions/ --output ./report/

# Evaluate Excel submissions
instantgrade --solution solution.xlsx --submissions ./excel_submissions/ --output ./excel_report/
```

## Supported File Types

### Python Jupyter Notebooks (.ipynb)
- Executes code cells and compares outputs
- AST-based code structure comparison
- Variable and function definition verification
- Exception and error handling analysis

### Excel Files (.xlsx, .xls)
- Cell value comparison across worksheets
- Formula evaluation and verification
- Conditional formatting checks
- Chart and pivot table analysis (with xlwings)

### Future Support (Planned)
- R Markdown files (.Rmd)
- Python scripts (.py)
- SQL files (.sql)
- MATLAB scripts (.m)

## Important links
- [Documentation](https://github.com/chandraveshchaudhari/instantgrade/wiki)
- [Quick tour](https://github.com/chandraveshchaudhari/instantgrade/blob/master/data/python_example1/basic_python_flow.ipynb)
- [Project maintainer (feel free to contact)](mailto:chandraveshchaudhari@gmail.com?subject=[GitHub]%20Evaluator) 
- [Future Improvements](https://github.com/chandraveshchaudhari/instantgrade/projects)
- [License](https://github.com/chandraveshchaudhari/instantgrade/blob/master/LICENSE.txt)

## Contribution
All kinds of contributions are appreciated:
- [Improving readability of documentation](https://github.com/chandraveshchaudhari/instantgrade/wiki)
- [Feature Request](https://github.com/chandraveshchaudhari/instantgrade/issues/new/choose)
- [Reporting bugs](https://github.com/chandraveshchaudhari/instantgrade/issues/new/choose)
- [Contribute code](https://github.com/chandraveshchaudhari/instantgrade/compare)
- [Asking questions in discussions](https://github.com/chandraveshchaudhari/instantgrade/discussions)

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

For detailed contribution guidelines, see the [Contributing Guide](https://chandraveshchaudhari.github.io/instantgrade/contributing.html).

## Documentation

Complete documentation is available at **[chandraveshchaudhari.github.io/instantgrade](https://chandraveshchaudhari.github.io/instantgrade/)**

### Building Documentation Locally

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build the documentation
cd docs
make html

# View the documentation
open build/html/index.html  # macOS
# or
xdg-open build/html/index.html  # Linux
# or
start build/html/index.html  # Windows
```

The documentation is built using:
- **Sphinx** - Documentation engine
- **MyST Parser** - Markdown support
- **Furo** - Clean, modern theme
- **Jupyter-Sphinx** - Notebook integration
- **Sphinx Autodoc** - Automatic API documentation

## Development & Deployment

### Continuous Integration
This project uses GitHub Actions for continuous integration and deployment:
- **Automated Testing**: Every push is automatically tested across multiple Python versions (3.10-3.12) and operating systems
- **Automatic PyPI Publishing**: New releases are automatically published to PyPI when version tags are pushed
- **Documentation Deployment**: Documentation is automatically built and deployed to GitHub Pages
- **Build Verification**: Package builds are verified before deployment

### Publishing New Versions
To publish a new version to PyPI:

1. Update the version number in `setup.py` and `pyproject.toml`
2. Update `CHANGELOG.md` with the new version
3. Commit the changes:
   ```bash
   git add setup.py pyproject.toml CHANGELOG.md
   git commit -m "Bump version to X.Y.Z"
   ```
4. Create and push a version tag:
   ```bash
   git tag vX.Y.Z
   git push origin master
   git push origin vX.Y.Z
   ```
5. GitHub Actions will automatically:
   - Build and publish to PyPI
   - Create a GitHub Release
   - Deploy updated documentation

For detailed instructions, see [PUBLISHING.md](PUBLISHING.md)

### CI/CD Status
![Test Package Build](https://github.com/chandraveshchaudhari/instantgrade/actions/workflows/test.yml/badge.svg)
![Publish to PyPI](https://github.com/chandraveshchaudhari/instantgrade/actions/workflows/publish.yml/badge.svg)
![Documentation](https://github.com/chandraveshchaudhari/instantgrade/actions/workflows/docs.yml/badge.svg)


