#!/usr/bin/env python3

import re
import os
import sys
import subprocess
from pathlib import Path

class StyleChecker:
    def __init__(self, filename):
        self.filename = filename
        self.errors = []
        self.warnings = []
        self.content = ""
        self.lines = []
        self.test_function_lines = set()  # Track lines that are in test functions

    def load_file(self):
        """Load the C file content"""
        try:
            with open(self.filename, 'r') as f:
                self.content = f.read()
                self.lines = self.content.splitlines()
            self._identify_test_functions()
            return True
        except FileNotFoundError:
            print(f"Error: File {self.filename} not found")
            return False

    def _identify_test_functions(self):
        """Identify lines that belong to test functions"""
        in_test_function = False
        brace_count = 0

        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()

            # Look for test function definitions
            if re.match(r'^\w*\s*test\w*\s*\([^)]*\)\s*$', stripped, re.IGNORECASE):
                in_test_function = True
                brace_count = 0
                self.test_function_lines.add(i)
                continue

            if in_test_function:
                self.test_function_lines.add(i)
                brace_count += stripped.count('{') - stripped.count('}')

                # Function ended
                if brace_count == 0 and '}' in stripped:
                    in_test_function = False

    def _is_in_test_function(self, line_num):
        """Check if a line is inside a test function"""
        return line_num in self.test_function_lines

    def check_tabs(self):
        """TABS: Check for tab characters"""
        issues = []
        for i, line in enumerate(self.lines, 1):
            if '\t' in line:
                issues.append(f"Line {i}: Contains tab character")

        if issues:
            self.errors.extend([f"TABS violation: {issue}" for issue in issues])
        return len(issues) == 0

    def check_line_length(self, max_length=60):
        """LLEN: Check line length (skip test functions)"""
        issues = []
        for i, line in enumerate(self.lines, 1):
            if self._is_in_test_function(i):
                continue  # Skip test functions

            if len(line) > max_length:
                issues.append(f"Line {i}: {len(line)} chars (max {max_length})")

        if issues:
            self.warnings.extend([f"LLEN warning: {issue}" for issue in issues])
        return len(issues) == 0

    def check_magic_numbers(self):
        """MAGIC: Check for magic numbers (skip test functions)"""
        issues = []
        # Look for numeric literals that aren't 0, 1, -1
        magic_pattern = r'\b(?!0\b|1\b|-1\b)\d+\b'

        for i, line in enumerate(self.lines, 1):
            if self._is_in_test_function(i):
                continue  # Skip test functions

            # Skip #define lines and comments
            if line.strip().startswith('#define') or line.strip().startswith('//'):
                continue

            matches = re.findall(magic_pattern, line)
            for match in matches:
                # Skip common non-magic numbers
                if match not in ['2', '10', '100']:  # Add more exceptions as needed
                    issues.append(f"Line {i}: Magic number '{match}'")

        if issues:
            self.warnings.extend([f"MAGIC warning: {issue}" for issue in issues])
        return len(issues) == 0

    def check_function_length(self, max_lines=20):
        """FLEN: Check function length (skip test functions)"""
        issues = []
        in_function = False
        function_start = 0
        function_name = ""
        brace_count = 0

        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()

            # Function definition pattern
            func_pattern = r'^\w+\s+\w+\s*\([^)]*\)\s*$'
            if re.match(func_pattern, stripped) and not stripped.startswith('//'):
                function_name = stripped.split('(')[0].strip().split()[-1]
                function_start = i
                in_function = True
                brace_count = 0
                continue

            if in_function:
                brace_count += stripped.count('{') - stripped.count('}')

                # Function ended
                if brace_count == 0 and '}' in stripped:
                    # Skip test functions
                    if re.match(r'.*test.*', function_name, re.IGNORECASE):
                        in_function = False
                        continue

                    function_length = i - function_start + 1
                    if function_length > max_lines:
                        issues.append(f"Function '{function_name}': {function_length} lines (max {max_lines})")
                    in_function = False

        if issues:
            self.warnings.extend([f"FLEN warning: {issue}" for issue in issues])
        return len(issues) == 0

    def check_forbidden_keywords(self):
        """GOTO: Check for forbidden keywords"""
        issues = []
        forbidden = ['goto', 'continue']

        for i, line in enumerate(self.lines, 1):
            # Skip comments
            if '//' in line:
                line = line[:line.index('//')]

            for keyword in forbidden:
                if re.search(r'\b' + keyword + r'\b', line):
                    issues.append(f"Line {i}: Forbidden keyword '{keyword}'")

            # Check for break outside switch
            if re.search(r'\bbreak\b', line):
                # This is a simplified check - would need better parsing for switch context
                self.warnings.append(f"GOTO warning: Line {i}: 'break' found - ensure it's only in switch statements")

        if issues:
            self.errors.extend([f"GOTO violation: {issue}" for issue in issues])
        return len(issues) == 0

    def check_infinite_loops(self):
        """INFIN: Check for infinite loops"""
        issues = []
        patterns = [
            r'while\s*\(\s*1\s*\)',
            r'while\s*\(\s*true\s*\)',
            r'for\s*\(\s*;\s*;\s*\)'
        ]

        for i, line in enumerate(self.lines, 1):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(f"Line {i}: Infinite loop pattern")

        if issues:
            self.errors.extend([f"INFIN violation: {issue}" for issue in issues])
        return len(issues) == 0

    def check_constants_caps(self):
        """CAPS: Check that #define constants are uppercase"""
        issues = []

        for i, line in enumerate(self.lines, 1):
            if line.strip().startswith('#define'):
                # Extract the constant name
                parts = line.strip().split()
                if len(parts) >= 2:
                    const_name = parts[1]
                    if not const_name.isupper():
                        issues.append(f"Line {i}: Constant '{const_name}' should be uppercase")

        if issues:
            self.errors.extend([f"CAPS violation: {issue}" for issue in issues])
        return len(issues) == 0

    def check_unused_return_values(self):
        """RETV: Check for unused return values (skip test functions)"""
        issues = []
        functions_with_returns = ['scanf', 'malloc', 'fopen']  # Removed strcmp - often used in tests

        for i, line in enumerate(self.lines, 1):
            if self._is_in_test_function(i):
                continue  # Skip test functions

            # Skip comments
            if '//' in line:
                line = line[:line.index('//')]

            for func in functions_with_returns:
                pattern = rf'\b{func}\s*\([^)]*\)\s*;'
                if re.search(pattern, line):
                    # Check if it's assigned or used in condition
                    if not re.search(rf'=.*{func}|if.*{func}|while.*{func}|return.*{func}', line):
                        issues.append(f"Line {i}: Unused return value from '{func}'")

        if issues:
            self.warnings.extend([f"RETV warning: {issue}" for issue in issues])
        return len(issues) == 0

    def check_braces(self):
        """BRACE: Basic check for missing braces"""
        issues = []
        control_structures = ['if', 'else', 'for', 'while']

        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()

            for structure in control_structures:
                pattern = rf'\b{structure}\s*\([^)]*\)\s*$'
                if re.match(pattern, stripped):
                    # Check next non-empty line
                    for j in range(i, min(i + 3, len(self.lines))):
                        if j < len(self.lines):
                            next_line = self.lines[j].strip()
                            if next_line and not next_line.startswith('//'):
                                if not next_line.startswith('{'):
                                    issues.append(f"Line {i}: {structure} statement might be missing braces")
                                break

        if issues:
            self.warnings.extend([f"BRACE warning: {issue}" for issue in issues])
        return len(issues) == 0

    def check_compilation(self):
        """FLAGS: Check compilation with required flags"""
        if not os.path.exists(self.filename):
            return False

        flags = ['-Wall', '-Wextra', '-Wfloat-equal', '-Wvla', '-pedantic', '-std=c99', '-g3']
        cmd = ['gcc'] + flags + ['-c', self.filename, '-o', '/tmp/style_check.o']

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.errors.append(f"FLAGS violation: Compilation failed with required flags")
                self.errors.append(f"Compiler output: {result.stderr}")
                return False
            else:
                # Clean up
                if os.path.exists('/tmp/style_check.o'):
                    os.remove('/tmp/style_check.o')
                return True
        except subprocess.CalledProcessError:
            self.errors.append("FLAGS violation: Could not compile with required flags")
            return False

    def check_all(self):
        """Run all automated checks"""
        if not self.load_file():
            return False

        print(f"Checking {self.filename} against style guidelines...\n")

        if self.test_function_lines:
            print(f"ℹ️  Skipping style checks for test functions (lines: {min(self.test_function_lines)}-{max(self.test_function_lines)})")
            print()

        checks = [
            ("TABS", self.check_tabs),
            ("LLEN", self.check_line_length),
            ("MAGIC", self.check_magic_numbers),
            ("FLEN", self.check_function_length),
            ("GOTO", self.check_forbidden_keywords),
            ("INFIN", self.check_infinite_loops),
            ("CAPS", self.check_constants_caps),
            ("RETV", self.check_unused_return_values),
            ("BRACE", self.check_braces),
            ("FLAGS", self.check_compilation)
        ]

        passed = 0
        total = len(checks)

        for name, check_func in checks:
            try:
                result = check_func()
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{name:8} {status}")
                if result:
                    passed += 1
            except Exception as e:
                print(f"{name:8} ❌ ERROR: {e}")

        print(f"\n📊 Results: {passed}/{total} checks passed")

        if self.errors:
            print(f"\n🔴 ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print(f"\n🟡 WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        if not self.errors and not self.warnings:
            print("\n🎉 All automated checks passed! Your code follows the style guidelines.")

        return len(self.errors) == 0

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 style_checker.py <file.c>")
        sys.exit(1)

    filename = sys.argv[1]
    checker = StyleChecker(filename)
    success = checker.check_all()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()