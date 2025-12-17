#!/usr/bin/env python3
"""
AI Infra Cost Estimator CLI

Command-line interface for estimating AI infrastructure costs.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

from ai_infra_cost_estimator.calculator.llm import LLMCostCalculator
from ai_infra_cost_estimator.calculator.infra import InfraCostCalculator
from ai_infra_cost_estimator.calculator.scaling import ScalingAnalyzer
from ai_infra_cost_estimator.report.markdown import MarkdownReportGenerator
from ai_infra_cost_estimator.report.json_report import JSONReportGenerator


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def validate_config(config: dict) -> tuple:
    """
    Validate configuration parameters.
    
    Returns:
        Tuple of (is_valid, list of errors)
    """
    errors = []
    required_fields = [
        'requests_per_day',
        'avg_input_tokens',
        'avg_output_tokens',
        'model'
    ]
    
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Validate numeric fields
    numeric_fields = {
        'requests_per_day': (1, 100_000_000),
        'avg_input_tokens': (1, 1_000_000),
        'avg_output_tokens': (1, 1_000_000),
        'cache_hit_ratio': (0, 1),
        'concurrency_limit': (1, 10000),
        'avg_latency_ms': (1, 60000)
    }
    
    for field, (min_val, max_val) in numeric_fields.items():
        if field in config:
            val = config[field]
            if not isinstance(val, (int, float)):
                errors.append(f"{field} must be a number")
            elif val < min_val or val > max_val:
                errors.append(f"{field} must be between {min_val} and {max_val}")
    
    return len(errors) == 0, errors


def run_estimation(config: dict, output_format: str = 'markdown') -> str:
    """
    Run the cost estimation with the given configuration.
    
    Args:
        config: Configuration dictionary
        output_format: Output format ('markdown' or 'json')
        
    Returns:
        Formatted report string
    """
    # Set defaults
    defaults = {
        'region': 'us-east-1',
        'cache_hit_ratio': 0.0,
        'concurrency_limit': 50,
        'avg_latency_ms': 500,
        'headroom_percent': 20.0
    }
    
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
    
    # Initialize calculators
    llm_calculator = LLMCostCalculator()
    infra_calculator = InfraCostCalculator()
    scaling_analyzer = ScalingAnalyzer()
    
    # Calculate LLM costs
    llm_result = llm_calculator.calculate(
        requests_per_day=config['requests_per_day'],
        avg_input_tokens=config['avg_input_tokens'],
        avg_output_tokens=config['avg_output_tokens'],
        model=config['model'],
        cache_hit_ratio=config['cache_hit_ratio']
    )
    
    # Calculate infrastructure costs
    infra_result = infra_calculator.calculate(
        requests_per_day=config['requests_per_day'],
        avg_latency_ms=config['avg_latency_ms'],
        concurrency_limit=config['concurrency_limit'],
        region=config['region'],
        instance_type=config.get('instance_type'),
        headroom_percent=config['headroom_percent']
    )
    
    # Run scaling analysis
    analysis = scaling_analyzer.analyze(
        requests_per_day=config['requests_per_day'],
        avg_input_tokens=config['avg_input_tokens'],
        avg_output_tokens=config['avg_output_tokens'],
        model=config['model'],
        cache_hit_ratio=config['cache_hit_ratio'],
        avg_latency_ms=config['avg_latency_ms'],
        concurrency_limit=config['concurrency_limit'],
        region=config['region'],
        instance_type=config.get('instance_type')
    )
    
    # Generate report
    if output_format == 'json':
        generator = JSONReportGenerator()
        report = generator.generate_report(config, llm_result, infra_result, analysis)
        return generator.to_json_string(report)
    else:
        generator = MarkdownReportGenerator()
        return generator.generate_full_report(config, llm_result, infra_result, analysis)


def list_models():
    """List all available models."""
    calculator = LLMCostCalculator()
    models = calculator.get_available_models()
    
    print("\n📋 Available Models:\n")
    print(f"{'Model':<20} {'Provider':<12} {'Input/1K':<10} {'Output/1K':<10}")
    print("-" * 55)
    
    for name, data in sorted(models.items()):
        print(f"{name:<20} {data['provider']:<12} ${data['input_per_1k']:<9.5f} ${data['output_per_1k']:<9.5f}")
    
    print()


def list_regions():
    """List all available regions."""
    calculator = InfraCostCalculator()
    regions = calculator.get_available_regions()
    
    print("\n🌍 Available Regions:\n")
    print(f"{'Code':<16} {'Name':<30} {'Multiplier':<10}")
    print("-" * 58)
    
    for code, data in sorted(regions.items()):
        print(f"{code:<16} {data['name']:<30} {data['multiplier']:<10.2f}x")
    
    print()


def list_instance_types():
    """List all available instance types."""
    calculator = InfraCostCalculator()
    instances = calculator.get_available_instance_types()
    
    print("\n💻 Available Instance Types:\n")
    print(f"{'Type':<12} {'vCPU':<6} {'Memory':<10} {'$/Hour':<10} {'Max Concurrent':<15}")
    print("-" * 60)
    
    for name, data in sorted(instances.items()):
        mem = f"{data['memory_gb']}GB"
        print(f"{name:<12} {data['vcpu']:<6} {mem:<10} ${data['cost_per_hour_usd']:<9.2f} {data['max_concurrent_requests']:<15}")
    
    print()


def compare_models(config: dict):
    """Compare costs across all models."""
    calculator = LLMCostCalculator()
    
    results = calculator.compare_models(
        requests_per_day=config['requests_per_day'],
        avg_input_tokens=config['avg_input_tokens'],
        avg_output_tokens=config['avg_output_tokens'],
        cache_hit_ratio=config.get('cache_hit_ratio', 0.0)
    )
    
    print("\n📊 Model Cost Comparison:\n")
    print(f"{'Model':<20} {'Provider':<12} {'Monthly Cost':<15} {'Cost/Request':<12}")
    print("-" * 65)
    
    sorted_results = sorted(results.items(), key=lambda x: x[1].monthly_total_cost)
    
    for name, result in sorted_results:
        print(f"{name:<20} {result.provider:<12} ${result.monthly_total_cost:<14,.2f} ${result.cost_per_request:<11.6f}")
    
    print()


def create_sample_config(output_path: str):
    """Create a sample configuration file."""
    sample_config = {
        'requests_per_day': 10000,
        'avg_input_tokens': 800,
        'avg_output_tokens': 400,
        'model': 'gpt-4o-mini',
        'region': 'us-east-1',
        'cache_hit_ratio': 0.2,
        'concurrency_limit': 50,
        'avg_latency_ms': 500,
        'headroom_percent': 20.0
    }
    
    with open(output_path, 'w') as f:
        yaml.dump(sample_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Sample configuration created: {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='AI Infra Cost Estimator - Estimate real-world AI + cloud costs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-cost-estimator run config.yaml
  ai-cost-estimator run config.yaml --format json
  ai-cost-estimator run config.yaml --output report.md
  ai-cost-estimator list-models
  ai-cost-estimator compare config.yaml
  ai-cost-estimator init my-config.yaml
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run cost estimation')
    run_parser.add_argument('config', help='Path to configuration YAML file')
    run_parser.add_argument('--format', '-f', choices=['markdown', 'json'], 
                           default='markdown', help='Output format')
    run_parser.add_argument('--output', '-o', help='Output file path (optional)')
    
    # List commands
    subparsers.add_parser('list-models', help='List available LLM models')
    subparsers.add_parser('list-regions', help='List available cloud regions')
    subparsers.add_parser('list-instances', help='List available instance types')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare costs across models')
    compare_parser.add_argument('config', help='Path to configuration YAML file')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Create sample configuration file')
    init_parser.add_argument('output', nargs='?', default='config.yaml',
                            help='Output file path (default: config.yaml)')
    
    # Version
    parser.add_argument('--version', '-v', action='version', 
                       version='AI Infra Cost Estimator 1.0.0')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.command == 'run':
            config = load_config(args.config)
            is_valid, errors = validate_config(config)
            
            if not is_valid:
                print("❌ Configuration errors:")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)
            
            report = run_estimation(config, args.format)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(report)
                print(f"✅ Report saved to: {args.output}")
            else:
                print(report)
        
        elif args.command == 'list-models':
            list_models()
        
        elif args.command == 'list-regions':
            list_regions()
        
        elif args.command == 'list-instances':
            list_instance_types()
        
        elif args.command == 'compare':
            config = load_config(args.config)
            is_valid, errors = validate_config(config)
            
            if not is_valid:
                print("❌ Configuration errors:")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)
            
            compare_models(config)
        
        elif args.command == 'init':
            create_sample_config(args.output)
    
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
