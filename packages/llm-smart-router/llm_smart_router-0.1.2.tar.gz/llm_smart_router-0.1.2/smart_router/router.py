"""
Smart Router Agent - Classification intelligente et sélection d'outils

Ce module implémente le routeur intelligent qui analyse les requêtes utilisateur
et sélectionne dynamiquement le sous-ensemble optimal d'outils MCP.
"""
import logging
import re
from typing import List, Dict, Optional, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
try:\n    from langchain_core.prompts import ChatPromptTemplate\nexcept ImportError:\n    try:
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain

from .models import (
    AGDomain,
    IntentCategory,
    QueryContext,
    RoutingDecision,
    ToolMetadata
)
from .tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class RouterAgent:
    """
    Agent de routage intelligent pour la Stack AG Intelligence
    
    Responsabilités:
    1. Analyse de la requête utilisateur
    2. Classification d'intention (IntentCategory)
    3. Sélection des domaines AG pertinents
    4. Filtrage dynamique des outils MCP
    5. Résolution des dépendances inter-outils
    
    Objectif: Réduire les 32 outils à un sous-ensemble optimal de 3-8 outils.
    """
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        tool_registry: Optional[ToolRegistry] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialise le routeur
        
        Args:
            llm: Modèle LangChain (ChatOpenAI ou compatible)
            tool_registry: Registre des outils MCP
            config: Configuration applicative
        """
        self.config = config or {}
        self.tool_registry = tool_registry or ToolRegistry()
        
        # Initialiser le LLM avec un modèle léger et rapide
        self.llm = llm or ChatOpenAI(
            model=self.config.get("router_model", "gpt-4o-mini"),
            temperature=0.1,  # Bas pour des décisions déterministes
            max_tokens=800
        )
        
        # Parser pour structurer la sortie
        self.output_parser = PydanticOutputParser(pydantic_object=RoutingDecision)
        
        # Prompt système pour le routeur
        self.routing_prompt = self._create_routing_prompt()
        
        # Chaîne LangChain pour le routage
        self.routing_chain = LLMChain(
            llm=self.llm,
            prompt=self.routing_prompt,
            output_parser=self.output_parser
        )
        
        # Cache pour optimisation
        self._cache: Dict[str, RoutingDecision] = {}
        
        logger.info(f"🧭 RouterAgent initialisé avec {len(self.tool_registry.get_all_tools())} outils")
    
    def _create_routing_prompt(self) -> ChatPromptTemplate:
        """Crée le prompt système optimisé pour le routage"""
        
        # Charger le prompt système depuis un fichier si disponible
        try:
            with open("config/router_system_prompt.md", "r", encoding="utf-8") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            # Utiliser le prompt par défaut
            system_prompt = self._get_default_system_prompt()
        
        template = f"""{system_prompt}

# Domaines AG disponibles
{self._format_domains()}

# Instructions de format
{self.output_parser.get_format_instructions()}

# Requête utilisateur
{{query}}

