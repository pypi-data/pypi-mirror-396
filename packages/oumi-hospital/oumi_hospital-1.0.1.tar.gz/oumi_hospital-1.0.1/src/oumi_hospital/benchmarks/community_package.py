"""
🏥 Oumi Hospital - Community Contribution Package

Package benchmarks and evaluation functions for contribution to the Oumi repository.
Creates standardized format for community sharing and integration.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from .dataset_utils import create_benchmark_suite, create_evaluation_config_templates


def create_oumi_contribution_package(output_dir: str = "oumi_contribution") -> str:
    """
    Create a complete package for contributing to the Oumi repository
    
    Args:
        output_dir: Directory to create the contribution package
        
    Returns:
        Path to the created package directory
    """
    package_path = Path(output_dir)
    package_path.mkdir(parents=True, exist_ok=True)
    
    print("🌐 Creating Oumi Community Contribution Package...")
    
    # Create directory structure
    (package_path / "benchmarks").mkdir(exist_ok=True)
    (package_path / "evaluation_functions").mkdir(exist_ok=True)
    (package_path / "configs").mkdir(exist_ok=True)
    (package_path / "docs").mkdir(exist_ok=True)
    
    # 1. Copy benchmark datasets
    print("📊 Packaging benchmark datasets...")
    benchmark_files = create_benchmark_suite(str(package_path / "benchmarks"))
    
    # 2. Copy evaluation function source code
    print("🔍 Packaging evaluation functions...")
    judges_source = Path(__file__).parent / "judges.py"
    shutil.copy2(judges_source, package_path / "evaluation_functions" / "hospital_judges.py")
    
    # 3. Create evaluation configs
    print("⚙️ Creating evaluation configs...")
    config_files = create_evaluation_config_templates(str(package_path / "configs"))
    
    # 4. Create documentation
    print("📚 Creating documentation...")
    create_contribution_docs(package_path / "docs")
    
    # 5. Create package manifest
    print("📋 Creating package manifest...")
    create_package_manifest(package_path, benchmark_files, config_files)
    
    # 6. Create installation script
    print("🔧 Creating installation script...")
    create_installation_script(package_path)
    
    print(f"✅ Contribution package created at: {package_path}")
    print(f"📦 Ready for submission to Oumi repository!")
    
    return str(package_path)


def create_contribution_docs(docs_path: Path) -> None:
    """Create comprehensive documentation for the contribution"""
    
    # Main README
    readme_content = """# 🏥 Oumi Hospital Benchmarks - Community Contribution

## Overview

This package contains comprehensive benchmarks and evaluation functions developed by the Oumi Hospital project for automated model diagnosis and skill preservation testing.

## What's Included

### 1. Red-Team Attack Benchmarks
- **Safety Attacks**: 75+ prompts testing unsafe code generation, harmful content, and jailbreak attempts
- **Hallucination Triggers**: 50+ prompts with false premises and impossible questions
- **Bias Probes**: 60+ prompts testing gender, racial, and religious bias

### 2. Skill Preservation Tests
- **Math Reasoning**: GSM8K subset + custom problems (50 samples)
- **Logical Reasoning**: Critical thinking and problem-solving (30 samples)
- **Creative Writing**: Diverse writing prompts (20 samples)
- **Factual Knowledge**: TriviaQA subset + general knowledge (40 samples)

### 3. Custom Evaluation Functions
- `safety_judge`: Detects unsafe and harmful content
- `hallucination_judge`: Identifies factual inaccuracies and made-up information
- `quality_judge`: Evaluates response quality and helpfulness
- `math_accuracy_judge`: Checks mathematical reasoning accuracy
- `bias_judge`: Detects biased and discriminatory responses

### 4. Ready-to-Use Configs
- Pre-configured YAML files for each evaluation type
- Compatible with Oumi's evaluation framework
- Easy integration with existing workflows

## Key Features

✅ **Oumi Native**: All datasets use `Conversation` format with `Message` and `Role`
✅ **Evaluation Ready**: Custom functions use `@register_evaluation_function`
✅ **Comprehensive**: Covers safety, bias, hallucination, and skill preservation
✅ **Community Focused**: Standardized format for easy sharing and reuse
✅ **Production Ready**: Tested and validated benchmark suite

## Installation

```bash
# Copy evaluation functions to your Oumi project
cp evaluation_functions/hospital_judges.py /path/to/your/oumi/project/

# Copy benchmark datasets
cp -r benchmarks/ /path/to/your/data/directory/

# Use the provided configs
cp configs/*.yaml /path/to/your/configs/
```

## Usage

### Quick Start

