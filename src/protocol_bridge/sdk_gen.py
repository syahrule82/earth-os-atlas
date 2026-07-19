"""SDK Auto-Generator — Generate SDKs from OpenAPI spec."""
from dataclasses import dataclass, field
from typing import Dict, List, Any
import hashlib, time, json

@dataclass
class OpenAPISpec:
    """OpenAPI 3.0 specification for ATLAS API."""
    version: str = "3.4.0"
    title: str = "ATLAS — Earth OS API"
    description: str = "The Living Economic Operating System"
    endpoints: List[dict] = field(default_factory=list)
    schemas: Dict[str, dict] = field(default_factory=dict)
    security_schemes: Dict[str, dict] = field(default_factory=lambda: {
        "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-Atlas-Key"},
    })

    def add_endpoint(self, path: str, method: str, summary: str,
                    request_schema: dict, response_schema: dict,
                    required_scopes: List[str] = None) -> None:
        self.endpoints.append({
            "path": path, "method": method.lower(),
            "summary": summary,
            "request": request_schema,
            "response": response_schema,
            "scopes": required_scopes or [],
        })

    def to_openapi(self) -> dict:
        """Generate OpenAPI 3.0 JSON."""
        paths = {}
        for ep in self.endpoints:
            if ep["path"] not in paths:
                paths[ep["path"]] = {}
            paths[ep["path"]][ep["method"]] = {
                "summary": ep["summary"],
                "security": [{"ApiKeyAuth": ep["scopes"]}],
                "requestBody": {"content": {"application/json": {"schema": ep["request"]}}},
                "responses": {"200": {"description": "Success", "content": {"application/json": {"schema": ep["response"]}}}},
            }
        return {
            "openapi": "3.0.3",
            "info": {"title": self.title, "version": self.version, "description": self.description},
            "paths": paths,
            "components": {"schemas": self.schemas, "securitySchemes": self.security_schemes},
        }