# Contexte additionnel (optionnel)
{{context}}
"""
        
        return ChatPromptTemplate.from_template(template)
    
    def _get_default_system_prompt(self) -> str:
        """Prompt système par défaut si le fichier n'existe pas"""
        return """Tu es un routeur intelligent spécialisé dans l'analyse de requêtes d'observabilité et d'automatisation.

Ta mission est de classifier chaque requête utilisateur et de sélectionner UNIQUEMENT les domaines et outils pertinents.

## Principes de Routage

1. **Minimalisme**: Sélectionne le MINIMUM d'outils nécessaires (3-8 maximum)
2. **Précision**: Identifie l'intention exacte (troubleshooting, monitoring, analysis, etc.)
3. **Multi-domaines**: Active plusieurs domaines si la requête est complexe
4. **Dépendances**: Considère les outils dépendants automatiquement

## Règles de Classification

### Indicateurs de Domaines
- **MAAG** (Metrics): cpu, ram, latency, slow, performance, high load
- **LAAG** (Logs): error, exception, log, crash, stacktrace
- **CAAG** (Code): commit, code, changed, diff, function, git
- **SAAG** (Security): vulnerability, cve, security, access, unauthorized
- **DAAG** (Data Quality): quality, null, missing, pii, schema
- **WAAG** (Workflow): pipeline, job, workflow, dag, task
- **RAG/KAG** (Knowledge): documentation, how to, explain, guide
- **TAAG** (Testing): test, coverage, regression, failed test
- **UAAG** (User): user, session, login, activity
- **IAAG** (Infrastructure): infrastructure, deployment, container, pod

### Patterns de Questions Multi-Domaines
- "Pourquoi X est lent?" → [MAAG, LAAG, CAAG]
- "Problème de sécurité dans le code" → [SAAG, CAAG]
- "Pipeline échoue depuis changement" → [WAAG, CAAG, LAAG]
- "Données corrompues après déploiement" → [DAAG, CAAG, IAAG]

## Confiance
- High (>0.8): Intention claire, domaines évidents
- Medium (0.5-0.8): Requête ambiguë, plusieurs interprétations
- Low (<0.5): Requête vague, nécessite clarification
"""
    
    def _format_domains(self) -> str:
        """Formate la liste des domaines avec statistiques"""
        stats = self.tool_registry.get_domain_statistics()
        lines = []
        for domain, count in stats.items():
            lines.append(f"- **{domain}**: {count} outils")
        return "\n".join(lines)
    
    def route_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> RoutingDecision:
        """
        Route une requête utilisateur vers les outils appropriés
        
        Args:
            query: Requête utilisateur
            context: Contexte additionnel (historique, session, etc.)
            use_cache: Utiliser le cache de routage
        
        Returns:
            RoutingDecision avec domaines et outils sélectionnés
        """
        start_time = datetime.now()
        
        # Vérifier le cache
        cache_key = self._get_cache_key(query, context)
        if use_cache and cache_key in self._cache:
            logger.info(f"✅ Cache hit pour la requête")
            return self._cache[cache_key]
        
        # Enrichir le contexte de la requête
        query_context = self._enrich_query_context(query, context)
        
        try:
            # Exécuter le routage via LangChain
            result = self.routing_chain.run(
                query=query,
                context=self._format_context(query_context)
            )
            
            # Parser le résultat
            if isinstance(result, str):
                decision = self.output_parser.parse(result)
            else:
                decision = result
            
            # Résoudre les dépendances d'outils
            decision = self._resolve_tool_dependencies(decision)
            
            # Enregistrer dans le cache
            if use_cache:
                self._cache[cache_key] = decision
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"🧭 Routage complété en {elapsed:.2f}s: "
                f"{len(decision.domains)} domaines, {len(decision.selected_tools)} outils"
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ Erreur de routage: {e}", exc_info=True)
            # Fallback: retourner une décision par défaut
            return self._get_fallback_decision(query)
    
    def _enrich_query_context(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> QueryContext:
        """Enrichit le contexte de la requête avec extraction de métadonnées"""
        
        # Normaliser la requête
        normalized = query.lower().strip()
        
        # Extraire des mots-clés
        keywords = self._extract_keywords(normalized)
        
        # Détecter des plages temporelles
        time_range = self._extract_time_range(normalized)
        
        # Extraire des entités
        entities = self._extract_entities(normalized)
        
        return QueryContext(
            raw_query=query,
            normalized_query=normalized,
            keywords=keywords,
            time_range_mentioned=time_range,
            entities=entities
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés importants de la requête"""
        # Mots-clés techniques communs
        technical_terms = [
            "cpu", "memory", "ram", "latency", "error", "exception", "crash",
            "commit", "code", "git", "branch", "vulnerability", "cve", "security",
            "log", "trace", "performance", "slow", "pipeline", "workflow",
            "test", "coverage", "quality", "data", "schema", "user", "access"
        ]
        
        keywords = []
        for term in technical_terms:
            if term in text:
                keywords.append(term)
        
        return keywords
    
    def _extract_time_range(self, text: str) -> Optional[str]:
        """Détecte les références temporelles dans la requête"""
        patterns = [
            r"depuis (\d+ (?:heures?|jours?|semaines?))",
            r"depuis (hier|aujourd'hui|ce matin)",
            r"dernier(?:e)? (commit|déploiement|release)",
            r"last (\d+ (?:hours?|days?|weeks?))",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extrait les entités nommées (services, fichiers, etc.)"""
        entities = {
            "services": [],
            "files": [],
            "users": []
        }
        
        # Pattern pour détecter des noms de services (api, backend, frontend, etc.)
        service_pattern = r'\b(?:api|backend|frontend|service|worker|gateway)\b'
        entities["services"] = re.findall(service_pattern, text)
        
        # Pattern pour détecter des fichiers
        file_pattern = r'\b[\w-]+\.(?:py|js|java|ts|yaml|json)\b'
        entities["files"] = re.findall(file_pattern, text)
        
        return entities
    
    def _format_context(self, query_context: QueryContext) -> str:
        """Formate le contexte pour le prompt"""
        parts = []
        
        if query_context.keywords:
            parts.append(f"Mots-clés détectés: {', '.join(query_context.keywords)}")
        
        if query_context.time_range_mentioned:
            parts.append(f"Plage temporelle: {query_context.time_range_mentioned}")
        
        if query_context.entities["services"]:
            parts.append(f"Services mentionnés: {', '.join(query_context.entities['services'])}")
        
        return "\n".join(parts) if parts else "Aucun contexte additionnel"
    
    def _resolve_tool_dependencies(self, decision: RoutingDecision) -> RoutingDecision:
        """Résout les dépendances entre outils et complète la liste"""
        
        # Récupérer tous les outils des domaines sélectionnés
        tools = self.tool_registry.get_tools_by_domains(decision.domains)
        
        # Filtrer par pertinence avec les mots-clés de la requête
        selected_tools = []
        for tool in tools:
            # Ajouter l'outil si son nom ou keywords correspondent
            if self._is_tool_relevant(tool, decision):
                selected_tools.append(tool.name)
        
        # Résoudre les dépendances
        resolved_tools = self.tool_registry.resolve_dependencies(selected_tools)
        
        # Mettre à jour la décision
        decision.selected_tools = resolved_tools
        
        # Calculer la complexité estimée
        decision.estimated_complexity = self._estimate_complexity(resolved_tools)
        
        return decision
    
    def _is_tool_relevant(self, tool: ToolMetadata, decision: RoutingDecision) -> bool:
        """Détermine si un outil est pertinent pour la décision"""
        # Un outil est pertinent si son domaine est sélectionné
        return tool.domain in decision.domains
    
    def _estimate_complexity(self, tools: List[str]) -> str:
        """Estime la complexité basée sur le nombre d'outils"""
        count = len(tools)
        if count <= 3:
            return "low"
        elif count <= 6:
            return "medium"
        else:
            return "high"
    
    def _get_cache_key(self, query: str, context: Optional[Dict[str, Any]]) -> str:
        """Génère une clé de cache pour la requête"""
        import hashlib
        content = query
        if context:
            content += str(sorted(context.items()))
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_fallback_decision(self, query: str) -> RoutingDecision:
        """Retourne une décision par défaut en cas d'erreur"""
        logger.warning("⚠️  Utilisation de la décision fallback")
        return RoutingDecision(
            domains=[AGDomain.RAG, AGDomain.LAAG],
            intent=IntentCategory.INVESTIGATION,
            confidence=0.3,
            reasoning="Fallback: Erreur de routage, utilisation des domaines par défaut",
            selected_tools=["document_search", "log_search"],
            estimated_complexity="low"
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne des statistiques sur l'utilisation du routeur"""
        return {
            "total_tools": len(self.tool_registry.get_all_tools()),
            "cache_size": len(self._cache),
            "domain_distribution": self.tool_registry.get_domain_statistics()
        }
    
    def clear_cache(self):
        """Vide le cache de routage"""
        self._cache.clear()
        logger.info("🗑️  Cache de routage vidé")
