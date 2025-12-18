"""
Models pour le Smart Router - Classification des intentions et domaines AG
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AGDomain(str, Enum):
    """Les 11 domaines de la Stack AG Intelligence"""
    MAAG = "MAAG"  # Metrics & Monitoring
    LAAG = "LAAG"  # Logs & Analysis
    CAAG = "CAAG"  # Change & Code Analysis
    SAAG = "SAAG"  # Security & Vulnerability
    DAAG = "DAAG"  # Data Quality & Governance
    WAAG = "WAAG"  # Workflow & Orchestration
    RAG = "RAG"    # Retrieval Augmented Generation
    KAG = "KAG"    # Knowledge Augmented Generation
    TAAG = "TAAG"  # Testing & Quality Assurance
    UAAG = "UAAG"  # User & Access Management
    IAAG = "IAAG"  # Infrastructure & Assets


class IntentCategory(str, Enum):
    """Catégories d'intention détectées"""
    INVESTIGATION = "investigation"           # Enquête sur un problème
    MONITORING = "monitoring"                 # Surveillance temps réel
    ANALYSIS = "analysis"                     # Analyse rétrospective
    SECURITY_AUDIT = "security_audit"         # Audit de sécurité
    CODE_REVIEW = "code_review"               # Revue de code
    DATA_QUALITY = "data_quality"             # Qualité des données
    DOCUMENTATION = "documentation"           # Recherche documentaire
    TROUBLESHOOTING = "troubleshooting"       # Résolution de problème
    WORKFLOW_STATUS = "workflow_status"       # État des workflows
    COMPLIANCE = "compliance"                 # Conformité et gouvernance


class QueryContext(BaseModel):
    """Contexte enrichi de la requête utilisateur"""
    raw_query: str = Field(..., description="Requête utilisateur brute")
    normalized_query: str = Field(..., description="Requête normalisée")
    keywords: List[str] = Field(default_factory=list, description="Mots-clés extraits")
    time_range_mentioned: Optional[str] = Field(None, description="Plage temporelle mentionnée")
    entities: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Entités détectées (services, fichiers, users, etc.)"
    )


class RoutingDecision(BaseModel):
    """Décision de routage structurée"""
    domains: List[AGDomain] = Field(
        ...,
        description="Domaines AG activés pour cette requête",
        min_items=1
    )
    intent: IntentCategory = Field(..., description="Intention principale détectée")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiance de la décision")
    reasoning: str = Field(..., description="Raisonnement pour cette décision")
    selected_tools: List[str] = Field(
        default_factory=list,
        description="Liste des outils MCP sélectionnés"
    )
    estimated_complexity: str = Field(
        default="medium",
        description="Complexité estimée: low, medium, high"
    )
    
    class Config:
        use_enum_values = True


class ToolMetadata(BaseModel):
    """Métadonnées d'un outil MCP"""
    name: str = Field(..., description="Nom de l'outil")
    domain: AGDomain = Field(..., description="Domaine AG auquel il appartient")
    description: str = Field(..., description="Description de l'outil")
    keywords: List[str] = Field(default_factory=list, description="Mots-clés associés")
    cost_weight: float = Field(default=1.0, ge=0.1, le=10.0, description="Poids de coût (latence)")
    dependencies: List[str] = Field(
        default_factory=list,
        description="Outils dont cet outil dépend"
    )
    
    class Config:
        use_enum_values = True
