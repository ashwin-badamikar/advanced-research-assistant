"""
Main Application - Advanced Research Assistant System
Entry point for the agentic research system
"""
import os
import sys
from typing import Dict, Any
from config.settings import settings
from workflows.research_workflow import ResearchWorkflow, WorkflowUtils

def main():
    """Main application entry point"""
    print("🤖 Advanced Research Assistant System")
    print("=" * 50)
    
    try:
        # Validate configuration
        settings.validate_config()
        print("✅ Configuration validated successfully")
        
        # Create output directories
        settings.create_directories()
        print(f"✅ Output directories created: {settings.OUTPUT_DIR}")
        
        # Initialize workflow
        workflow = ResearchWorkflow()
        print("✅ Research workflow initialized")
        
        # Interactive mode
        if len(sys.argv) == 1:
            run_interactive_mode(workflow)
        else:
            # Command line mode
            run_command_line_mode(sys.argv[1:], workflow)
            
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}")
        print("\nPlease check your configuration and try again.")
        print("\nCommon issues:")
        print("- Make sure your API keys are set in the .env file")
        print("- Ensure all required dependencies are installed")
        return 1
    
    return 0

def run_interactive_mode(workflow: ResearchWorkflow):
    """Run the application in interactive mode"""
    print("\n🎯 Interactive Research Mode")
    print("Type 'help' for available commands or 'quit' to exit")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'help':
                show_help()
            elif user_input.lower() == 'formats':
                show_formats(workflow)
            elif user_input.lower() == 'examples':
                show_examples()
            elif user_input.lower() == 'status':
                show_status(workflow)
            elif user_input.lower() == 'test':
                test_system_components()
            elif user_input.startswith('research:'):
                # Quick research command
                query = user_input[9:].strip()
                if query:
                    run_quick_research(workflow, query)
                else:
                    print("❌ Please provide a research query after 'research:'")
            else:
                # Full research mode
                if user_input:
                    run_full_research_mode(workflow, user_input)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("Type 'help' for available commands")

def run_command_line_mode(args: list, workflow: ResearchWorkflow):
    """Run the application in command line mode"""
    if len(args) < 1:
        print("❌ Please provide a research query")
        return
    
    research_query = " ".join(args)
    print(f"\n🔍 Starting research: {research_query}")
    
    # Use default settings for command line mode
    results = workflow.execute_research_project(
        research_query=research_query,
        output_format="comprehensive_report",
        target_audience="professional",
        depth_level="detailed"
    )
    
    display_results(results)

def run_quick_research(workflow: ResearchWorkflow, query: str):
    """Run a quick research with default settings"""
    print(f"\n🚀 Quick Research: {query}")
    
    try:
        results = workflow.execute_research_project(
            research_query=query,
            output_format="executive_briefing",
            target_audience="professional", 
            depth_level="detailed"
        )
        
        display_results(results)
        
    except Exception as e:
        print(f"❌ Research failed: {str(e)}")
        print("This might be due to:")
        print("- Network connectivity issues")
        print("- API rate limits")
        print("- Invalid API keys")

def run_full_research_mode(workflow: ResearchWorkflow, initial_query: str = ""):
    """Run full research mode with user customization"""
    print("\n📊 Full Research Mode")
    
    # Get research query
    if initial_query:
        research_query = initial_query
        print(f"Research Query: {research_query}")
    else:
        research_query = input("Enter your research query: ").strip()
    
    if not research_query:
        print("❌ Research query is required")
        return
    
    # Get output format
    print(f"\nAvailable formats: {', '.join(workflow.list_available_formats())}")
    output_format = input("Output format (press Enter for 'comprehensive_report'): ").strip()
    if not output_format:
        output_format = "comprehensive_report"
    
    # Get target audience
    print(f"\nAvailable audiences: {', '.join(workflow.list_target_audiences())}")
    target_audience = input("Target audience (press Enter for 'professional'): ").strip()
    if not target_audience:
        target_audience = "professional"
    
    # Get depth level
    print(f"\nAvailable depth levels: {', '.join(workflow.list_depth_levels())}")
    depth_level = input("Depth level (press Enter for 'detailed'): ").strip()
    if not depth_level:
        depth_level = "detailed"
    
    # Validate inputs
    validation = WorkflowUtils.validate_inputs(research_query, output_format, target_audience, depth_level)
    if not validation["valid"]:
        print("❌ Invalid inputs:")
        for error in validation["errors"]:
            print(f"  - {error}")
        return
    
    # Show estimation
    duration_estimate = WorkflowUtils.estimate_duration(depth_level, output_format)
    print(f"\n⏱️  Estimated duration: {duration_estimate}")
    
    # Confirm execution
    confirm = input("\nProceed with research? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Research cancelled.")
        return
    
    # Execute research
    try:
        results = workflow.execute_research_project(
            research_query=research_query,
            output_format=output_format,
            target_audience=target_audience,
            depth_level=depth_level
        )
        
        display_results(results)
        
    except Exception as e:
        print(f"❌ Research failed: {str(e)}")
        print("Please check your configuration and try again.")

