"""
Quality Assessor Tool - Custom tool for assessing research quality
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import re
import json
from datetime import datetime

class QualityMetrics(BaseModel):
    """Data model for quality assessment metrics"""
    credibility_score: float = Field(ge=0, le=10)
    relevance_score: float = Field(ge=0, le=10)
    accuracy_score: float = Field(ge=0, le=10)
    completeness_score: float = Field(ge=0, le=10)
    timeliness_score: float = Field(ge=0, le=10)
    overall_score: float = Field(ge=0, le=10)
    assessment_notes: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

class QualityAssessor(BaseTool):
    """
    Custom tool for assessing the quality of research content and sources.
    Evaluates credibility, relevance, accuracy, completeness, and timeliness.
    """
    
    name: str = "Quality Assessor"
    description: str = (
        "Assesses the quality of research content and sources using multiple criteria. "
        "Evaluates credibility, relevance, accuracy, completeness, and timeliness. "
        "Provides detailed scores and recommendations for improvement."
    )
    
    def __init__(self):
        super().__init__()
        self._assessment_history: Dict[str, QualityMetrics] = {}
        self._domain_expertise: Dict[str, List[str]] = {
            "academic": ["peer-reviewed", "citations", "methodology", "abstract"],
            "news": ["byline", "date", "source attribution", "fact-checking"],
            "government": [".gov", "official", "policy", "legislation"],
            "commercial": ["company", "product", "marketing", "sales"]
        }
    
    def _run(self, action: str, content: str = "", source_url: str = "", 
             content_type: str = "web", target_score: float = 8.0, domain: str = "general") -> str:
        """
        Execute quality assessment actions
        
        Args:
            action: Action to perform (assess, history, benchmark, improve)
            content: Content to assess (required for assess action)
            source_url: Source URL (optional)
            content_type: Type of content (web, academic, news, etc.)
            target_score: Target score for improvement suggestions
            domain: Domain for benchmarking (general, academic, commercial, etc.)
        """
        try:
            if action == "assess":
                if not content:
                    return "Error: Content is required for assessment"
                return self._assess_content(content, source_url, content_type)
            elif action == "history":
                return self._get_assessment_history()
            elif action == "benchmark":
                return self._benchmark_against_standards(domain)
            elif action == "improve":
                return self._suggest_improvements(target_score)
            else:
                return f"Unknown action: {action}. Available actions: assess, history, benchmark, improve"
        except Exception as e:
            return f"Error in quality assessor: {str(e)}"
    
    def _assess_content(self, content: str, source_url: str = "", content_type: str = "web") -> str:
        """Assess the quality of content"""
        # Perform quality assessment
        metrics = self._calculate_quality_metrics(content, source_url, content_type)
        
        # Store assessment
        assessment_id = self._generate_assessment_id(content, source_url)
        self._assessment_history[assessment_id] = metrics
        
        # Format results
        result = self._format_assessment_results(metrics, assessment_id)
        return result
    
    def _calculate_quality_metrics(self, content: str, source_url: str, content_type: str) -> QualityMetrics:
        """Calculate quality metrics for content"""
        
        # Credibility Assessment
        credibility_score = self._assess_credibility(content, source_url, content_type)
        
        # Relevance Assessment
        relevance_score = self._assess_relevance(content)
        
        # Accuracy Assessment
        accuracy_score = self._assess_accuracy(content)
        
        # Completeness Assessment
        completeness_score = self._assess_completeness(content)
        
        # Timeliness Assessment
        timeliness_score = self._assess_timeliness(content)
        
        # Calculate overall score
        overall_score = (credibility_score + relevance_score + accuracy_score + 
                        completeness_score + timeliness_score) / 5
        
        # Generate notes and recommendations
        notes = self._generate_assessment_notes(content, source_url)
        recommendations = self._generate_recommendations(
            credibility_score, relevance_score, accuracy_score, 
            completeness_score, timeliness_score
        )
        
        return QualityMetrics(
            credibility_score=credibility_score,
            relevance_score=relevance_score,
            accuracy_score=accuracy_score,
            completeness_score=completeness_score,
            timeliness_score=timeliness_score,
            overall_score=overall_score,
            assessment_notes=notes,
            recommendations=recommendations
        )
    
    def _assess_credibility(self, content: str, source_url: str, content_type: str) -> float:
        """Assess source credibility"""
        score = 5.0  # Base score
        
        # URL-based credibility indicators
        if source_url:
            if any(domain in source_url.lower() for domain in ['.edu', '.gov', '.org']):
                score += 2.0
            elif any(domain in source_url.lower() for domain in ['.com', '.net']):
                score += 0.5
        
        # Content-based credibility indicators
        credibility_indicators = [
            r'peer.?reviewed', r'published in', r'journal', r'study shows',
            r'research indicates', r'according to experts', r'data suggests'
        ]
        
        for indicator in credibility_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                score += 0.3
        
        # Check for bias indicators (reduce score)
        bias_indicators = [
            r'always', r'never', r'everyone knows', r'obviously',
            r'without a doubt', r'definitely proves'
        ]
        
        for indicator in bias_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                score -= 0.2
        
        return min(10.0, max(0.0, score))
    
    def _assess_relevance(self, content: str) -> float:
        """Assess content relevance"""
        score = 5.0  # Base score
        
        # Check for specific, actionable information
        if re.search(r'\d+%|\d+\.\d+|statistics|data|findings', content, re.IGNORECASE):
            score += 1.5
        
        # Check for recent references
        current_year = datetime.now().year
        years_mentioned = re.findall(r'\b(20\d{2})\b', content)
        if years_mentioned:
            recent_years = [year for year in years_mentioned if int(year) >= current_year - 2]
            if recent_years:
                score += 1.0
        
        # Check for comprehensive coverage
        if len(content.split()) > 500:
            score += 1.0
        elif len(content.split()) < 100:
            score -= 1.0
        
        return min(10.0, max(0.0, score))
    
    def _assess_accuracy(self, content: str) -> float:
        """Assess content accuracy"""
        score = 6.0  # Base score (assume neutral)
        
        # Check for citations and references
        citation_patterns = [
            r'\[\d+\]', r'\(\d{4}\)', r'et al\.', r'according to',
            r'source:', r'reference:', r'study by'
        ]
        
        citation_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) 
                           for pattern in citation_patterns)
        
        if citation_count > 5:
            score += 2.0
        elif citation_count > 2:
            score += 1.0
        
        # Check for factual language
        factual_indicators = [
            r'research shows', r'data indicates', r'study found',
            r'analysis reveals', r'evidence suggests'
        ]
        
        for indicator in factual_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                score += 0.3
        
        return min(10.0, max(0.0, score))
    
    def _assess_completeness(self, content: str) -> float:
        """Assess content completeness"""
        score = 5.0  # Base score
        
        word_count = len(content.split())
        
        # Adjust score based on content length
        if word_count > 1000:
            score += 2.0
        elif word_count > 500:
            score += 1.0
        elif word_count < 100:
            score -= 2.0
        
        # Check for structured content
        structure_indicators = [
            r'introduction', r'conclusion', r'methodology', r'results',
            r'discussion', r'background', r'summary'
        ]
        
        structure_count = sum(1 for indicator in structure_indicators 
                            if re.search(indicator, content, re.IGNORECASE))
        
        score += structure_count * 0.5
        
        return min(10.0, max(0.0, score))
    
    def _assess_timeliness(self, content: str) -> float:
        """Assess content timeliness"""
        score = 5.0  # Base score
        
        current_year = datetime.now().year
        
        # Look for dates in content
        dates_found = re.findall(r'\b(20\d{2})\b', content)
        
        if dates_found:
            most_recent_year = max(int(year) for year in dates_found)
            years_old = current_year - most_recent_year
            
            if years_old <= 1:
                score += 3.0
            elif years_old <= 3:
                score += 1.0
            elif years_old <= 5:
                score += 0.0
            else:
                score -= 2.0
        
        # Check for temporal language
        recent_indicators = [
            r'recent', r'latest', r'current', r'updated', r'new',
            r'this year', r'recently', r'now'
        ]
        
        for indicator in recent_indicators:
            if re.search(indicator, content, re.IGNORECASE):
                score += 0.2
        
        return min(10.0, max(0.0, score))
    
    def _generate_assessment_notes(self, content: str, source_url: str) -> List[str]:
        """Generate assessment notes"""
        notes = []
        
        word_count = len(content.split())
        notes.append(f"Content length: {word_count} words")
        
        if source_url:
            notes.append(f"Source URL: {source_url}")
        
        # Add specific observations
        if re.search(r'\d+%|\d+\.\d+', content):
            notes.append("Contains quantitative data")
        
        if re.search(r'study|research|analysis', content, re.IGNORECASE):
            notes.append("References research or studies")
        
        citation_count = len(re.findall(r'\[\d+\]|\(\d{4}\)', content))
        if citation_count > 0:
            notes.append(f"Contains {citation_count} citations")
        
        return notes
    
    def _generate_recommendations(self, credibility: float, relevance: float, 
                                accuracy: float, completeness: float, timeliness: float) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if credibility < 6.0:
            recommendations.append("Seek more credible sources (academic, government, established organizations)")
        
        if relevance < 6.0:
            recommendations.append("Focus on more specific and actionable information")
        
        if accuracy < 6.0:
            recommendations.append("Add more citations and references to support claims")
        
        if completeness < 6.0:
            recommendations.append("Expand content with more comprehensive coverage")
        
        if timeliness < 6.0:
            recommendations.append("Update with more recent information and sources")
        
        if not recommendations:
            recommendations.append("Content meets quality standards")
        
        return recommendations
    
    def _format_assessment_results(self, metrics: QualityMetrics, assessment_id: str) -> str:
        """Format assessment results for output"""
        result = f"""
