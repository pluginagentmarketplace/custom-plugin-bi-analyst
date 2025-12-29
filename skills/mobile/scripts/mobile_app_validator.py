#!/usr/bin/env python3
"""
Mobile App Validator
BI Analyst Plugin - Mobile Skill
Validates mobile app configuration and best practices.
"""

import os
import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ValidationResult:
    """Result of a validation check."""
    category: str
    check_name: str
    passed: bool
    severity: str  # critical, warning, info
    message: str
    suggestion: Optional[str] = None


class MobileAppValidator:
    """Validate mobile app configuration and structure."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.results: list[ValidationResult] = []
        self.platform = self._detect_platform()

    def _detect_platform(self) -> str:
        """Detect mobile platform/framework."""
        # React Native
        if (self.project_path / "package.json").exists():
            try:
                package = json.loads((self.project_path / "package.json").read_text())
                deps = package.get("dependencies", {})
                if "react-native" in deps:
                    return "react-native"
                if "expo" in deps:
                    return "expo"
            except:
                pass

        # Flutter
        if (self.project_path / "pubspec.yaml").exists():
            return "flutter"

        # iOS Native
        if list(self.project_path.glob("*.xcodeproj")) or list(self.project_path.glob("*.xcworkspace")):
            return "ios-native"

        # Android Native
        if (self.project_path / "build.gradle").exists() or (self.project_path / "build.gradle.kts").exists():
            return "android-native"

        return "unknown"

    def validate_all(self) -> dict:
        """Run all validations."""
        self._validate_project_structure()
        self._validate_dependencies()
        self._validate_security()
        self._validate_performance()
        self._validate_accessibility()
        self._validate_testing()

        return self._generate_report()

    def _add_result(self, result: ValidationResult):
        """Add validation result."""
        self.results.append(result)

    def _validate_project_structure(self):
        """Validate project structure."""
        if self.platform == "react-native" or self.platform == "expo":
            self._validate_react_native_structure()
        elif self.platform == "flutter":
            self._validate_flutter_structure()
        elif self.platform == "ios-native":
            self._validate_ios_structure()
        elif self.platform == "android-native":
            self._validate_android_structure()

    def _validate_react_native_structure(self):
        """Validate React Native project structure."""
        # Check for src directory
        if (self.project_path / "src").exists():
            self._add_result(ValidationResult(
                category="Structure",
                check_name="Source directory",
                passed=True,
                severity="info",
                message="src/ directory found"
            ))
        else:
            self._add_result(ValidationResult(
                category="Structure",
                check_name="Source directory",
                passed=False,
                severity="warning",
                message="No src/ directory found",
                suggestion="Organize code in src/ directory"
            ))

        # Check for navigation
        nav_files = list(self.project_path.rglob("*navigation*")) + \
                   list(self.project_path.rglob("*Navigation*"))
        if nav_files:
            self._add_result(ValidationResult(
                category="Structure",
                check_name="Navigation setup",
                passed=True,
                severity="info",
                message="Navigation configuration found"
            ))

        # Check for screens/components organization
        screens_dir = self.project_path / "src" / "screens"
        components_dir = self.project_path / "src" / "components"
        if screens_dir.exists() or components_dir.exists():
            self._add_result(ValidationResult(
                category="Structure",
                check_name="Component organization",
                passed=True,
                severity="info",
                message="Screens/Components directories found"
            ))

    def _validate_flutter_structure(self):
        """Validate Flutter project structure."""
        lib_dir = self.project_path / "lib"
        if lib_dir.exists():
            self._add_result(ValidationResult(
                category="Structure",
                check_name="lib directory",
                passed=True,
                severity="info",
                message="lib/ directory found"
            ))

            # Check for feature-based structure
            features_dir = lib_dir / "features"
            if features_dir.exists():
                self._add_result(ValidationResult(
                    category="Structure",
                    check_name="Feature-based architecture",
                    passed=True,
                    severity="info",
                    message="Feature-based structure detected"
                ))

    def _validate_ios_structure(self):
        """Validate iOS project structure."""
        # Check for Info.plist
        info_plist = list(self.project_path.rglob("Info.plist"))
        if info_plist:
            self._add_result(ValidationResult(
                category="Structure",
                check_name="Info.plist",
                passed=True,
                severity="info",
                message="Info.plist found"
            ))

        # Check for SwiftUI or UIKit
        swift_files = list(self.project_path.rglob("*.swift"))
        has_swiftui = any("SwiftUI" in f.read_text() for f in swift_files[:10] if f.exists())
        if has_swiftui:
            self._add_result(ValidationResult(
                category="Structure",
                check_name="UI Framework",
                passed=True,
                severity="info",
                message="SwiftUI detected"
            ))

    def _validate_android_structure(self):
        """Validate Android project structure."""
        # Check for AndroidManifest.xml
        manifest = list(self.project_path.rglob("AndroidManifest.xml"))
        if manifest:
            self._add_result(ValidationResult(
                category="Structure",
                check_name="AndroidManifest.xml",
                passed=True,
                severity="info",
                message="AndroidManifest.xml found"
            ))

        # Check for Jetpack Compose
        kotlin_files = list(self.project_path.rglob("*.kt"))
        has_compose = any("@Composable" in f.read_text() for f in kotlin_files[:10] if f.exists())
        if has_compose:
            self._add_result(ValidationResult(
                category="Structure",
                check_name="UI Framework",
                passed=True,
                severity="info",
                message="Jetpack Compose detected"
            ))

    def _validate_dependencies(self):
        """Validate dependencies and versions."""
        if self.platform in ["react-native", "expo"]:
            self._validate_npm_dependencies()
        elif self.platform == "flutter":
            self._validate_flutter_dependencies()

    def _validate_npm_dependencies(self):
        """Validate npm dependencies."""
        package_json = self.project_path / "package.json"
        if not package_json.exists():
            return

        try:
            package = json.loads(package_json.read_text())
            deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}

            # Check for outdated React Native
            if "react-native" in deps:
                version = deps["react-native"].replace("^", "").replace("~", "")
                if version.startswith("0.6") or version.startswith("0.5"):
                    self._add_result(ValidationResult(
                        category="Dependencies",
                        check_name="React Native version",
                        passed=False,
                        severity="warning",
                        message=f"Outdated React Native version: {version}",
                        suggestion="Consider upgrading to 0.72+"
                    ))

            # Check for testing libraries
            test_libs = ["jest", "@testing-library/react-native", "detox"]
            has_testing = any(lib in deps for lib in test_libs)
            self._add_result(ValidationResult(
                category="Dependencies",
                check_name="Testing libraries",
                passed=has_testing,
                severity="warning" if not has_testing else "info",
                message="Testing libraries " + ("found" if has_testing else "not found"),
                suggestion=None if has_testing else "Add jest and @testing-library/react-native"
            ))

            # Check for TypeScript
            has_typescript = "typescript" in deps
            self._add_result(ValidationResult(
                category="Dependencies",
                check_name="TypeScript",
                passed=has_typescript,
                severity="warning" if not has_typescript else "info",
                message="TypeScript " + ("enabled" if has_typescript else "not found"),
                suggestion=None if has_typescript else "Consider adding TypeScript for type safety"
            ))

        except Exception as e:
            pass

    def _validate_flutter_dependencies(self):
        """Validate Flutter dependencies."""
        pubspec = self.project_path / "pubspec.yaml"
        if not pubspec.exists():
            return

        content = pubspec.read_text()

        # Check for state management
        state_mgmt = ["provider", "riverpod", "bloc", "getx", "mobx"]
        has_state_mgmt = any(sm in content for sm in state_mgmt)
        self._add_result(ValidationResult(
            category="Dependencies",
            check_name="State management",
            passed=has_state_mgmt,
            severity="warning" if not has_state_mgmt else "info",
            message="State management " + ("configured" if has_state_mgmt else "not found"),
            suggestion=None if has_state_mgmt else "Add Riverpod or Provider for state management"
        ))

    def _validate_security(self):
        """Validate security configurations."""
        # Check for hardcoded secrets
        secret_patterns = [
            r'api[_-]?key\s*[:=]\s*["\'][^"\']+["\']',
            r'secret\s*[:=]\s*["\'][^"\']+["\']',
            r'password\s*[:=]\s*["\'][^"\']+["\']',
            r'token\s*[:=]\s*["\'][^"\']+["\']',
        ]

        source_files = []
        if self.platform in ["react-native", "expo"]:
            source_files = list(self.project_path.rglob("*.js")) + \
                          list(self.project_path.rglob("*.ts")) + \
                          list(self.project_path.rglob("*.tsx"))
        elif self.platform == "flutter":
            source_files = list(self.project_path.rglob("*.dart"))
        elif self.platform == "ios-native":
            source_files = list(self.project_path.rglob("*.swift"))
        elif self.platform == "android-native":
            source_files = list(self.project_path.rglob("*.kt"))

        secrets_found = False
        for file_path in source_files[:50]:  # Limit to first 50 files
            try:
                content = file_path.read_text()
                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        secrets_found = True
                        break
            except:
                pass
            if secrets_found:
                break

        self._add_result(ValidationResult(
            category="Security",
            check_name="Hardcoded secrets",
            passed=not secrets_found,
            severity="critical" if secrets_found else "info",
            message="Hardcoded secrets " + ("detected!" if secrets_found else "not found"),
            suggestion="Use environment variables or secure storage" if secrets_found else None
        ))

        # Check for secure storage
        secure_storage_libs = [
            "react-native-keychain",
            "@react-native-async-storage/async-storage",
            "expo-secure-store",
            "flutter_secure_storage",
        ]

        has_secure_storage = False
        if self.platform in ["react-native", "expo"]:
            package_json = self.project_path / "package.json"
            if package_json.exists():
                content = package_json.read_text()
                has_secure_storage = any(lib in content for lib in secure_storage_libs)
        elif self.platform == "flutter":
            pubspec = self.project_path / "pubspec.yaml"
            if pubspec.exists():
                content = pubspec.read_text()
                has_secure_storage = "flutter_secure_storage" in content

        self._add_result(ValidationResult(
            category="Security",
            check_name="Secure storage",
            passed=has_secure_storage,
            severity="warning" if not has_secure_storage else "info",
            message="Secure storage " + ("configured" if has_secure_storage else "not found"),
            suggestion="Add secure storage for sensitive data" if not has_secure_storage else None
        ))

    def _validate_performance(self):
        """Validate performance best practices."""
        if self.platform in ["react-native", "expo"]:
            # Check for Hermes engine
            if self.platform == "react-native":
                android_build = self.project_path / "android" / "app" / "build.gradle"
                if android_build.exists():
                    content = android_build.read_text()
                    hermes_enabled = "hermesEnabled = true" in content or \
                                    "enableHermes: true" in content
                    self._add_result(ValidationResult(
                        category="Performance",
                        check_name="Hermes engine",
                        passed=hermes_enabled,
                        severity="warning" if not hermes_enabled else "info",
                        message="Hermes " + ("enabled" if hermes_enabled else "not enabled"),
                        suggestion="Enable Hermes for better performance" if not hermes_enabled else None
                    ))

            # Check for memo/useMemo usage
            source_files = list(self.project_path.rglob("*.tsx")) + \
                          list(self.project_path.rglob("*.jsx"))
            memo_usage = 0
            for file_path in source_files[:20]:
                try:
                    content = file_path.read_text()
                    memo_usage += content.count("memo(") + content.count("useMemo(")
                except:
                    pass

            if memo_usage > 0:
                self._add_result(ValidationResult(
                    category="Performance",
                    check_name="Memoization",
                    passed=True,
                    severity="info",
                    message=f"Memoization used ({memo_usage} instances)"
                ))

    def _validate_accessibility(self):
        """Validate accessibility implementation."""
        a11y_found = False

        if self.platform in ["react-native", "expo"]:
            source_files = list(self.project_path.rglob("*.tsx")) + \
                          list(self.project_path.rglob("*.jsx"))
            a11y_props = ["accessible", "accessibilityLabel", "accessibilityRole"]

            for file_path in source_files[:20]:
                try:
                    content = file_path.read_text()
                    if any(prop in content for prop in a11y_props):
                        a11y_found = True
                        break
                except:
                    pass

        self._add_result(ValidationResult(
            category="Accessibility",
            check_name="Accessibility props",
            passed=a11y_found,
            severity="warning" if not a11y_found else "info",
            message="Accessibility properties " + ("found" if a11y_found else "not found"),
            suggestion="Add accessibilityLabel to interactive elements" if not a11y_found else None
        ))

    def _validate_testing(self):
        """Validate testing setup."""
        test_dirs = ["__tests__", "tests", "test", "spec"]
        has_tests = any((self.project_path / d).exists() for d in test_dirs)

        if not has_tests:
            # Check for test files anywhere
            test_files = list(self.project_path.rglob("*.test.*")) + \
                        list(self.project_path.rglob("*.spec.*")) + \
                        list(self.project_path.rglob("*_test.*"))
            has_tests = len(test_files) > 0

        self._add_result(ValidationResult(
            category="Testing",
            check_name="Test files exist",
            passed=has_tests,
            severity="warning" if not has_tests else "info",
            message="Tests " + ("found" if has_tests else "not found"),
            suggestion="Add unit tests for components and utilities" if not has_tests else None
        ))

    def _generate_report(self) -> dict:
        """Generate validation report."""
        critical = [r for r in self.results if r.severity == "critical" and not r.passed]
        warnings = [r for r in self.results if r.severity == "warning" and not r.passed]
        passed = [r for r in self.results if r.passed]

        return {
            "platform": self.platform,
            "summary": {
                "total_checks": len(self.results),
                "passed": len(passed),
                "critical_issues": len(critical),
                "warnings": len(warnings),
                "ready_for_production": len(critical) == 0,
            },
            "results_by_category": self._group_by_category(),
            "critical_issues": [
                {
                    "check": r.check_name,
                    "message": r.message,
                    "suggestion": r.suggestion,
                }
                for r in critical
            ],
            "recommendations": [r.suggestion for r in self.results if r.suggestion and not r.passed],
        }

    def _group_by_category(self) -> dict:
        """Group results by category."""
        grouped = {}
        for result in self.results:
            if result.category not in grouped:
                grouped[result.category] = {"passed": 0, "failed": 0}
            if result.passed:
                grouped[result.category]["passed"] += 1
            else:
                grouped[result.category]["failed"] += 1
        return grouped


def main():
    """Main entry point."""
    import sys

    project_path = sys.argv[1] if len(sys.argv) > 1 else "."

    validator = MobileAppValidator(project_path)
    report = validator.validate_all()

    print(json.dumps(report, indent=2))

    if not report["summary"]["ready_for_production"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