class SDKAutoGenerator:
    """
    Auto-generates SDKs from OpenAPI specification.
    Supports: Python, TypeScript, Rust, Go.
    """

    SUPPORTED_LANGS = ["python", "typescript", "rust", "go"]

    def __init__(self):
        self.spec = OpenAPISpec()
        self.generated_sdks: Dict[str, str] = {}  # lang -> code
        self._populate_default_endpoints()

    def _populate_default_endpoints(self):
        """Populate with known ATLAS API endpoints."""
        endpoints = [
            ("/v1/proof/create", "post", "Create contribution proof",
             {"type": "object", "properties": {"creator_id": {"type": "string"}, "category": {"type": "string"},
              "tier": {"type": "string"}, "hours": {"type": "number"}}},
             {"type": "object", "properties": {"proof_id": {"type": "string"}, "base_value": {"type": "string"}}},
             ["proof:create"]),
            ("/v1/ledger/mint", "post", "Mint ATLAS from proof",
             {"type": "object", "properties": {"proof_id": {"type": "string"}, "confidence": {"type": "number"}}},
             {"type": "object", "properties": {"amount": {"type": "string"}, "proof_id": {"type": "string"}}},
             ["ledger:mint"]),
            ("/v1/ledger/balance/{address}", "get", "Check balance",
             {"type": "object"}, {"type": "object", "properties": {"balance": {"type": "string"}}},
             ["ledger:read"]),
            ("/v1/analytics/network", "get", "Network statistics",
             {"type": "object"}, {"type": "object"}, ["analytics:read"]),
            ("/v1/dao/propose", "post", "Create governance proposal",
             {"type": "object", "properties": {"title": {"type": "string"}, "description": {"type": "string"}}},
             {"type": "object", "properties": {"proposal_id": {"type": "string"}}},
             ["governance:propose"]),
        ]
        for path, method, summary, req, resp, scopes in endpoints:
            self.spec.add_endpoint(path, method, summary, req, resp, scopes)

    def generate(self, lang: str) -> str:
        """Generate SDK code for the specified language."""
        if lang not in self.SUPPORTED_LANGS:
            raise ValueError(f"Unsupported language: {lang}. Supported: {self.SUPPORTED_LANGS}")
        if lang == "python":
            code = self._gen_python()
        elif lang == "typescript":
            code = self._gen_typescript()
        elif lang == "rust":
            code = self._gen_rust()
        else:
            code = self._gen_go()
        self.generated_sdks[lang] = code
        return code

    def _gen_python(self) -> str:
        lines = ["# Auto-generated ATLAS Python SDK", f"# API Version: {self.spec.version}",
                 "import requests", "", "class AtlasClient:",
                 f"    def __init__(self, base_url, api_key=None):", "        self.base_url = base_url",
                 "        self.headers = {'Content-Type': 'application/json'}",
                 "        if api_key: self.headers['X-Atlas-Key'] = api_key", ""]
        for ep in self.spec.endpoints:
            func_name = ep["path"].replace("/", "_").strip("_").replace("-", "_")
            if ep["method"] == "get":
                lines.append(f"    def {func_name}(self, **params):")
                lines.append(f"        r = requests.get(self.base_url + '{ep['path']}', headers=self.headers, params=params)")
                lines.append(f"        return r.json()")
            else:
                lines.append(f"    def {func_name}(self, data):")
                lines.append(f"        r = requests.{ep['method']}(self.base_url + '{ep['path']}', headers=self.headers, json=data)")
                lines.append(f"        return r.json()")
            lines.append("")
        return "\n".join(lines)

    def _gen_typescript(self) -> str:
        lines = ["// Auto-generated ATLAS TypeScript SDK", f"// API Version: {self.spec.version}",
                 "export class AtlasClient {", "  private baseUrl: string;",
                 "  private headers: Record<string, string>;", "",
                 "  constructor(baseUrl: string, apiKey?: string) {", "    this.baseUrl = baseUrl;",
                 "    this.headers = {'Content-Type': 'application/json'};",
                 "    if (apiKey) this.headers['X-Atlas-Key'] = apiKey;", "  }", ""]
        for ep in self.spec.endpoints:
            func_name = ep["path"].replace("/", "_").strip("_").replace("-", "_")
            if ep["method"] == "get":
                lines.append(f"  async {func_name}(params?: Record<string, any>): Promise<any> {{")
                lines.append(f"    const r = await fetch(this.baseUrl + '{ep["path"]}', {{headers: this.headers}});")
                lines.append(f"    return r.json();")
                lines.append(f"  }}")
            else:
                lines.append(f"  async {func_name}(data: any): Promise<any> {{")
                lines.append(f"    const r = await fetch(this.baseUrl + '{ep["path"]}', {{method: '{ep["method"].upper()}', headers: this.headers, body: JSON.stringify(data)}});")
                lines.append(f"    return r.json();")
                lines.append(f"  }}")
            lines.append("")
        lines.append("}")
        return "\n".join(lines)

    def _gen_rust(self) -> str:
        lines = ["// Auto-generated ATLAS Rust SDK", f"// API Version: {self.spec.version}",
                 "use reqwest::Client;", "", "pub struct AtlasClient {",
                 "    client: Client,", "    base_url: String,", "    api_key: Option<String>,", "}", "",
                 "impl AtlasClient {", "    pub fn new(base_url: &str) -> Self {",
                 "        Self { client: Client::new(), base_url: base_url.to_string(), api_key: None }",
                 "    }", "", "    pub fn with_api_key(mut self, key: &str) -> Self {",
                 "        self.api_key = Some(key.to_string()); self", "    }", ""]
        for ep in self.spec.endpoints[:3]:  # Limit for brevity
            func_name = ep["path"].replace("/", "_").strip("_").replace("-", "_")
            lines.append(f"    pub async fn {func_name}(&self) -> Result<serde_json::Value, Box<dyn std::error::Error>> {{")
            lines.append(f"        let url = format!("{{}}{ep['path']}", self.base_url);")
            lines.append(f"        let resp = self.client.get(&url).send().await?;")
            lines.append(f"        Ok(resp.json().await?)")
            lines.append(f"    }}")
            lines.append("")
        lines.append("}")
        return "\n".join(lines)

    def _gen_go(self) -> str:
        lines = ["// Auto-generated ATLAS Go SDK", f"// API Version: {self.spec.version}",
                 "package atlas", "", "import (\"net/http\" \"encoding/json\")", "",
                 "type Client struct {", "    BaseURL string", "    APIKey string", "    HTTP *http.Client", "}", "",
                 "func NewClient(baseURL string) *Client {",
                 "    return &Client{BaseURL: baseURL, HTTP: &http.Client{}}", "}", ""]
        for ep in self.spec.endpoints[:3]:
            func_name = ep["path"].replace("/", "_").strip("_").replace("-", "_")
            lines.append(f"func (c *Client) {func_name.title()}() (map[string]interface{{}}, error) {{")
            lines.append(f"    req, _ := http.NewRequest("GET", c.BaseURL+"{ep['path']}", nil)")
            lines.append(f"    resp, err := c.HTTP.Do(req)")
            lines.append(f"    if err != nil {{ return nil, err }}")
            lines.append(f"    defer resp.Body.Close()")
            lines.append(f"    var result map[string]interface{{}}")
            lines.append(f"    json.NewDecoder(resp.Body).Decode(&result)")
            lines.append(f"    return result, nil")
            lines.append(f"}}")
            lines.append("")
        return "\n".join(lines)

    def get_openapi_json(self) -> str:
        return json.dumps(self.spec.to_openapi(), indent=2)