Quality Assessment Results (ID: {assessment_id})
{'='*50}

QUALITY SCORES:
- Credibility: {metrics.credibility_score:.1f}/10
- Relevance: {metrics.relevance_score:.1f}/10
- Accuracy: {metrics.accuracy_score:.1f}/10
- Completeness: {metrics.completeness_score:.1f}/10
- Timeliness: {metrics.timeliness_score:.1f}/10

OVERALL SCORE: {metrics.overall_score:.1f}/10

ASSESSMENT NOTES:
{chr(10).join(f'- {note}' for note in metrics.assessment_notes)}

RECOMMENDATIONS:
{chr(10).join(f'- {rec}' for rec in metrics.recommendations)}
"""
        return result
    
    def _get_assessment_history(self) -> str:
        """Get assessment history"""
        if not self._assessment_history:
            return "No assessments performed yet."
        
        result = "Assessment History:\n"
        for assessment_id, metrics in self._assessment_history.items():
            result += f"- {assessment_id}: Overall Score {metrics.overall_score:.1f}/10\n"
        
        return result
    
    def _benchmark_against_standards(self, domain: str = "general") -> str:
        """Benchmark against quality standards"""
        if not self._assessment_history:
            return "No assessments available for benchmarking."
        
        scores = [metrics.overall_score for metrics in self._assessment_history.values()]
        avg_score = sum(scores) / len(scores)
        
        result = f"""
