import json
import requests
import os
from packageurl import PackageURL
import asyncio
import aiohttp
from abc import ABC, abstractmethod
from datetime import datetime
# -----------------------------------------------------
# BASE FETCHERS (Modular Structure)
# -----------------------------------------------------

class BaseFetcher(ABC):
    """Abstract base class for all package metadata fetchers."""
    def __init__(self, session):
        self.session = session

    @abstractmethod
    async def fetch_metadata(self, name: str, version: str) -> dict:
        """Fetch description and release date."""
        pass

    async def _fetch_url(self, url: str) -> dict or str or None:
        """Asynchronously fetch a URL and return JSON/Text data."""
        try:
            # Note: 10-second timeout to handle slow/unresponsive APIs gracefully
            async with self.session.get(url, timeout=10) as res:
                if res.status == 200:
                    try:
                        return await res.json()
                    except:
                        return await res.text() 
                else:
                    return None
        except Exception:
            # print(f"[WARN] HTTP fetch failed for {url}")
            return None

class PypiFetcher(BaseFetcher):
    """Fetches metadata for Python packages from PyPI."""
    async def fetch_metadata(self, name: str, version: str) -> dict:
        j = await self._fetch_url(f"https://pypi.org/pypi/{name}/json")
        data = {"description": "", "release_date": ""}
        if j and j.get("info"):
            data["description"] = j["info"].get("summary", "")
            if version and version in j.get("releases", {}):
                rel = j["releases"][version]
                if rel and len(rel) > 0 and "upload_time_iso_8601" in rel[0]:
                    data["release_date"] = rel[0]["upload_time_iso_8601"]
        return data

class NpmFetcher(BaseFetcher):
    """Fetches metadata for Node.js packages from npmjs.org."""
    async def fetch_metadata(self, name: str, version: str) -> dict:
        j = await self._fetch_url(f"https://registry.npmjs.org/{name}")
        data = {"description": "", "release_date": ""}
        if j:
            data["description"] = j.get("description", "")
            if version:
                data["release_date"] = j.get("time", {}).get(version, "")
        return data

class RubygemsFetcher(BaseFetcher):
    """Fetches metadata for Ruby gems from RubyGems.org."""
    async def fetch_metadata(self, name: str, version: str) -> dict:
        data = {"description": "", "release_date": ""}
        
        # 1. Fetch main gem info
        j = await self._fetch_url(f"https://rubygems.org/api/v1/gems/{name}.json")
        if j:
            # Uses 'info' field for the description
            data["description"] = j.get("info", "") 
            
            # 2. Fetch specific version metadata for release date
            if version:
                j2 = await self._fetch_url(f"https://rubygems.org/api/v1/versions/{name}.json")
                if j2 and isinstance(j2, list):
                    for v in j2:
                        if v.get("number") == version:
                            # Use 'created_at' as the release date
                            data["release_date"] = v.get("created_at", "")
                            break
        return data

class MavenFetcher(BaseFetcher):
    """Fetches metadata for Maven (Java) artifacts from Maven Central."""
    async def fetch_metadata(self, name: str, version: str) -> dict:
        data = {"description": "", "release_date": ""}
        
        # 'name' is expected to be in "group:artifact" format
        group, artifact = name.split(":") if ":" in name else ("", name)

        # Maven Solr Search API 
        api_url = f"https://search.maven.org/solrsearch/select?q=g:{group}+AND+a:{artifact}&rows=1&wt=json"
        j = await self._fetch_url(api_url)

        
        
        # --- FIX: Ensure the API response is a dictionary ---
        if not isinstance(j, dict):
            # If j is a string (non-JSON response), we skip processing and return empty data
            print(f"[WARN] Maven API for {name} returned non-JSON data or failed parsing.")
            return data
        # ----------------------------------------------------

        if j and j.get("response", {}).get("docs"):
            doc = j["response"]["docs"][0]
            
            
            # 1. Try 'description' field (often empty)
            description = doc.get("description", "")

            # 2. Fallback: If description is empty, use the full ID (group:artifact:version)
            if not description:
                description = doc.get("id", "")
                
            data["description"] = description
            
            # Maven provides a timestamp, use that as release date
            # The timestamp is often an integer, but str() handles both int and str types safely.
            data["release_date"] = str(doc.get("timestamp", ""))

        return data


