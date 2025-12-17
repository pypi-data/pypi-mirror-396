"""
🧠 The Neurologist - Skill Preservation Agent

This agent checks if a model retains its core capabilities after treatment.
Prevents catastrophic forgetting by comparing before/after performance.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.utils.oumi_integration import OumiWrapper
from src.benchmarks.skill_tests import SkillTestSuite
from src.utils.console import hospital_console

logger = logging.getLogger(__name__)
console = hospital_console.console


@dataclass
class SkillScore:
    """Individual skill domain score"""
    domain: str
    score_before: float
    score_after: float
    degradation: float
    status: str  # "preserved", "degraded", "improved"
    
    @property
    def degradation_percent(self) -> float:
        """Degradation as percentage"""
        if self.score_before == 0:
            return 0.0
        return (self.score_before - self.score_after) / self.score_before * 100


@dataclass
class SkillReport:
    """Complete skill preservation analysis"""
    model_before: str
    model_after: str
    skill_scores: List[SkillScore]
    overall_degradation: float
    verdict: str  # "safe", "caution", "critical"
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "model_before": self.model_before,
            "model_after": self.model_after,
            "skill_scores": [
                {
                    "domain": score.domain,
                    "score_before": score.score_before,
                    "score_after": score.score_after,
                    "degradation": score.degradation,
                    "degradation_percent": score.degradation_percent,
                    "status": score.status
                }
                for score in self.skill_scores
            ],
            "overall_degradation": self.overall_degradation,
            "verdict": self.verdict,
            "recommendations": self.recommendations
        }


class Neurologist:
    """
    The Neurologist checks for skill preservation after model treatment.
    
    Key capabilities:
    - Compare model performance before/after training
    - Detect catastrophic forgetting across skill domains
    - Generate adaptive training recommendations
    - Use Oumi evaluation framework for consistent scoring
    """
    
    def __init__(self, degradation_threshold: float = 10.0):
        """
        Initialize the Neurologist.
        
        Args:
            degradation_threshold: Percentage degradation threshold for concern
        """
        self.degradation_threshold = degradation_threshold
        self.oumi = OumiWrapper()
        self.skill_suite = SkillTestSuite()
        
    def check_skill_preservation(
        self, 
        model_before: str, 
        model_after: str,
        output_dir: Optional[str] = None
    ) -> SkillReport:
        """
        Compare skill performance between two models.
        
        Args:
            model_before: Path or ID of original model
            model_after: Path or ID of treated model
            output_dir: Directory to save detailed results
            
        Returns:
            SkillReport with complete analysis
        """
        console.print(Panel.fit(
            "🧠 [bold blue]Neurological Assessment[/bold blue]\n"
            f"Checking skill preservation between models...",
            border_style="blue"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Load skill test datasets
            task = progress.add_task("Loading skill test datasets...", total=None)
            skill_datasets = self.skill_suite.get_all_datasets()
            progress.update(task, description="✅ Skill datasets loaded")
            
            # Evaluate both models
            skill_scores = []
            
            for domain, conversations in skill_datasets.items():
                progress.update(task, description=f"Evaluating {domain} skills...")
                
                # Score original model
                score_before = self._evaluate_model_on_domain(
                    model_before, domain, conversations
                )
                
                # Score treated model  
                score_after = self._evaluate_model_on_domain(
                    model_after, domain, conversations
                )
                
                # Calculate degradation
                degradation = score_before - score_after
                degradation_pct = (degradation / score_before * 100) if score_before > 0 else 0
                
                # Determine status
                if degradation_pct > self.degradation_threshold:
                    status = "degraded"
                elif degradation_pct < -5:  # Improvement threshold
                    status = "improved"
                else:
                    status = "preserved"
                
                skill_score = SkillScore(
                    domain=domain,
                    score_before=score_before,
                    score_after=score_after,
                    degradation=degradation,
                    status=status
                )
                skill_scores.append(skill_score)
                
                progress.update(task, description=f"✅ {domain}: {status}")
        
        # Calculate overall metrics
        overall_degradation = sum(s.degradation_percent for s in skill_scores) / len(skill_scores)
        
        # Generate verdict and recommendations
        verdict, recommendations = self._generate_recommendations(skill_scores, overall_degradation)
        
        # Create report
        report = SkillReport(
            model_before=model_before,
            model_after=model_after,
            skill_scores=skill_scores,
            overall_degradation=overall_degradation,
            verdict=verdict,
            recommendations=recommendations
        )
        
        # Display results
        self._display_results(report)
        
        # Save detailed report if requested
        if output_dir:
            self._save_report(report, output_dir)
        
        return report
    
    def _evaluate_model_on_domain(
        self, 
        model_id: str, 
        domain: str, 
        conversations: List
    ) -> float:
        """
        Evaluate a model on a specific skill domain.
        
        Args:
            model_id: Model identifier
            domain: Skill domain name
            conversations: Test conversations for this domain
            
        Returns:
            Average score for this domain
        """
        try:
            # Get model responses using Oumi inference
            responses = self.oumi.batch_infer(model_id, conversations)
            
            # Evaluate responses using domain-specific judge
            evaluation_function = self.skill_suite.get_evaluation_function(domain)
            scores = self.oumi.evaluate_responses(
                conversations, 
                responses, 
                evaluation_function
            )
            
            # Return average score
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Error evaluating {model_id} on {domain}: {e}")
            return 0.0
    
    def _generate_recommendations(
        self, 
        skill_scores: List[SkillScore], 
        overall_degradation: float
    ) -> Tuple[str, List[str]]:
        """
        Generate verdict and training recommendations based on skill analysis.
        
        Args:
            skill_scores: Individual domain scores
            overall_degradation: Overall degradation percentage
            
        Returns:
            Tuple of (verdict, recommendations)
        """
        degraded_domains = [s for s in skill_scores if s.status == "degraded"]
        severely_degraded = [s for s in skill_scores if s.degradation_percent > 20]
        
        # Determine verdict
        if len(severely_degraded) > 0:
            verdict = "critical"
        elif len(degraded_domains) > len(skill_scores) // 2:
            verdict = "caution"
        else:
            verdict = "safe"
        
        # Generate recommendations
        recommendations = []
        
        if verdict == "critical":
            recommendations.extend([
                "🚨 CRITICAL: Severe skill degradation detected",
                "Reduce learning rate by 50% (e.g., 3e-4 → 1.5e-4)",
                "Decrease LoRA rank (e.g., 16 → 8)",
                "Add replay buffer: mix 30% original training data",
                "Consider shorter training (reduce epochs by 1)"
            ])
        elif verdict == "caution":
            recommendations.extend([
                "⚠️ CAUTION: Moderate skill degradation detected",
                "Reduce learning rate by 25% (e.g., 1e-4 → 7.5e-5)",
                "Consider adding skill-specific examples to training data",
                "Monitor closely during next training iteration"
            ])
        else:
            recommendations.extend([
                "✅ SAFE: Skills well preserved",
                "Current training parameters appear optimal",
                "Safe to proceed with similar hyperparameters"
            ])
        
        # Domain-specific recommendations
        for score in degraded_domains:
            if score.domain == "math":
                recommendations.append(f"📊 Math skills degraded: Add GSM8K examples to training mix")
            elif score.domain == "reasoning":
                recommendations.append(f"🧩 Reasoning degraded: Include logical reasoning examples")
            elif score.domain == "writing":
                recommendations.append(f"✍️ Writing degraded: Add creative writing samples")
            elif score.domain == "factual":
                recommendations.append(f"📚 Factual knowledge degraded: Include knowledge-rich examples")
        
        return verdict, recommendations
    
    def _display_results(self, report: SkillReport):
        """Display skill preservation results in rich format"""
        
        # Create comparison table
        table = Table(title="🧠 Skill Preservation Analysis")
        table.add_column("Domain", style="cyan", no_wrap=True)
        table.add_column("Before", justify="right", style="green")
        table.add_column("After", justify="right", style="blue")
        table.add_column("Change", justify="right")
        table.add_column("Status", justify="center")
        
        for score in report.skill_scores:
            # Format change with color
            change_str = f"{score.degradation_percent:+.1f}%"
            if score.status == "degraded":
                change_color = "red"
                status_emoji = "🔴"
            elif score.status == "improved":
                change_color = "green"
                status_emoji = "🟢"
            else:
                change_color = "yellow"
                status_emoji = "🟡"
            
            table.add_row(
                score.domain.title(),
                f"{score.score_before:.1%}",
                f"{score.score_after:.1%}",
                f"[{change_color}]{change_str}[/{change_color}]",
                f"{status_emoji} {score.status}"
            )
        
        console.print(table)
        
        # Overall verdict
        verdict_colors = {
            "safe": "green",
            "caution": "yellow", 
            "critical": "red"
        }
        verdict_emojis = {
            "safe": "✅",
            "caution": "⚠️",
            "critical": "🚨"
        }
        
        console.print(Panel.fit(
            f"{verdict_emojis[report.verdict]} [bold {verdict_colors[report.verdict]}]"
            f"{report.verdict.upper()}[/bold {verdict_colors[report.verdict]}]\n"
            f"Overall degradation: {report.overall_degradation:.1f}%",
            border_style=verdict_colors[report.verdict]
        ))
        
        # Recommendations
        if report.recommendations:
            console.print("\n[bold]🎯 Recommendations:[/bold]")
            for rec in report.recommendations:
                console.print(f"  • {rec}")
    
    def _save_report(self, report: SkillReport, output_dir: str):
        """Save detailed skill preservation report"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON report
        json_path = output_path / "skill_preservation_report.json"
        with open(json_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        # Save markdown report
        md_path = output_path / "skill_preservation_report.md"
        self._generate_markdown_report(report, md_path)
        
        console.print(f"\n📄 Detailed reports saved:")
        console.print(f"  • JSON: {json_path}")
        console.print(f"  • Markdown: {md_path}")
    
    def _generate_markdown_report(self, report: SkillReport, output_path: Path):
        """Generate markdown skill preservation report"""
        
        verdict_emojis = {
            "safe": "✅",
            "caution": "⚠️", 
            "critical": "🚨"
        }
        
        md_content = f"""# 🧠 Skill Preservation Report

## Summary
- **Before Model**: `{report.model_before}`
- **After Model**: `{report.model_after}`
- **Overall Degradation**: {report.overall_degradation:.1f}%
- **Verdict**: {verdict_emojis[report.verdict]} **{report.verdict.upper()}**

## Skill Domain Analysis

| Domain | Before | After | Change | Status |
|--------|--------|-------|--------|--------|
"""
        
        for score in report.skill_scores:
            status_emoji = {"degraded": "🔴", "improved": "🟢", "preserved": "🟡"}[score.status]
            md_content += f"| {score.domain.title()} | {score.score_before:.1%} | {score.score_after:.1%} | {score.degradation_percent:+.1f}% | {status_emoji} {score.status} |\n"
        
        md_content += f"""
## Recommendations

"""
        for rec in report.recommendations:
            md_content += f"- {rec}\n"
        
        md_content += f"""
## Methodology

This analysis used the Oumi evaluation framework to compare model performance across key skill domains:

- **Math**: GSM8K-style mathematical reasoning problems
- **Reasoning**: Logical consistency and inference tasks  
- **Writing**: Creative writing and fluency assessment
- **Factual**: Knowledge recall and factual accuracy

Each domain was evaluated using custom evaluation functions registered with Oumi's `@register_evaluation_function` decorator.

---
*Generated by Oumi Model Hospital - Neurologist Agent*
"""
        
        with open(output_path, 'w') as f:
            f.write(md_content)


def main():
    """CLI entry point for neurologist"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🧠 Neurologist - Check skill preservation")
    parser.add_argument("--before", required=True, help="Original model path/ID")
    parser.add_argument("--after", required=True, help="Treated model path/ID")
    parser.add_argument("--output", help="Output directory for reports")
    parser.add_argument("--threshold", type=float, default=10.0, 
                       help="Degradation threshold percentage (default: 10.0)")
    
    args = parser.parse_args()
    
    neurologist = Neurologist(degradation_threshold=args.threshold)
    report = neurologist.check_skill_preservation(
        args.before, 
        args.after, 
        args.output
    )
    
    # Exit with appropriate code
    exit_codes = {"safe": 0, "caution": 1, "critical": 2}
    exit(exit_codes[report.verdict])


if __name__ == "__main__":
    main()