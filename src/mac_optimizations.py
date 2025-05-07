"""Module for Mac M-series GPU optimizations using Metal Performance Shaders (MPS)."""

from typing import Dict, Optional, List
import torch
import time
import psutil
from pydantic import BaseModel
from src.config import MacConfig
from src.benchmarks import benchmark

class GPULayerConfig(BaseModel):
    """Configuration for GPU layer optimization."""
    layer_name: str
    precision: str = "float32"  # float32 or float16
    memory_format: str = "contiguous"  # contiguous or channels_last
    compute_units: int = 0  # 0 means auto

class MPSOptimizer:
    """Handles GPU layer configuration and optimization for M-series chips."""
    
    def __init__(self, config: MacConfig) -> None:
        """
        Initialize the MPS optimizer.
        
        Args:
            config: Mac-specific configuration
        """
        if not torch.backends.mps.is_available():
            raise RuntimeError("MPS (Metal Performance Shaders) is not available")
        
        self.config = config
        self.device = torch.device("mps")
        self._layer_configs: Dict[str, GPULayerConfig] = {}
        self._layer_metrics: Dict[str, Dict[str, float]] = {}
        
    @benchmark("gpu_layer_config")
    def configure_layer(self, layer_name: str, config: GPULayerConfig) -> None:
        """
        Configure a specific layer for GPU optimization.
        
        Args:
            layer_name: Name of the layer to configure
            config: Layer-specific configuration
        """
        self._layer_configs[layer_name] = config
        self._layer_metrics[layer_name] = {
            "compute_time_ms": 0.0,
            "memory_usage_mb": 0.0,
            "throughput_items_per_sec": 0.0
        }
    
    @benchmark("gpu_model_optimization")
    def optimize_model_layers(self, model: torch.nn.Module) -> torch.nn.Module:
        """
        Apply GPU layer optimizations to a PyTorch model.
        
        Args:
            model: PyTorch model to optimize
            
        Returns:
            Optimized model
        """
        model = model.to(self.device)
        
        # Apply layer-specific optimizations
        for name, module in model.named_modules():
            if name in self._layer_configs:
                config = self._layer_configs[name]
                module = self._apply_layer_config(module, config)
                
                # Measure initial performance
                self._measure_layer_performance(name, module)
        
        return model
    
    def _apply_layer_config(
        self, 
        module: torch.nn.Module, 
        config: GPULayerConfig
    ) -> torch.nn.Module:
        """
        Apply configuration to a specific layer.
        
        Args:
            module: PyTorch module to optimize
            config: Layer configuration
            
        Returns:
            Optimized module
        """
        # Convert precision if needed
        if config.precision == "float16":
            # Convert all parameters to float16
            for param in module.parameters():
                param.data = param.data.to(dtype=torch.float16)
            # Convert buffers (like running_mean in BatchNorm) to float16
            for buf in module.buffers():
                buf.data = buf.data.to(dtype=torch.float16)
            # Set module to float16 mode
            module = module.half()
        else:
            # Ensure float32 for consistency
            for param in module.parameters():
                param.data = param.data.to(dtype=torch.float32)
            for buf in module.buffers():
                buf.data = buf.data.to(dtype=torch.float32)
            module = module.float()
        
        # Set memory format
        if config.memory_format == "channels_last":
            module = module.to(memory_format=torch.channels_last)
        else:
            module = module.to(memory_format=torch.contiguous_format)
        
        return module
    
    def _measure_layer_performance(self, layer_name: str, module: torch.nn.Module) -> None:
        """
        Measure performance metrics for a layer.
        
        Args:
            layer_name: Name of the layer to measure
            module: The PyTorch module to measure
        """
        # Create sample input based on module type
        if isinstance(module, torch.nn.Linear):
            sample_size = (1, module.in_features)
        elif isinstance(module, torch.nn.Conv2d):
            sample_size = (1, module.in_channels, 32, 32)  # Standard image size
        else:
            sample_size = (1, 3, 32, 32)  # Default size
        
        x = torch.randn(sample_size, device=self.device)
        
        # Match input dtype to module
        x = x.to(dtype=next(module.parameters()).dtype)
        
        # Warm-up run
        with torch.no_grad():
            module(x)
        torch.mps.synchronize()
        
        # Measure compute time
        start_time = time.perf_counter()
        with torch.no_grad():
            for _ in range(100):  # Multiple runs for better averaging
                module(x)
        torch.mps.synchronize()
        end_time = time.perf_counter()
        compute_time = (end_time - start_time) * 1000 / 100  # Convert to ms per iteration
        
        # Measure memory usage
        torch.mps.empty_cache()
        process = psutil.Process()
        start_mem = process.memory_info().rss / 1024 / 1024  # MB
        with torch.no_grad():
            output = module(x)
        torch.mps.synchronize()
        end_mem = process.memory_info().rss / 1024 / 1024  # MB
        
        # Calculate throughput
        batch_size = x.size(0)
        throughput = batch_size / (compute_time / 1000)  # items per second
        
        # Store metrics
        self._layer_metrics[layer_name] = {
            "compute_time_ms": compute_time,
            "memory_usage_mb": end_mem - start_mem,
            "throughput_items_per_sec": throughput
        }
    
    @benchmark("gpu_layer_performance")
    def get_layer_performance(self, layer_name: str) -> Dict[str, float]:
        """
        Get performance metrics for a specific layer.
        
        Args:
            layer_name: Name of the layer to measure
            
        Returns:
            Dictionary of performance metrics
        """
        if layer_name not in self._layer_configs:
            raise ValueError(f"Layer {layer_name} not configured")
        
        return self._layer_metrics[layer_name]
    
    def cleanup(self) -> None:
        """Clean up GPU resources."""
        torch.mps.empty_cache()
        self._layer_configs.clear()
        self._layer_metrics.clear()