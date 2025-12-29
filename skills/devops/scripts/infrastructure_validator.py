#!/usr/bin/env python3
"""
Infrastructure Validator
BI Analyst Plugin - DevOps Skill
Validates infrastructure configuration and deployment readiness.
"""

import os
import re
import yaml
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    category: str
    check_name: str
    passed: bool
    severity: str  # critical, warning, info
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


class InfrastructureValidator:
    """Validate infrastructure configuration for deployment readiness."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.results: list[ValidationResult] = []

    def validate_all(self) -> dict:
        """Run all validation checks."""
        self._validate_docker()
        self._validate_kubernetes()
        self._validate_terraform()
        self._validate_cicd()
        self._validate_security()
        self._validate_monitoring()

        return self._generate_report()

    def _add_result(self, result: ValidationResult):
        """Add validation result."""
        self.results.append(result)

    def _validate_docker(self):
        """Validate Docker configuration."""
        # Check Dockerfile exists
        dockerfile = self.project_path / "Dockerfile"
        if not dockerfile.exists():
            self._add_result(ValidationResult(
                category="Docker",
                check_name="Dockerfile exists",
                passed=False,
                severity="critical",
                message="Dockerfile not found in project root",
                suggestion="Create a Dockerfile for containerization"
            ))
            return

        content = dockerfile.read_text()

        # Check for multi-stage build
        if content.count("FROM ") > 1:
            self._add_result(ValidationResult(
                category="Docker",
                check_name="Multi-stage build",
                passed=True,
                severity="info",
                message="Multi-stage build detected - good for image size optimization",
                file_path=str(dockerfile)
            ))
        else:
            self._add_result(ValidationResult(
                category="Docker",
                check_name="Multi-stage build",
                passed=False,
                severity="warning",
                message="Single-stage build detected",
                file_path=str(dockerfile),
                suggestion="Consider multi-stage build to reduce image size"
            ))

        # Check for non-root user
        if "USER " in content and "root" not in content.split("USER ")[-1].split()[0]:
            self._add_result(ValidationResult(
                category="Docker",
                check_name="Non-root user",
                passed=True,
                severity="info",
                message="Container runs as non-root user",
                file_path=str(dockerfile)
            ))
        else:
            self._add_result(ValidationResult(
                category="Docker",
                check_name="Non-root user",
                passed=False,
                severity="warning",
                message="Container may run as root",
                file_path=str(dockerfile),
                suggestion="Add 'USER appuser' after creating non-root user"
            ))

        # Check for HEALTHCHECK
        if "HEALTHCHECK" in content:
            self._add_result(ValidationResult(
                category="Docker",
                check_name="Health check",
                passed=True,
                severity="info",
                message="HEALTHCHECK instruction present",
                file_path=str(dockerfile)
            ))
        else:
            self._add_result(ValidationResult(
                category="Docker",
                check_name="Health check",
                passed=False,
                severity="warning",
                message="No HEALTHCHECK instruction found",
                file_path=str(dockerfile),
                suggestion="Add HEALTHCHECK for container orchestration"
            ))

        # Check .dockerignore
        dockerignore = self.project_path / ".dockerignore"
        if dockerignore.exists():
            self._add_result(ValidationResult(
                category="Docker",
                check_name=".dockerignore exists",
                passed=True,
                severity="info",
                message=".dockerignore file found",
                file_path=str(dockerignore)
            ))
        else:
            self._add_result(ValidationResult(
                category="Docker",
                check_name=".dockerignore exists",
                passed=False,
                severity="warning",
                message=".dockerignore not found",
                suggestion="Create .dockerignore to exclude unnecessary files"
            ))

    def _validate_kubernetes(self):
        """Validate Kubernetes manifests."""
        k8s_dirs = ["k8s", "kubernetes", "manifests", "deploy"]
        k8s_path = None

        for dir_name in k8s_dirs:
            candidate = self.project_path / dir_name
            if candidate.exists():
                k8s_path = candidate
                break

        if not k8s_path:
            self._add_result(ValidationResult(
                category="Kubernetes",
                check_name="K8s manifests exist",
                passed=False,
                severity="info",
                message="No Kubernetes manifests directory found",
                suggestion="Create k8s/ directory for Kubernetes manifests"
            ))
            return

        yaml_files = list(k8s_path.rglob("*.yaml")) + list(k8s_path.rglob("*.yml"))

        for yaml_file in yaml_files:
            try:
                content = yaml.safe_load(yaml_file.read_text())
                if not content:
                    continue

                kind = content.get("kind", "")

                # Check Deployment best practices
                if kind == "Deployment":
                    self._validate_k8s_deployment(content, yaml_file)

                # Check Service
                if kind == "Service":
                    self._validate_k8s_service(content, yaml_file)

            except yaml.YAMLError as e:
                self._add_result(ValidationResult(
                    category="Kubernetes",
                    check_name="Valid YAML",
                    passed=False,
                    severity="critical",
                    message=f"Invalid YAML: {str(e)}",
                    file_path=str(yaml_file)
                ))

    def _validate_k8s_deployment(self, content: dict, file_path: Path):
        """Validate Kubernetes Deployment manifest."""
        spec = content.get("spec", {})
        template = spec.get("template", {}).get("spec", {})
        containers = template.get("containers", [])

        # Check replicas
        replicas = spec.get("replicas", 1)
        if replicas < 2:
            self._add_result(ValidationResult(
                category="Kubernetes",
                check_name="High availability",
                passed=False,
                severity="warning",
                message=f"Only {replicas} replica(s) configured",
                file_path=str(file_path),
                suggestion="Use at least 2 replicas for high availability"
            ))

        # Check resource limits
        for container in containers:
            resources = container.get("resources", {})
            if not resources.get("limits") or not resources.get("requests"):
                self._add_result(ValidationResult(
                    category="Kubernetes",
                    check_name="Resource limits",
                    passed=False,
                    severity="warning",
                    message=f"Container '{container.get('name')}' missing resource limits/requests",
                    file_path=str(file_path),
                    suggestion="Define CPU and memory limits for predictable scheduling"
                ))

            # Check liveness/readiness probes
            if not container.get("livenessProbe"):
                self._add_result(ValidationResult(
                    category="Kubernetes",
                    check_name="Liveness probe",
                    passed=False,
                    severity="warning",
                    message=f"Container '{container.get('name')}' missing livenessProbe",
                    file_path=str(file_path),
                    suggestion="Add livenessProbe for automatic restart on failure"
                ))

            if not container.get("readinessProbe"):
                self._add_result(ValidationResult(
                    category="Kubernetes",
                    check_name="Readiness probe",
                    passed=False,
                    severity="warning",
                    message=f"Container '{container.get('name')}' missing readinessProbe",
                    file_path=str(file_path),
                    suggestion="Add readinessProbe for traffic management"
                ))

    def _validate_k8s_service(self, content: dict, file_path: Path):
        """Validate Kubernetes Service manifest."""
        spec = content.get("spec", {})
        service_type = spec.get("type", "ClusterIP")

        if service_type == "NodePort":
            self._add_result(ValidationResult(
                category="Kubernetes",
                check_name="Service type",
                passed=False,
                severity="warning",
                message="NodePort service type detected",
                file_path=str(file_path),
                suggestion="Consider using ClusterIP with Ingress for production"
            ))

    def _validate_terraform(self):
        """Validate Terraform configuration."""
        tf_dirs = ["terraform", "infra", "infrastructure"]
        tf_path = None

        for dir_name in tf_dirs:
            candidate = self.project_path / dir_name
            if candidate.exists():
                tf_path = candidate
                break

        if not tf_path:
            return

        # Check for backend configuration
        backend_found = False
        tf_files = list(tf_path.rglob("*.tf"))

        for tf_file in tf_files:
            content = tf_file.read_text()
            if "backend" in content and ("s3" in content or "gcs" in content or "azurerm" in content):
                backend_found = True
                break

        if backend_found:
            self._add_result(ValidationResult(
                category="Terraform",
                check_name="Remote backend",
                passed=True,
                severity="info",
                message="Remote state backend configured"
            ))
        else:
            self._add_result(ValidationResult(
                category="Terraform",
                check_name="Remote backend",
                passed=False,
                severity="critical",
                message="No remote state backend found",
                suggestion="Configure S3/GCS/Azure backend for state management"
            ))

        # Check for state locking
        for tf_file in tf_files:
            content = tf_file.read_text()
            if "dynamodb_table" in content or "gcs" in content:
                self._add_result(ValidationResult(
                    category="Terraform",
                    check_name="State locking",
                    passed=True,
                    severity="info",
                    message="State locking configured"
                ))
                break

    def _validate_cicd(self):
        """Validate CI/CD configuration."""
        cicd_files = [
            (".github/workflows", "GitHub Actions"),
            (".gitlab-ci.yml", "GitLab CI"),
            ("Jenkinsfile", "Jenkins"),
            (".circleci/config.yml", "CircleCI"),
        ]

        found_cicd = False
        for path, name in cicd_files:
            full_path = self.project_path / path
            if full_path.exists():
                found_cicd = True
                self._add_result(ValidationResult(
                    category="CI/CD",
                    check_name="CI/CD configured",
                    passed=True,
                    severity="info",
                    message=f"{name} configuration found",
                    file_path=str(full_path)
                ))
                break

        if not found_cicd:
            self._add_result(ValidationResult(
                category="CI/CD",
                check_name="CI/CD configured",
                passed=False,
                severity="warning",
                message="No CI/CD configuration found",
                suggestion="Set up GitHub Actions or other CI/CD pipeline"
            ))

    def _validate_security(self):
        """Validate security configurations."""
        # Check for secrets in code
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
            (r'AWS_ACCESS_KEY_ID\s*=\s*["\']AKIA', "AWS access key"),
        ]

        for py_file in self.project_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                for pattern, desc in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self._add_result(ValidationResult(
                            category="Security",
                            check_name="No hardcoded secrets",
                            passed=False,
                            severity="critical",
                            message=f"{desc} detected",
                            file_path=str(py_file),
                            suggestion="Use environment variables or secrets manager"
                        ))
            except:
                pass

        # Check .env in .gitignore
        gitignore = self.project_path / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            if ".env" in content:
                self._add_result(ValidationResult(
                    category="Security",
                    check_name=".env in .gitignore",
                    passed=True,
                    severity="info",
                    message=".env files are ignored by git"
                ))
            else:
                self._add_result(ValidationResult(
                    category="Security",
                    check_name=".env in .gitignore",
                    passed=False,
                    severity="critical",
                    message=".env not in .gitignore",
                    suggestion="Add .env to .gitignore to prevent secret leakage"
                ))

    def _validate_monitoring(self):
        """Validate monitoring configuration."""
        monitoring_indicators = [
            ("prometheus", "Prometheus metrics"),
            ("grafana", "Grafana dashboards"),
            ("/metrics", "Metrics endpoint"),
            ("/health", "Health endpoint"),
            ("sentry", "Sentry error tracking"),
            ("datadog", "Datadog monitoring"),
        ]

        found_monitoring = []
        for py_file in self.project_path.rglob("*.py"):
            try:
                content = py_file.read_text().lower()
                for indicator, name in monitoring_indicators:
                    if indicator in content and name not in found_monitoring:
                        found_monitoring.append(name)
            except:
                pass

        if found_monitoring:
            self._add_result(ValidationResult(
                category="Monitoring",
                check_name="Monitoring configured",
                passed=True,
                severity="info",
                message=f"Found: {', '.join(found_monitoring)}"
            ))
        else:
            self._add_result(ValidationResult(
                category="Monitoring",
                check_name="Monitoring configured",
                passed=False,
                severity="warning",
                message="No monitoring configuration detected",
                suggestion="Add Prometheus metrics and health endpoints"
            ))

    def _generate_report(self) -> dict:
        """Generate validation report."""
        critical = [r for r in self.results if r.severity == "critical" and not r.passed]
        warnings = [r for r in self.results if r.severity == "warning" and not r.passed]
        passed = [r for r in self.results if r.passed]

        deployment_ready = len(critical) == 0

        return {
            "summary": {
                "deployment_ready": deployment_ready,
                "total_checks": len(self.results),
                "passed": len(passed),
                "critical_issues": len(critical),
                "warnings": len(warnings),
            },
            "results_by_category": self._group_by_category(),
            "critical_issues": [
                {
                    "check": r.check_name,
                    "message": r.message,
                    "file": r.file_path,
                    "suggestion": r.suggestion,
                }
                for r in critical
            ],
            "warnings": [
                {
                    "check": r.check_name,
                    "message": r.message,
                    "suggestion": r.suggestion,
                }
                for r in warnings
            ],
        }

    def _group_by_category(self) -> dict:
        """Group results by category."""
        grouped = {}
        for result in self.results:
            if result.category not in grouped:
                grouped[result.category] = {"passed": 0, "failed": 0, "checks": []}
            if result.passed:
                grouped[result.category]["passed"] += 1
            else:
                grouped[result.category]["failed"] += 1
            grouped[result.category]["checks"].append({
                "name": result.check_name,
                "passed": result.passed,
                "severity": result.severity,
                "message": result.message,
            })
        return grouped


def main():
    """Main entry point."""
    import sys

    project_path = sys.argv[1] if len(sys.argv) > 1 else "."

    validator = InfrastructureValidator(project_path)
    report = validator.validate_all()

    print(json.dumps(report, indent=2))

    # Exit with error if not deployment ready
    if not report["summary"]["deployment_ready"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
