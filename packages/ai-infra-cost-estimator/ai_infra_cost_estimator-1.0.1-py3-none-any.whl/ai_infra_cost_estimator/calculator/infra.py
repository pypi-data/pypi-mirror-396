"""
Infrastructure Cost Calculator Module

Calculates compute infrastructure costs based on request volume,
concurrency requirements, and scaling parameters.
"""

import json
import math
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class PodRequirement:
    """Requirements for a single pod/instance."""
    instance_type: str
    vcpu: int
    memory_gb: int
    cost_per_hour: float
    max_concurrent_requests: int
    description: str


@dataclass
class InfraCostResult:
    """Results from infrastructure cost calculation."""
    requests_per_second: float
    required_concurrency: float
    required_pods: int
    instance_type: str
    cost_per_pod_hour: float
    cost_per_pod_month: float
    total_monthly_cost: float
    total_yearly_cost: float
    region: str
    region_multiplier: float
    utilization_percent: float
    headroom_pods: int
    total_pods_with_headroom: int
    breakdown: Dict = field(default_factory=dict)


class InfraCostCalculator:
    """
    Calculator for compute infrastructure costs.
    
    Estimates pod/instance requirements based on request volume,
    latency, and concurrency constraints.
    """
    
    HOURS_PER_DAY = 24
    DAYS_PER_MONTH = 30
    HOURS_PER_MONTH = HOURS_PER_DAY * DAYS_PER_MONTH  # 720 hours
    
    def __init__(self, pricing_file: Optional[str] = None):
        """
        Initialize the infrastructure cost calculator.
        
        Args:
            pricing_file: Path to the pricing JSON file.
                         Defaults to bundled pricing/models.json
        """
        if pricing_file is None:
            # Use package resources to find bundled pricing file
            try:
                import ai_infra_cost_estimator.pricing as pricing_pkg
                pricing_file = os.path.join(
                    os.path.dirname(pricing_pkg.__file__), 
                    'models.json'
                )
            except (ImportError, AttributeError):
                # Fallback for development
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                pricing_file = os.path.join(base_dir, 'pricing', 'models.json')
        
        self.pricing_data = self._load_pricing(pricing_file)
        self.compute_types = self.pricing_data.get('infra', {}).get('compute', {})
        self.regions = self.pricing_data.get('infra', {}).get('regions', {})
        self.defaults = self.pricing_data.get('infra', {}).get('defaults', {})
    
    def _load_pricing(self, pricing_file: str) -> Dict:
        """Load pricing data from JSON file."""
        try:
            with open(pricing_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Pricing file not found: {pricing_file}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in pricing file: {pricing_file}")
    
    def get_available_instance_types(self) -> Dict[str, Dict]:
        """Return all available instance types with their specs."""
        return self.compute_types
    
    def get_available_regions(self) -> Dict[str, Dict]:
        """Return all available regions with pricing multipliers."""
        return self.regions
    
    def calculate_required_pods(
        self,
        requests_per_day: int,
        avg_latency_ms: float,
        concurrency_limit: int
    ) -> Tuple[float, float, int]:
        """
        Calculate the number of pods required.
        
        Args:
            requests_per_day: Total requests per day
            avg_latency_ms: Average request latency in milliseconds
            concurrency_limit: Maximum concurrent requests per pod
            
        Returns:
            Tuple of (rps, required_concurrency, required_pods)
        """
        # Calculate requests per second
        rps = requests_per_day / 86400  # seconds in a day
        
        # Calculate required concurrency
        # Each request occupies a slot for avg_latency_ms
        avg_latency_seconds = avg_latency_ms / 1000
        required_concurrency = rps * avg_latency_seconds
        
        # Apply overhead multiplier for safety margin
        overhead = self.defaults.get('overhead_multiplier', 1.2)
        required_concurrency_with_overhead = required_concurrency * overhead
        
        # Calculate required pods
        required_pods = math.ceil(required_concurrency_with_overhead / concurrency_limit)
        
        # Ensure minimum of 1 pod
        required_pods = max(required_pods, self.defaults.get('min_replicas', 1))
        
        return rps, required_concurrency, required_pods
    
    def select_instance_type(
        self,
        required_concurrency: float,
        preferred_type: Optional[str] = None
    ) -> PodRequirement:
        """
        Select the most appropriate instance type.
        
        Args:
            required_concurrency: Required concurrent requests
            preferred_type: Preferred instance type name
            
        Returns:
            PodRequirement with instance specifications
        """
        if preferred_type and preferred_type in self.compute_types:
            instance = self.compute_types[preferred_type]
            return PodRequirement(
                instance_type=preferred_type,
                vcpu=instance['vcpu'],
                memory_gb=instance['memory_gb'],
                cost_per_hour=instance['cost_per_hour_usd'],
                max_concurrent_requests=instance['max_concurrent_requests'],
                description=instance.get('description', '')
            )
        
        # Auto-select based on concurrency needs
        sorted_instances = sorted(
            self.compute_types.items(),
            key=lambda x: x[1]['max_concurrent_requests']
        )
        
        for name, instance in sorted_instances:
            if instance['max_concurrent_requests'] >= required_concurrency:
                return PodRequirement(
                    instance_type=name,
                    vcpu=instance['vcpu'],
                    memory_gb=instance['memory_gb'],
                    cost_per_hour=instance['cost_per_hour_usd'],
                    max_concurrent_requests=instance['max_concurrent_requests'],
                    description=instance.get('description', '')
                )
        
        # Return largest instance if none sufficient
        name, instance = sorted_instances[-1]
        return PodRequirement(
            instance_type=name,
            vcpu=instance['vcpu'],
            memory_gb=instance['memory_gb'],
            cost_per_hour=instance['cost_per_hour_usd'],
            max_concurrent_requests=instance['max_concurrent_requests'],
            description=instance.get('description', '')
        )
    
    def get_region_multiplier(self, region: str) -> float:
        """Get the pricing multiplier for a region."""
        if region in self.regions:
            return self.regions[region].get('multiplier', 1.0)
        return 1.0
    
    def calculate(
        self,
        requests_per_day: int,
        avg_latency_ms: float = None,
        concurrency_limit: int = None,
        region: str = "us-east-1",
        instance_type: Optional[str] = None,
        headroom_percent: float = 20.0
    ) -> InfraCostResult:
        """
        Calculate infrastructure costs.
        
        Args:
            requests_per_day: Number of requests per day
            avg_latency_ms: Average latency in milliseconds
            concurrency_limit: Max concurrent requests per pod
            region: Cloud region for pricing
            instance_type: Specific instance type (auto-selects if None)
            headroom_percent: Additional capacity percentage for headroom
            
        Returns:
            InfraCostResult with detailed cost breakdown
        """
        # Use defaults if not provided
        if avg_latency_ms is None:
            avg_latency_ms = self.defaults.get('avg_latency_ms', 500)
        
        # Calculate base requirements
        rps, required_concurrency, _ = self.calculate_required_pods(
            requests_per_day=requests_per_day,
            avg_latency_ms=avg_latency_ms,
            concurrency_limit=concurrency_limit or 50
        )
        
        # Select instance type
        pod_req = self.select_instance_type(
            required_concurrency=required_concurrency,
            preferred_type=instance_type
        )
        
        # Use instance's concurrency limit if not specified
        if concurrency_limit is None:
            concurrency_limit = pod_req.max_concurrent_requests
        
        # Recalculate with actual concurrency limit
        _, _, required_pods = self.calculate_required_pods(
            requests_per_day=requests_per_day,
            avg_latency_ms=avg_latency_ms,
            concurrency_limit=concurrency_limit
        )
        
        # Calculate headroom
        headroom_pods = math.ceil(required_pods * (headroom_percent / 100))
        total_pods = required_pods + headroom_pods
        
        # Get region multiplier
        region_multiplier = self.get_region_multiplier(region)
        
        # Calculate costs
        cost_per_pod_hour = pod_req.cost_per_hour * region_multiplier
        cost_per_pod_month = cost_per_pod_hour * self.HOURS_PER_MONTH
        total_monthly_cost = cost_per_pod_month * total_pods
        total_yearly_cost = total_monthly_cost * 12
        
        # Calculate utilization
        max_capacity = total_pods * concurrency_limit
        utilization = (required_concurrency / max_capacity * 100) if max_capacity > 0 else 0
        
        # Build breakdown
        breakdown = {
            "instance_specs": {
                "type": pod_req.instance_type,
                "vcpu": pod_req.vcpu,
                "memory_gb": pod_req.memory_gb,
                "max_concurrent": pod_req.max_concurrent_requests
            },
            "capacity": {
                "total_rps_capacity": total_pods * concurrency_limit / (avg_latency_ms / 1000),
                "current_rps": rps,
                "headroom_rps": (total_pods * concurrency_limit / (avg_latency_ms / 1000)) - rps
            },
            "costs": {
                "per_hour": cost_per_pod_hour * total_pods,
                "per_day": cost_per_pod_hour * total_pods * 24,
                "per_month": total_monthly_cost,
                "per_year": total_yearly_cost
            }
        }
        
        return InfraCostResult(
            requests_per_second=rps,
            required_concurrency=required_concurrency,
            required_pods=required_pods,
            instance_type=pod_req.instance_type,
            cost_per_pod_hour=cost_per_pod_hour,
            cost_per_pod_month=cost_per_pod_month,
            total_monthly_cost=total_monthly_cost,
            total_yearly_cost=total_yearly_cost,
            region=region,
            region_multiplier=region_multiplier,
            utilization_percent=utilization,
            headroom_pods=headroom_pods,
            total_pods_with_headroom=total_pods,
            breakdown=breakdown
        )
    
    def compare_instance_types(
        self,
        requests_per_day: int,
        avg_latency_ms: float = None,
        region: str = "us-east-1"
    ) -> Dict[str, InfraCostResult]:
        """
        Compare costs across different instance types.
        
        Args:
            requests_per_day: Number of requests per day
            avg_latency_ms: Average latency in milliseconds
            region: Cloud region for pricing
            
        Returns:
            Dictionary mapping instance type to cost results
        """
        results = {}
        for instance_type in self.compute_types:
            results[instance_type] = self.calculate(
                requests_per_day=requests_per_day,
                avg_latency_ms=avg_latency_ms,
                region=region,
                instance_type=instance_type
            )
        return results
    
    def compare_regions(
        self,
        requests_per_day: int,
        avg_latency_ms: float = None,
        instance_type: Optional[str] = None
    ) -> Dict[str, InfraCostResult]:
        """
        Compare costs across different regions.
        
        Args:
            requests_per_day: Number of requests per day
            avg_latency_ms: Average latency in milliseconds
            instance_type: Specific instance type
            
        Returns:
            Dictionary mapping region to cost results
        """
        results = {}
        for region in self.regions:
            results[region] = self.calculate(
                requests_per_day=requests_per_day,
                avg_latency_ms=avg_latency_ms,
                region=region,
                instance_type=instance_type
            )
        return results
