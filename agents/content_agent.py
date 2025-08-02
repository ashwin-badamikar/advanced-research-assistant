"""
Content Agent - Specialized agent for content creation and presentation
"""
from crewai import Agent
from crewai_tools import FileWriterTool, DirectoryReadTool, FileReadTool
from config.settings import settings
from tools.citation_manager import CitationManager
from tools.quality_assessor import QualityAssessor
import os

class ContentAgentConfig:
    """Configuration for the Content Agent"""
    
    @staticmethod
    def create_content_agent() -> Agent:
        """Create and configure the Content Agent"""
        
        # Initialize tools
        file_writer_tool = FileWriterTool()
        file_read_tool = FileReadTool()
        directory_read_tool = DirectoryReadTool()
        citation_manager = CitationManager()
        quality_assessor = QualityAssessor()
        
        return Agent(
            role="Senior Content Strategist & Technical Writer",
            goal="""Create high-quality, well-structured, and engaging content based on 
                    research findings and analytical insights. Ensure all content is 
                    properly formatted, cited, and optimized for the target audience.""",
            
            backstory="""You are an expert content strategist and technical writer with 
                        extensive experience in creating compelling, informative content 
                        across various formats and audiences. You excel at transforming 
                        complex research and analytical findings into clear, engaging, 
                        and actionable content. Your expertise includes academic writing, 
                        business communications, technical documentation, and digital content 
                        creation. You understand the importance of proper citation, 
                        audience-appropriate tone, and content structure.""",
            
            tools=[
                file_writer_tool,
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
    def get_content_instructions() -> str:
        """Get detailed instructions for the content agent"""
        return """
        As the Content Agent, follow these guidelines:

        1. CONTENT STRUCTURE:
           - Create clear, logical content hierarchies
           - Use appropriate headings and subheadings
           - Implement consistent formatting and style
           - Ensure smooth transitions between sections

        2. WRITING QUALITY:
           - Write in clear, concise, and engaging prose
           - Adapt tone and style to target audience
           - Use active voice and strong verbs
           - Eliminate jargon unless necessary and defined

        3. RESEARCH INTEGRATION:
           - Seamlessly integrate research findings
           - Transform analytical insights into readable content
           - Balance detail with accessibility
           - Highlight key findings and implications

        4. CITATION AND ATTRIBUTION:
           - Use Citation Manager for all source attributions
           - Follow consistent citation style throughout
           - Provide proper credit for all information sources
           - Include bibliography or reference list

        5. CONTENT TYPES:
           - Executive summaries and abstracts
           - Detailed research reports
           - Presentation materials
           - Briefing documents
           - Technical documentation

        6. QUALITY ASSURANCE:
           - Use Quality Assessor to evaluate content
           - Ensure factual accuracy and completeness
           - Proofread for grammar, spelling, and clarity
           - Verify all citations and references

        7. FORMATTING AND PRESENTATION:
           - Use appropriate document formatting
           - Include visual elements where beneficial
           - Create scannable content with bullet points and lists
           - Optimize for both print and digital consumption

        8. AUDIENCE CONSIDERATIONS:
           - Tailor complexity to audience expertise level
           - Include appropriate context and background
           - Anticipate reader questions and address them
           - Provide actionable recommendations when appropriate

        9. FILE OPERATIONS:
           - Use FileWriterTool to save all final content to the outputs directory
           - Use descriptive filenames with timestamps
           - Create both summary and detailed versions when appropriate
           - Ensure proper file formatting and encoding
        """
    
    @staticmethod
    def save_content_to_file(content: str, filename: str, output_dir: str = None) -> str:
        """Save content to file in the output directory"""
        if output_dir is None:
            output_dir = settings.OUTPUT_DIR
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create full file path
        file_path = os.path.join(output_dir, filename)
        
        try:
            # Save content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Content successfully saved to: {file_path}"
        
        except Exception as e:
            return f"Error saving content to file: {str(e)}"

class ContentTemplates:
    """Content templates for different document types"""
    
    @staticmethod
    def executive_summary_template() -> str:
        """Template for executive summary"""
        return """
# Executive Summary

## Key Findings
[Summarize 3-5 most important findings]

## Methodology
[Brief description of research approach]

## Recommendations
[List of actionable recommendations]

## Strategic Implications
[High-level impact and implications]

## Next Steps
[Recommended actions and timeline]
"""
    
    @staticmethod
    def research_report_template() -> str:
        """Template for detailed research report"""
        return """
# [Report Title]

## Executive Summary
[Brief overview of key findings and recommendations]

## Table of Contents
[Automatically generated based on sections]

## 1. Introduction
### 1.1 Background
### 1.2 Research Objectives
### 1.3 Scope and Limitations

## 2. Methodology
### 2.1 Research Approach
### 2.2 Data Sources
### 2.3 Analysis Methods

## 3. Findings
### 3.1 [Key Finding Area 1]
### 3.2 [Key Finding Area 2]
### 3.3 [Key Finding Area 3]

## 4. Analysis and Insights
### 4.1 Trend Analysis
### 4.2 Comparative Analysis
### 4.3 Gap Analysis

## 5. Recommendations
### 5.1 Strategic Recommendations
### 5.2 Tactical Recommendations
### 5.3 Implementation Considerations

## 6. Conclusion
[Summary of key insights and future directions]

## References
[Complete bibliography using consistent citation style]

## Appendices
[Supporting data, detailed tables, additional resources]
"""
    
    @staticmethod
    def presentation_template() -> str:
        """Template for presentation materials"""
        return """
# [Presentation Title]

## Slide 1: Title Slide
- Title
- Subtitle
- Date
- Presenter(s)

## Slide 2: Agenda
- Key topics to be covered
- Time allocation

## Slide 3: Executive Summary
- Key findings (3-5 bullet points)
- Main recommendations

## Slide 4-6: Key Findings
- One key finding per slide
- Supporting data/evidence
- Visual elements

## Slide 7-8: Analysis & Insights
- Trends and patterns
- Comparative analysis
- Strategic implications

## Slide 9: Recommendations
- Prioritized recommendations
- Implementation timeline
- Success metrics

## Slide 10: Next Steps
- Immediate actions
- Long-term strategy
- Resource requirements

## Slide 11: Questions & Discussion
- Contact information
- Additional resources
"""

class ContentQualityChecker:
    """Quality checking utilities for content"""
    
    @staticmethod
    def check_readability(text: str) -> dict:
        """Basic readability assessment"""
        sentences = text.split('.')
        words = text.split()
        
        if not sentences or not words:
            return {"readability": "insufficient_content"}
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        # Simple readability scoring
        if avg_words_per_sentence <= 15:
            readability = "easy"
        elif avg_words_per_sentence <= 20:
            readability = "moderate"
        else:
            readability = "difficult"
        
        return {
            "readability": readability,
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "total_words": len(words),
            "total_sentences": len(sentences)
        }
    
    @staticmethod
    def check_structure(text: str) -> dict:
        """Check document structure"""
        lines = text.split('\n')
        
        headings = sum(1 for line in lines if line.startswith('#'))
        bullet_points = sum(1 for line in lines if line.strip().startswith('-') or line.strip().startswith('*'))
        
        return {
            "has_headings": headings > 0,
            "heading_count": headings,
            "bullet_points": bullet_points,
            "total_lines": len(lines)
        }