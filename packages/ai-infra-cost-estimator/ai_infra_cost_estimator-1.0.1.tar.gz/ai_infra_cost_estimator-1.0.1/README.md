# 🚀 AI Infra Cost Estimator

**Estimate real-world AI + cloud costs before scaling breaks you.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Problem

Most AI startups underestimate costs because **LLM usage, concurrency, and infrastructure scaling are tightly coupled**.

A small growth in requests can cause **non-linear cost jumps** that catch founders off guard.

This tool estimates:
- 💰 **LLM API costs** (tokens, caching impact)
- 🖥️ **Infrastructure costs** (compute, pods, scaling)
- 📈 **Scaling thresholds** (when costs jump)
- 💡 **Optimization recommendations**

**Before you deploy.**

---

## ✨ Features

- **Multi-model support**: OpenAI, Anthropic, Google, Meta, Mistral
- **Infrastructure estimation**: Pod/container scaling calculations
- **Caching analysis**: See how caching affects your costs
- **Scaling breakpoints**: Know when you'll need more resources
- **Cost projections**: See costs at 1.5x, 2x, 3x, 5x growth
- **Optimization recommendations**: Actionable cost-saving suggestions
- **Multiple output formats**: Markdown reports & JSON for automation

---

## 📊 Example Output

```
### Monthly Cost Summary

LLM Cost:     $1,820
Infra Cost:   $640
────────────────────────────
Total:        $2,460

Cost per Request: $0.0082
Yearly Estimate:  $29,520

### Scaling Alerts
- At 18,000 req/day → scale to 2 pods
- At 45,000 req/day → cost doubles to $4,920/month

### Recommendations
1. 🟠 Improve cache hit ratio to 40%
   Potential Savings: $520/month
   
2. 🟡 Consider switching to gpt-3.5-turbo
   Potential Savings: $890/month
```

---

## 🚀 Quick Start

### Installation

**Option 1: Install via pip (Recommended)**

```bash
pip install ai-infra-cost-estimator
```

**Option 2: Install from source**

```bash
# Clone the repository
git clone https://github.com/MindTheInfraAI/AI_Infra_Cost_Estimator.git
cd AI_Infra_Cost_Estimator

# Install the package
pip install -e .
```

### Basic Usage

```bash
# Run with a config file
ai-cost-estimator run config.yaml

# Output as JSON
ai-cost-estimator run config.yaml --format json

# Save report to file
ai-cost-estimator run config.yaml --output report.md
```

### Create Your Configuration

```bash
# Generate sample config
ai-cost-estimator init my-config.yaml
```

Edit `my-config.yaml`:

```yaml
requests_per_day: 10000
avg_input_tokens: 800
avg_output_tokens: 400
model: gpt-4o-mini
region: us-east-1
cache_hit_ratio: 0.2
concurrency_limit: 50
```

---

## 📖 CLI Commands

| Command | Description |
|---------|-------------|
| `run <config>` | Run cost estimation |
| `run <config> --format json` | Output as JSON |
| `run <config> -o report.md` | Save to file |
| `list-models` | Show available LLM models |
| `list-regions` | Show available cloud regions |
| `list-instances` | Show available instance types |
| `compare <config>` | Compare costs across all models |
| `init [filename]` | Create sample configuration |

### Examples

```bash
# List all supported models with pricing
ai-cost-estimator list-models

# Compare your workload across all models
ai-cost-estimator compare examples/startup.yaml

# Use a specific example config
ai-cost-estimator run examples/enterprise.yaml
```

---

## 📁 Configuration Reference

```yaml
# Required Parameters
requests_per_day: 10000      # Daily API request volume
avg_input_tokens: 800        # Average tokens per input/prompt
avg_output_tokens: 400       # Average tokens per response
model: gpt-4o-mini           # LLM model name

# Optional Parameters (with defaults)
region: us-east-1            # Cloud region
cache_hit_ratio: 0.0         # Cache effectiveness (0.0 - 1.0)
concurrency_limit: 50        # Max concurrent requests per pod
avg_latency_ms: 500          # Average request latency
headroom_percent: 20.0       # Extra capacity buffer
instance_type: auto          # small, medium, large, xlarge, gpu_t4, gpu_a100
```

---

## 🤖 Supported Models

> ⚠️ **Important Disclaimer:** The pricing shown below are **estimated values** for reference purposes only. Actual costs may vary based on provider pricing changes, volume discounts, and regional variations. **Please verify current pricing** from the official provider documentation before making business decisions.

| Model | Provider | Input/1K | Output/1K |
|-------|----------|----------|-----------|
| gpt-4o | OpenAI | $0.0025 | $0.01 |
| gpt-4o-mini | OpenAI | $0.00015 | $0.0006 |
| gpt-4-turbo | OpenAI | $0.01 | $0.03 |
| gpt-3.5-turbo | OpenAI | $0.0005 | $0.0015 |
| claude-3-5-sonnet | Anthropic | $0.003 | $0.015 |
| claude-3-opus | Anthropic | $0.015 | $0.075 |
| claude-3-haiku | Anthropic | $0.00025 | $0.00125 |
| gemini-1.5-pro | Google | $0.00125 | $0.005 |
| gemini-1.5-flash | Google | $0.000075 | $0.0003 |
| llama-3.1-70b | Meta | $0.00079 | $0.00079 |
| llama-3.1-8b | Meta | $0.00018 | $0.00018 |
| mistral-large | Mistral | $0.002 | $0.006 |
| mistral-small | Mistral | $0.0002 | $0.0006 |

*Always check official pricing pages for current rates.*