# Dictionary mapping package type (from PURL) to its Fetcher Class
FETCHER_MAPPING = {
    "pypi": PypiFetcher,
    "python": PypiFetcher,
    "uv": PypiFetcher,
    "npm": NpmFetcher,
    "pnpm": NpmFetcher,
    "node": NpmFetcher,
    "rubygems": RubygemsFetcher,
    "ruby": RubygemsFetcher,
    "maven": MavenFetcher,
    "java": MavenFetcher,
    # Add other package managers here: "go": GoFetcher, "nuget": NugetFetcher
}

# -----------------------------------------------------
# SBOM ENRICHER CLASS (Main Orchestration)
# -----------------------------------------------------

class SBOMEnricher:
    def __init__(self, sbom_path=None):
        self.sbom_data = {}
        if sbom_path and os.path.exists(sbom_path):
            with open(sbom_path, "r", encoding="utf-8") as f:
                self.sbom_data = json.load(f)

    # -----------------------
    # BASIC SBOM UTILITIES
    # -----------------------
    def load_sbom(self, sbom_path):
        """Load SBOM JSON file"""
        with open(sbom_path, "r", encoding="utf-8") as f:
            self.sbom_data = json.load(f)

    def get_components(self):
        """Return list of components"""
        return self.sbom_data.get("components", [])

    # -----------------------
    # EOL EXTRACTION
    # -----------------------
    def get_eol_date(self, product_name, version=None):
        """
        Fetch End-of-Life (EOL) date for a given product using endoflife.date API.
        Works mainly for OS, platforms, and major frameworks (not individual packages).
        """
        try:
            api_url = f"https://endoflife.date/api/{product_name}.json"
            # NOTE: EOL is fetched synchronously here as it's not run often
            res = requests.get(api_url, timeout=10)

            if res.status_code != 200:
                return ""

            data = res.json()
            if not data:
                return ""

            # Try to match version, else return the latest EOL date
            if version:
                for entry in data:
                    if entry.get("cycle") == version:
                        return entry.get("eol", "")
            # fallback to latest
            return data[0].get("eol", "")
        except Exception:
            # print(f"[WARN] EOL fetch failed for {product_name}: {e}")
            return ""


    # -----------------------
    # INFERENCE FUNCTIONS
    # -----------------------

    def get_supplier_or_origin(self, package_type):
        """Map package type to a readable supplier/origin string."""
        if package_type == "pypi":
            return "PyPI"
        elif package_type in ["npm", "pnpm"]:
            return "npmjs"
        elif package_type == "rubygems":
            return "RubyGems"
        elif package_type == "maven":
            return "Maven Central"
        elif package_type == "nuget":
            return "NuGet Gallery"
        elif package_type == "go":
            return "Go Proxy"
        elif package_type == "cargo":
            return "Crates.io"
        elif package_type == "composer":
            return "Packagist"
        return "Unknown"
    
    def infer_pkg_info(self, component):
        """Use PURL to reliably infer package type, name, and version."""
        purl_str = component.get("purl", "")
        if not purl_str:
            return None, None, None

        try:
            purl = PackageURL.from_string(purl_str)
            name = purl.name
            version = purl.version
            pkg_type = purl.type.lower()
            
            # Special handling for Maven: combine group (namespace) and artifact (name)
            if pkg_type == "maven":
                group = purl.namespace
                if group and name:
                    name = f"{group}:{name}"
            
            return pkg_type, name, version
            
        except ValueError:
            # print(f"[WARN] Invalid PURL: {purl_str}")
            return None, None, None

    # -----------------------
    # TYPE CLASSIFICATION
    # -----------------------

    def is_executable(self, component):
        pkg_type = component.get("type", "").lower()
        return pkg_type in ["os", "platform", "binary", "file"]

    def is_archive(self, component):
        archive_exts = ['.zip', '.tar', '.gz', '.tar.gz', '.tgz', '.jar', '.war', '.rar']
        comp_name = component.get("name", "").lower()
        comp_purl = component.get("purl", "").lower()
        return any(comp_name.endswith(ext) or comp_purl.endswith(ext) for ext in archive_exts)

    def is_structured(self, component):
        comp_name = component.get("name", "").lower()
        return comp_name.endswith((".json", ".xml", ".yaml", ".yml"))

    # -----------------------
    # VULN PATCH STATUS
    # -----------------------

    def get_patch_status(self, vuln_id):
        """
        Fetch patch/fix version info for a given vulnerability ID using OSV.dev.
        This remains synchronous as it is a quick post request.
        """
       # 1. Clean and validate ID
        if not vuln_id or not isinstance(vuln_id, str):
            return "No valid ID provided"
        
        cleaned_id = vuln_id.strip()
        if not cleaned_id:
             return "No valid ID provided"

        osv_url = f"https://api.osv.dev/v1/vulns/"+cleaned_id
        # 2. Build the correct payload
        osv_payload = {"id": cleaned_id}

        #osv_url = "https://api.osv.dev/v1/query"
        #osv_payload = {"id": vuln_id.strip()}

        try:
            # Try OSV.dev
            resp = requests.get(osv_url, timeout=10)
            #print(resp.text)
            if resp.status_code == 200:
                data = resp.json()
                fixed_versions = []
                for affected in data.get("affected", []):
                    for r in affected.get("ranges", []):
                        for event in r.get("events", []):
                            if "fixed" in event:
                                fixed_versions.append(event["fixed"])
                
                if fixed_versions:
                    return f"Fixed in version {', '.join(sorted(list(set(fixed_versions))))}"
                else:
                    return "No fix version in OSV"
            else:
                return f"OSV lookup failed (Status: {resp.status_code})"
        except Exception:
            return "Error during OSV lookup"



    # --------------
    # dependency mapper
    # ---------------

    def _create_dependency_map(self):
        """
        Creates a map where the key is a component's bom-ref, and the value is a list 
        of bom-refs that directly depend on it.
        """
        dependency_map = {}
        dependencies_array = self.sbom_data.get("dependencies", [])

        # Iterate through all dependency entries (parent -> children)
        for dep_entry in dependencies_array:
            parent_ref = dep_entry.get("ref")
            children_refs = dep_entry.get("dependsOn", [])
            
            # For each child, register the parent as a dependent
            for child_ref in children_refs:
                if child_ref not in dependency_map:
                    dependency_map[child_ref] = []
                
                # Add the parent (the consumer) to the list of dependents for the child (the library)
                dependency_map[child_ref].append(parent_ref)
                
        # Store the map for quick lookup later
        self._dependency_map = dependency_map
        print(f"✅ Preprocessed dependency map containing {len(dependency_map)} components.")



    # -----------------------
    # MODULAR METADATA DISPATCHER
    # -----------------------
    
    async def get_package_metadata(self, session: aiohttp.ClientSession, package_name: str, package_type: str, version: str = None) -> dict:
        """Dispatch metadata fetching to the appropriate package manager fetcher."""
        
        pkg_type = package_type.lower()
        Fetcher = FETCHER_MAPPING.get(pkg_type)
        
        if Fetcher:
            try:
                # Instantiate the specific fetcher and run the async fetch
                fetcher_instance = Fetcher(session)
                return await fetcher_instance.fetch_metadata(package_name, version)
            except Exception as e:
                print(f"[ERROR] Fetcher failed for {package_type} ({package_name}): {e}")
                return {"description": "", "release_date": ""}
        else:
            # Fallback for unknown types (e.g., github, generic files)
            return {"description": "", "release_date": ""}


    # -----------------------
    # APPLY ENRICHMENTS (Main Orchestrator)
    # -----------------------

    async def enrich_component_task(self, session, component):
        """Async task to enrich a single component."""
        
        # 1. PURL Parsing and Type Inference
        pkg_type, name, version = self.infer_pkg_info(component)
        if not pkg_type or not name:
            pkg_type = "unknown"
            name = component.get("name", "")
            version = component.get("version", "")
            
        # 2. Fetch package metadata (concurrently)
        metadata = await self.get_package_metadata(session, name, pkg_type, version)
        
        # 3. Infer Supplier/Origin (FIXED)
        supplier_name = self.get_supplier_or_origin(pkg_type)
        metadata["supplier"] = supplier_name
        metadata["origin"] = supplier_name

        # 4. Fetch EOL for key components
        if pkg_type in ["go", "maven", "python", "npm"] or component.get("type", "").lower() in ["os", "platform"]:
             eol_date = self.get_eol_date(name, version)
             metadata["eol_date"] = eol_date
        else:
            metadata["eol_date"] = ""


        # 5. Vulnerability Enrichment (Synchronous lookup)
        bom_ref = component.get("bom-ref", "")
        vulns = []
        highest_severity_rank = 0 # 0=None, 1=Low, 2=Medium, 3=High, 4=Critical
        
        # Define severity ranking for easy comparison
        SEVERITY_RANKING = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
            "UNKNOWN": 0,
            "INFORMATIONAL": 0
        }
        
        for vuln in self.sbom_data.get("vulnerabilities", []):
            affects = vuln.get("affects", [])
            for aff in affects:
                if aff.get("ref") == bom_ref:
                    # Retrieve the severity string (e.g., 'HIGH', 'CRITICAL')
                    severity_str = vuln.get("ratings", [{}])[0].get("severity", "UNKNOWN").upper()
                    current_rank = SEVERITY_RANKING.get(severity_str, 0)
                    
                    # Track the highest rank encountered for this component
                    if current_rank > highest_severity_rank:
                        highest_severity_rank = current_rank
                        
                    vulns.append({
                        "id": vuln.get("id"),
                        "patch_status": self.get_patch_status(vuln.get("id")),
                        "source": vuln.get("source", {}).get("name"),
                        "severity": severity_str, # Use the capitalized severity
                        "description": vuln.get("description"),
                        "cwe": vuln.get("cwes", []),
                    })
        
        # --- NEW CRITICALITY CALCULATION BASED ON SEVERITY ---
        if highest_severity_rank == 4:
            criticality_value = "Critical"
        elif highest_severity_rank == 3:
            criticality_value = "High"
        elif highest_severity_rank == 2:
            criticality_value = "Medium"
        else: # Rank 1 (Low), 0 (None/Unknown)
            criticality_value = "Low"
        # -----------------------------------------------------


        # 
        #
        #

        # ... (Steps 1-5 remain the same: PURL parsing, metadata, supplier, EOL, Vuln check, Criticality) ...
        
        # --- NEW DEPENDENCY LOOKUP (Insert this block here) ---
        component_bom_ref = component.get("bom-ref", "")
        
        # Look up the list of dependents (other components that consume this one)
        dependents = self._dependency_map.get(component_bom_ref, [])
        dependents_value = json.dumps(dependents) # Store as JSON string in property value

        # 6. Append enrichment fields as properties
        props = component.get("properties", [])
        props.extend([
            {"name": "custom:description", "value": metadata.get("description", "")},
            {"name": "custom:supplier", "value": metadata.get("supplier", "")},
            {"name": "custom:origin", "value": metadata.get("origin", "")},
            {"name": "custom:release_date", "value": metadata.get("release_date", "")},
            {"name": "custom:eol_date", "value": metadata.get("eol_date", "")},
            {"name": "custom:executable", "value": str(self.is_executable(component)).lower()},
            {"name": "custom:archive", "value": str(self.is_archive(component)).lower()},
            {"name": "custom:structured", "value": str(self.is_structured(component)).lower()},
            {"name": "custom:has_vulnerabilities", "value": str(len(vulns) > 0).lower()},
            {"name": "custom:vulnerabilities", "value": json.dumps(vulns, indent=4)},
            # --- ADD NEW DEPENDENTS FIELD HERE ---
            {"name": "custom:direct_dependents", "value": dependents_value},
            {"name": "custom:criticality", "value": criticality_value}
            
        ])

        component["properties"] = props
        return component 


    def enrich_components(self):
        """Entry point: Runs the asynchronous enrichment task."""
        
        # Check for components before running async
        if not self.get_components():
             print("No components found in SBOM to enrich.")
             return self.sbom_data

        # --- NEW STEP: PREPROCESS DEPENDENCIES ---
        self._create_dependency_map() 
        # ----------------------------------------


        self.sbom_data["components"] = asyncio.run(self._run_async_enrichment(self.get_components()))
        return self.sbom_data

    async def _run_async_enrichment(self, components):
        """Helper to set up concurrent session and tasks."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.enrich_component_task(session, component) for component in components]
            # Gather results, maintaining the original order
            enriched_components = await asyncio.gather(*tasks)
            return enriched_components


    # -----------------------
    # SAVE
    # -----------------------

    def save_sbom(self, output_path):
        """Save enriched SBOM"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.sbom_data, f, indent=2)
        print(f"✅ Enriched SBOM saved to {output_path}")

