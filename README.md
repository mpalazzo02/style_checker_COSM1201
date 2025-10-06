# C Style Checker

A simple style checker for the non-subjective parts of the C programming style guidelines as per the [Exercises in C Style Guide](https://github.com/csnwc/Exercises-In-C/blob/main/exercisesInC.pdf).

## About

This is a personal project designed to help developers adhere to the style guidelines outlined in the "Exercises in C" book. It automatically checks your C code against common style rules to help you avoid simple formatting mistakes.

**If you find this helpful star the repository, it's FREE!**

## Installation & Usage

### 1. Clone the Repository

```bash
git clone https://github.com/mpalazzo02/style_checker_COSM1201.git
```

### 2. Navigate to the Directory

```bash
cd style_checker_COSM1201
```

### 3. Run the Style Checker

```bash
python3 style_checker.py <file_to_check.c>
```

**Example:**
```bash
python3 style_checker.py my_program.c
```

## Style Guidelines Checked

This tool automatically checks your C code against the following **10 style guidelines**:

| Rule | Name | Description | Type |
|------|------|-------------|------|
| **TABS** | Tab Characters | No tab characters allowed - use spaces only | Error |
| **LLEN** | Line Length | Lines should be ≤ 60 characters (skips test functions) | Warning |
| **MAGIC** | Magic Numbers | Avoid magic numbers (except 0, 1, -1) - use named constants | Warning |
| **FLEN** | Function Length | Functions should be ≤ 20 lines (skips test functions) | Warning |
| **GOTO** | Forbidden Keywords | No `goto` or `continue` statements allowed | Error |
| **INFIN** | Infinite Loops | No infinite loops (`while(1)`, `for(;;)`, etc.) | Error |
| **CAPS** | Constant Names | `#define` constants must be UPPERCASE | Error |
| **RETV** | Return Values | Don't ignore return values from functions like `scanf`, `malloc`, `fopen` | Warning |
| **BRACE** | Missing Braces | Control structures should use braces `{}` | Warning |
| **FLAGS** | Compilation | Code must compile with strict flags: `-Wall -Wextra -Wfloat-equal -Wvla -pedantic -std=c99 -g3` | Error |

### Special Handling for Test Functions
- **Test functions are automatically detected** and excluded from `LLEN`, `MAGIC`, `FLEN`, and `RETV` checks
- Test functions are identified by having "test" in their name (case-insensitive)

## Features

- Checks 10 fundamental C style guidelines automatically
- Smart test function detection - skips style checks where appropriate
- Easy to use command-line interface
- Clear results with errors vs warnings distinction
- Helps avoid common formatting mistakes and penalties
- Based on established C programming standards

## Limitations

**Important Notes:**

- This script is a **basic** style checker and does not cover all style guidelines
- It focuses on the fundamentals to help you avoid simple penalties
- **Not perfect** - use as a guide, not absolute truth
- Manual review of your code is still recommended

## Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Make your improvements or add new checks
3. Test your changes
4. Submit a pull request

### Ideas for Contributions:
- Additional style checks
- Better error messages
- Performance improvements
- Documentation updates

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues or have suggestions, please:
- [Open an issue](https://github.com/mpalazzo02/style_checker_COSM1201/issues)
- Start a discussion
