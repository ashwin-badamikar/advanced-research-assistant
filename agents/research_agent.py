"""
Research Agent - Specialized agent for information gathering and research
"""
from crewai import Agent
from crewai_tools import SerperDevTool, FileReadTool, DirectoryReadTool
from config.settings import settings
from tools.citation_manager import CitationManager
from tools.quality_assessor import QualityAssessor

class ResearchAgentConfig:
    """Configuration for the Research Agent"""
    
    @staticmethod
    def create_research_agent() -> Agent:
        """Create and configure the Research Agent"""
        
        # Initialize tools
        search_tool = SerperDevTool(api_key=settings.SERPER_API_KEY)
        file_read_tool = FileReadTool()
        directory_read_tool = DirectoryReadTool()
        citation_manager = CitationManager()
        quality_assessor = QualityAssessor()
        
        return Agent(
            role="Senior Research Specialist",
            goal="""Conduct comprehensive research on any given topic by gathering, 
                    evaluating, and organizing information from multiple reliable sources. 
                    Ensure all research is thorough, accurate, and properly cited.""",
            
            backstory="""You are an experienced research specialist with expertise in 
                        academic and professional research methodologies. You have a keen eye 
                        for identifying credible sources, extracting relevant information, 
                        and organizing research findings in a systematic manner. You understand 
                        the importance of source credibility, data accuracy, and comprehensive 
                        coverage of research topics.""",
            
            tools=[
                search_tool,
                file_read_tool,
                directory_read_tool,
                citation_manager,
                quality_assessor
            ],
            
            verbose=settings.AGENT_CONFIG["verbose"],
            memory=settings.AGENT_CONFIG["memory"],
            max_iter=settings.AGENT_CONFIG["max_iter"],
            max_execution_time=settings.AGENT_CONFIG["max_execution_time"],
            
            # Advanced agent configuration
            llm_config={
                "model": settings.LLM_MODEL,
                "temperature": settings.TEMPERATURE,
                "max_tokens": settings.MAX_TOKENS
            },
        )
    
    @staticmethod
    def get_research_instructions() -> str:
        """Get detailed instructions for the research agent"""
        return """
        As the Research Agent, follow these guidelines:

        1. RESEARCH METHODOLOGY:
           - Start with broad searches, then narrow down to specific aspects
           - Use multiple search queries to ensure comprehensive coverage
           - Prioritize recent, credible sources
           - Cross-reference information from multiple sources

        2. SOURCE EVALUATION:
           - Use the Quality Assessor tool to evaluate each source
           - Prioritize academic, government, and established organization sources
           - Check publication dates and ensure information is current
           - Verify author credentials when possible

        3. INFORMATION ORGANIZATION:
           - Use the Citation Manager to track all sources
           - Organize findings by topic and subtopic
           - Note conflicting information and explain discrepancies
           - Maintain detailed records of search strategies

        4. QUALITY ASSURANCE:
           - Fact-check critical claims against multiple sources
           - Flag uncertain or contested information
           - Provide confidence levels for different findings
           - Document any limitations in the research

        5. COLLABORATION:
           - Clearly communicate findings to other agents
           - Provide raw data and processed insights
           - Share source credibility assessments
           - Flag areas needing further investigation
        """