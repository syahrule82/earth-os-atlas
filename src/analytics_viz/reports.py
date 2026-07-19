"""Report Builder — Custom reports with exportable formats."""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import time, json, hashlib

class ExportFormat(Enum):
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    MARKDOWN = "markdown"
    PDF_DATA = "pdf_data"  # Structured data for PDF rendering

@dataclass
class CustomReport:
    """A custom analytics report."""
    report_id: str
    title: str
    description: str
    author: str
    sections: List[dict] = field(default_factory=list)  # [{"title": "", "data": {}, "chart_type": ""}]
    created_at: float = field(default_factory=time.time)
    parameters: dict = field(default_factory=dict)
    exported: Dict[str, str] = field(default_factory=dict)  # format -> content

class ReportBuilder:
    """Build custom analytics reports with multiple export formats."""

    def __init__(self):
        self.reports: Dict[str, CustomReport] = {}

    def create_report(self, title: str, description: str,
                      author: str, sections: List[dict] = None) -> CustomReport:
        """Create a new custom report."""
        report = CustomReport(
            report_id=hashlib.sha256(f"{title}:{author}:{time.time()}".encode()).hexdigest()[:16],
            title=title, description=description, author=author,
            sections=sections or [],
        )
        self.reports[report.report_id] = report
        return report

    def add_section(self, report_id: str, title: str, data: dict,
                   chart_type: str = "table") -> bool:
        report = self.reports.get(report_id)
        if not report:
            return False
        report.sections.append({
            "title": title, "data": data, "chart_type": chart_type,
        })
        return True

    def export(self, report_id: str, fmt: ExportFormat) -> Optional[str]:
        """Export a report to the specified format."""
        report = self.reports.get(report_id)
        if not report:
            return None

        if fmt == ExportFormat.JSON:
            content = json.dumps({
                "title": report.title,
                "description": report.description,
                "author": report.author,
                "created_at": report.created_at,
                "sections": report.sections,
            }, indent=2)
        elif fmt == ExportFormat.CSV:
            lines = ["section_title,key,value"]
            for section in report.sections:
                title = section["title"]
                data = section["data"]
                if isinstance(data, dict):
                    for k, v in data.items():
                        lines.append(f"{title},{k},{v}")
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            for k, v in item.items():
                                lines.append(f"{title},{k},{v}")
            content = "\n".join(lines)
        elif fmt == ExportFormat.MARKDOWN:
            lines = [f"# {report.title}", "", report.description, "",
                     f"*Author: {report.author}*", f"*Generated: {time.ctime(report.created_at)}*", ""]
            for section in report.sections:
                lines.append(f"## {section['title']}")
                lines.append("")
                data = section["data"]
                if isinstance(data, dict):
                    lines.append("| Key | Value |")
                    lines.append("|-----|-------|")
                    for k, v in data.items():
                        lines.append(f"| {k} | {v} |")
                elif isinstance(data, list):
                    for item in data:
                        lines.append(f"- {item}")
                lines.append("")
            content = "\n".join(lines)
        elif fmt == ExportFormat.HTML:
            lines = [f"<html><head><title>{report.title}</title></head><body>",
                     f"<h1>{report.title}</h1>",
                     f"<p>{report.description}</p>",
                     f"<p><em>Author: {report.author}</em></p>"]
            for section in report.sections:
                lines.append(f"<h2>{section['title']}</h2>")
                data = section["data"]
                if isinstance(data, dict):
                    lines.append("<table border='1'>")
                    for k, v in data.items():
                        lines.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
                    lines.append("</table>")
                elif isinstance(data, list):
                    lines.append("<ul>")
                    for item in data:
                        lines.append(f"<li>{item}</li>")
                    lines.append("</ul>")
            lines.append("</body></html>")
            content = "\n".join(lines)
        else:
            content = json.dumps(report.sections)

        report.exported[fmt.value] = content
        return content

    def get_report(self, report_id: str) -> Optional[CustomReport]:
        return self.reports.get(report_id)

    def list_reports(self) -> List[dict]:
        return [{"id": r.report_id, "title": r.title, "author": r.author,
                 "sections": len(r.sections), "created": r.created_at}
                for r in self.reports.values()]
