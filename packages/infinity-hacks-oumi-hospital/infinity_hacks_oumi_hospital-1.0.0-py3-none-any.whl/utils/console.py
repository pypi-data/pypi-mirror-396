"""
🏥 Oumi Hospital - Rich Console Theme

Hospital-themed Rich console with custom colors, spinners, and progress displays.
"""

from rich.console import Console
from rich.theme import Theme
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn, 
    BarColumn, 
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn
)
from rich.spinner import Spinner
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from typing import Optional, Dict, Any

# Hospital color scheme
HOSPITAL_THEME = Theme({
    # Primary hospital colors
    "hospital.primary": "#2E8B57",      # Sea Green (medical green)
    "hospital.secondary": "#4682B4",    # Steel Blue (trust, reliability)
    "hospital.accent": "#DC143C",       # Crimson (urgency, alerts)
    "hospital.success": "#32CD32",      # Lime Green (success, healthy)
    "hospital.warning": "#FF8C00",      # Dark Orange (warnings)
    "hospital.error": "#FF4500",        # Red Orange (errors, critical)
    "hospital.info": "#4169E1",         # Royal Blue (information)
    
    # Severity colors
    "severity.critical": "bold red",
    "severity.high": "bold orange3", 
    "severity.moderate": "bold yellow",
    "severity.low": "bold green",
    
    # Agent colors
    "agent.diagnostician": "#4682B4",   # Steel Blue
    "agent.pharmacist": "#32CD32",      # Lime Green  
    "agent.neurologist": "#9370DB",     # Medium Purple
    "agent.surgeon": "#DC143C",         # Crimson
    
    # Status colors
    "status.scanning": "cyan",
    "status.processing": "yellow", 
    "status.complete": "green",
    "status.failed": "red",
    
    # UI elements
    "header": "bold #2E8B57",
    "subheader": "#4682B4",
    "emphasis": "bold #DC143C",
    "success": "bold #32CD32",
    "warning": "bold #FF8C00", 
    "error": "bold #FF4500",
    "info": "#4169E1"
})

# Custom hospital spinners
HOSPITAL_SPINNERS = {
    "heartbeat": Spinner("hearts", text="💓", style="red"),
    "pulse": Spinner("dots12", text="🫀", style="hospital.primary"),
    "scan": Spinner("line", text="🔍", style="agent.diagnostician"),
    "synthesis": Spinner("bouncingBall", text="💊", style="agent.pharmacist"),
    "analysis": Spinner("dots", text="🧠", style="agent.neurologist"), 
    "surgery": Spinner("arc", text="🔧", style="agent.surgeon"),
    "healing": Spinner("star", text="✨", style="hospital.success")
}

