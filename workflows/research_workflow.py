"""
Research Workflow - Orchestrates the multi-agent research system
"""
from crewai import Crew, Task, Process
from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime
from config.settings import settings
from agents.research_agent import ResearchAgentConfig
from agents.analysis_agent import AnalysisAgentConfig
from agents.content_agent import ContentAgentConfig

class ResearchWorkflow:
    """
    Main workflow orchestrator for the Advanced Research Assistant System
    Coordinates research, analysis, and content creation agents
    """
    
    def __init__(self):
        """Initialize the research workflow"""
        self.research_agent = ResearchAgentConfig.create_research_agent()
        self.analysis_agent = AnalysisAgentConfig.create_analysis_agent()
        self.content_agent = ContentAgentConfig.create_content_agent()
        
        # Ensure output directories exist
        settings.create_directories()
        
        # Workflow state tracking
        self.workflow_state = {
            "status": "initialized",
            "current_task": None,
            "completed_tasks": [],
            "results": {},
            "errors": []
        }
    
    def execute_research_project(self, 
                                research_query: str,
                                output_format: str = "comprehensive_report",
                                target_audience: str = "professional",
                                depth_level: str = "detailed") -> Dict[str, Any]:
        """
        Execute a complete research project
        
        Args:
            research_query: The main research question or topic
            output_format: Type of output (report, presentation, summary, briefing)
            target_audience: Target audience (academic, professional, general, executive)
            depth_level: Level of detail (overview, detailed, comprehensive, expert)
        
        Returns:
            Dictionary containing results and metadata
        """
        try:
            # Update workflow state
            self.workflow_state["status"] = "running"
            self.workflow_state["start_time"] = datetime.now().isoformat()
            
            # Create tasks
            tasks = self._create_research_tasks(research_query, output_format, target_audience, depth_level)
            
            # Create crew
            crew = Crew(
                agents=[self.research_agent, self.analysis_agent, self.content_agent],
                tasks=tasks,
                process=Process.sequential,
                verbose=True,
                memory=True,
                full_output=True
            )
            
            # Execute workflow
            print(f"🚀 Starting research project: {research_query}")
            result = crew.kickoff()
            
            # Process results
            final_results = self._process_workflow_results(result, research_query, output_format)
            
            # Update workflow state
            self.workflow_state["status"] = "completed"
            self.workflow_state["end_time"] = datetime.now().isoformat()
            self.workflow_state["results"] = final_results
            
            return final_results
            
        except Exception as e:
            self.workflow_state["status"] = "error"
            self.workflow_state["errors"].append(str(e))
            print(f"❌ Error in research workflow: {str(e)}")
            return {"error": str(e), "status": "failed"}
    
    def _create_research_tasks(self, 
                              research_query: str,
                              output_format: str,
                              target_audience: str,
                              depth_level: str) -> List[Task]:
        """Create the sequence of tasks for the research workflow"""
        
        # Task 1: Research and Information Gathering
        research_task = Task(
            description=f"""
            Conduct comprehensive research on: "{research_query}"
            
            REQUIREMENTS:
            - Depth Level: {depth_level}
            - Target Audience: {target_audience}
            - Use multiple reliable sources (minimum 8-10 sources)
            - Prioritize recent information (last 2-3 years when possible)
            - Include both quantitative and qualitative data
            - Assess source credibility using the Quality Assessor tool
            - Document all sources using the Citation Manager tool
            
            RESEARCH AREAS TO COVER:
            1. Current state and recent developments
            2. Key trends and patterns
            3. Major players and stakeholders
            4. Challenges and opportunities
            5. Future outlook and predictions
            6. Best practices and lessons learned
            7. Comparative analysis where relevant
            8. Statistical data and metrics
            
            DELIVERABLES:
            - Comprehensive research findings organized by topic
            - Source credibility assessments for all materials
            - Properly formatted citations for all sources
            - Identification of any research gaps or limitations
            - Raw data and supporting evidence
            
            {ResearchAgentConfig.get_research_instructions()}
            """,
            agent=self.research_agent,
            expected_output="""
            A comprehensive research report containing:
            1. Executive summary of research findings
            2. Detailed findings organized by key themes
            3. Source analysis and credibility assessments
            4. Data tables and key statistics
            5. Complete bibliography with quality scores
            6. Research limitations and gaps identified
            """
        )
        
        # Task 2: Analysis and Insight Generation
        analysis_task = Task(
            description=f"""
            Analyze the research findings and generate strategic insights for: "{research_query}"
            
            REQUIREMENTS:
            - Build upon the research findings from the previous task
            - Depth Level: {depth_level}
            - Target Audience: {target_audience}
            - Identify patterns, trends, and correlations
            - Generate actionable insights and recommendations
            - Assess risks and opportunities
            - Provide strategic implications
            
            ANALYSIS AREAS:
            1. Trend Analysis: Identify key trends and their implications
            2. Comparative Analysis: Compare different approaches, solutions, or options
            3. Gap Analysis: Identify missing elements or opportunities
            4. Risk Assessment: Evaluate potential risks and mitigation strategies
            5. Impact Analysis: Assess potential impacts of different scenarios
            6. Strategic Analysis: Develop strategic recommendations
            7. Quantitative Analysis: Analyze numerical data and statistics
            8. Qualitative Analysis: Synthesize themes and patterns from qualitative data
            
            DELIVERABLES:
            - Key insights ranked by importance and impact
            - Trend analysis with future implications
            - Strategic recommendations with implementation guidance
            - Risk assessment with mitigation strategies
            - Quantitative analysis results
            - Visual data summaries preparation
            
            {AnalysisAgentConfig.get_analysis_instructions()}
            """,
            agent=self.analysis_agent,
            expected_output="""
            A comprehensive analysis report containing:
            1. Executive summary of key insights
            2. Detailed trend analysis and implications
            3. Strategic recommendations prioritized by impact
            4. Risk assessment and mitigation strategies
            5. Comparative analysis results
            6. Quantitative findings and statistical analysis
            7. Implementation roadmap for recommendations
            """
        )
        
        # Task 3: Content Creation and Presentation
        content_task = Task(
            description=f"""
            Create high-quality content based on research and analysis for: "{research_query}"
            
            REQUIREMENTS:
            - Output Format: {output_format}
            - Target Audience: {target_audience}
            - Depth Level: {depth_level}
            - Integrate research findings and analytical insights
            - Use proper citations and formatting
            - Ensure content quality and readability
            - Save final content to output directory
            
            CONTENT SPECIFICATIONS:
            
            {self._get_output_format_specifications(output_format, target_audience, depth_level)}
            
            QUALITY REQUIREMENTS:
            - Professional writing style appropriate for {target_audience} audience
            - Clear, logical structure with smooth transitions
            - Proper grammar, spelling, and formatting
            - Comprehensive citations using consistent style
            - Visual elements suggested where appropriate
            - Executive summary for all formats
            - Actionable recommendations included
            
            USE TOOLS:
            - Citation Manager: For all source references and bibliography
            - Quality Assessor: To evaluate content quality before finalization
            - File Write Tool: To save the final content to {settings.OUTPUT_DIR}
            
            {ContentAgentConfig.get_content_instructions()}
            """,
            agent=self.content_agent,
            expected_output=f"""
            A complete {output_format} tailored for {target_audience} audience containing:
            1. Executive summary with key findings and recommendations
            2. Well-structured main content with clear sections
            3. Integrated research findings and analytical insights
            4. Professional formatting and presentation
            5. Complete bibliography with proper citations
            6. Quality assessment report
            7. File saved to output directory with appropriate naming
            """
        )
        
        return [research_task, analysis_task, content_task]
    
    def _get_output_format_specifications(self, output_format: str, target_audience: str, depth_level: str) -> str:
        """Get specific requirements for different output formats"""
        
        specifications = {
            "comprehensive_report": f"""
            CREATE A COMPREHENSIVE RESEARCH REPORT:
            - Length: 3000-5000 words (for detailed depth)
            - Structure: Title page, executive summary, table of contents, introduction, 
              methodology, findings, analysis, recommendations, conclusion, references
            - Include data tables, charts suggestions, and appendices
            - Professional academic/business formatting
            """,
            
            "executive_briefing": f"""
            CREATE AN EXECUTIVE BRIEFING:
            - Length: 1000-1500 words
            - Structure: Executive summary, key findings, strategic implications, 
              recommendations, next steps
            - Focus on high-level insights and strategic implications
            - Include key metrics and performance indicators
            """,
            
            "presentation": f"""
            CREATE PRESENTATION CONTENT:
            - Structure: 15-20 slides worth of content
            - Include slide titles, bullet points, and speaker notes
            - Visual elements suggestions for each slide
            - Focus on key messages and actionable insights
            """,
            
            "technical_summary": f"""
            CREATE A TECHNICAL SUMMARY:
            - Length: 2000-3000 words
            - Structure: Abstract, introduction, technical findings, methodology,
              results, discussion, conclusion, technical appendices
            - Include detailed technical analysis and data
            - Appropriate for expert/technical audience
            """,
            
            "policy_brief": f"""
            CREATE A POLICY BRIEF:
            - Length: 1500-2000 words
            - Structure: Executive summary, issue background, policy analysis,
              recommendations, implementation considerations
            - Focus on policy implications and recommendations
            - Include cost-benefit analysis where relevant
            """
        }
        
        return specifications.get(output_format, specifications["comprehensive_report"])
    
    def _process_workflow_results(self, crew_result, research_query: str, output_format: str) -> Dict[str, Any]:
        """Process and organize the workflow results"""
        
        # Generate unique project ID and timestamp
        project_id = self._generate_project_id(research_query)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create project metadata
        metadata = {
            "project_id": project_id,
            "timestamp": timestamp,
            "research_query": research_query,
            "output_format": output_format,
            "workflow_duration": self._calculate_duration(),
            "agents_used": ["research_agent", "analysis_agent", "content_agent"],
            "tools_used": ["serper_search", "citation_manager", "quality_assessor", "file_operations"]
        }
        
        # Extract results from crew execution
        try:
            if hasattr(crew_result, 'raw'):
                final_output = crew_result.raw
            else:
                final_output = str(crew_result)
            
            # Save workflow summary
            summary_filename = f"workflow_summary_{timestamp}.json"
            summary_path = os.path.join(settings.OUTPUT_DIR, summary_filename)
            
            workflow_summary = {
                "metadata": metadata,
                "workflow_state": self.workflow_state,
                "final_output_preview": final_output[:500] + "..." if len(final_output) > 500 else final_output
            }
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_summary, f, indent=2, ensure_ascii=False)
            
            results = {
                "status": "success",
                "metadata": metadata,
                "final_output": final_output,
                "summary_file": summary_path,
                "output_directory": settings.OUTPUT_DIR
            }
            
            return results
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "metadata": metadata
            }
    
    def _generate_project_id(self, research_query: str) -> str:
        """Generate a unique project ID"""
        import hashlib
        query_hash = hashlib.md5(research_query.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"research_{timestamp}_{query_hash}"
    
    def _calculate_duration(self) -> str:
        """Calculate workflow duration"""
        if "start_time" in self.workflow_state and "end_time" in self.workflow_state:
            start = datetime.fromisoformat(self.workflow_state["start_time"])
            end = datetime.fromisoformat(self.workflow_state["end_time"])
            duration = end - start
            return str(duration)
        return "unknown"
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return self.workflow_state.copy()
    
    def list_available_formats(self) -> List[str]:
        """List available output formats"""
        return [
            "comprehensive_report",
            "executive_briefing", 
            "presentation",
            "technical_summary",
            "policy_brief"
        ]
    
    def list_target_audiences(self) -> List[str]:
        """List available target audiences"""
        return [
            "academic",
            "professional", 
            "executive",
            "technical",
            "general"
        ]
    
    def list_depth_levels(self) -> List[str]:
        """List available depth levels"""
        return [
            "overview",
            "detailed",
            "comprehensive", 
            "expert"
        ]

# Workflow utility functions
class WorkflowUtils:
    """Utility functions for workflow management"""
    
    @staticmethod
    def validate_inputs(research_query: str, output_format: str, target_audience: str, depth_level: str) -> Dict[str, Any]:
        """Validate workflow inputs"""
        workflow = ResearchWorkflow()
        
        errors = []
        
        if not research_query or len(research_query.strip()) < 10:
            errors.append("Research query must be at least 10 characters long")
        
        if output_format not in workflow.list_available_formats():
            errors.append(f"Invalid output format. Available: {workflow.list_available_formats()}")
        
        if target_audience not in workflow.list_target_audiences():
            errors.append(f"Invalid target audience. Available: {workflow.list_target_audiences()}")
        
        if depth_level not in workflow.list_depth_levels():
            errors.append(f"Invalid depth level. Available: {workflow.list_depth_levels()}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def estimate_duration(depth_level: str, output_format: str) -> str:
        """Estimate workflow duration"""
        base_times = {
            "overview": 300,      # 5 minutes
            "detailed": 600,      # 10 minutes  
            "comprehensive": 900,  # 15 minutes
            "expert": 1200        # 20 minutes
        }
        
        format_multipliers = {
            "executive_briefing": 0.8,
            "presentation": 0.9,
            "comprehensive_report": 1.2,
            "technical_summary": 1.1,
            "policy_brief": 1.0
        }
        
        base_time = base_times.get(depth_level, 600)
        multiplier = format_multipliers.get(output_format, 1.0)
        
        estimated_seconds = int(base_time * multiplier)
        minutes = estimated_seconds // 60
        
        return f"Approximately {minutes} minutes"