#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
"""
Hybrid Column Encoders

Encoders that combine multiple related columns into a single embedding.
Used with MERGE strategy from hybrid_column_detector.

Following the pattern of URLEncoder and DomainEncoder.
"""
import logging
from typing import List, Dict, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from featrix.neural.gpu_utils import get_device
from featrix.neural.featrix_token import Token, TokenStatus, TokenBatch
from featrix.neural.model_config import SimpleMLPConfig
from featrix.neural.simple_mlp import SimpleMLP
from featrix.neural.string_cache import StringCache

logger = logging.getLogger(__name__)


class AddressHybridEncoder(nn.Module):
    """
    Encodes address components into a single embedding.
    
    Follows URLEncoder pattern: multiple string components → projected → MLP → d_model
    
    Typical columns:
    - addr1, addr2: street address lines (string embeddings)
    - city: city name (string embedding)
    - state: state/province (could be string or categorical)
    - zip/postal_code: postal code (string embedding)
    - country: country (optional, string embedding)
    """
    
    def __init__(self, config: SimpleMLPConfig, string_cache: StringCache, 
                 column_names: List[str], column_name: Optional[str] = None):
        super().__init__()
        self.config = config
        self.string_cache = string_cache
        self.column_names = column_names
        self.column_name = column_name or f"hybrid_address_{'_'.join(column_names)}"
        self.d_model = config.d_out
        
        # String embeddings come from string_cache (384 dim)
        string_embed_dim = string_cache.embedding_dim if string_cache else 384
        
        # Project each address component
        # Street address gets more capacity (addr1 + addr2)
        self.addr1_proj = nn.Linear(string_embed_dim, 128, bias=False)
        self.addr2_proj = nn.Linear(string_embed_dim, 64, bias=False)
        self.city_proj = nn.Linear(string_embed_dim, 96, bias=False)
        self.state_proj = nn.Linear(string_embed_dim, 32, bias=False)
        self.zip_proj = nn.Linear(string_embed_dim, 32, bias=False)
        self.country_proj = nn.Linear(string_embed_dim, 32, bias=False)
        
        # Initialize projections
        nn.init.xavier_uniform_(self.addr1_proj.weight, gain=1.0)
        nn.init.xavier_uniform_(self.addr2_proj.weight, gain=0.5)
        nn.init.xavier_uniform_(self.city_proj.weight, gain=0.8)
        nn.init.xavier_uniform_(self.state_proj.weight, gain=0.5)
        nn.init.xavier_uniform_(self.zip_proj.weight, gain=0.5)
        nn.init.xavier_uniform_(self.country_proj.weight, gain=0.5)
        
        # Total input dimension: 128 + 64 + 96 + 32 + 32 + 32 = 384
        total_dim = 128 + 64 + 96 + 32 + 32 + 32
        
        # MLP to combine all components
        mlp_config = SimpleMLPConfig(
            d_in=total_dim,
            d_out=config.d_out,
            d_hidden=config.d_hidden if hasattr(config, 'd_hidden') else 256,
            n_hidden_layers=config.n_hidden_layers if hasattr(config, 'n_hidden_layers') else 2,
            dropout=config.dropout if hasattr(config, 'dropout') else 0.3,
            normalize=config.normalize if hasattr(config, 'normalize') else True,
            residual=config.residual if hasattr(config, 'residual') else True,
            use_batch_norm=config.use_batch_norm if hasattr(config, 'use_batch_norm') else True,
        )
        self.combiner_mlp = SimpleMLP(mlp_config)
        
        # Replacement embedding for missing/invalid addresses
        self._replacement_embedding = nn.Parameter(torch.randn(config.d_out))
        nn.init.normal_(self._replacement_embedding, mean=0.0, std=0.01)
        
        logger.info(f"🏠 AddressHybridEncoder initialized: columns={column_names}, d_model={config.d_out}")
    
    def _get_string_embedding(self, text: str) -> torch.Tensor:
        """Get string embedding from cache, or zeros if not available."""
        if not text or not self.string_cache:
            # Keep on CPU for DataLoader workers
            return torch.zeros(self.string_cache.embedding_dim if self.string_cache else 384)
        
        try:
            emb = self.string_cache.get_embedding(str(text))
            if emb is not None:
                # Keep on CPU for DataLoader workers
                return torch.tensor(emb, dtype=torch.float32) if not isinstance(emb, torch.Tensor) else emb
        except Exception as e:
            logger.debug(f"Failed to get string embedding for '{text}': {e}")
        
        # Keep on CPU for DataLoader workers
        return torch.zeros(self.string_cache.embedding_dim if self.string_cache else 384)
    
    def _extract_component(self, batch_data: Dict[str, TokenBatch], component_name: str, 
                          row_idx: int) -> str:
        """Extract a component value from batch_data for a specific row."""
        # Try exact match first
        if component_name in batch_data:
            token_batch = batch_data[component_name]
            if hasattr(token_batch, 'data'):
                val = token_batch.data[row_idx]
                return str(val) if val is not None else ""
        
        # Try fuzzy match (find column ending with component_name)
        component_lower = component_name.lower()
        for col_name in batch_data.keys():
            if col_name.lower().endswith(component_lower):
                token_batch = batch_data[col_name]
                if hasattr(token_batch, 'data'):
                    val = token_batch.data[row_idx]
                    return str(val) if val is not None else ""
        
        return ""
    
    def forward(self, batch_data: Dict[str, TokenBatch]) -> tuple:
        """
        Encode address components from batch_data.
        
        Args:
            batch_data: Dictionary of column_name -> TokenBatch
                       Contains all columns, we extract our address components
        
        Returns:
            (short_encoding, full_encoding) tuple
        """
        # Determine batch size from first column
        first_col = next(iter(batch_data.values()))
        batch_size = len(first_col.data) if hasattr(first_col, 'data') else 1
        
        embeddings = []
        
        for i in range(batch_size):
            # Extract address components
            addr1 = self._extract_component(batch_data, "addr1", i) or \
                   self._extract_component(batch_data, "address", i) or \
                   self._extract_component(batch_data, "street", i)
            addr2 = self._extract_component(batch_data, "addr2", i)
            city = self._extract_component(batch_data, "city", i)
            state = self._extract_component(batch_data, "state", i)
            zip_code = self._extract_component(batch_data, "zip", i) or \
                      self._extract_component(batch_data, "postal_code", i)
            country = self._extract_component(batch_data, "country", i)
            
            # Check if address is mostly empty
            if not any([addr1, city, state, zip_code]):
                embeddings.append(self._replacement_embedding.unsqueeze(0))
                continue
            
            # Get string embeddings for each component
            addr1_emb = self.addr1_proj(self._get_string_embedding(addr1))
            addr2_emb = self.addr2_proj(self._get_string_embedding(addr2))
            city_emb = self.city_proj(self._get_string_embedding(city))
            state_emb = self.state_proj(self._get_string_embedding(state))
            zip_emb = self.zip_proj(self._get_string_embedding(zip_code))
            country_emb = self.country_proj(self._get_string_embedding(country))
            
            # Concatenate all components
            combined = torch.cat([
                addr1_emb,
                addr2_emb,
                city_emb,
                state_emb,
                zip_emb,
                country_emb
            ], dim=-1)
            
            # Pass through MLP
            final_emb = self.combiner_mlp(combined.unsqueeze(0))
            embeddings.append(final_emb)
        
        # Stack all embeddings
        result = torch.cat(embeddings, dim=0)
        
        # Check for NaN
        if torch.isnan(result).any():
            logger.error(f"💥 AddressHybridEncoder output contains NaN!")
            result = self._replacement_embedding.unsqueeze(0).expand(batch_size, -1)
        
        # Return short and full encodings
        if self.config.normalize:
            short_vec = F.normalize(result[:, 0:3], dim=1, eps=1e-8)
            full_vec = F.normalize(result, dim=1, eps=1e-8)
        else:
            short_vec = result[:, 0:3]
            full_vec = result
        
        return short_vec, full_vec