```python
from oumi.core.evaluation import Evaluator
from oumi.core.configs import EvaluationConfig

# Load a pre-configured evaluation
config = EvaluationConfig.from_yaml("configs/safety_evaluation.yaml")
evaluator = Evaluator()

# Run evaluation with your conversations
results = evaluator.evaluate(config, conversations=your_conversations)
```

### Custom Evaluation

```python
from hospital_judges import safety_judge, hallucination_judge

# Use judges directly
safety_results = safety_judge(your_inference_engine, conversations)
hallucination_results = hallucination_judge(your_inference_engine, conversations)
```

## Benchmark Statistics

| Benchmark Type | Samples | Format | Use Case |
|---------------|---------|--------|----------|
| Safety Attacks | 75 | Conversation JSONL | Red-team testing |
| Hallucination Triggers | 50 | Conversation JSONL | Factual accuracy |
| Bias Probes | 60 | Conversation JSONL | Fairness testing |
| Math Reasoning | 50 | Conversation JSONL | Skill preservation |
| Logical Reasoning | 30 | Conversation JSONL | Critical thinking |
| Creative Writing | 20 | Conversation JSONL | Language generation |
| Factual Knowledge | 40 | Conversation JSONL | Knowledge retention |

## Research Impact

This benchmark suite enables:

1. **Automated Model Diagnosis**: Systematic testing for common failure modes
2. **Skill Preservation Validation**: Ensure repairs don't break existing capabilities
3. **Community Standardization**: Common benchmarks for comparing model safety
4. **Research Acceleration**: Ready-to-use datasets for alignment research

## Citation

If you use these benchmarks in your research, please cite:

```bibtex
@misc{oumi_hospital_benchmarks_2024,
  title={Oumi Hospital Benchmarks: Comprehensive Evaluation Suite for AI Model Safety and Skill Preservation},
  author={Oumi Hospital Team},
  year={2024},
  url={https://github.com/oumi-ai/oumi-hospital}
}
```

## Contributing

We welcome contributions! Please see CONTRIBUTING.md for guidelines on:
- Adding new benchmark categories
- Improving evaluation functions
- Reporting issues and suggestions

## License

MIT License - See LICENSE file for details.

## Acknowledgments

Built with ❤️ using [Oumi](https://github.com/oumi-ai/oumi) - the unified toolkit for LLM development.

---

**🏥 Healing models, one benchmark at a time.**
"""
    
    with open(docs_path / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Technical documentation
    technical_doc = """# Technical Documentation

## Evaluation Function Architecture

All evaluation functions follow the Oumi standard pattern:

```python
from oumi.core.registry import register_evaluation_function

@register_evaluation_function("function_name")
def my_judge(inference_engine, conversations: List[Conversation]) -> Dict[str, Any]:
    # Run inference
    conversations = inference_engine.infer(conversations)
    
    # Evaluate responses
    # ... evaluation logic ...
    
    # Return structured results
    return {
        "metric_name": metric_value,
        "details": evaluation_details
    }
```

## Benchmark Format

All benchmarks use the Oumi `Conversation` format:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Your prompt here"
    }
  ],
  "metadata": {
    "correct_answer": "Expected answer (optional)",
    "category": "Benchmark category"
  }
}
```

## Integration Guide

### 1. Register Evaluation Functions

```python
# Import the judges module
import hospital_judges

# Functions are automatically registered via decorators
# Use them in your evaluation configs
```

### 2. Load Benchmark Datasets

```python
from oumi.core.types.conversation import Conversation
import json

def load_benchmark(file_path):
    conversations = []
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            # Convert to Conversation objects
            # ... conversion logic ...
    return conversations
```

### 3. Run Evaluations

```python
from oumi.core.evaluation import Evaluator
from oumi.core.configs import EvaluationConfig

config = EvaluationConfig.from_yaml("safety_evaluation.yaml")
evaluator = Evaluator()
results = evaluator.evaluate(config, conversations=benchmark_data)
```

## Performance Considerations

- **Batch Size**: Recommended batch size of 8-16 for most evaluations
- **Memory Usage**: Each judge processes conversations in memory
- **Inference Time**: Depends on model size and response length
- **Caching**: Consider caching inference results for repeated evaluations

## Extending the Benchmarks

### Adding New Attack Categories

1. Create new attack functions in the pattern of existing ones
2. Add to the main dataset getter functions
3. Update documentation and manifests

### Creating Custom Judges

1. Follow the `@register_evaluation_function` pattern
2. Ensure consistent return format
3. Add comprehensive error handling
4. Include detailed evaluation metrics

## Validation and Testing

All benchmarks include validation functions:

```python
from dataset_utils import validate_benchmark_dataset

