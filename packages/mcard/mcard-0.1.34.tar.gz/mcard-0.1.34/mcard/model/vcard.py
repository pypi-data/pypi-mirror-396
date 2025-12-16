"""VCard Model (Application Plane) - Implementation of Arena + Action.

This module defines the VCard, which represents the sovereign decision layer
in the MVP Cards architecture. VCard is the IO Monad that manages all side effects.

DOTS Vocabulary Role: Arena + Action
====================================

VCard is both:
- **Arena**: The interface type defining what can interact (subject_did, capabilities, external_refs)
- **Action**: The morphism where interactions (PCards) act on systems (MCards) to produce new systems

EOS Role: Sovereign Decision
============================

VCard is the controlled symmetry breaker. It:
- Manages credentials and authorization
- Controls side effects (IO Monad pattern)
- Acts as the ingress/egress gatekeeper for the PKC boundary

The Four Roles:
1. Identity & Credential Container (The "Who")
2. Verification Hub (The "Rules")
3. Side Effect Manager (The "Bridge")
4. Input/Output Gatekeeper (The "Gate")

See Also:
    - docs/WorkingNotes/Permanent/Projects/PKC Kernel/VCard.md
    - docs/VCard_Impl.md
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
import json
import hashlib

from mcard.model.card import MCard
from mcard.model.dots import (
    create_vcard_dots_metadata, 
    DOTSMetadata, 
    DOTSRole,
    CardPlane,
    EOSRole
)


class CapabilityScope(Enum):
    """Scope of a capability token."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"
    DELEGATE = "delegate"


class GatekeeperDirection(Enum):
    """Direction of gatekeeper authorization."""
    INGRESS = "ingress"  # Content entering the PKC
    EGRESS = "egress"    # Content leaving the PKC


@dataclass
class Capability:
    """A capability token defining authorized actions.
    
    Capabilities are the authorization units in VCard.
    They define what actions a subject can perform.
    """
    capability_id: str
    actor_did: str
    scope: CapabilityScope
    resource_pattern: str  # Regex or glob pattern for resources
    expires_at: Optional[datetime] = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    transferable: bool = False
    
    def is_valid(self) -> bool:
        """Check if the capability is still valid."""
        if self.expires_at is None:
            return True
        return datetime.now() < self.expires_at
    
    def matches_resource(self, resource_hash: str) -> bool:
        """Check if this capability applies to a resource."""
        import re
        return bool(re.match(self.resource_pattern, resource_hash))


@dataclass
class ExternalRef:
    """A verified external reference managed by VCard.
    
    External references are the IO Monad's way of tracking
    side effects without performing them.
    """
    uri: str  # file://, https://, s3://, ipfs://
    content_hash: str
    status: str  # "verified", "pending", "stale", "invalid"
    signature: Optional[str] = None
    last_verified: Optional[datetime] = None
    qos_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GatekeeperEvent:
    """An ingress or egress gatekeeper event.
    
    Records authorization decisions at the PKC boundary.
    """
    direction: GatekeeperDirection
    timestamp: datetime
    source_did: Optional[str]  # For ingress
    destination_did: Optional[str]  # For egress
    content_hash: str
    authorized: bool
    capability_used: Optional[str] = None
    signature: Optional[str] = None


