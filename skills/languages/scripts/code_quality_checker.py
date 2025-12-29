#!/usr/bin/env python3
"""
Code Quality Checker
BI Analyst Plugin - Languages Skill
Analyzes code quality across multiple programming languages.
"""

import os
import re
import ast
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict


@dataclass
class CodeMetrics:
    """Code quality metrics for a file."""
    file_path: str
    language: str
    lines_of_code: int = 0
    blank_lines: int = 0
    comment_lines: int = 0
    functions: int = 0
    classes: int = 0
    complexity: int = 0
    has_docstrings: bool = False
    has_type_hints: bool = False
    issues: list = field(default_factory=list)


class CodeQualityChecker:
    """Check code quality across multiple languages."""

    LANGUAGE_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.go': 'go',
        '.rs': 'rust',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.hpp': 'cpp',
        '.h': 'c',
        '.rb': 'ruby',
        '.php': 'php',
    }

    def __init__(self, project_path: str, exclude_dirs: Optional[list] = None):
        self.project_path = Path(project_path)
        self.exclude_dirs = exclude_dirs or [
            'node_modules', 'venv', '.venv', '__pycache__',
            'dist', 'build', '.git', 'vendor', 'target'
        ]
        self.metrics: list[CodeMetrics] = []

    def analyze_project(self) -> dict:
        """Analyze all source files in the project."""
        source_files = self._find_source_files()

        for file_path in source_files:
            metrics = self._analyze_file(file_path)
            if metrics:
                self.metrics.append(metrics)

        return self._generate_report()

    def _find_source_files(self) -> list[Path]:
        """Find all source files in the project."""
        source_files = []

        for ext in self.LANGUAGE_EXTENSIONS:
            for file_path in self.project_path.rglob(f'*{ext}'):
                # Skip excluded directories
                if any(excluded in file_path.parts for excluded in self.exclude_dirs):
                    continue
                source_files.append(file_path)

        return source_files

    def _analyze_file(self, file_path: Path) -> Optional[CodeMetrics]:
        """Analyze a single source file."""
        ext = file_path.suffix
        language = self.LANGUAGE_EXTENSIONS.get(ext, 'unknown')

        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return None

        metrics = CodeMetrics(
            file_path=str(file_path.relative_to(self.project_path)),
            language=language
        )

        # Count lines
        lines = content.split('\n')
        metrics.lines_of_code = len([l for l in lines if l.strip()])
        metrics.blank_lines = len([l for l in lines if not l.strip()])
        metrics.comment_lines = self._count_comments(content, language)

        # Language-specific analysis
        if language == 'python':
            self._analyze_python(content, metrics)
        elif language in ['javascript', 'typescript']:
            self._analyze_javascript(content, metrics)
        elif language == 'go':
            self._analyze_go(content, metrics)
        elif language == 'rust':
            self._analyze_rust(content, metrics)
        elif language == 'java':
            self._analyze_java(content, metrics)
        else:
            self._analyze_generic(content, metrics)

        # Common quality checks
        self._check_common_issues(content, metrics)

        return metrics

    def _count_comments(self, content: str, language: str) -> int:
        """Count comment lines based on language."""
        count = 0

        # Single-line comments
        if language in ['python', 'ruby']:
            count += len(re.findall(r'^\s*#', content, re.MULTILINE))
        else:  # C-style comments
            count += len(re.findall(r'^\s*//', content, re.MULTILINE))

        # Multi-line comments
        if language == 'python':
            count += len(re.findall(r'"""[\s\S]*?"""', content)) * 2
            count += len(re.findall(r"'''[\s\S]*?'''", content)) * 2
        else:
            count += content.count('/*') + content.count('*/')

        return count

    def _analyze_python(self, content: str, metrics: CodeMetrics):
        """Analyze Python-specific metrics."""
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            metrics.issues.append(f"Syntax error: {str(e)}")
            return

        # Count functions and classes
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metrics.functions += 1

                # Check for docstring
                if ast.get_docstring(node):
                    metrics.has_docstrings = True

                # Check for type hints
                if node.returns or any(arg.annotation for arg in node.args.args):
                    metrics.has_type_hints = True

                # Calculate complexity
                complexity = self._calculate_python_complexity(node)
                metrics.complexity = max(metrics.complexity, complexity)

            elif isinstance(node, ast.ClassDef):
                metrics.classes += 1

        # Python-specific issues
        if not metrics.has_type_hints:
            metrics.issues.append("Missing type hints")

        if metrics.functions > 0 and not metrics.has_docstrings:
            metrics.issues.append("Missing docstrings")

        # Check for print statements
        if 'print(' in content and not '# noqa' in content:
            metrics.issues.append("Debug print statements found")

        # Check for bare except
        if re.search(r'except\s*:', content):
            metrics.issues.append("Bare except clause found")

    def _calculate_python_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for Python function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                complexity += sum(1 for _ in child.generators)

        return complexity

    def _analyze_javascript(self, content: str, metrics: CodeMetrics):
        """Analyze JavaScript/TypeScript metrics."""
        # Count functions
        metrics.functions = len(re.findall(
            r'(?:function\s+\w+|const\s+\w+\s*=\s*(?:async\s+)?(?:\([^)]*\)|[a-z_]\w*)\s*=>)',
            content
        ))

        # Count classes
        metrics.classes = len(re.findall(r'class\s+\w+', content))

        # Check for TypeScript types
        if '.ts' in metrics.file_path:
            metrics.has_type_hints = bool(re.search(r':\s*\w+', content))

        # Check for JSDoc
        if '/**' in content:
            metrics.has_docstrings = True

        # Issues
        if 'console.log' in content:
            metrics.issues.append("Console.log statements found")

        if 'any' in content and '.ts' in metrics.file_path:
            metrics.issues.append("TypeScript 'any' type usage detected")

        if 'var ' in content:
            metrics.issues.append("'var' keyword used instead of 'let' or 'const'")

    def _analyze_go(self, content: str, metrics: CodeMetrics):
        """Analyze Go metrics."""
        # Count functions
        metrics.functions = len(re.findall(r'func\s+', content))

        # Count structs (classes equivalent)
        metrics.classes = len(re.findall(r'type\s+\w+\s+struct', content))

        # Go has implicit typing but check for documentation
        if re.search(r'//\s*\w+\s+', content):  # Go doc comments
            metrics.has_docstrings = True

        metrics.has_type_hints = True  # Go is statically typed

        # Issues
        if 'panic(' in content:
            metrics.issues.append("Panic calls found - consider error handling")

        if re.search(r'_\s*=\s*', content):
            metrics.issues.append("Ignored error values detected")

    def _analyze_rust(self, content: str, metrics: CodeMetrics):
        """Analyze Rust metrics."""
        # Count functions
        metrics.functions = len(re.findall(r'fn\s+\w+', content))

        # Count structs and enums
        metrics.classes = len(re.findall(r'(?:struct|enum)\s+\w+', content))

        # Rust doc comments
        if '///' in content or '//!' in content:
            metrics.has_docstrings = True

        metrics.has_type_hints = True  # Rust is statically typed

        # Issues
        if 'unwrap()' in content:
            metrics.issues.append("unwrap() calls - consider proper error handling")

        if 'unsafe' in content:
            metrics.issues.append("Unsafe blocks detected")

    def _analyze_java(self, content: str, metrics: CodeMetrics):
        """Analyze Java metrics."""
        # Count methods
        metrics.functions = len(re.findall(
            r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+\w+\s*\([^)]*\)\s*(?:throws\s+\w+(?:\s*,\s*\w+)*)?\s*\{',
            content
        ))

        # Count classes
        metrics.classes = len(re.findall(r'(?:class|interface|enum)\s+\w+', content))

        # JavaDoc
        if '/**' in content:
            metrics.has_docstrings = True

        metrics.has_type_hints = True  # Java is statically typed

        # Issues
        if 'System.out.print' in content:
            metrics.issues.append("System.out.print statements found")

        if 'catch (Exception ' in content:
            metrics.issues.append("Catching generic Exception")

    def _analyze_generic(self, content: str, metrics: CodeMetrics):
        """Generic analysis for unsupported languages."""
        # Count function-like patterns
        metrics.functions = len(re.findall(r'(?:function|def|fn|func)\s+\w+', content))
        metrics.classes = len(re.findall(r'(?:class|struct|type)\s+\w+', content))

    def _check_common_issues(self, content: str, metrics: CodeMetrics):
        """Check for common issues across all languages."""
        # Large file
        if metrics.lines_of_code > 500:
            metrics.issues.append(f"Large file ({metrics.lines_of_code} lines)")

        # High complexity
        if metrics.complexity > 10:
            metrics.issues.append(f"High complexity ({metrics.complexity})")

        # Low comment ratio
        if metrics.lines_of_code > 50:
            comment_ratio = metrics.comment_lines / metrics.lines_of_code
            if comment_ratio < 0.1:
                metrics.issues.append("Low documentation coverage")

        # TODO/FIXME comments
        todo_count = len(re.findall(r'(?:TODO|FIXME|XXX|HACK)', content, re.IGNORECASE))
        if todo_count > 0:
            metrics.issues.append(f"{todo_count} TODO/FIXME comments")

        # Long lines
        long_lines = [i for i, line in enumerate(content.split('\n'), 1) if len(line) > 120]
        if long_lines:
            metrics.issues.append(f"{len(long_lines)} lines exceed 120 characters")

    def _generate_report(self) -> dict:
        """Generate comprehensive quality report."""
        if not self.metrics:
            return {"error": "No source files found"}

        # Aggregate by language
        by_language = defaultdict(lambda: {
            "files": 0, "lines": 0, "functions": 0, "classes": 0, "issues": 0
        })

        for m in self.metrics:
            by_language[m.language]["files"] += 1
            by_language[m.language]["lines"] += m.lines_of_code
            by_language[m.language]["functions"] += m.functions
            by_language[m.language]["classes"] += m.classes
            by_language[m.language]["issues"] += len(m.issues)

        total_issues = sum(len(m.issues) for m in self.metrics)
        files_with_issues = sum(1 for m in self.metrics if m.issues)

        return {
            "summary": {
                "total_files": len(self.metrics),
                "total_lines": sum(m.lines_of_code for m in self.metrics),
                "total_functions": sum(m.functions for m in self.metrics),
                "total_classes": sum(m.classes for m in self.metrics),
                "total_issues": total_issues,
                "files_with_issues": files_with_issues,
                "quality_score": self._calculate_quality_score(),
            },
            "by_language": dict(by_language),
            "files_with_most_issues": [
                {
                    "path": m.file_path,
                    "language": m.language,
                    "lines": m.lines_of_code,
                    "issues": m.issues,
                }
                for m in sorted(self.metrics, key=lambda x: len(x.issues), reverse=True)[:10]
                if m.issues
            ],
            "recommendations": self._generate_recommendations(),
        }

    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score (0-100)."""
        if not self.metrics:
            return 0

        scores = []
        for m in self.metrics:
            file_score = 100

            # Deduct for issues
            file_score -= len(m.issues) * 5

            # Deduct for missing docs
            if not m.has_docstrings and m.functions > 0:
                file_score -= 10

            # Deduct for missing types
            if not m.has_type_hints and m.language in ['python', 'javascript']:
                file_score -= 10

            # Deduct for high complexity
            if m.complexity > 10:
                file_score -= (m.complexity - 10) * 2

            scores.append(max(0, file_score))

        return round(sum(scores) / len(scores), 1)

    def _generate_recommendations(self) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Type hints
        no_types = [m for m in self.metrics if not m.has_type_hints and m.language == 'python']
        if no_types:
            recommendations.append(f"Add type hints to {len(no_types)} Python files")

        # Documentation
        no_docs = [m for m in self.metrics if not m.has_docstrings and m.functions > 0]
        if no_docs:
            recommendations.append(f"Add documentation to {len(no_docs)} files")

        # Complexity
        complex_files = [m for m in self.metrics if m.complexity > 10]
        if complex_files:
            recommendations.append(f"Reduce complexity in {len(complex_files)} files")

        # Large files
        large_files = [m for m in self.metrics if m.lines_of_code > 500]
        if large_files:
            recommendations.append(f"Consider splitting {len(large_files)} large files")

        return recommendations


def main():
    """Main entry point."""
    import sys

    project_path = sys.argv[1] if len(sys.argv) > 1 else "."

    checker = CodeQualityChecker(project_path)
    report = checker.analyze_project()

    print(json.dumps(report, indent=2))

    # Exit with warning if quality score is low
    if report.get("summary", {}).get("quality_score", 0) < 70:
        sys.exit(1)


if __name__ == "__main__":
    main()
