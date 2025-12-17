"""
Command Line Interface for Oumi Hospital
"""

import click
from rich.console import Console
from pathlib import Path

from .core import OumiHospital

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def main():
    """
    🏥 Oumi Hospital - LLM-Powered Multi-Agent AI Model Repair System
    
    Revolutionary autonomous diagnosis, treatment, and healing of unsafe AI models.
    """
    pass


@main.command()
@click.argument('model_path', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output path for healed model')
@click.option('--groq-key', help='Groq API key for LLM coordination')
def heal(model_path, output, groq_key):
    """
    Heal an unsafe AI model using multi-agent coordination
    
    MODEL_PATH: Path to the unsafe model to heal
    """
    console.print("🏥 [bold cyan]Oumi Hospital - AI Model Repair[/bold cyan]")
    
    hospital = OumiHospital(groq_api_key=groq_key)
    
    try:
        healed_path = hospital.heal_model(model_path, output)
        console.print(f"\n🎉 [bold green]Success![/bold green] Healed model saved to: {healed_path}")
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Error:[/bold red] {e}")
        raise click.ClickException(str(e))


@main.command()
@click.argument('model_path', type=click.Path(exists=True))
def diagnose(model_path):
    """
    Run comprehensive diagnosis on a model
    
    MODEL_PATH: Path to the model to diagnose
    """
    console.print("🔍 [bold cyan]Running Model Diagnosis[/bold cyan]")
    
    hospital = OumiHospital()
    
    try:
        diagnosis = hospital.agents["diagnostician"].diagnose(model_path)
        
        console.print("\n📊 [bold]Diagnosis Results:[/bold]")
        console.print(f"   Safety Score: {diagnosis.get('safety_score', 'N/A')}")
        console.print(f"   Risk Level: {diagnosis.get('risk_level', 'N/A')}")
        console.print(f"   Recommended Treatment: {diagnosis.get('treatment', 'N/A')}")
        
    except Exception as e:
        console.print(f"\n❌ [bold red]Error:[/bold red] {e}")
        raise click.ClickException(str(e))


@main.command()
def demo():
    """
    Run the interactive Oumi Hospital demo
    """
    console.print("🎬 [bold cyan]Starting Oumi Hospital Demo[/bold cyan]")
    
    hospital = OumiHospital()
    hospital.quick_demo()


@main.command()
def status():
    """
    Show status of all agents
    """
    console.print("🏥 [bold cyan]Oumi Hospital Agent Status[/bold cyan]")
    
    hospital = OumiHospital()
    status = hospital.get_agent_status()
    
    console.print("\n📋 [bold]Agent Status:[/bold]")
    for name, info in status.items():
        status_icon = "✅" if info["initialized"] else "❌"
        console.print(f"   {status_icon} {name.title()}: {info['type']}")


@main.command()
@click.option('--quick', is_flag=True, help='Run demo without pauses')
def hackathon_demo(quick):
    """
    Run the full hackathon demonstration
    """
    console.print("🎬 [bold cyan]Hackathon Live Demo - Oumi Hospital[/bold cyan]")
    
    try:
        # Import and run the hackathon demo
        import subprocess
        import sys
        
        demo_script = Path(__file__).parent.parent.parent / "HACKATHON_LIVE_DEMO.py"
        
        if demo_script.exists():
            cmd = [sys.executable, str(demo_script)]
            if quick:
                cmd.append("--quick")
            subprocess.run(cmd)
        else:
            console.print("❌ Hackathon demo script not found")
            
    except Exception as e:
        console.print(f"❌ [bold red]Demo error:[/bold red] {e}")


if __name__ == "__main__":
    main()