---

## 🌍 Supported Regions

| Region | Location | Price Multiplier |
|--------|----------|-----------------|
| us-east-1 | N. Virginia | 1.0x |
| us-west-2 | Oregon | 1.0x |
| eu-west-1 | Ireland | 1.1x |
| eu-central-1 | Frankfurt | 1.15x |
| ap-south-1 | Mumbai | 0.9x |
| ap-southeast-1 | Singapore | 1.05x |
| ap-northeast-1 | Tokyo | 1.2x |

---

## 📂 Project Structure

```
ai-infra-cost-estimator/
├── ai_infra_cost_estimator/  # Main package (pip installable)
│   ├── __init__.py
│   ├── cli.py               # Command-line interface
│   ├── calculator/
│   │   ├── __init__.py
│   │   ├── llm.py           # LLM cost calculations
│   │   ├── infra.py         # Infrastructure cost calculations
│   │   └── scaling.py       # Scaling analysis & recommendations
│   ├── report/
│   │   ├── __init__.py
│   │   ├── markdown.py      # Markdown report generator
│   │   └── json_report.py   # JSON report generator
│   └── pricing/
│       ├── __init__.py
│       └── models.json      # Model & infra pricing data
├── examples/
│   ├── startup.yaml         # Startup configuration
│   ├── enterprise.yaml      # Enterprise configuration
│   ├── budget.yaml          # Budget-conscious config
│   ├── chatbot.yaml         # Chatbot application config
│   └── code_assistant.yaml  # Code assistant config
├── pyproject.toml           # Package configuration
├── MANIFEST.in
├── README.md
└── LICENSE
```

---

## 🧮 How It Works

### LLM Cost Calculation

```
effective_requests = requests_per_day × (1 - cache_hit_ratio)
daily_tokens = effective_requests × (input_tokens + output_tokens)
monthly_cost = (daily_tokens / 1000) × price_per_1k × 30
```

### Infrastructure Calculation

```
requests_per_second = requests_per_day / 86400
required_concurrency = rps × avg_latency_seconds × overhead_multiplier
required_pods = ceil(required_concurrency / concurrency_limit)
monthly_cost = pods × cost_per_hour × 720
```

### Scaling Breakpoints

The analyzer finds:
- When you need to add pods
- When costs double
- Impact of cache improvements
- Cheaper model alternatives

---

## 👥 Who This Is For

- **AI SaaS Founders** - Understand costs before launch
- **Platform Engineers** - Plan infrastructure scaling
- **Cloud Architects** - Optimize deployment strategy
- **Indie Hackers** - Build within budget constraints

---

## 🔧 Programmatic Usage

```python
from ai_infra_cost_estimator import (
    LLMCostCalculator,
    InfraCostCalculator,
    ScalingAnalyzer,
    MarkdownReportGenerator
)

# Calculate LLM costs
llm_calc = LLMCostCalculator()
llm_result = llm_calc.calculate(
    requests_per_day=10000,
    avg_input_tokens=800,
    avg_output_tokens=400,
    model="gpt-4o-mini",
    cache_hit_ratio=0.2
)

print(f"Monthly LLM Cost: ${llm_result.monthly_total_cost:.2f}")

# Calculate infrastructure costs
infra_calc = InfraCostCalculator()
infra_result = infra_calc.calculate(
    requests_per_day=10000,
    avg_latency_ms=500,
    concurrency_limit=50,
    region="us-east-1"
)

print(f"Monthly Infra Cost: ${infra_result.total_monthly_cost:.2f}")

# Get scaling analysis
analyzer = ScalingAnalyzer()
analysis = analyzer.analyze(
    requests_per_day=10000,
    avg_input_tokens=800,
    avg_output_tokens=400,
    model="gpt-4o-mini",
    cache_hit_ratio=0.2
)

for alert in analysis.scaling_alerts:
    print(f"⚠️ {alert}")

for rec in analysis.recommendations[:3]:
    print(f"💡 {rec.title}: Save ${rec.potential_savings:.2f}/month")
```

---

## 🛣️ Roadmap

- [ ] **v1.1**: GPU cost estimation for self-hosted models
- [ ] **v1.2**: Multi-region deployment cost comparison
- [ ] **v1.3**: API endpoint for integration
- [ ] **v2.0**: Real-time cloud integration (AWS, GCP, Azure)

---

## 📝 Assumptions

These estimates are based on:

- Stateless inference workloads
- HTTP-based serving
- Average token sizes (actual may vary)
- Public API pricing (enterprise pricing may differ)
- No model fine-tuning costs

**Clear assumptions = trust.**

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/MindTheInfraAI/AI_Infra_Cost_Estimator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MindTheInfraAI/AI_Infra_Cost_Estimator/discussions)

---

## ⚠️ Disclaimer

> **This tool provides estimated costs for planning and budgeting purposes only.**
> 
> - All model pricing values are **approximations** and may not reflect current actual pricing
> - LLM providers frequently update their pricing — **always verify with official documentation**
> - Infrastructure costs vary by cloud provider, region, and specific configurations
> - Enterprise agreements, volume discounts, and promotional pricing are not factored in
> - **Please recheck and validate all estimates** before making financial or business decisions
>
> **Official Pricing Pages:**
> - [OpenAI Pricing](https://openai.com/pricing)
> - [Anthropic Pricing](https://www.anthropic.com/pricing)
> - [Google AI Pricing](https://cloud.google.com/vertex-ai/pricing)
> - [Mistral Pricing](https://mistral.ai/pricing/)

---

**Built for builders who want to understand their AI costs before they scale.**

