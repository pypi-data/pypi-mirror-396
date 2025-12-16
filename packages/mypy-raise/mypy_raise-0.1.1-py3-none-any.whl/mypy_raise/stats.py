from dataclasses import dataclass


@dataclass
class AnalysisStats:
    """Statistics for exception analysis."""

    files_checked: int = 0
    functions_checked: int = 0
    violations_found: int = 0
    exceptions_caught: int = 0

    def compliance_rate(self) -> float:
        """Calculate compliance rate."""
        if self.functions_checked == 0:
            return 100.0
        compliant = self.functions_checked - self.violations_found
        return (compliant / self.functions_checked) * 100

    def format_summary(self) -> str:
        """Format statistics summary."""
        lines = [
            '\n' + '=' * 60,
            'mypy-raise Analysis Summary',
            '=' * 60,
            f'Files checked: {self.files_checked}',
            f'Functions analyzed: {self.functions_checked}',
            f'Violations found: {self.violations_found}',
            f'Compliance rate: {self.compliance_rate():.1f}%',
            '=' * 60,
        ]
        return '\n'.join(lines)


# Global statistics instance
STATS = AnalysisStats()