class VCard(MCard):
    """VCard - The Application Plane unit (Arena + Action).
    
    VCard is the sovereign decision layer that:
    1. Holds identity and credentials (DID, keys, capabilities)
    2. Manages verification (test cases, PCard references)
    3. Describes side effects (external refs, IO operations)
    4. Gates all ingress/egress (nothing enters or leaves without authorization)
    
    DOTS Role: Arena + Action
    EOS Role: Sovereign Decision (controlled symmetry breaking)
    """
    
    def __init__(
        self,
        subject_did: str,
        controller_pubkeys: List[str],
        capabilities: Optional[List[Capability]] = None,
        external_refs: Optional[List[ExternalRef]] = None,
        hash_function: str = "sha256"
    ):
        """Initialize a VCard.
        
        Args:
            subject_did: The primary DID of the VCard owner.
            controller_pubkeys: Public keys that control this VCard.
            capabilities: Authorization capabilities.
            external_refs: Verified external references.
            hash_function: Hash algorithm to use.
        """
        self.subject_did = subject_did
        self.controller_pubkeys = controller_pubkeys
        self.capabilities = capabilities or []
        self.external_refs = external_refs or []
        self.export_manifest: List[str] = []  # Hashes registered for egress
        self.gatekeeper_log: List[GatekeeperEvent] = []
        
        # Serialize VCard state to content
        content = self._serialize_state()
        super().__init__(content, hash_function)
    
    def _serialize_state(self) -> str:
        """Serialize VCard state to JSON content."""
        return json.dumps({
            "type": "VCard",
            "subject_did": self.subject_did,
            "controller_pubkeys": self.controller_pubkeys,
            "capabilities": [
                {
                    "id": c.capability_id,
                    "actor": c.actor_did,
                    "scope": c.scope.value,
                    "resource_pattern": c.resource_pattern,
                    "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                    "transferable": c.transferable
                }
                for c in self.capabilities
            ],
            "external_refs": [
                {
                    "uri": r.uri,
                    "content_hash": r.content_hash,
                    "status": r.status
                }
                for r in self.external_refs
            ],
            "export_manifest": self.export_manifest
        }, sort_keys=True)
    
    def get_dots_metadata(self) -> DOTSMetadata:
        """Get DOTS metadata for this VCard.
        
        VCard is Arena (interface type) + Action (morphism).
        """
        return create_vcard_dots_metadata(
            credential_hash=self.hash
        )
    
    # =========================================================================
    # Role 1: Identity & Credential Container
    # =========================================================================
    
    def add_capability(self, capability: Capability) -> None:
        """Add a new capability to this VCard."""
        self.capabilities.append(capability)
    
    def get_valid_capabilities(self) -> List[Capability]:
        """Get all currently valid capabilities."""
        return [c for c in self.capabilities if c.is_valid()]
    
    def has_capability(self, scope: CapabilityScope, resource_hash: str) -> bool:
        """Check if VCard has a valid capability for a resource."""
        for cap in self.get_valid_capabilities():
            if cap.scope == scope and cap.matches_resource(resource_hash):
                return True
        return False
    
    # =========================================================================
    # Role 2: Verification Hub (CLM Balanced Dimension)
    # =========================================================================
    
    def add_pcard_reference(self, pcard_hash: str) -> None:
        """Register a PCard for verification."""
        # PCard references are stored as external refs with special URI
        ref = ExternalRef(
            uri=f"pcard://{pcard_hash}",
            content_hash=pcard_hash,
            status="verified"
        )
        self.external_refs.append(ref)
    
    def get_pcard_references(self) -> List[str]:
        """Get all registered PCard hashes."""
        return [
            ref.content_hash 
            for ref in self.external_refs 
            if ref.uri.startswith("pcard://")
        ]
    
    # =========================================================================
    # Role 3: Side Effect Manager (IO Monad)
    # =========================================================================
    
    def add_external_ref(self, ref: ExternalRef) -> None:
        """Add an external reference (describes a side effect)."""
        self.external_refs.append(ref)
    
    def get_external_refs_by_status(self, status: str) -> List[ExternalRef]:
        """Get external references by verification status."""
        return [r for r in self.external_refs if r.status == status]
    
    def verify_external_ref(self, uri: str, new_hash: str) -> bool:
        """Verify an external reference and update its status.
        
        This is the QoS (Quality of Service) check.
        """
        for ref in self.external_refs:
            if ref.uri == uri:
                if ref.content_hash == new_hash:
                    ref.status = "verified"
                    ref.last_verified = datetime.now()
                    return True
                else:
                    ref.status = "stale"
                    return False
        return False
    
    # =========================================================================
    # Role 4: Input/Output Gatekeeper
    # =========================================================================
    
    def authorize_ingress(
        self,
        source_did: str,
        content_hash: str,
        capability_id: Optional[str] = None
    ) -> bool:
        """Authorize content entering the PKC (ingress).
        
        Args:
            source_did: DID of the content source.
            content_hash: Hash of the content to be imported.
            capability_id: Optional specific capability to use.
            
        Returns:
            True if authorized, False otherwise.
        """
        authorized = False
        used_capability = None
        
        # Check if source has ingress capability
        for cap in self.get_valid_capabilities():
            if cap.actor_did == source_did and cap.scope in [CapabilityScope.WRITE, CapabilityScope.ADMIN]:
                if capability_id is None or cap.capability_id == capability_id:
                    authorized = True
                    used_capability = cap.capability_id
                    break
        
        # Log the gatekeeper event
        event = GatekeeperEvent(
            direction=GatekeeperDirection.INGRESS,
            timestamp=datetime.now(),
            source_did=source_did,
            destination_did=None,
            content_hash=content_hash,
            authorized=authorized,
            capability_used=used_capability
        )
        self.gatekeeper_log.append(event)
        
        return authorized
    
    def register_for_egress(self, content_hash: str) -> bool:
        """Register content for potential egress.
        
        Content must be registered before it can be authorized for export.
        
        Args:
            content_hash: Hash of the content to register.
            
        Returns:
            True if registration successful.
        """
        if content_hash not in self.export_manifest:
            self.export_manifest.append(content_hash)
            return True
        return False
    
    def authorize_egress(
        self,
        destination_did: str,
        content_hash: str,
        capability_id: Optional[str] = None
    ) -> bool:
        """Authorize content leaving the PKC (egress).
        
        Content must be in export_manifest and destination must have capability.
        
        Args:
            destination_did: DID of the content destination.
            content_hash: Hash of the content to be exported.
            capability_id: Optional specific capability to use.
            
        Returns:
            True if authorized, False otherwise.
        """
        # Content must be registered for egress
        if content_hash not in self.export_manifest:
            event = GatekeeperEvent(
                direction=GatekeeperDirection.EGRESS,
                timestamp=datetime.now(),
                source_did=None,
                destination_did=destination_did,
                content_hash=content_hash,
                authorized=False
            )
            self.gatekeeper_log.append(event)
            return False
        
        authorized = False
        used_capability = None
        
        # Check egress capability
        for cap in self.get_valid_capabilities():
            if cap.scope in [CapabilityScope.READ, CapabilityScope.ADMIN]:
                if cap.matches_resource(content_hash):
                    if capability_id is None or cap.capability_id == capability_id:
                        authorized = True
                        used_capability = cap.capability_id
                        break
        
        # Log the gatekeeper event
        event = GatekeeperEvent(
            direction=GatekeeperDirection.EGRESS,
            timestamp=datetime.now(),
            source_did=None,
            destination_did=destination_did,
            content_hash=content_hash,
            authorized=authorized,
            capability_used=used_capability
        )
        self.gatekeeper_log.append(event)
        
        return authorized
    
    def get_gatekeeper_log(
        self,
        direction: Optional[GatekeeperDirection] = None
    ) -> List[GatekeeperEvent]:
        """Get gatekeeper audit log, optionally filtered by direction."""
        if direction is None:
            return self.gatekeeper_log
        return [e for e in self.gatekeeper_log if e.direction == direction]
    
    # =========================================================================
    # EOS Compliance
    # =========================================================================
    
    def simulate_mode(self) -> 'VCardSimulation':
        """Enter simulation mode for EOS compliance.
        
        Returns a simulation context that isolates side effects.
        """
        return VCardSimulation(self)


class VCardSimulation:
    """Simulation context for VCard (EOS Compliance).
    
    Provides isolation of side effects for development/testing.
    All operations are logged but not executed.
    """
    
    def __init__(self, vcard: VCard):
        self.vcard = vcard
        self.simulation_log: List[Dict[str, Any]] = []
    
    def log_effect(self, effect_type: str, details: Dict[str, Any]) -> None:
        """Log a simulated side effect."""
        self.simulation_log.append({
            "timestamp": datetime.now().isoformat(),
            "effect_type": effect_type,
            "details": details,
            "simulated": True
        })
    
    def get_simulation_log(self) -> List[Dict[str, Any]]:
        """Get the simulation log."""
        return self.simulation_log
