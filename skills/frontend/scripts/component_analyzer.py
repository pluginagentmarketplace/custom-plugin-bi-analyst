#!/usr/bin/env python3
"""
Frontend Component Analyzer
BI Analyst Plugin - Frontend Skill
Analyzes React/Vue/Angular component structure, complexity, and best practices.
"""

import os
import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict


@dataclass
class ComponentMetrics:
    """Metrics for a single component."""
    name: str
    file_path: str
    lines_of_code: int = 0
    jsx_complexity: int = 0
    hooks_count: int = 0
    props_count: int = 0
    state_variables: int = 0
    dependencies: list = field(default_factory=list)
    has_tests: bool = False
    accessibility_score: float = 0.0
    issues: list = field(default_factory=list)


class FrontendComponentAnalyzer:
    """Analyze frontend component quality and structure."""

    REACT_HOOKS = [
        'useState', 'useEffect', 'useContext', 'useReducer',
        'useCallback', 'useMemo', 'useRef', 'useImperativeHandle',
        'useLayoutEffect', 'useDebugValue', 'useId', 'useTransition',
        'useDeferredValue', 'useSyncExternalStore', 'useInsertionEffect'
    ]

    ACCESSIBILITY_PATTERNS = {
        'aria-label': 10,
        'aria-describedby': 10,
        'role=': 5,
        'alt=': 10,
        'tabIndex': 5,
        '<button': 5,
        '<a href': 5,
        'aria-hidden': 5,
        'aria-live': 10,
    }

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.components: list[ComponentMetrics] = []
        self.summary = defaultdict(int)

    def analyze_project(self) -> dict:
        """Analyze all components in the project."""
        component_files = self._find_component_files()

        for file_path in component_files:
            metrics = self._analyze_component(file_path)
            if metrics:
                self.components.append(metrics)

        return self._generate_report()

    def _find_component_files(self) -> list[Path]:
        """Find all component files in the project."""
        extensions = ['.tsx', '.jsx', '.vue', '.svelte']
        component_files = []

        src_path = self.project_path / 'src'
        if not src_path.exists():
            src_path = self.project_path

        for ext in extensions:
            component_files.extend(src_path.rglob(f'*{ext}'))

        # Filter out test files and stories
        return [
            f for f in component_files
            if not any(x in str(f) for x in ['.test.', '.spec.', '.stories.', '__tests__'])
        ]

    def _analyze_component(self, file_path: Path) -> Optional[ComponentMetrics]:
        """Analyze a single component file."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return None

        name = file_path.stem
        metrics = ComponentMetrics(name=name, file_path=str(file_path))

        # Lines of code
        lines = content.split('\n')
        metrics.lines_of_code = len([l for l in lines if l.strip() and not l.strip().startswith('//')])

        # Hooks analysis
        metrics.hooks_count = sum(content.count(hook) for hook in self.REACT_HOOKS)

        # Props analysis
        props_match = re.findall(r'interface\s+\w*Props\s*\{([^}]+)\}', content, re.DOTALL)
        if props_match:
            metrics.props_count = len(re.findall(r'\w+\s*[?:]', props_match[0]))

        # State variables
        metrics.state_variables = content.count('useState')

        # JSX complexity (nested elements)
        metrics.jsx_complexity = self._calculate_jsx_complexity(content)

        # Dependencies
        import_matches = re.findall(r"from\s+['\"]([^'\"]+)['\"]", content)
        metrics.dependencies = list(set(import_matches))

        # Check for tests
        test_file = file_path.with_suffix('.test.tsx')
        if not test_file.exists():
            test_file = file_path.with_suffix('.test.jsx')
        metrics.has_tests = test_file.exists()

        # Accessibility score
        metrics.accessibility_score = self._calculate_a11y_score(content)

        # Issues detection
        metrics.issues = self._detect_issues(content, metrics)

        return metrics

    def _calculate_jsx_complexity(self, content: str) -> int:
        """Calculate JSX nesting complexity."""
        complexity = 0
        max_depth = 0
        current_depth = 0

        for char in content:
            if char == '<':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '>':
                if current_depth > 0:
                    current_depth -= 1

        complexity = max_depth + content.count('&&') + content.count('? ')
        return complexity

    def _calculate_a11y_score(self, content: str) -> float:
        """Calculate accessibility score based on patterns."""
        total_possible = sum(self.ACCESSIBILITY_PATTERNS.values())
        achieved = 0

        for pattern, points in self.ACCESSIBILITY_PATTERNS.items():
            if pattern in content:
                achieved += points

        return round((achieved / total_possible) * 100, 1) if total_possible > 0 else 0

    def _detect_issues(self, content: str, metrics: ComponentMetrics) -> list[str]:
        """Detect common issues in components."""
        issues = []

        # Large component
        if metrics.lines_of_code > 300:
            issues.append(f"Component too large ({metrics.lines_of_code} lines). Consider splitting.")

        # Too many hooks
        if metrics.hooks_count > 10:
            issues.append(f"Too many hooks ({metrics.hooks_count}). Consider custom hook extraction.")

        # Too many props
        if metrics.props_count > 10:
            issues.append(f"Too many props ({metrics.props_count}). Consider component composition.")

        # No tests
        if not metrics.has_tests:
            issues.append("No test file found for this component.")

        # Low accessibility
        if metrics.accessibility_score < 30:
            issues.append(f"Low accessibility score ({metrics.accessibility_score}%). Add ARIA attributes.")

        # Console statements
        if 'console.log' in content:
            issues.append("Console.log statements found. Remove before production.")

        # Inline styles
        if 'style={{' in content:
            issues.append("Inline styles detected. Consider using CSS modules or styled-components.")

        # Any type usage
        if ': any' in content or 'as any' in content:
            issues.append("TypeScript 'any' type detected. Use proper typing.")

        return issues

    def _generate_report(self) -> dict:
        """Generate analysis report."""
        if not self.components:
            return {"error": "No components found"}

        total_issues = sum(len(c.issues) for c in self.components)
        tested_count = sum(1 for c in self.components if c.has_tests)
        avg_a11y = sum(c.accessibility_score for c in self.components) / len(self.components)

        return {
            "summary": {
                "total_components": len(self.components),
                "total_lines_of_code": sum(c.lines_of_code for c in self.components),
                "average_component_size": round(sum(c.lines_of_code for c in self.components) / len(self.components), 1),
                "test_coverage": f"{(tested_count / len(self.components)) * 100:.1f}%",
                "average_accessibility_score": f"{avg_a11y:.1f}%",
                "total_issues": total_issues,
            },
            "components": [
                {
                    "name": c.name,
                    "path": c.file_path,
                    "lines": c.lines_of_code,
                    "hooks": c.hooks_count,
                    "props": c.props_count,
                    "complexity": c.jsx_complexity,
                    "has_tests": c.has_tests,
                    "a11y_score": f"{c.accessibility_score}%",
                    "issues": c.issues,
                }
                for c in sorted(self.components, key=lambda x: len(x.issues), reverse=True)
            ],
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        untested = [c for c in self.components if not c.has_tests]
        if untested:
            recommendations.append(
                f"Add tests for {len(untested)} components: {', '.join(c.name for c in untested[:5])}"
            )

        large_components = [c for c in self.components if c.lines_of_code > 200]
        if large_components:
            recommendations.append(
                f"Refactor {len(large_components)} large components: {', '.join(c.name for c in large_components[:3])}"
            )

        low_a11y = [c for c in self.components if c.accessibility_score < 40]
        if low_a11y:
            recommendations.append(
                f"Improve accessibility for {len(low_a11y)} components"
            )

        return recommendations


def main():
    """Main entry point."""
    import sys

    project_path = sys.argv[1] if len(sys.argv) > 1 else "."

    analyzer = FrontendComponentAnalyzer(project_path)
    report = analyzer.analyze_project()

    print(json.dumps(report, indent=2))

    # Exit with error code if critical issues found
    if report.get("summary", {}).get("total_issues", 0) > 20:
        sys.exit(1)


if __name__ == "__main__":
    main()