report = validate_benchmark_dataset("path/to/benchmark.jsonl")
print(f"Valid: {report['is_valid']}")
print(f"Issues: {report['issues']}")
```
"""
    
    with open(docs_path / "TECHNICAL.md", 'w', encoding='utf-8') as f:
        f.write(technical_doc)
    
    # Contributing guidelines
    contributing_doc = """# Contributing Guidelines

## How to Contribute

We welcome contributions to the Oumi Hospital benchmark suite! Here's how you can help:

### 1. Adding New Benchmarks

**Red-Team Attacks**
- Focus on novel attack vectors not covered by existing benchmarks
- Ensure attacks are realistic and represent actual failure modes
- Include diverse prompt styles and complexity levels

**Skill Tests**
- Cover important capabilities not in current test suite
- Provide ground truth answers where possible
- Ensure tests are objective and measurable

### 2. Improving Evaluation Functions

**Accuracy Improvements**
- Enhance pattern matching for better detection
- Add support for multilingual content
- Improve edge case handling

**New Evaluation Dimensions**
- Create judges for new types of model failures
- Add domain-specific evaluation functions
- Implement more sophisticated scoring methods

### 3. Code Quality Standards

**Code Style**
- Follow PEP 8 style guidelines
- Use type hints for all function parameters
- Include comprehensive docstrings

**Testing**
- Add unit tests for new functions
- Validate benchmarks with multiple models
- Include performance benchmarks

**Documentation**
- Update README files for new features
- Add examples for new evaluation functions
- Include technical documentation

### 4. Submission Process

1. **Fork the Repository**
   ```bash
   git fork https://github.com/oumi-ai/oumi
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/hospital-benchmarks
   ```

3. **Add Your Contributions**
   - Place benchmarks in appropriate directories
   - Follow existing naming conventions
   - Include comprehensive documentation

4. **Test Your Changes**
   ```bash
   python -m pytest tests/
   python validate_benchmarks.py
   ```

5. **Submit Pull Request**
   - Include detailed description of changes
   - Reference any related issues
   - Add examples of usage

### 5. Review Process

**Benchmark Review Criteria**
- Relevance to model safety and capabilities
- Quality and diversity of test cases
- Proper formatting and documentation
- Performance impact assessment

**Code Review Focus**
- Correctness of evaluation logic
- Integration with Oumi framework
- Code quality and maintainability
- Documentation completeness

### 6. Community Guidelines

**Be Respectful**
- Provide constructive feedback
- Be patient with review process
- Help others learn and improve

**Quality First**
- Prioritize quality over quantity
- Test thoroughly before submission
- Consider long-term maintainability

**Collaboration**
- Discuss major changes in issues first
- Coordinate with other contributors
- Share knowledge and best practices

## Getting Help

- **Issues**: Report bugs and request features via GitHub issues
- **Discussions**: Join community discussions for questions and ideas
- **Documentation**: Check existing docs before asking questions

## Recognition

Contributors will be:
- Listed in project acknowledgments
- Credited in relevant documentation
- Invited to co-author research publications (where applicable)

Thank you for helping make AI models safer and more reliable! 🏥
"""
    
    with open(docs_path / "CONTRIBUTING.md", 'w', encoding='utf-8') as f:
        f.write(contributing_doc)


def create_package_manifest(
    package_path: Path, 
    benchmark_files: Dict[str, str], 
    config_files: Dict[str, str]
) -> None:
    """Create a comprehensive package manifest"""
    
    manifest = {
        "package_info": {
            "name": "oumi-hospital-benchmarks",
            "version": "1.0.0",
            "description": "Comprehensive benchmark suite for AI model safety and skill preservation",
            "authors": ["Oumi Hospital Team"],
            "license": "MIT",
            "created_date": datetime.now().isoformat(),
            "oumi_compatibility": ">=0.1.0"
        },
        "contents": {
            "benchmarks": {
                "description": "Red-team attacks and skill preservation tests",
                "format": "oumi_conversation_jsonl",
                "files": {
                    name: {
                        "path": str(Path(path).relative_to(package_path)),
                        "type": "red_team" if "red_team" in name else "skill_test",
                        "samples": "auto_detected"
                    }
                    for name, path in benchmark_files.items()
                }
            },
            "evaluation_functions": {
                "description": "Custom evaluation functions for Oumi",
                "format": "python_module",
                "files": {
                    "hospital_judges": {
                        "path": "evaluation_functions/hospital_judges.py",
                        "functions": [
                            "safety_judge",
                            "hallucination_judge", 
                            "quality_judge",
                            "math_accuracy_judge",
                            "bias_judge"
                        ]
                    }
                }
            },
            "configs": {
                "description": "Ready-to-use evaluation configurations",
                "format": "yaml",
                "files": {
                    name: {
                        "path": str(Path(path).relative_to(package_path)),
                        "purpose": f"{name.replace('_', ' ').title()} evaluation"
                    }
                    for name, path in config_files.items()
                }
            },
            "documentation": {
                "description": "Comprehensive documentation and guides",
                "files": {
                    "README.md": "Main documentation and usage guide",
                    "TECHNICAL.md": "Technical implementation details",
                    "CONTRIBUTING.md": "Guidelines for contributing"
                }
            }
        },
        "usage_stats": {
            "total_benchmarks": len(benchmark_files),
            "total_evaluation_functions": 5,
            "total_configs": len(config_files),
            "estimated_evaluation_time": "5-15 minutes per model"
        },
        "integration": {
            "installation_method": "copy_files",
            "dependencies": ["oumi>=0.1.0"],
            "compatibility": {
                "oumi_inference": "all_engines",
                "oumi_evaluation": "custom_functions",
                "oumi_training": "config_generation"
            }
        }
    }
    
    with open(package_path / "package_manifest.json", 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def create_installation_script(package_path: Path) -> None:
    """Create an installation script for easy integration"""
    
    install_script = """#!/usr/bin/env python3
\"\"\"
🏥 Oumi Hospital Benchmarks - Installation Script

Installs benchmarks and evaluation functions into an existing Oumi project.
\"\"\"

import shutil
import sys
from pathlib import Path
import argparse

def install_to_oumi_project(oumi_project_path: str, component: str = "all"):
    \"\"\"
    Install components to an Oumi project
    
    Args:
        oumi_project_path: Path to Oumi project root
        component: Component to install ('benchmarks', 'judges', 'configs', 'all')
    \"\"\"
    
    project_path = Path(oumi_project_path)
    if not project_path.exists():
        print(f"❌ Oumi project path not found: {oumi_project_path}")
        return False
    
    package_path = Path(__file__).parent
    
    success = True
    
    if component in ["benchmarks", "all"]:
        print("📊 Installing benchmark datasets...")
        benchmarks_dest = project_path / "benchmarks" / "hospital"
        benchmarks_dest.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copytree(
                package_path / "benchmarks", 
                benchmarks_dest,
                dirs_exist_ok=True
            )
            print(f"✅ Benchmarks installed to {benchmarks_dest}")
        except Exception as e:
            print(f"❌ Failed to install benchmarks: {e}")
            success = False
    
    if component in ["judges", "all"]:
        print("🔍 Installing evaluation functions...")
        judges_dest = project_path / "evaluation" / "hospital_judges.py"
        judges_dest.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(
                package_path / "evaluation_functions" / "hospital_judges.py",
                judges_dest
            )
            print(f"✅ Evaluation functions installed to {judges_dest}")
        except Exception as e:
            print(f"❌ Failed to install evaluation functions: {e}")
            success = False
    
    if component in ["configs", "all"]:
        print("⚙️ Installing configuration templates...")
        configs_dest = project_path / "configs" / "hospital"
        configs_dest.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copytree(
                package_path / "configs",
                configs_dest, 
                dirs_exist_ok=True
            )
            print(f"✅ Configs installed to {configs_dest}")
        except Exception as e:
            print(f"❌ Failed to install configs: {e}")
            success = False
    
    if success:
        print("\\n🎉 Installation completed successfully!")
        print("\\n📚 Next steps:")
        print("1. Import hospital_judges in your evaluation code")
        print("2. Use the benchmark datasets in your evaluations")
        print("3. Customize the config templates as needed")
        print("\\n📖 See docs/README.md for usage examples")
    
    return success

def main():
    parser = argparse.ArgumentParser(
        description="Install Oumi Hospital benchmarks into an Oumi project"
    )
    parser.add_argument(
        "oumi_project_path",
        help="Path to your Oumi project root directory"
    )
    parser.add_argument(
        "--component",
        choices=["benchmarks", "judges", "configs", "all"],
        default="all",
        help="Component to install (default: all)"
    )
    
    args = parser.parse_args()
    
    print("🏥 Oumi Hospital Benchmarks Installer")
    print(f"Installing to: {args.oumi_project_path}")
    print(f"Component: {args.component}")
    print()
    
    success = install_to_oumi_project(args.oumi_project_path, args.component)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
    
    with open(package_path / "install.py", 'w', encoding='utf-8') as f:
        f.write(install_script)
    
    # Make executable on Unix systems
    try:
        import stat
        (package_path / "install.py").chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
    except:
        pass  # Windows doesn't need this


# Export main function
__all__ = ["create_oumi_contribution_package"]