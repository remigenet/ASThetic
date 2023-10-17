# AST-Based Code Analysis for Selective Imports

## Introduction

This project is an exploration into the possibilities offered by manipulating Abstract Syntax Trees (ASTs) to improve Python code efficiency. The current focus is on enabling selective importing to minimize the overhead in Python applications by importing only what is absolutely necessary from large modules.

Please note, this project is in the early stages, and while the selective imports feature is operational, there is still a lot of ground to cover. Many cases remain unhandled, and contributions are welcomed.

## Current Features

- **Selective Imports**: The tool can analyze a codebase and identify which specific functions or components are being used, allowing it to potentially rewrite imports to be more efficient.
- **AST Analysis Foundations**: The groundwork has been laid for more sophisticated code analysis by leveraging ASTs, enabling a more in-depth understanding of code semantics without execution.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8 or newer

### Installation

```
git clone <repository-url>
cd <repository-dir>
pip install -r requirements.txt
```

## Usage

To analyze a Python file and optimize its import statements, you can use the script provided in the repository:

```
Use the function smart_import to selectively imports the only parts of the codes that defines it.
It aims to reproduce fidely a python execution so variable in enclosing scopes even after the function will be taken with the module.
The signature of the function is as follows:
smart_import(module_path: str, importer_globals: Optional[dict] = None, importer_locals: Optional[dict] = None,
                 targets: Set[str], return_ast: bool = False) \
        -> Union[Tuple[str, ...], Tuple[Callable[..., Any], ...]]
By defaults it will return an executable function, but parameter return_ast = True makes the AST module being return instead.
```

This will generate an output detailing the optimized imports based on the current capabilities of the tool.

## Project Status

- The selective imports feature is the first that has been partially implemented. It can currently handle a subset of common cases and patterns.
- Advanced code optimizations, additional AST node type handling, and other features are planned for the future but are not yet implemented.
- Error handling and edge cases in AST analysis are areas needing improvement.

## Contributing

Given the early-stage nature of the project, contributions, ideas, and discussions are highly encouraged. If you encounter an issue or have a suggestion, please open an issue. If you wish to contribute directly, feel free to make a pull request.

For more detailed information, check out the `CONTRIBUTING.md` file (to be added soon).

## Roadmap

- **Extensive Testing**: Adding more test cases, especially for edge cases in Python syntax and structure.
- **Code Optimization**: Beyond selective imports, future updates will look at automatically suggesting code optimizations based on AST analysis.
- **Documentation and Examples**: As features are added and existing ones are stabilized, detailed documentation and usage examples will be provided.

## License

This project is licensed under the GNU License - see the `LICENSE.md` file for details.
