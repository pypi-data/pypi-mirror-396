"""
Context Pack Generator for msh.

Generates AI-ready context packs for assets or projects.
"""
import os
import json
import glob
from typing import Dict, Any, List, Optional
from msh.ai.metadata_cache import MetadataCache
from msh.ai.manifest import ManifestGenerator
from msh.logger import logger


class ContextPackGenerator:
    """Generates AI-ready context packs."""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize context pack generator.
        
        Args:
            project_root: Project root directory. Defaults to current working directory.
        """
        if project_root is None:
            project_root = os.getcwd()
        
        self.project_root = project_root
        self.cache = MetadataCache(project_root=project_root)
        self.manifest_gen = ManifestGenerator(project_root=project_root)
    
    def generate_context_pack(
        self,
        asset_id: Optional[str] = None,
        include_tests: bool = False,
        include_history: bool = False,
        user_request: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-ready context pack.
        
        Args:
            asset_id: Optional asset ID to focus the context pack on
            include_tests: Include test metadata
            include_history: Include recent run/deploy history
            user_request: Natural language request the user made
            
        Returns:
            Context pack dictionary matching context_pack schema
        """
        # Ensure manifest exists
        manifest = self.cache.load_manifest()
        if not manifest:
            logger.info("Manifest not found, generating...")
            manifest = self.manifest_gen.generate_manifest()
        
        # Load lineage
        lineage = self.cache.load_lineage()
        if not lineage:
            logger.info("Lineage not found, generating...")
            lineage = self.manifest_gen.generate_lineage()
        
        # Load schemas
        schemas = self.cache.load_schemas()
        if not schemas:
            logger.info("Schemas not found, generating...")
            schemas = self.manifest_gen.generate_schemas()
        
        # Load tests if requested
        tests = None
        if include_tests:
            tests_data = self.cache.load_tests()
            if not tests_data:
                logger.info("Tests not found, generating...")
                tests_data = self.manifest_gen.generate_tests_index()
            tests = tests_data.get("tests", {})
        
        # Load glossary (will be implemented in Phase 3)
        glossary_terms = []
        glossary_file = os.path.join(self.project_root, ".msh", "glossary.json")
        if os.path.exists(glossary_file):
            try:
                with open(glossary_file, "r") as f:
                    glossary_data = json.load(f)
                    glossary_terms = glossary_data.get("terms", [])
            except Exception as e:
                logger.warning(f"Failed to load glossary: {e}")
        
        # Filter assets if asset_id specified
        assets = manifest.get("assets", [])
        
        # Load execution metrics if requested
        execution_metrics = {}
        if include_history:
            execution_metrics = self._load_execution_metrics(assets)
        if asset_id:
            # Find the specific asset
            target_asset = None
            for asset in assets:
                if asset.get("id") == asset_id:
                    target_asset = asset
                    break
            
            if target_asset:
                # Include upstream and downstream assets
                upstream_ids = set(target_asset.get("lineage", {}).get("upstream", []))
                downstream_ids = set()
                
                # Find downstream assets
                for edge in lineage.get("edges", []):
                    if edge.get("from") == asset_id:
                        downstream_ids.add(edge.get("to"))
                
                # Build focused asset list
                focused_assets = [target_asset]
                for asset in assets:
                    asset_id_check = asset.get("id")
                    if asset_id_check in upstream_ids or asset_id_check in downstream_ids:
                        focused_assets.append(asset)
                
                assets = focused_assets
            else:
                logger.warning(f"Asset '{asset_id}' not found in manifest")
                assets = []
        
        # Build context pack
        context_pack = {
            "project": manifest.get("project", {}),
            "assets": self._optimize_assets(assets, execution_metrics if include_history else None),
            "lineage": lineage.get("edges", []),
        }
        
        if include_tests and tests:
            context_pack["tests"] = self._optimize_tests(tests, assets)
        
        if include_history and execution_metrics:
            context_pack["execution_metrics"] = execution_metrics
        
        if glossary_terms:
            context_pack["glossary_terms"] = glossary_terms
        
        if user_request:
            context_pack["user_request"] = user_request
        
        # Add metrics and policies (will be populated from glossary in Phase 3)
        context_pack["metrics"] = []
        context_pack["policies"] = []
        
        return context_pack
    
    def _optimize_assets(
        self,
        assets: List[Dict[str, Any]],
        execution_metrics: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Optimize assets for LLM token limits.
        
        Truncates large schemas and SQL if needed.
        """
        optimized = []
        
        for asset in assets:
            optimized_asset = asset.copy()
            
            # Truncate SQL if too long
            transform_block = optimized_asset.get("blocks", {}).get("transform", {})
            sql = transform_block.get("sql", "")
            if len(sql) > 2000:
                optimized_asset["blocks"]["transform"]["sql"] = sql[:2000] + "\n... (truncated)"
            
            # Limit schema columns
            schema = optimized_asset.get("schema", {})
            columns = schema.get("columns", [])
            if len(columns) > 50:
                schema["columns"] = columns[:50]
                schema["_truncated"] = True
                schema["_total_columns"] = len(columns)
            
            # Attach execution metrics if available
            asset_id = optimized_asset.get("id")
            if execution_metrics and asset_id and asset_id in execution_metrics:
                optimized_asset["execution_metrics"] = execution_metrics[asset_id]
            
            optimized.append(optimized_asset)
        
        return optimized
    
    def _optimize_tests(
        self,
        tests: Dict[str, Any],
        assets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Optimize test data for context pack."""
        asset_ids = {asset.get("id") for asset in assets}
        optimized_tests = []
        
        for asset_id, test_data in tests.items():
            if asset_id in asset_ids:
                optimized_tests.append({
                    "asset_id": asset_id,
                    "tests": test_data.get("tests", [])[:10],  # Limit to 10 tests
                    "count": test_data.get("count", 0),
                })
        
        return optimized_tests
    
    def _load_execution_metrics(
        self,
        assets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Load execution metrics from catalog and run_meta files.
        
        Args:
            assets: List of asset metadata
            
        Returns:
            Dictionary mapping asset IDs to execution metrics
        """
        metrics = {}
        
        # Try to load from catalog first
        catalog_file = os.path.join(self.project_root, ".msh", "msh_catalog.json")
        catalog_data = {}
        
        if os.path.exists(catalog_file):
            try:
                with open(catalog_file, "r") as f:
                    catalog_data = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load catalog: {e}")
        
        # Load metrics for each asset
        for asset in assets:
            asset_id = asset.get("id")
            if not asset_id:
                continue
            
            asset_metrics = {
                "last_run": None,
                "average_duration_seconds": None,
                "success_rate": None,
                "rows_processed_avg": None,
                "run_count": 0
            }
            
            # Try to get from catalog
            catalog_assets = catalog_data.get("assets", [])
            for catalog_asset in catalog_assets:
                if catalog_asset.get("name") == asset_id:
                    ingest_stats = catalog_asset.get("ingest", {})
                    if ingest_stats.get("status") != "no_metrics_found":
                        # Extract metrics from ingest stats
                        if "rows_loaded" in ingest_stats:
                            asset_metrics["rows_processed_avg"] = ingest_stats.get("rows_loaded", 0)
                        if "duration_seconds" in ingest_stats:
                            asset_metrics["average_duration_seconds"] = ingest_stats.get("duration_seconds")
                        if "timestamp" in ingest_stats:
                            asset_metrics["last_run"] = ingest_stats.get("timestamp")
                    break
            
            # Try to load from run_meta files
            run_meta_dir = os.path.join(self.project_root, ".msh", "run_meta")
            if os.path.exists(run_meta_dir):
                # Find all run_meta files for this asset
                raw_table_pattern = f"raw_{asset_id}_*.json"
                meta_files = glob.glob(os.path.join(run_meta_dir, raw_table_pattern))
                
                if meta_files:
                    durations = []
                    successes = 0
                    total_runs = 0
                    rows_processed = []
                    
                    for meta_file in meta_files[-10:]:  # Last 10 runs
                        try:
                            with open(meta_file, "r") as f:
                                meta_data = json.load(f)
                                total_runs += 1
                                
                                if "duration_seconds" in meta_data:
                                    durations.append(meta_data["duration_seconds"])
                                if "rows_loaded" in meta_data:
                                    rows_processed.append(meta_data["rows_loaded"])
                                if meta_data.get("status") == "success":
                                    successes += 1
                                
                                # Update last_run if this is more recent
                                if "timestamp" in meta_data:
                                    if not asset_metrics["last_run"] or meta_data["timestamp"] > asset_metrics["last_run"]:
                                        asset_metrics["last_run"] = meta_data["timestamp"]
                        except Exception as e:
                            logger.debug(f"Failed to load run_meta file {meta_file}: {e}")
                            continue
                    
                    # Calculate aggregates
                    if durations:
                        asset_metrics["average_duration_seconds"] = sum(durations) / len(durations)
                    if total_runs > 0:
                        asset_metrics["success_rate"] = successes / total_runs
                    if rows_processed:
                        asset_metrics["rows_processed_avg"] = sum(rows_processed) / len(rows_processed)
                    asset_metrics["run_count"] = total_runs
            
            if asset_metrics["run_count"] > 0 or asset_metrics["last_run"]:
                metrics[asset_id] = asset_metrics
        
        return metrics