Quality Benchmark Report
{'='*25}
Average Quality Score: {avg_score:.1f}/10
Total Assessments: {len(scores)}
Quality Standard: {'Meets Standards' if avg_score >= 7.0 else 'Below Standards'}
"""
        return result
    
    def _suggest_improvements(self, target_score: float = 8.0) -> str:
        """Suggest improvements to reach target quality"""
        if not self._assessment_history:
            return "No assessments available for improvement suggestions."
        
        latest_metrics = list(self._assessment_history.values())[-1]
        
        improvements = []
        if latest_metrics.credibility_score < target_score:
            improvements.append("Improve source credibility")
        if latest_metrics.relevance_score < target_score:
            improvements.append("Enhance content relevance")
        if latest_metrics.accuracy_score < target_score:
            improvements.append("Add more supporting evidence")
        if latest_metrics.completeness_score < target_score:
            improvements.append("Expand content comprehensiveness")
        if latest_metrics.timeliness_score < target_score:
            improvements.append("Update with recent information")
        
        if not improvements:
            return f"Content already meets target quality score of {target_score}/10"
        
        return f"To reach target score of {target_score}/10:\n" + "\n".join(f"- {imp}" for imp in improvements)
    
    def _generate_assessment_id(self, content: str, source_url: str) -> str:
        """Generate a unique assessment ID"""
        import hashlib
        combined = f"{content[:100]}{source_url}"
        return hashlib.md5(combined.encode()).hexdigest()[:8]