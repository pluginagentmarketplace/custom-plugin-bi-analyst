#!/usr/bin/env python3
"""
System Design Analyzer
BI Analyst Plugin - Architecture Skill
Analyzes system architecture and provides design recommendations.
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict


@dataclass
class ServiceMetrics:
    """Metrics for a single service/module."""
    name: str
    type: str  # api, worker, gateway, database
    dependencies: list = field(default_factory=list)
    endpoints: int = 0
    models: int = 0
    complexity_score: float = 0.0
    issues: list = field(default_factory=list)


@dataclass
class ArchitectureAnalysis:
    """Complete architecture analysis."""
    style: str
    services: list[ServiceMetrics] = field(default_factory=list)
    coupling_score: float = 0.0
    cohesion_score: float = 0.0
    recommendations: list = field(default_factory=list)


class SystemDesignAnalyzer:
    """Analyze system architecture and design patterns."""

    SERVICE_INDICATORS = {
        'api': ['routes', 'endpoints', 'api', 'controllers', 'views'],
        'worker': ['worker', 'consumer', 'processor', 'job', 'task'],
        'gateway': ['gateway', 'proxy', 'ingress', 'router'],
        'database': ['models', 'entities', 'schema', 'migrations'],
    }

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.services: list[ServiceMetrics] = []
        self.dependency_graph: dict[str, list[str]] = defaultdict(list)

    def analyze(self) -> dict:
        """Perform complete architecture analysis."""
        # Detect architecture style
        style = self._detect_architecture_style()

        # Find and analyze services/modules
        self._find_services()

        # Analyze dependencies
        self._analyze_dependencies()

        # Calculate metrics
        coupling = self._calculate_coupling()
        cohesion = self._calculate_cohesion()

        # Generate recommendations
        recommendations = self._generate_recommendations(style, coupling, cohesion)

        return {
            "architecture": {
                "style": style,
                "total_services": len(self.services),
                "coupling_score": coupling,
                "cohesion_score": cohesion,
            },
            "services": [
                {
                    "name": s.name,
                    "type": s.type,
                    "dependencies": s.dependencies,
                    "endpoints": s.endpoints,
                    "models": s.models,
                    "complexity": s.complexity_score,
                    "issues": s.issues,
                }
                for s in self.services
            ],
            "dependency_graph": dict(self.dependency_graph),
            "patterns_detected": self._detect_patterns(),
            "recommendations": recommendations,
            "health_score": self._calculate_health_score(coupling, cohesion),
        }

    def _detect_architecture_style(self) -> str:
        """Detect the overall architecture style."""
        # Check for microservices indicators
        docker_compose = self.project_path / "docker-compose.yml"
        if docker_compose.exists():
            content = docker_compose.read_text()
            service_count = content.count("build:") + content.count("image:")
            if service_count > 3:
                return "microservices"

        # Check for serverless
        serverless_files = ["serverless.yml", "template.yaml", "sam.yaml"]
        for f in serverless_files:
            if (self.project_path / f).exists():
                return "serverless"

        # Check for modular structure
        modules_dir = self.project_path / "modules"
        packages_dir = self.project_path / "packages"
        if modules_dir.exists() or packages_dir.exists():
            return "modular-monolith"

        # Check directory depth for layered
        src_path = self.project_path / "src"
        if src_path.exists():
            layers = ["domain", "application", "infrastructure", "presentation"]
            layer_count = sum(1 for l in layers if (src_path / l).exists())
            if layer_count >= 3:
                return "layered"

        return "monolith"

    def _find_services(self):
        """Find and categorize services/modules."""
        # Look for service directories
        potential_service_dirs = [
            self.project_path / "services",
            self.project_path / "apps",
            self.project_path / "packages",
            self.project_path / "modules",
            self.project_path / "src",
        ]

        for services_dir in potential_service_dirs:
            if services_dir.exists() and services_dir.is_dir():
                for item in services_dir.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        service = self._analyze_service(item)
                        if service:
                            self.services.append(service)

        # If no services found, analyze as single service
        if not self.services:
            service = self._analyze_service(self.project_path)
            if service:
                service.name = self.project_path.name
                self.services.append(service)

    def _analyze_service(self, service_path: Path) -> Optional[ServiceMetrics]:
        """Analyze a single service/module."""
        if not service_path.exists():
            return None

        service = ServiceMetrics(
            name=service_path.name,
            type=self._determine_service_type(service_path)
        )

        # Count endpoints
        service.endpoints = self._count_endpoints(service_path)

        # Count models
        service.models = self._count_models(service_path)

        # Analyze dependencies
        service.dependencies = self._get_service_dependencies(service_path)

        # Calculate complexity
        service.complexity_score = self._calculate_service_complexity(service_path)

        # Detect issues
        service.issues = self._detect_service_issues(service)

        return service

    def _determine_service_type(self, path: Path) -> str:
        """Determine the type of service."""
        path_lower = str(path).lower()

        for service_type, indicators in self.SERVICE_INDICATORS.items():
            if any(ind in path_lower for ind in indicators):
                return service_type

        # Check file contents
        for py_file in path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if any(f in content for f in ['@app.route', '@router.', 'FastAPI(', 'Flask(']):
                    return 'api'
                if any(f in content for f in ['celery', 'worker', 'consumer']):
                    return 'worker'
            except:
                pass

        return 'module'

    def _count_endpoints(self, path: Path) -> int:
        """Count API endpoints in service."""
        count = 0
        patterns = [
            r'@app\.\w+\s*\(',  # Flask
            r'@router\.\w+\s*\(',  # FastAPI
            r'def\s+\w+.*request',  # Django views
            r'@api_view',  # DRF
        ]

        for py_file in path.rglob("*.py"):
            try:
                content = py_file.read_text()
                for pattern in patterns:
                    count += len(re.findall(pattern, content))
            except:
                pass

        return count

    def _count_models(self, path: Path) -> int:
        """Count data models in service."""
        count = 0
        patterns = [
            r'class\s+\w+\(.*Model\)',  # Django/SQLAlchemy
            r'class\s+\w+\(.*BaseModel\)',  # Pydantic
            r'@dataclass',  # Dataclasses
        ]

        for py_file in path.rglob("*.py"):
            try:
                content = py_file.read_text()
                for pattern in patterns:
                    count += len(re.findall(pattern, content))
            except:
                pass

        return count

    def _get_service_dependencies(self, path: Path) -> list[str]:
        """Get dependencies between services."""
        dependencies = set()

        for py_file in path.rglob("*.py"):
            try:
                content = py_file.read_text()
                # Look for imports from other services
                imports = re.findall(r'from\s+(\w+)', content)
                for imp in imports:
                    if imp not in ['app', 'src', 'tests', path.name]:
                        dependencies.add(imp)
            except:
                pass

        return list(dependencies)

    def _calculate_service_complexity(self, path: Path) -> float:
        """Calculate complexity score for service."""
        total_complexity = 0
        file_count = 0

        for py_file in path.rglob("*.py"):
            try:
                content = py_file.read_text()
                # Simple complexity heuristics
                complexity = 0
                complexity += content.count('if ') * 1
                complexity += content.count('for ') * 1
                complexity += content.count('while ') * 1
                complexity += content.count('try:') * 1
                complexity += content.count('except') * 1
                complexity += content.count('class ') * 2
                complexity += content.count('def ') * 1

                total_complexity += complexity
                file_count += 1
            except:
                pass

        return round(total_complexity / max(file_count, 1), 2)

    def _detect_service_issues(self, service: ServiceMetrics) -> list[str]:
        """Detect potential issues in service design."""
        issues = []

        # Too many dependencies
        if len(service.dependencies) > 10:
            issues.append(f"High coupling: {len(service.dependencies)} dependencies")

        # High complexity
        if service.complexity_score > 100:
            issues.append(f"High complexity score: {service.complexity_score}")

        # Large number of endpoints
        if service.endpoints > 50:
            issues.append(f"Too many endpoints: {service.endpoints}")

        # Many models in non-database service
        if service.type != 'database' and service.models > 20:
            issues.append(f"Many models in {service.type} service: {service.models}")

        return issues

    def _analyze_dependencies(self):
        """Build dependency graph."""
        for service in self.services:
            for dep in service.dependencies:
                self.dependency_graph[service.name].append(dep)

    def _calculate_coupling(self) -> float:
        """Calculate overall coupling score (0-100, lower is better)."""
        if not self.services:
            return 0

        total_deps = sum(len(s.dependencies) for s in self.services)
        max_possible = len(self.services) * (len(self.services) - 1)

        if max_possible == 0:
            return 0

        coupling = (total_deps / max_possible) * 100
        return round(coupling, 1)

    def _calculate_cohesion(self) -> float:
        """Calculate overall cohesion score (0-100, higher is better)."""
        if not self.services:
            return 0

        # Cohesion based on service focus (models:endpoints ratio)
        cohesion_scores = []
        for service in self.services:
            if service.type == 'api' and service.endpoints > 0:
                # Good cohesion: reasonable model-to-endpoint ratio
                ratio = service.models / service.endpoints
                if 0.1 <= ratio <= 2:
                    cohesion_scores.append(80)
                elif 0.05 <= ratio <= 5:
                    cohesion_scores.append(60)
                else:
                    cohesion_scores.append(40)
            else:
                cohesion_scores.append(70)  # Default for non-API services

        return round(sum(cohesion_scores) / len(cohesion_scores), 1) if cohesion_scores else 0

    def _detect_patterns(self) -> list[str]:
        """Detect architectural patterns in use."""
        patterns = []

        # Check for event-driven
        for service in self.services:
            if service.type == 'worker':
                patterns.append('event-driven')
                break

        # Check for API Gateway
        for service in self.services:
            if service.type == 'gateway':
                patterns.append('api-gateway')
                break

        # Check for layered architecture
        layers = ['domain', 'application', 'infrastructure', 'presentation']
        for service_path in [self.project_path / "src"]:
            if service_path.exists():
                found_layers = sum(1 for l in layers if (service_path / l).exists())
                if found_layers >= 3:
                    patterns.append('layered-architecture')

        # Check for repository pattern
        for py_file in self.project_path.rglob("*repository*.py"):
            patterns.append('repository')
            break

        # Check for CQRS
        cqrs_indicators = ['command', 'query', 'handler']
        cqrs_count = sum(1 for ind in cqrs_indicators
                        for _ in self.project_path.rglob(f"*{ind}*.py"))
        if cqrs_count >= 2:
            patterns.append('cqrs')

        return list(set(patterns))

    def _generate_recommendations(
        self,
        style: str,
        coupling: float,
        cohesion: float
    ) -> list[str]:
        """Generate architecture recommendations."""
        recommendations = []

        # Coupling recommendations
        if coupling > 50:
            recommendations.append(
                "HIGH COUPLING: Consider introducing an event bus or API gateway "
                "to reduce direct service dependencies"
            )
        elif coupling > 30:
            recommendations.append(
                "MODERATE COUPLING: Review service boundaries and consider "
                "extracting shared functionality into libraries"
            )

        # Cohesion recommendations
        if cohesion < 50:
            recommendations.append(
                "LOW COHESION: Services may have too many responsibilities. "
                "Consider splitting into focused microservices"
            )

        # Style-specific recommendations
        if style == 'monolith':
            recommendations.append(
                "Consider modular monolith approach to prepare for future scaling"
            )

        if style == 'microservices' and len(self.services) < 3:
            recommendations.append(
                "Few services detected. Verify if microservices architecture "
                "is the right choice for this scale"
            )

        # Service-specific recommendations
        large_services = [s for s in self.services if s.complexity_score > 100]
        if large_services:
            recommendations.append(
                f"Consider splitting complex services: "
                f"{', '.join(s.name for s in large_services[:3])}"
            )

        return recommendations

    def _calculate_health_score(self, coupling: float, cohesion: float) -> float:
        """Calculate overall architecture health score (0-100)."""
        # Weight: 40% coupling, 40% cohesion, 20% patterns
        coupling_score = max(0, 100 - coupling)
        patterns = self._detect_patterns()
        pattern_score = min(len(patterns) * 20, 100)

        health = (coupling_score * 0.4) + (cohesion * 0.4) + (pattern_score * 0.2)
        return round(health, 1)


def main():
    """Main entry point."""
    import sys

    project_path = sys.argv[1] if len(sys.argv) > 1 else "."

    analyzer = SystemDesignAnalyzer(project_path)
    report = analyzer.analyze()

    print(json.dumps(report, indent=2))

    # Exit with warning if health score is low
    if report.get("health_score", 0) < 50:
        sys.exit(1)


if __name__ == "__main__":
    main()