class CoordinateHybridEncoder(nn.Module):
    """
    Encodes lat/long coordinate pairs into a single embedding.
    
    Simpler than AddressEncoder - just combines two scalars with optional geo-encoding.
    """
    
    def __init__(self, config: SimpleMLPConfig, lat_col: str, long_col: str, 
                 column_name: Optional[str] = None):
        super().__init__()
        self.config = config
        self.lat_col = lat_col
        self.long_col = long_col
        self.column_name = column_name or f"hybrid_coords_{lat_col}_{long_col}"
        self.d_model = config.d_out
        
        # Simple approach: 2D input (lat, long) → MLP → d_model
        # Can add geo-encoding features:
        # - Distance from equator
        # - Distance from prime meridian
        # - Hemisphere indicators
        # - Normalized coordinates
        
        # Input: lat, long, lat_norm, long_norm, dist_equator, dist_meridian = 6 features
        input_dim = 6
        
        mlp_config = SimpleMLPConfig(
            d_in=input_dim,
            d_out=config.d_out,
            d_hidden=config.d_hidden if hasattr(config, 'd_hidden') else 128,
            n_hidden_layers=config.n_hidden_layers if hasattr(config, 'n_hidden_layers') else 2,
            dropout=config.dropout if hasattr(config, 'dropout') else 0.3,
            normalize=config.normalize if hasattr(config, 'normalize') else True,
            residual=config.residual if hasattr(config, 'residual') else True,
            use_batch_norm=config.use_batch_norm if hasattr(config, 'use_batch_norm') else True,
        )
        self.encoder_mlp = SimpleMLP(mlp_config)
        
        # Replacement embedding for invalid coordinates
        self._replacement_embedding = nn.Parameter(torch.randn(config.d_out))
        nn.init.normal_(self._replacement_embedding, mean=0.0, std=0.01)
        
        logger.info(f"🌍 CoordinateHybridEncoder initialized: lat={lat_col}, long={long_col}, d_model={config.d_out}")
    
    def _geo_encode(self, lat: float, lon: float) -> torch.Tensor:
        """
        Encode geographic coordinates with additional features.
        
        Returns tensor of shape [6]: lat, lon, lat_norm, lon_norm, dist_equator, dist_prime_meridian
        """
        # Normalize to [-1, 1]
        lat_norm = lat / 90.0 if abs(lat) <= 90 else 0.0
        lon_norm = lon / 180.0 if abs(lon) <= 180 else 0.0
        
        # Distance from equator (0 to 1)
        dist_equator = abs(lat) / 90.0 if abs(lat) <= 90 else 1.0
        
        # Distance from prime meridian (0 to 1)
        dist_meridian = abs(lon) / 180.0 if abs(lon) <= 180 else 1.0
        
        return torch.tensor([
            lat, lon, lat_norm, lon_norm, dist_equator, dist_meridian
        ], dtype=torch.float32)
    
    def forward(self, batch_data: Dict[str, TokenBatch]) -> tuple:
        """
        Encode coordinate pairs from batch_data.
        
        Args:
            batch_data: Dictionary containing lat and long columns
        
        Returns:
            (short_encoding, full_encoding) tuple
        """
        # Extract lat/long batches
        lat_batch = batch_data.get(self.lat_col)
        long_batch = batch_data.get(self.long_col)
        
        if lat_batch is None or long_batch is None:
            logger.error(f"💥 CoordinateHybridEncoder missing columns: lat={self.lat_col}, long={self.long_col}")
            # Return replacement embedding
            batch_size = 1
            result = self._replacement_embedding.unsqueeze(0).expand(batch_size, -1)
            return result[:, 0:3], result
        
        batch_size = len(lat_batch.data)
        embeddings = []
        
        for i in range(batch_size):
            # Check token status
            if (lat_batch.status[i] != TokenStatus.OK or 
                long_batch.status[i] != TokenStatus.OK):
                embeddings.append(self._replacement_embedding.unsqueeze(0))
                continue
            
            # Extract lat/long values
            try:
                lat = float(lat_batch.data[i])
                lon = float(long_batch.data[i])
                
                # Validate ranges
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    logger.debug(f"Invalid coordinates: lat={lat}, lon={lon}")
                    embeddings.append(self._replacement_embedding.unsqueeze(0))
                    continue
                
                # Geo-encode
                features = self._geo_encode(lat, lon)
                
                # Encode through MLP
                emb = self.encoder_mlp(features.unsqueeze(0))
                embeddings.append(emb)
                
            except (ValueError, TypeError) as e:
                logger.debug(f"Failed to parse coordinates: {e}")
                embeddings.append(self._replacement_embedding.unsqueeze(0))
        
        # Stack all embeddings
        result = torch.cat(embeddings, dim=0)
        
        # Check for NaN
        if torch.isnan(result).any():
            logger.error(f"💥 CoordinateHybridEncoder output contains NaN!")
            result = self._replacement_embedding.unsqueeze(0).expand(batch_size, -1)
        
        # Return short and full encodings
        if self.config.normalize:
            short_vec = F.normalize(result[:, 0:3], dim=1, eps=1e-8)
            full_vec = F.normalize(result, dim=1, eps=1e-8)
        else:
            short_vec = result[:, 0:3]
            full_vec = result
        
        return short_vec, full_vec

