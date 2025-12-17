"""PCard Model (Control Plane) - Implementation of LENS/CHART values.

This module defines the PCard, which represents the execution unit in the DOTS framework.
PCards are MCards that contain a valid CLM (Cubical Logic Model) specification.
"""

from typing import Optional, Dict, List, Any, Union
import yaml
from mcard.model.card import MCard
from mcard.model.dots import create_pcard_dots_metadata, DOTSMetadata

class PCard(MCard):
    """PCard - The Control Plane unit (Lens + Chart).
    
    A PCard is an MCard whose content is a valid CLM specification.
    It represents a transformation (Lens) with a specific interaction pattern (Chart).
    
    DOTS Role:
        - LENS: When viewed as a tight morphism (Abstract <-> Concrete).
        - CHART: When viewed as a loose morphism (Interaction Pattern).
    """
    
    def __init__(self, content: Union[str, bytes], hash_function: Union[str, Any] = "sha256"):
        """Initialize a PCard.
        
        Args:
            content: The CLM YAML string.
            hash_function: Hash function to use.
            
        Raises:
            ValueError: If content is not valid YAML or valid CLM structure.
        """
        super().__init__(content, hash_function)
        self._parsed_clm = self._validate_and_parse()
        
    def _validate_and_parse(self) -> Dict[str, Any]:
        """Validate content is valid YAML CLM and return parsed dict."""
        try:
            content_str = self.get_content(as_text=True)
            clm = yaml.safe_load(content_str)
            
            if not isinstance(clm, dict):
                raise ValueError("PCard content must be a YAML dictionary")
                
            return clm
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML content for PCard: {e}")
            
    def get_dots_metadata(self) -> DOTSMetadata:
        """Get DOTS metadata for this PCard.
        
        Automatically extracts dependencies from the CLM structure if available.
        """
        tight_refs = []
        loose_refs = []
        
        # Extract dependencies if they exist in standard CLM fields
        # (This is a simplified extraction logic)
        for key in ['tight_deps', 'dependencies']:
            if key in self._parsed_clm and isinstance(self._parsed_clm[key], list):
                tight_refs.extend(self._parsed_clm[key])
                
        for key in ['loose_deps', 'alternatives']:
            if key in self._parsed_clm and isinstance(self._parsed_clm[key], list):
                loose_refs.extend(self._parsed_clm[key])
        
        return create_pcard_dots_metadata(
            spec_hash=self.hash,
            tight_refs=tight_refs if tight_refs else None,
            loose_refs=loose_refs if loose_refs else None
        )
    
    @property
    def clm(self) -> Dict[str, Any]:
        """Get the parsed CLM dictionary."""
        return self._parsed_clm
    
    @property
    def abstract_spec(self) -> Optional[Dict[str, Any]]:
        """Get the abstract specification section."""
        return self._parsed_clm.get('abstract_spec')
        
    @property
    def concrete_impl(self) -> Optional[Dict[str, Any]]:
        """Get the concrete implementation section."""
        return self._parsed_clm.get('concrete_impl') or self._parsed_clm.get('impl')

    @property
    def balanced_expectations(self) -> Optional[Dict[str, Any]]:
        """Get the balanced expectations (tests) section."""
        return self._parsed_clm.get('balanced_expectations') or self._parsed_clm.get('expectations')
