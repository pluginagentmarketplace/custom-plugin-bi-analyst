#!/usr/bin/env python3
"""
Backend API Analyzer
BI Analyst Plugin - Backend Skill
Analyzes API endpoints, patterns, and best practices compliance.
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
class EndpointMetrics:
    """Metrics for a single API endpoint."""
    path: str
    method: str
    function_name: str
    file_path: str
    line_number: int = 0
    has_docstring: bool = False
    has_type_hints: bool = False
    has_validation: bool = False
    has_error_handling: bool = False
    has_authentication: bool = False
    response_model: Optional[str] = None
    parameters: list = field(default_factory=list)
    issues: list = field(default_factory=list)


class BackendAPIAnalyzer:
    """Analyze backend API structure and quality."""

    HTTP_METHODS = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']

    FASTAPI_DECORATORS = [
        '@app.get', '@app.post', '@app.put', '@app.patch', '@app.delete',
        '@router.get', '@router.post', '@router.put', '@router.patch', '@router.delete'
    ]

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.endpoints: list[EndpointMetrics] = []
        self.summary = defaultdict(int)

    def analyze_project(self) -> dict:
        """Analyze all API endpoints in the project."""
        python_files = self._find_python_files()

        for file_path in python_files:
            self._analyze_file(file_path)

        return self._generate_report()

    def _find_python_files(self) -> list[Path]:
        """Find all Python files that may contain API endpoints."""
        api_dirs = ['api', 'routes', 'routers', 'endpoints', 'views', 'controllers']

        python_files = []
        for dir_name in api_dirs:
            dir_path = self.project_path / dir_name
            if dir_path.exists():
                python_files.extend(dir_path.rglob('*.py'))

        # Also check app directory
        app_path = self.project_path / 'app'
        if app_path.exists():
            for subdir in api_dirs:
                subdir_path = app_path / subdir
                if subdir_path.exists():
                    python_files.extend(subdir_path.rglob('*.py'))

        # Check main.py and app.py in root
        for main_file in ['main.py', 'app.py']:
            main_path = self.project_path / main_file
            if main_path.exists():
                python_files.append(main_path)

        return list(set(python_files))

    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file for API endpoints."""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
        except Exception as e:
            return

        lines = content.split('\n')

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                endpoint = self._extract_endpoint_info(node, lines, file_path)
                if endpoint:
                    self.endpoints.append(endpoint)

    def _extract_endpoint_info(self, node: ast.FunctionDef, lines: list, file_path: Path) -> Optional[EndpointMetrics]:
        """Extract endpoint information from a function definition."""
        # Check for route decorators
        route_info = None
        for decorator in node.decorator_list:
            decorator_str = self._get_decorator_string(decorator, lines, node.lineno)
            if decorator_str:
                route_info = self._parse_route_decorator(decorator_str)
                if route_info:
                    break

        if not route_info:
            return None

        path, method = route_info

        endpoint = EndpointMetrics(
            path=path,
            method=method.upper(),
            function_name=node.name,
            file_path=str(file_path),
            line_number=node.lineno
        )

        # Check for docstring
        endpoint.has_docstring = ast.get_docstring(node) is not None

        # Check for type hints
        endpoint.has_type_hints = self._has_type_hints(node)

        # Check for validation (Pydantic models)
        func_source = '\n'.join(lines[node.lineno - 1:node.end_lineno])
        endpoint.has_validation = 'BaseModel' in func_source or 'Depends(' in func_source

        # Check for error handling
        endpoint.has_error_handling = 'HTTPException' in func_source or 'try:' in func_source

        # Check for authentication
        auth_patterns = ['Depends(get_current_user)', 'oauth2_scheme', 'api_key', 'Authorization']
        endpoint.has_authentication = any(p in func_source for p in auth_patterns)

        # Extract response model
        response_match = re.search(r'response_model\s*=\s*(\w+)', func_source)
        if response_match:
            endpoint.response_model = response_match.group(1)

        # Extract parameters
        for arg in node.args.args:
            param_name = arg.arg
            param_type = ast.unparse(arg.annotation) if arg.annotation else 'Any'
            endpoint.parameters.append(f"{param_name}: {param_type}")

        # Detect issues
        endpoint.issues = self._detect_endpoint_issues(endpoint, func_source)

        return endpoint

    def _get_decorator_string(self, decorator, lines: list, func_lineno: int) -> Optional[str]:
        """Get decorator as string from source."""
        try:
            # Look at lines before the function definition
            for i in range(max(0, func_lineno - 10), func_lineno):
                line = lines[i].strip()
                if line.startswith('@') and any(m in line.lower() for m in self.HTTP_METHODS):
                    return line
        except:
            pass
        return None

    def _parse_route_decorator(self, decorator_str: str) -> Optional[tuple]:
        """Parse route decorator to extract path and method."""
        for method in self.HTTP_METHODS:
            patterns = [
                rf'@\w+\.{method}\s*\(\s*["\']([^"\']+)["\']',
                rf'@{method}\s*\(\s*["\']([^"\']+)["\']',
            ]
            for pattern in patterns:
                match = re.search(pattern, decorator_str, re.IGNORECASE)
                if match:
                    return (match.group(1), method)
        return None

    def _has_type_hints(self, node: ast.FunctionDef) -> bool:
        """Check if function has type hints."""
        has_return_hint = node.returns is not None

        has_param_hints = any(
            arg.annotation is not None
            for arg in node.args.args
            if arg.arg not in ['self', 'cls']
        )

        return has_return_hint or has_param_hints

    def _detect_endpoint_issues(self, endpoint: EndpointMetrics, source: str) -> list[str]:
        """Detect common issues in endpoint implementation."""
        issues = []

        # No docstring
        if not endpoint.has_docstring:
            issues.append("Missing docstring for API documentation")

        # No type hints
        if not endpoint.has_type_hints:
            issues.append("Missing type hints for request/response")

        # No validation for POST/PUT/PATCH
        if endpoint.method in ['POST', 'PUT', 'PATCH'] and not endpoint.has_validation:
            issues.append("Missing request body validation")

        # No error handling
        if not endpoint.has_error_handling:
            issues.append("No explicit error handling found")

        # Public endpoint without rate limiting hint
        if not endpoint.has_authentication and endpoint.method in ['GET', 'POST']:
            issues.append("Consider rate limiting for public endpoint")

        # SQL injection risk (raw string formatting with user input)
        sql_risk_patterns = [r'f"SELECT', r'f"INSERT', r'f"UPDATE', r'f"DELETE', r'%s.*SELECT']
        if any(re.search(p, source) for p in sql_risk_patterns):
            issues.append("SECURITY: Potential SQL injection vulnerability")

        # Hardcoded secrets
        secret_patterns = ['password=', 'secret=', 'api_key=', 'token=']
        if any(p in source.lower() for p in secret_patterns):
            if '"' in source or "'" in source:  # Likely hardcoded
                issues.append("SECURITY: Possible hardcoded credentials")

        return issues

    def _generate_report(self) -> dict:
        """Generate analysis report."""
        if not self.endpoints:
            return {"error": "No API endpoints found"}

        # Group by method
        by_method = defaultdict(list)
        for ep in self.endpoints:
            by_method[ep.method].append(ep)

        # Count issues
        total_issues = sum(len(e.issues) for e in self.endpoints)
        security_issues = sum(
            1 for e in self.endpoints
            for issue in e.issues if 'SECURITY' in issue
        )

        return {
            "summary": {
                "total_endpoints": len(self.endpoints),
                "methods": {m: len(eps) for m, eps in by_method.items()},
                "documented_endpoints": sum(1 for e in self.endpoints if e.has_docstring),
                "typed_endpoints": sum(1 for e in self.endpoints if e.has_type_hints),
                "authenticated_endpoints": sum(1 for e in self.endpoints if e.has_authentication),
                "total_issues": total_issues,
                "security_issues": security_issues,
            },
            "endpoints": [
                {
                    "path": e.path,
                    "method": e.method,
                    "function": e.function_name,
                    "file": e.file_path,
                    "line": e.line_number,
                    "documented": e.has_docstring,
                    "typed": e.has_type_hints,
                    "validated": e.has_validation,
                    "authenticated": e.has_authentication,
                    "issues": e.issues,
                }
                for e in sorted(self.endpoints, key=lambda x: (x.path, x.method))
            ],
            "recommendations": self._generate_recommendations(),
            "rest_compliance": self._check_rest_compliance(),
        }

    def _generate_recommendations(self) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        undocumented = [e for e in self.endpoints if not e.has_docstring]
        if undocumented:
            recommendations.append(
                f"Add docstrings to {len(undocumented)} endpoints for OpenAPI documentation"
            )

        untyped = [e for e in self.endpoints if not e.has_type_hints]
        if untyped:
            recommendations.append(
                f"Add type hints to {len(untyped)} endpoints for better validation"
            )

        security_issues = [e for e in self.endpoints if any('SECURITY' in i for i in e.issues)]
        if security_issues:
            recommendations.append(
                f"URGENT: Fix security issues in {len(security_issues)} endpoints"
            )

        public_endpoints = [e for e in self.endpoints if not e.has_authentication]
        if len(public_endpoints) > len(self.endpoints) * 0.7:
            recommendations.append(
                "Consider adding authentication to more endpoints"
            )

        return recommendations

    def _check_rest_compliance(self) -> dict:
        """Check REST API design compliance."""
        checks = {
            "uses_proper_http_methods": True,
            "consistent_naming": True,
            "versioned_api": False,
            "uses_nouns_not_verbs": True,
        }

        # Check for API versioning
        checks["versioned_api"] = any(
            '/v1/' in e.path or '/v2/' in e.path or '/api/v' in e.path
            for e in self.endpoints
        )

        # Check for verb usage in paths (anti-pattern)
        verb_patterns = ['/get', '/create', '/update', '/delete', '/fetch', '/add']
        if any(any(v in e.path.lower() for v in verb_patterns) for e in self.endpoints):
            checks["uses_nouns_not_verbs"] = False

        return checks


def main():
    """Main entry point."""
    import sys

    project_path = sys.argv[1] if len(sys.argv) > 1 else "."

    analyzer = BackendAPIAnalyzer(project_path)
    report = analyzer.analyze_project()

    print(json.dumps(report, indent=2))

    # Exit with error if security issues found
    if report.get("summary", {}).get("security_issues", 0) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
