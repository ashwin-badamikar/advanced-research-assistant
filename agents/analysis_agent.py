"""
Analysis Agent - Specialized agent for data analysis and insight generation
"""
from crewai import Agent
from config.settings import settings
import pandas as pd
import json

class AnalysisAgentConfig:
    """Configuration for the Analysis Agent"""
    
    @staticmethod
    def create_analysis_agent() -> Agent:
        """Create and configure the Analysis Agent"""
        
        return Agent(
            role="Senior Data Analyst & Insights Specialist",
            goal="""Analyze research data and information to extract meaningful insights, 
                    identify patterns, trends, and relationships. Transform raw research 
                    into actionable intelligence and strategic recommendations.""",
            
            backstory="""You are a highly skilled data analyst with extensive experience 
                        in research analysis, statistical evaluation, and insight generation. 
                        You excel at identifying patterns in complex data, synthesizing 
                        information from multiple sources, and translating analytical 
                        findings into clear, actionable insights. Your expertise spans 
                        quantitative and qualitative analysis, trend identification, 
                        and strategic recommendation development.""",
            
            tools=[],  # We'll add analysis tools later if needed
            
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
    def get_analysis_instructions() -> str:
        """Get detailed instructions for the analysis agent"""
        return """
        As the Analysis Agent, follow these guidelines:

        1. DATA ANALYSIS APPROACH:
           - Review all research data systematically
           - Identify key themes, patterns, and trends
           - Look for correlations and causal relationships
           - Quantify findings where possible

        2. ANALYTICAL TECHNIQUES:
           - Comparative analysis across sources and time periods
           - Trend analysis for temporal data
           - Gap analysis to identify missing information
           - Risk-benefit analysis for recommendations
           - SWOT analysis when appropriate

        3. INSIGHT GENERATION:
           - Extract actionable insights from raw data
           - Identify surprising or counterintuitive findings
           - Synthesize complex information into clear conclusions
           - Prioritize insights by importance and impact

        4. QUALITY VALIDATION:
           - Cross-validate findings across multiple sources
           - Assess statistical significance where applicable
           - Identify and flag potential biases or limitations
           - Provide confidence intervals for quantitative findings

        5. STRATEGIC RECOMMENDATIONS:
           - Develop practical, implementable recommendations
           - Prioritize recommendations by impact and feasibility
           - Consider short-term and long-term implications
           - Account for potential risks and mitigation strategies

        6. VISUALIZATION PREPARATION:
           - Identify data suitable for visualization
           - Suggest appropriate chart types and formats
           - Prepare data summaries for presentation
           - Highlight key statistics and metrics

        7. COLLABORATION:
           - Build upon research findings from the Research Agent
           - Prepare analytical insights for the Content Agent
           - Flag areas requiring additional research
           - Communicate uncertainty and confidence levels clearly
        """

class AnalysisTools:
    """Additional analysis utilities for the Analysis Agent"""
    
    @staticmethod
    def calculate_trend(data_points: list) -> dict:
        """Calculate trend analysis for numerical data"""
        if len(data_points) < 2:
            return {"trend": "insufficient_data", "change": 0}
        
        # Simple trend calculation
        start_value = data_points[0]
        end_value = data_points[-1]
        change_percent = ((end_value - start_value) / start_value) * 100 if start_value != 0 else 0
        
        if change_percent > 5:
            trend = "increasing"
        elif change_percent < -5:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change_percent": round(change_percent, 2),
            "start_value": start_value,
            "end_value": end_value
        }
    
    @staticmethod
    def analyze_sentiment_distribution(sentiments: list) -> dict:
        """Analyze distribution of sentiment scores"""
        if not sentiments:
            return {"distribution": "no_data"}
        
        positive = sum(1 for s in sentiments if s > 0.1)
        negative = sum(1 for s in sentiments if s < -0.1)
        neutral = len(sentiments) - positive - negative
        
        return {
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral,
            "positive_percent": round((positive / len(sentiments)) * 100, 1),
            "negative_percent": round((negative / len(sentiments)) * 100, 1),
            "neutral_percent": round((neutral / len(sentiments)) * 100, 1)
        }
    
    @staticmethod
    def identify_key_themes(text_data: list) -> list:
        """Identify key themes from text data"""
        # Simple keyword frequency analysis
        word_freq = {}
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        for text in text_data:
            words = text.lower().split()
            for word in words:
                # Clean word
                word = ''.join(c for c in word if c.isalnum())
                if len(word) > 3 and word not in stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top themes
        sorted_themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [theme[0] for theme in sorted_themes[:10]]