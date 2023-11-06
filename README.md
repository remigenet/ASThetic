# AST-Based Code Analysis for Selective Imports

## Introduction

This project, ASThetic, is a foray into refining Python code efficiency via Abstract Syntax Trees (ASTs). The goal is to provide tools that not only streamline imports by loading only essential components from large modules but also explore advanced code dissection and the potential for subsequent Cythonization. This could significantly reduce overhead and improve the performance of Python applications. Given that this project is in the developmental phase, the doors are open for collaboration to enhance its features.

## Current Feature

- **Selective Imports**: There's a tool in development that analyzes a codebase to detect which specific functions or components are being used. This facilitates the optimization of import statements for greater efficiency. This is still a work-in-progress, and the scope for improvement is vast, especially with the community’s support.

## Getting Started

These instructions will guide you through setting up the project for development and testing.

### Prerequisites

- Python 3.8 or newer.

### Installation

This project does not require any external packages beyond the Python standard library. To get started, clone the repository:

```bash
git clone https://github.com/remigenet/ASThetic/
cd ASThetic
```

## Usage

To optimize import statements in a Python file, the following script can be used:

```python
from your_module import smart_import

# Example usage of smart_import

smart_import(module_path: str = 'C:/Users/remig/Desktop/pythonProject/test_files/a.py',
                 importer_globals: Optional[dict] = None,
                 importer_locals: Optional[dict] = None,
                 targets: set = {'g', 'b'},
                 return_ast: Optional[bool] = False) 
        -> Union[Tuple[str, ...], Tuple[Callable[..., Any], ...]]:

# 'result' will contain either a callable or an AST, depending on the 'return_ast' parameter
```

Running this script will produce optimized import statements reflective of the tool's current functionality.

## Project Status

- **Selective Imports**: The selective import feature is currently able to handle a basic subset of patterns and is under active development for expansion and refinement.
- Future enhancements to include better error handling, broader AST node type coverage, and further code optimization strategies are in the pipeline.

## Contributing

This project welcomes feedback and contributions. If an issue is encountered or an improvement is envisioned, opening an issue is encouraged. Contributions can also be made directly via pull requests. A `CONTRIBUTING.md` file will soon be provided with more guidelines on how to get involved.

## Roadmap

- **Robust Selective Imports**: The completion of a fully functional selective import mechanism is the immediate priority.
- **Testing**: The development of a comprehensive test suite to handle a wide range of Python syntax and structural cases is planned.
- **Code Optimization**: Plans are in place to extend the project to include automatic suggestions for code optimizations based on AST analysis.
- **Cythonization**: Looking ahead, the project aims to facilitate partial code pre-compilation in C with Cython to enhance efficiency.
- **Documentation and Examples**: As features become stable and new ones are introduced, detailed documentation and examples will be made available.

## License

This project is licensed under the GNU General Public License v3.0, as detailed in the `LICENSE.md` file. The preamble of the license articulates the freedom to share and change all versions of a program—to ensure it remains free software for all users.

For any clarifications or questions, please feel free to initiate a discussion in the issues section.
