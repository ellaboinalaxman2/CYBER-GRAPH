"""Model registry for Member 3 - AI Engine."""

import json
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

from src.core.logging import get_logger
from src.model_registry.model_version import ModelVersion


class ModelRegistry:
    """
    Registry for managing model versions.
    
    Features:
    - Register models
    - List models
    - Get model by version
    - Set active model
    - Delete models
    """
    
    def __init__(self, registry_path: str = "./data/models/registry"):
        """
        Initialize the model registry.
        
        Args:
            registry_path: Path to registry directory
        """
        self.logger = get_logger("model_registry.registry")
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        
        self._registry_file = self.registry_path / "registry.json"
        self._models: Dict[str, ModelVersion] = {}
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Load registry from file."""
        if self._registry_file.exists():
            try:
                with open(self._registry_file, 'r') as f:
                    data = json.load(f)
                    
                    for version, model_data in data.items():
                        self._models[version] = ModelVersion(
                            version=version,
                            name=model_data.get("name", "unknown"),
                            path=model_data.get("path", ""),
                            created_at=datetime.fromisoformat(
                                model_data.get("created_at", datetime.utcnow().isoformat()).replace('Z', '+00:00')
                            ),
                            metrics=model_data.get("metrics", {}),
                            config=model_data.get("config", {}),
                            status=model_data.get("status", "active"),
                            description=model_data.get("description"),
                        )
                
                self.logger.info(f"Loaded {len(self._models)} models from registry")
            except Exception as e:
                self.logger.warning(f"Failed to load registry: {e}")
    
    def _save_registry(self) -> None:
        """Save registry to file."""
        try:
            data = {}
            for version, model in self._models.items():
                data[version] = model.to_dict()
            
            with open(self._registry_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"Saved {len(self._models)} models to registry")
        except Exception as e:
            self.logger.error(f"Failed to save registry: {e}")
    
    def register(
        self,
        model_path: str,
        name: str,
        version: Optional[str] = None,
        metrics: Optional[Dict[str, float]] = None,
        config: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
    ) -> ModelVersion:
        """
        Register a model.
        
        Args:
            model_path: Path to model file
            name: Model name
            version: Version string (auto-generated if None)
            metrics: Model metrics
            config: Model configuration
            description: Model description
            
        Returns:
            ModelVersion: Registered model version
        """
        if version is None:
            version = self._generate_version()
        
        # Check if version exists
        if version in self._models:
            self.logger.warning(f"Model version {version} already exists, overwriting")
        
        model_version = ModelVersion(
            version=version,
            name=name,
            path=model_path,
            created_at=datetime.utcnow(),
            metrics=metrics or {},
            config=config or {},
            status="active",
            description=description,
        )
        
        self._models[version] = model_version
        self._save_registry()
        
        self.logger.info(f"Registered model {name} version {version}")
        return model_version
    
    def _generate_version(self) -> str:
        """Generate a version string."""
        return f"v{len(self._models) + 1:02d}"
    
    def get_model(self, version: Optional[str] = None) -> Optional[ModelVersion]:
        """
        Get a model by version.
        
        Args:
            version: Version string (None for active)
            
        Returns:
            Optional[ModelVersion]: Model version
        """
        if version is None:
            # Get active model
            for model in self._models.values():
                if model.status == "active":
                    return model
            # Return latest if no active
            if self._models:
                return list(self._models.values())[-1]
            return None
        
        return self._models.get(version)
    
    def list_models(self) -> List[ModelVersion]:
        """
        List all models.
        
        Returns:
            List[ModelVersion]: List of models
        """
        return list(self._models.values())
    
    def set_active(self, version: str) -> bool:
        """
        Set a model as active.
        
        Args:
            version: Version string
            
        Returns:
            bool: True if successful
        """
        if version not in self._models:
            self.logger.error(f"Model version {version} not found")
            return False
        
        # Deactivate all
        for model in self._models.values():
            model.status = "archived"
        
        # Activate target
        self._models[version].status = "active"
        self._save_registry()
        
        self.logger.info(f"Set model version {version} as active")
        return True
    
    def delete_model(self, version: str) -> bool:
        """
        Delete a model.
        
        Args:
            version: Version string
            
        Returns:
            bool: True if successful
        """
        if version not in self._models:
            self.logger.error(f"Model version {version} not found")
            return False
        
        # Delete file if exists
        model = self._models[version]
        if Path(model.path).exists():
            try:
                Path(model.path).unlink()
                self.logger.info(f"Deleted model file: {model.path}")
            except Exception as e:
                self.logger.warning(f"Failed to delete model file: {e}")
        
        # Remove from registry
        del self._models[version]
        self._save_registry()
        
        self.logger.info(f"Deleted model version {version}")
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dict[str, Any]: Statistics
        """
        return {
            "total_models": len(self._models),
            "active_model": self.get_model().version if self.get_model() else None,
            "models": [v.to_dict() for v in self._models.values()],
        }