class HospitalConsole:
    """Rich console with hospital theme and custom methods"""
    
    def __init__(self):
        self.console = Console(theme=HOSPITAL_THEME, width=120)
        self._current_progress: Optional[Progress] = None
    
    def print_header(self, title: str, subtitle: Optional[str] = None):
        """Print hospital header with logo"""
        header_text = Text()
        header_text.append("🏥 ", style="bold red")
        header_text.append("OUMI MODEL HOSPITAL", style="header")
        
        if subtitle:
            header_text.append(f"\n{subtitle}", style="subheader")
        
        panel = Panel(
            Align.center(header_text),
            border_style="hospital.primary",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()
    
    def print_agent_banner(self, agent_name: str, description: str, emoji: str):
        """Print agent introduction banner"""
        agent_text = Text()
        agent_text.append(f"{emoji} ", style="bold")
        agent_text.append(f"Agent: {agent_name}", style=f"agent.{agent_name.lower()}")
        agent_text.append(f"\n{description}", style="info")
        
        self.console.print(Panel(agent_text, border_style=f"agent.{agent_name.lower()}"))
    
    def print_diagnosis_result(self, result: Dict[str, Any]):
        """Print diagnosis results in a formatted table"""
        table = Table(title="🔍 Diagnosis Results", border_style="agent.diagnostician")
        
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")
        table.add_column("Status", justify="center")
        
        # Failure rate with severity color
        failure_rate = result.get("failure_rate", 0.0)
        severity = self._get_severity_from_rate(failure_rate)
        severity_style = f"severity.{severity.lower()}"
        
        table.add_row(
            "Failure Rate",
            f"{failure_rate:.1%}",
            Text(severity, style=severity_style)
        )
        
        table.add_row(
            "Total Tests", 
            str(result.get("total_tests", 0)),
            "📊"
        )
        
        table.add_row(
            "Failed Tests",
            str(result.get("failed_tests", 0)), 
            "❌" if result.get("failed_tests", 0) > 0 else "✅"
        )
        
        self.console.print(table)
    
    def print_skill_preservation(self, results: Dict[str, Dict[str, float]]):
        """Print skill preservation results"""
        table = Table(title="🧠 Skill Preservation Check", border_style="agent.neurologist")
        
        table.add_column("Skill Domain", style="bold")
        table.add_column("Before", justify="right")
        table.add_column("After", justify="right") 
        table.add_column("Change", justify="right")
        table.add_column("Status", justify="center")
        
        for domain, scores in results.items():
            before = scores.get("before", 0.0)
            after = scores.get("after", 0.0)
            change = after - before
            
            # Determine status
            if change >= -0.05:  # Less than 5% degradation
                status = "✅"
                change_style = "success"
            elif change >= -0.1:  # 5-10% degradation
                status = "⚠️"
                change_style = "warning"
            else:  # More than 10% degradation
                status = "❌"
                change_style = "error"
            
            table.add_row(
                domain.title(),
                f"{before:.1%}",
                f"{after:.1%}",
                Text(f"{change:+.1%}", style=change_style),
                status
            )
        
        self.console.print(table)
    
    def print_recipe_summary(self, config: Dict[str, Any]):
        """Print training recipe summary"""
        table = Table(title="🔧 Treatment Recipe", border_style="agent.surgeon")
        
        table.add_column("Parameter", style="bold")
        table.add_column("Value", justify="right")
        table.add_column("Reason", style="info")
        
        # Extract key parameters
        training = config.get("training", {})
        peft = config.get("peft", {})
        
        table.add_row(
            "Learning Rate",
            f"{training.get('learning_rate', 'N/A')}",
            "Severity-adjusted"
        )
        
        table.add_row(
            "LoRA Rank", 
            str(peft.get("lora_r", "N/A")),
            "Skill-preservation safe"
        )
        
        table.add_row(
            "Epochs",
            str(training.get("num_train_epochs", "N/A")),
            "Optimal for severity"
        )
        
        self.console.print(table)
    
    def create_progress(self, description: str, spinner_type: str = "pulse") -> Progress:
        """Create a hospital-themed progress display"""
        spinner = HOSPITAL_SPINNERS.get(spinner_type, HOSPITAL_SPINNERS["pulse"])
        
        progress = Progress(
            SpinnerColumn(spinner=spinner.name, style=spinner.style),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console
        )
        
        self._current_progress = progress
        return progress
    
    def print_success(self, message: str):
        """Print success message"""
        self.console.print(f"✅ {message}", style="success")
    
    def print_warning(self, message: str):
        """Print warning message"""
        self.console.print(f"⚠️ {message}", style="warning")
    
    def print_error(self, message: str):
        """Print error message"""
        self.console.print(f"❌ {message}", style="error")
    
    def print_info(self, message: str):
        """Print info message"""
        self.console.print(f"ℹ️ {message}", style="info")
    
    def print_step(self, step: int, total: int, description: str):
        """Print step progress"""
        self.console.print(f"[{step}/{total}] {description}", style="info")
    
    def _get_severity_from_rate(self, failure_rate: float) -> str:
        """Get severity classification from failure rate"""
        if failure_rate >= 0.7:
            return "CRITICAL"
        elif failure_rate >= 0.5:
            return "HIGH"
        elif failure_rate >= 0.3:
            return "MODERATE"
        else:
            return "LOW"
    
    def print_demo_banner(self):
        """Print demo mode banner"""
        demo_text = Text()
        demo_text.append("🎬 ", style="bold yellow")
        demo_text.append("DEMO MODE", style="bold yellow")
        demo_text.append("\nSlower output for presentation", style="yellow")
        
        panel = Panel(
            Align.center(demo_text),
            border_style="yellow",
            padding=(0, 2)
        )
        self.console.print(panel)
    
    def print_community_message(self):
        """Print community contribution message"""
        community_text = Text()
        community_text.append("🌐 ", style="bold hospital.primary")
        community_text.append("COMMUNITY IMPACT", style="header")
        community_text.append("\nRecipes will be shared with the Oumi community", style="info")
        community_text.append("\nHelping heal models everywhere! 🌍", style="success")
        
        panel = Panel(
            Align.center(community_text),
            border_style="hospital.primary",
            padding=(1, 2)
        )
        self.console.print(panel)


# Global console instance
hospital_console = HospitalConsole()

# Convenience functions
def print_header(title: str, subtitle: Optional[str] = None):
    hospital_console.print_header(title, subtitle)

def print_agent_banner(agent_name: str, description: str, emoji: str):
    hospital_console.print_agent_banner(agent_name, description, emoji)

def print_success(message: str):
    hospital_console.print_success(message)

def print_warning(message: str):
    hospital_console.print_warning(message)

def print_error(message: str):
    hospital_console.print_error(message)

def print_info(message: str):
    hospital_console.print_info(message)

__all__ = [
    "HospitalConsole",
    "hospital_console", 
    "HOSPITAL_THEME",
    "HOSPITAL_SPINNERS",
    "print_header",
    "print_agent_banner",
    "print_success",
    "print_warning", 
    "print_error",
    "print_info"
]