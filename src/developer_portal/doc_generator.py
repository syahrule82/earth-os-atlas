"""Documentation Generator — Auto-generate docs from code, Mermaid diagrams."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time, re

@dataclass
class AutoDoc:
    """Auto-generated documentation for a module."""
    module_name: str
    docstring: str
    classes: List[dict] = field(default_factory=list)  # [{"name": "", "docstring": "", "methods": []}]
    functions: List[dict] = field(default_factory=list)
    generated_at: float = field(default_factory=time.time)

@dataclass
class MermaidDiagramGenerator:
    """Generates Mermaid diagrams for documentation."""

    def architecture_diagram(self, layers: List[str]) -> str:
        """Generate a Mermaid architecture diagram."""
        lines = ["graph TD"]
        for i, layer in enumerate(layers):
            if i > 0:
                lines.append(f"    L{i-1} --> L{i}")
            lines.append(f"    L{i}[{layer}]")
        return "\n".join(lines)

    def flow_diagram(self, steps: List[str]) -> str:
        """Generate a Mermaid flowchart."""
        lines = ["graph LR"]
        for i, step in enumerate(steps):
            if i > 0:
                lines.append(f"    S{i-1} --> S{i}")
            lines.append(f"    S{i}[{step}]")
        return "\n".join(lines)

    def sequence_diagram(self, participants: List[str], messages: List[tuple]) -> str:
        """Generate a Mermaid sequence diagram."""
        lines = ["sequenceDiagram"]
        for p in participants:
            lines.append(f"    participant {p}")
        for sender, receiver, msg in messages:
            lines.append(f"    {sender}->>{receiver}: {msg}")
        return "\n".join(lines)

    def er_diagram(self, entities: List[dict]) -> str:
        """Generate a Mermaid ER diagram."""
        lines = ["erDiagram"]
        for entity in entities:
            name = entity["name"]
            attributes = entity.get("attributes", [])
            for attr in attributes:
                lines.append(f"    {name} {{
                    {attr["type"]} {attr["name"]}
                }}")
            for rel in entity.get("relationships", []):
                lines.append(f"    {name} ||--o{{ {rel["target"]} : {rel["label"]}")
        return "\n".join(lines)

class DocGenerator:
    """
    Auto-generates documentation from code docstrings.
    Supports: Python, Markdown, Mermaid diagrams.
    """

    def __init__(self):
        self.docs: Dict[str, AutoDoc] = {}
        self.mermaid = MermaidDiagramGenerator()

    def generate_module_doc(self, module_name: str, source_code: str) -> AutoDoc:
        """Generate documentation from Python source code."""
        doc = AutoDoc(module_name=module_name, docstring="")

        # Extract module docstring
        module_match = re.search(r'^"""(.*?)"""', source_code, re.DOTALL)
        if module_match:
            doc.docstring = module_match.group(1).strip()

        # Extract classes
        class_pattern = re.finditer(
            r'class\s+(\w+).*?:\s*"""(.*?)"""', source_code, re.DOTALL
        )
        for match in class_pattern:
            class_name = match.group(1)
            class_doc = match.group(2).strip()
            methods = []
            # Find methods in the class (simplified)
            method_pattern = re.finditer(
                r'def\s+(\w+)\(.*?\).*?:\s*"""(.*?)"""', source_code, re.DOTALL
            )
            for m in method_pattern:
                methods.append({"name": m.group(1), "docstring": m.group(2).strip()})
            doc.classes.append({"name": class_name, "docstring": class_doc, "methods": methods})

        # Extract standalone functions
        func_pattern = re.finditer(
            r'^def\s+(\w+)\(.*?\).*?:\s*"""(.*?)"""', source_code, re.DOTALL | re.MULTILINE
        )
        for match in func_pattern:
            doc.functions.append({"name": match.group(1), "docstring": match.group(2).strip()})

        self.docs[module_name] = doc
        return doc

    def to_markdown(self, module_name: str) -> str:
        """Convert auto-doc to Markdown."""
        doc = self.docs.get(module_name)
        if not doc:
            return f"# {module_name}\n\nNo documentation available."

        lines = [f"# {doc.module_name}", ""]
        if doc.docstring:
            lines.append(doc.docstring)
            lines.append("")

        if doc.classes:
            lines.append("## Classes")
            lines.append("")
            for cls in doc.classes:
                lines.append(f"### {cls['name']}")
                lines.append("")
                lines.append(cls['docstring'])
                lines.append("")
                if cls['methods']:
                    lines.append("**Methods:**")
                    lines.append("")
                    for method in cls['methods']:
                        lines.append(f"- `{method['name']}()`: {method['docstring']}")
                    lines.append("")

        if doc.functions:
            lines.append("## Functions")
            lines.append("")
            for func in doc.functions:
                lines.append(f"### `{func['name']}()`")
                lines.append("")
                lines.append(func['docstring'])
                lines.append("")

        return "\n".join(lines)

    def generate_architecture_doc(self, layers: List[str]) -> str:
        """Generate architecture documentation with Mermaid diagram."""
        mermaid = self.mermaid.architecture_diagram(layers)
        lines = ["# ATLAS Architecture", "", "```mermaid", mermaid, "```", "",
                 "## Layer Details", ""]
        for i, layer in enumerate(layers, 1):
            lines.append(f"### Layer {i}: {layer}")
            lines.append("")
        return "\n".join(lines)

    def generate_changelog(self, commits: List[dict]) -> str:
        """Auto-generate changelog from commits."""
        lines = ["# Changelog", ""]
        for commit in commits:
            lines.append(f"## {commit.get('date', 'Unknown')}")
            lines.append("")
            msg = commit.get('message', '')
            lines.append(f"- {msg}")
            lines.append("")
        return "\n".join(lines)

    def stats(self) -> dict:
        return {
            "total_docs": len(self.docs),
            "total_classes": sum(len(d.classes) for d in self.docs.values()),
            "total_functions": sum(len(d.functions) for d in self.docs.values()),
        }