def display_results(results: Dict[str, Any]):
    """Display research results"""
    print("\n" + "=" * 60)
    print("📋 RESEARCH RESULTS")
    print("=" * 60)
    
    if results.get("status") == "success":
        print("✅ Research completed successfully!")
        
        metadata = results.get("metadata", {})
        print(f"\n📊 Project Details:")
        print(f"  - Project ID: {metadata.get('project_id', 'N/A')}")
        print(f"  - Duration: {metadata.get('workflow_duration', 'N/A')}")
        print(f"  - Output Directory: {results.get('output_directory', 'N/A')}")
        
        if "summary_file" in results:
            print(f"  - Summary File: {results['summary_file']}")
        
        # Show preview of results
        final_output = results.get("final_output", "")
        if final_output:
            print(f"\n📄 Output Preview:")
            preview = final_output[:500] + "..." if len(final_output) > 500 else final_output
            print(preview)
            
        # Show file locations
        if os.path.exists(settings.OUTPUT_DIR):
            files = os.listdir(settings.OUTPUT_DIR)
            if files:
                print(f"\n📁 Generated Files:")
                for file in files:
                    print(f"  - {file}")
        
    else:
        print("❌ Research failed!")
        error = results.get("error", "Unknown error occurred")
        print(f"Error: {error}")

def test_system_components():
    """Test system components"""
    print("\n🧪 Testing System Components...")
    
    # Test configuration
    try:
        settings.validate_config()
        print("✅ Configuration: Valid")
    except Exception as e:
        print(f"❌ Configuration: {str(e)}")
    
    # Test workflow initialization
    try:
        workflow = ResearchWorkflow()
        print("✅ Workflow: Initialized successfully")
    except Exception as e:
        print(f"❌ Workflow: {str(e)}")
    
    # Test custom tools
    try:
        from tools.citation_manager import CitationManager
        from tools.quality_assessor import QualityAssessor
        
        citation_mgr = CitationManager()
        quality_assessor = QualityAssessor()
        
        # Test citation manager
        result = citation_mgr._run("add", title="Test Article", url="https://example.com")
        if "successfully" in result:
            print("✅ Citation Manager: Working")
        else:
            print(f"⚠️ Citation Manager: {result}")
        
        # Test quality assessor
        result = quality_assessor._run("assess", content="This is a test content for quality assessment.")
        if "Quality Assessment Results" in result:
            print("✅ Quality Assessor: Working")
        else:
            print(f"⚠️ Quality Assessor: {result}")
            
    except Exception as e:
        print(f"❌ Custom Tools: {str(e)}")

def show_help():
    """Show help information"""
    help_text = """
🤖 Advanced Research Assistant - Available Commands:

QUICK COMMANDS:
  research: <query>     - Quick research with default settings
  help                  - Show this help message
  formats              - Show available output formats
  examples             - Show example research queries
  status               - Show current workflow status
  test                 - Test system components
  quit/exit/q          - Exit the application

FULL RESEARCH MODE:
  Simply type your research query and press Enter to start the 
  interactive configuration process.

EXAMPLES:
  research: artificial intelligence trends 2024
  research: sustainable energy solutions for manufacturing
  research: remote work productivity best practices

TROUBLESHOOTING:
  - Use 'test' command to check system components
  - Ensure API keys are set in .env file
  - Check internet connectivity for web searches
"""
    print(help_text)

def show_formats(workflow: ResearchWorkflow):
    """Show available formats and options"""
    print("\n📋 Available Options:")
    print(f"Output Formats: {', '.join(workflow.list_available_formats())}")
    print(f"Target Audiences: {', '.join(workflow.list_target_audiences())}")
    print(f"Depth Levels: {', '.join(workflow.list_depth_levels())}")

def show_examples():
    """Show example research queries"""
    examples = [
        "Artificial intelligence trends in healthcare 2024",
        "Sustainable manufacturing practices in automotive industry", 
        "Remote work impact on employee productivity and satisfaction",
        "Blockchain applications in supply chain management",
        "Climate change adaptation strategies for coastal cities",
        "Digital transformation challenges in small businesses",
        "Cybersecurity best practices for financial institutions",
        "Renewable energy adoption in developing countries"
    ]
    
    print("\n💡 Example Research Queries:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")

def show_status(workflow: ResearchWorkflow):
    """Show current workflow status"""
    status = workflow.get_workflow_status()
    print(f"\n📊 Workflow Status: {status.get('status', 'Unknown')}")
    
    if status.get('current_task'):
        print(f"Current Task: {status['current_task']}")
    
    if status.get('completed_tasks'):
        print(f"Completed Tasks: {len(status['completed_tasks'])}")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)