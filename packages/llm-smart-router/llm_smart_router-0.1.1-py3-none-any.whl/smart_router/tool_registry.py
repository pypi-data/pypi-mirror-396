"""
Tool Registry - Mapper intelligent vers les outils MCP réels du projet ARCAQ

Ce module charge dynamiquement les outils depuis le code existant sans duplication.
"""
from typing import Dict, List, Optional, Any
import logging
from .models import AGDomain, ToolMetadata

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registre centralisé qui mappe dynamiquement les outils MCP réels
    
    Ce registre charge automatiquement les outils depuis:
    - src/core/tool_definitions.py (45 outils OpenMetadata)
    - src/tools/ag_tools.py (63 outils AG Intelligence)
    
    Total: 108 outils MCP réels chargés dynamiquement.
    Aucune duplication - les outils sont lus directement depuis le code source.
    """
    
    # Mapping intelligent nom d'outil → domaine AG
    TOOL_TO_DOMAIN_MAP = {
        # Outils AG - MAAG (Metrics)
        "get_metric_timeseries": AGDomain.MAAG,
        "analyze_metric_trend": AGDomain.MAAG,
        "get_kpi_dashboard": AGDomain.MAAG,
        "detect_metric_anomalies": AGDomain.MAAG,
        
        # Outils AG - DAAG (Data Quality)
        "get_data_quality_score": AGDomain.DAAG,
        "detect_pii_in_data": AGDomain.DAAG,
        "create_data_contract_via_api": AGDomain.DAAG,
        "list_data_contracts_via_api": AGDomain.DAAG,
        "add_quality_test_to_contract": AGDomain.DAAG,
        
        # Outils AG - WAAG (Workflow)
        "get_workflow_status": AGDomain.WAAG,
        "analyze_workflow_failures": AGDomain.WAAG,
        "get_bottleneck_analysis": AGDomain.WAAG,
        "search_jira_blockers": AGDomain.WAAG,
        "get_sprint_velocity": AGDomain.WAAG,
        "get_backlog_health": AGDomain.WAAG,
        "get_team_capacity": AGDomain.WAAG,
        "get_deployment_frequency": AGDomain.WAAG,
        
        # Outils AG - CAAG (Change & Code)
        "get_entity_changes": AGDomain.CAAG,
        "analyze_change_frequency": AGDomain.CAAG,
        "update_entity_description": AGDomain.CAAG,
        "batch_update_column_descriptions": AGDomain.CAAG,
        "patch_entity": AGDomain.CAAG,
        "create_domain": AGDomain.CAAG,
        "assign_asset_to_domain": AGDomain.CAAG,
        "create_data_product": AGDomain.CAAG,
        "delete_data_product": AGDomain.CAAG,
        "update_data_product": AGDomain.CAAG,
        "create_glossary": AGDomain.CAAG,
        "create_glossary_term": AGDomain.CAAG,
        "update_glossary_term": AGDomain.CAAG,
        "add_tag_to_field": AGDomain.CAAG,
        "assign_classification_tag": AGDomain.CAAG,
        "search_security_issues": AGDomain.CAAG,
        "search_complex_code": AGDomain.CAAG,
        "get_codebase_health_score": AGDomain.CAAG,
        "search_technical_debt": AGDomain.CAAG,
        
        # Outils AG - TAAG (Testing)
        "get_test_results": AGDomain.TAAG,
        "detect_flaky_tests": AGDomain.TAAG,
        "get_quality_gate_status": AGDomain.TAAG,
        "ai_suggest_quality_tests": AGDomain.TAAG,
        "get_table_quality_tests": AGDomain.TAAG,
        "suggest_quality_tests": AGDomain.TAAG,
        "create_quality_test": AGDomain.TAAG,
        "get_active_experiments": AGDomain.TAAG,
        "get_experiment_insights": AGDomain.TAAG,
        
        # Outils AG - SAAG (Security)
        "get_security_risk_score": AGDomain.SAAG,
        "detect_anomalous_access": AGDomain.SAAG,
        "get_pii_access_report": AGDomain.SAAG,
        "check_gdpr_compliance": AGDomain.SAAG,
        "assess_ai_act_risk": AGDomain.SAAG,
        "get_compliance_dashboard": AGDomain.SAAG,
        "search_violations_by_severity": AGDomain.SAAG,
        
        # Outils AG - UAAG (User & Access)
        "identify_domain_experts": AGDomain.UAAG,
        "get_collaboration_patterns": AGDomain.UAAG,
        "get_user_activity_timeline": AGDomain.UAAG,
        "add_owner": AGDomain.UAAG,
        "lookup_team_by_name": AGDomain.UAAG,
        
        # Outils AG - IAAG (Infrastructure & Integration)
        "get_integration_status": AGDomain.IAAG,
        "get_all_integrations_status": AGDomain.IAAG,
        "detect_connectivity_issues": AGDomain.IAAG,
        "get_integration_health_summary": AGDomain.IAAG,
        "trigger_reindex": AGDomain.IAAG,
        "get_reindex_status": AGDomain.IAAG,
        "reindex_entity": AGDomain.IAAG,
        "get_cost_optimization_opportunities": AGDomain.IAAG,
        
        # Outils AG - LAAG (Logs & Errors)
        "correlate_errors": AGDomain.LAAG,
        "analyze_error_patterns": AGDomain.LAAG,
        "calculate_mttd_mttr": AGDomain.LAAG,
        
        # Outils AG - KAG (Knowledge Graph)
        "search_pii_flows": AGDomain.KAG,
        "search_cross_border_flows": AGDomain.KAG,
        "get_lineage_for_entity": AGDomain.KAG,
        "generate_flow_compliance_report": AGDomain.KAG,
        "map_kpi_to_code": AGDomain.KAG,
        
        # Outils AG - RAG (Documentation)
        "search_business_terms": AGDomain.RAG,
        "find_stale_documentation": AGDomain.RAG,
        "find_code_doc_gaps": AGDomain.RAG,
        "get_documentation_health": AGDomain.RAG,
        
        # Outils OpenMetadata - RAG (Documentation/Search)
        "structure_discover": AGDomain.RAG,
        "excel_kb_propose_mapping": AGDomain.RAG,
        "excel_kb_set_mapping": AGDomain.RAG,
        "excel_kb_build_records": AGDomain.RAG,
        "excel_kb_plan_actions": AGDomain.RAG,
        "excel_kb_get_state": AGDomain.RAG,
        "search_metadata": AGDomain.RAG,
        "search_for_entities_by_attribute": AGDomain.RAG,
        "search_for_similar_terms": AGDomain.RAG,
        "search_documentation": AGDomain.RAG,
        "get_entity_details": AGDomain.RAG,
        "list_domains": AGDomain.RAG,
        "list_data_products": AGDomain.RAG,
        "list_domain_assets": AGDomain.RAG,
        
        # Outils OpenMetadata - KAG (Knowledge Graph/Lineage)
        "get_entity_lineage": AGDomain.KAG,
        "link_glossary_term_to_entity": AGDomain.KAG,
    }
    
    def __init__(self):
        """Initialise le registre en chargeant les outils réels"""
        self._tools: Dict[str, ToolMetadata] = {}
        self._domain_to_tools: Dict[AGDomain, List[str]] = {domain: [] for domain in AGDomain}
        self._load_real_tools()
    
    def _load_real_tools(self):
        """Charge dynamiquement les outils depuis le code existant"""
        try:
            # Charger les outils OpenMetadata
            self._load_openmetadata_tools()
            
            # Charger les outils AG
            self._load_ag_tools()
            
            logger.info(f"✅ Registre chargé: {len(self._tools)} outils MCP réels")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement outils: {e}", exc_info=True)
            self._load_fallback_tools()
    
    def _load_openmetadata_tools(self):
        """Charge les outils OpenMetadata depuis tool_definitions.py"""
        try:
            from src.core.tool_definitions import (
                get_excel_kb_tools,
                get_search_tools,
                get_lineage_tools,
                get_entity_tools,
                get_domain_tools,
                get_glossary_tools,
                get_team_tools,
                get_tagging_tools,
                get_data_quality_tools,
                get_admin_tools
            )
            
            all_om_tools = (
                get_excel_kb_tools() +
                get_search_tools() +
                get_lineage_tools() +
                get_entity_tools() +
                get_domain_tools() +
                get_glossary_tools() +
                get_team_tools() +
                get_tagging_tools() +
                get_data_quality_tools() +
                get_admin_tools()
            )
            
            for tool_def in all_om_tools:
                self._parse_and_register_tool(tool_def, source="openmetadata")
            
            logger.info(f"✅ {len(all_om_tools)} outils OpenMetadata chargés")
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur chargement OpenMetadata: {e}")
    
    def _load_ag_tools(self):
        """Charge les outils AG depuis ag_tools.py"""
        try:
            from src.tools.ag_tools import get_ag_tool_definitions
            
            ag_tools = get_ag_tool_definitions()
            
            for tool_def in ag_tools:
                self._parse_and_register_tool(tool_def, source="ag")
            
            logger.info(f"✅ {len(ag_tools)} outils AG chargés")
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur chargement AG tools: {e}")
    
    def _parse_and_register_tool(self, tool_def: Dict[str, Any], source: str):
        """Parse une définition d'outil et l'enregistre"""
        try:
            # Extraire le nom
            if "function" in tool_def:
                name = tool_def["function"]["name"]
                description = tool_def["function"].get("description", "")
            elif "name" in tool_def:
                name = tool_def["name"]
                description = tool_def.get("description", "")
            else:
                return
            
            # Déterminer le domaine
            domain = self._infer_domain(name, description, source)
            
            # Extraire les keywords depuis la description
            keywords = self._extract_keywords(name, description)
            
            # Calculer le cost_weight
            cost_weight = self._estimate_cost_weight(name, description)
            
            # Créer et enregistrer l'outil
            tool = ToolMetadata(
                name=name,
                domain=domain,
                description=description,
                keywords=keywords,
                cost_weight=cost_weight
            )
            
            self._register_tool(tool)
            
        except Exception as e:
            logger.debug(f"Impossible de parser l'outil: {e}")
    
    def _infer_domain(self, name: str, description: str, source: str) -> AGDomain:
        """Infère le domaine AG d'un outil"""
        # Utiliser le mapping prédéfini si disponible
        if name in self.TOOL_TO_DOMAIN_MAP:
            return self.TOOL_TO_DOMAIN_MAP[name]
        
        # Sinon, inférer depuis le nom/description
        name_lower = name.lower()
        desc_lower = description.lower()
        
        # MAAG - Metrics
        if any(kw in name_lower or kw in desc_lower for kw in ["metric", "kpi", "performance", "monitoring"]):
            return AGDomain.MAAG
        
        # LAAG - Logs
        if any(kw in name_lower or kw in desc_lower for kw in ["log", "error", "exception"]):
            return AGDomain.LAAG
        
        # CAAG - Change/Code
        if any(kw in name_lower or kw in desc_lower for kw in ["change", "update", "create", "code", "complexity"]):
            return AGDomain.CAAG
        
        # SAAG - Security
        if any(kw in name_lower or kw in desc_lower for kw in ["security", "vulnerability", "compliance", "gdpr"]):
            return AGDomain.SAAG
        
        # DAAG - Data Quality
        if any(kw in name_lower or kw in desc_lower for kw in ["quality", "contract", "pii"]):
            return AGDomain.DAAG
        
        # WAAG - Workflow
        if any(kw in name_lower or kw in desc_lower for kw in ["workflow", "pipeline", "sprint", "jira"]):
            return AGDomain.WAAG
        
        # KAG - Knowledge Graph
        if any(kw in name_lower or kw in desc_lower for kw in ["lineage", "flow", "link", "relationship"]):
            return AGDomain.KAG
        
        # TAAG - Testing
        if any(kw in name_lower or kw in desc_lower for kw in ["test", "quality gate", "flaky"]):
            return AGDomain.TAAG
        
        # UAAG - User
        if any(kw in name_lower or kw in desc_lower for kw in ["user", "owner", "team", "expert"]):
            return AGDomain.UAAG
        
        # IAAG - Infrastructure
        if any(kw in name_lower or kw in desc_lower for kw in ["integration", "reindex", "infrastructure", "cost"]):
            return AGDomain.IAAG
        
        # Default: RAG pour les outils de recherche/documentation
        return AGDomain.RAG
    
    def _extract_keywords(self, name: str, description: str) -> List[str]:
        """Extrait des keywords depuis le nom et la description"""
        keywords = []
        
        # Mots-clés du nom
        name_parts = name.replace("_", " ").split()
        keywords.extend(name_parts)
        
        # Mots-clés importants de la description
        important_words = [
            "metric", "quality", "test", "workflow", "pipeline", "security",
            "vulnerability", "lineage", "integration", "code", "change",
            "user", "team", "error", "log", "pii", "compliance"
        ]
        
        desc_lower = description.lower()
        for word in important_words:
            if word in desc_lower and word not in keywords:
                keywords.append(word)
        
        return keywords[:10]  # Limiter à 10 keywords
    
    def _estimate_cost_weight(self, name: str, description: str) -> float:
        """Estime le coût relatif d'un outil"""
        # Outils lourds (analyse complexe, AI, batch)
        if any(kw in name.lower() for kw in ["analyze", "detect", "batch", "ai", "suggest"]):
            return 3.0
        
        # Outils moyens (recherche, aggregation)
        if any(kw in name.lower() for kw in ["search", "get", "calculate"]):
            return 2.0
        
        # Outils légers (list, lookup, status)
        if any(kw in name.lower() for kw in ["list", "lookup", "status"]):
            return 1.0
        
        return 2.0  # Default
    
    def _register_tool(self, tool: ToolMetadata):
        """Enregistre un outil dans le registre"""
        self._tools[tool.name] = tool
        self._domain_to_tools[tool.domain].append(tool.name)
    
    def _load_fallback_tools(self):
        """Charge un ensemble minimal d'outils en cas d'échec"""
        fallback_tools = [
            ToolMetadata(
                name="search_metadata",
                domain=AGDomain.RAG,
                description="Search metadata",
                keywords=["search", "metadata"],
                cost_weight=2.0
            ),
            ToolMetadata(
                name="get_entity_details",
                domain=AGDomain.RAG,
                description="Get entity details",
                keywords=["entity", "details"],
                cost_weight=2.0
            ),
        ]
        
        for tool in fallback_tools:
            self._register_tool(tool)
        
        logger.warning(f"⚠️ Mode fallback: {len(fallback_tools)} outils chargés")

    
    def get_tools_by_domain(self, domain: AGDomain) -> List[ToolMetadata]:
        """Récupère tous les outils d'un domaine spécifique"""
        tool_names = self._domain_to_tools.get(domain, [])
        return [self._tools[name] for name in tool_names]
    
    def get_tools_by_domains(self, domains: List[AGDomain]) -> List[ToolMetadata]:
        """Récupère tous les outils pour plusieurs domaines"""
        tools = []
        for domain in domains:
            tools.extend(self.get_tools_by_domain(domain))
        return tools
    
    def get_tool(self, tool_name: str) -> Optional[ToolMetadata]:
        """Récupère un outil par son nom"""
        return self._tools.get(tool_name)
    
    def get_all_tools(self) -> List[ToolMetadata]:
        """Récupère tous les outils enregistrés"""
        return list(self._tools.values())
    
    def search_tools_by_keywords(self, keywords: List[str]) -> List[ToolMetadata]:
        """Recherche d'outils par mots-clés"""
        matching_tools = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for tool in self._tools.values():
            tool_keywords_lower = [kw.lower() for kw in tool.keywords]
            if any(kw in tool_keywords_lower for kw in keywords_lower):
                matching_tools.append(tool)
        
        return matching_tools
    
    def resolve_dependencies(self, tool_names: List[str]) -> List[str]:
        """Résout les dépendances et retourne une liste complète d'outils"""
        resolved = set(tool_names)
        to_check = list(tool_names)
        
        while to_check:
            current = to_check.pop()
            tool = self._tools.get(current)
            if tool and tool.dependencies:
                for dep in tool.dependencies:
                    if dep not in resolved:
                        resolved.add(dep)
                        to_check.append(dep)
        
        return list(resolved)
    
    def get_domain_statistics(self) -> Dict[str, int]:
        """Statistiques sur la distribution des outils par domaine"""
        return {
            domain.value: len(tools)
            for domain, tools in self._domain_to_tools.items()
        }
