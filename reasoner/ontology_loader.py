"""
Ontology Loader for Satellite Monitoring System
"""

import os
import sys
from pathlib import Path

# Add the project root directory to sys.path to resolve 'utils'
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from owlready2 import get_ontology, sync_reasoner_pellet, sync_reasoner
from utils.constants import ONTOLOGY_PATH, ONTOLOGY_NAMESPACE
from utils.logger import get_logger

logger = get_logger()

class OntologyLoader:
    """Load and manage the satellite ontology"""
    
    def __init__(self):
        self.onto = None
        self.is_loaded = False
        self.namespace = None
    
    def load(self) -> bool:
        try:
            ontology_file = Path(ONTOLOGY_PATH)
        

            # Use absolute path string directly instead of URI to avoid Windows path issues with owlready2
            file_uri = str(ontology_file.resolve())
            self.onto = get_ontology(file_uri).load()

            # Use the ontology base IRI when available; fallback to configured namespace
            self.namespace = getattr(self.onto, "base_iri", None) or ONTOLOGY_NAMESPACE

            self.is_loaded = True
            logger.info(f"Ontology loaded successfully from {ONTOLOGY_PATH}", "OntologyLoader")
            self._log_ontology_stats()
            return True

        except Exception as e:
            logger.error(f"Failed to load ontology: {str(e)}", "OntologyLoader")
            return False

    def get_class(self, class_name: str):
        if not self.is_loaded:
            return None
        matches = [c for c in self.onto.classes() if c.name == class_name]
        return matches[0] if matches else None

    def get_individual(self, individual_name: str):
        if not self.is_loaded:
            return None
        matches = [i for i in self.onto.individuals() if i.name == individual_name]
        return matches[0] if matches else None

    def get_property(self, property_name: str):
        if not self.is_loaded:
            return None
        matches = [p for p in self.onto.properties() if p.name == property_name]
        return matches[0] if matches else None

    def _log_ontology_stats(self):
        """Log basic ontology statistics"""
        try:
            classes = list(self.onto.classes())
            individuals = list(self.onto.individuals())
            properties = list(self.onto.properties())
            
            logger.info(f"Ontology contains {len(classes)} classes", "OntologyLoader")
            logger.info(f"Ontology contains {len(individuals)} individuals", "OntologyLoader")
            logger.info(f"Ontology contains {len(properties)} properties", "OntologyLoader")
        except Exception as e:
            logger.warning(f"Could not retrieve ontology stats: {str(e)}", "OntologyLoader")
    
    def get_class(self, class_name: str):
        """Get class by name"""
        if not self.is_loaded:
            return None
        
        try:
            # Try with namespace first
            return self.onto[f"{self.namespace}{class_name}"]
        except:
            try:
                # Try without namespace
                return self.onto[class_name]
            except:
                return None
    
    def get_individual(self, individual_name: str):
        """Get individual by name"""
        if not self.is_loaded:
            return None
        
        try:
            return self.onto[f"{self.namespace}{individual_name}"]
        except:
            try:
                return self.onto[individual_name]
            except:
                return None
    
    def get_property(self, property_name: str):
        """Get property by name"""
        if not self.is_loaded:
            return None
        
        try:
            return self.onto[f"{self.namespace}{property_name}"]
        except:
            try:
                return self.onto[property_name]
            except:
                return None
    
    def get_all_classes(self):
        """Get all classes in ontology"""
        if not self.is_loaded:
            return []
        
        try:
            return list(self.onto.classes())
        except Exception as e:
            logger.warning(f"Error retrieving classes: {str(e)}", "OntologyLoader")
            return []
    
    def get_all_individuals(self):
        """Get all individuals in ontology"""
        if not self.is_loaded:
            return []
        
        try:
            return list(self.onto.individuals())
        except Exception as e:
            logger.warning(f"Error retrieving individuals: {str(e)}", "OntologyLoader")
            return []
    
    def get_all_properties(self):
        """Get all properties in ontology"""
        if not self.is_loaded:
            return []
        
        try:
            return list(self.onto.properties())
        except Exception as e:
            logger.warning(f"Error retrieving properties: {str(e)}", "OntologyLoader")
            return []
    
    def get_ontology(self):
        """Get the ontology object"""
        return self.onto if self.is_loaded else None

# Global ontology loader instance
_ontology_loader = None

def get_ontology_loader() -> OntologyLoader:
    """Get global ontology loader instance"""
    global _ontology_loader
    if _ontology_loader is None:
        _ontology_loader = OntologyLoader()
    return _ontology_loader
