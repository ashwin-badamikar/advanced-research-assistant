"""
Citation Manager Tool - Custom tool for managing research citations
"""
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import json
import re
from datetime import datetime
import hashlib

class CitationData(BaseModel):
    """Data model for citation information"""
    title: str
    authors: List[str] = Field(default_factory=list)
    url: str
    date_accessed: str
    source_type: str = "web"
    publication_date: Optional[str] = None
    publisher: Optional[str] = None
    doi: Optional[str] = None
    citation_id: str

class CitationManager(BaseTool):
    """
    Custom tool for managing research citations in multiple formats.
    Supports APA, MLA, and Chicago citation styles.
    """
    
    name: str = "Citation Manager"
    description: str = (
        "Manages research citations in multiple formats (APA, MLA, Chicago). "
        "Can add citations, format them properly, generate bibliographies, "
        "and track citation usage across research projects. "
        "Usage examples: "
        "action='add' title='Article Title' url='https://example.com' authors=['Author Name'] OR "
        "action='format' citation_id='abc123' style='APA' OR "
        "action='list' OR action='bibliography' style='APA'"
    )
    
    def __init__(self):
        super().__init__()
        self._citations: Dict[str, CitationData] = {}
        self._citation_usage: Dict[str, int] = {}
    
    def _run(self, action: str, title: str = "", url: str = "", authors: Optional[List[str]] = None,
             citation_id: str = "", style: str = "APA", target_score: float = 8.0, **kwargs) -> str:
        """
        Execute citation management actions
        
        Args:
            action: Action to perform (add, format, list, bibliography, usage)
            title: Title for new citation (required for add)
            url: URL for new citation (required for add)
            authors: List of authors (optional for add)
            citation_id: Citation ID (required for format, usage)
            style: Citation style (default APA)
            **kwargs: Additional citation metadata
        """
        try:
            if action == "add":
                return self._add_citation(title, url, authors or [], **kwargs)
            elif action == "format":
                return self._format_citation(citation_id, style)
            elif action == "list":
                return self._list_citations()
            elif action == "bibliography":
                return self._generate_bibliography(style)
            elif action == "usage":
                return self._track_usage(citation_id)
            else:
                return f"Unknown action: {action}. Available actions: add, format, list, bibliography, usage"
        except Exception as e:
            return f"Error in citation manager: {str(e)}"
    
    def _add_citation(self, title: str, url: str, authors: List[str] = None, **kwargs) -> str:
        """Add a new citation to the manager"""
        if not title:
            return "Error: Title is required for citations"
        if not url:
            url = "No URL provided"  # Allow citations without URLs
        
        # Generate unique citation ID
        citation_id = self._generate_citation_id(title, url)
        
        # Create citation data
        try:
            citation_data = {
                "title": title,
                "authors": authors or [],
                "url": url,
                "date_accessed": datetime.now().strftime("%Y-%m-%d"),
                "citation_id": citation_id,
                "source_type": kwargs.get("source_type", "web"),
                "publication_date": kwargs.get("publication_date"),
                "publisher": kwargs.get("publisher"),
                "doi": kwargs.get("doi")
            }
            
            citation = CitationData(**citation_data)
            self._citations[citation_id] = citation
            return f"Citation added successfully with ID: {citation_id}"
            
        except Exception as e:
            return f"Error creating citation: {str(e)}"
    
    def _format_citation(self, citation_id: str, style: str = "APA") -> str:
        """Format a citation in the specified style"""
        if not citation_id:
            return "Error: Citation ID is required for formatting"
            
        if citation_id not in self._citations:
            return f"Citation with ID {citation_id} not found. Available IDs: {list(self._citations.keys())}"
        
        citation = self._citations[citation_id]
        
        if style.upper() == "APA":
            return self._format_apa(citation)
        elif style.upper() == "MLA":
            return self._format_mla(citation)
        elif style.upper() == "CHICAGO":
            return self._format_chicago(citation)
        else:
            return f"Unsupported citation style: {style}. Supported styles: APA, MLA, Chicago"
    
    def _format_apa(self, citation: CitationData) -> str:
        """Format citation in APA style"""
        authors_str = ""
        if citation.authors:
            if len(citation.authors) == 1:
                authors_str = citation.authors[0]
            elif len(citation.authors) == 2:
                authors_str = f"{citation.authors[0]} & {citation.authors[1]}"
            else:
                authors_str = f"{', '.join(citation.authors[:-1])}, & {citation.authors[-1]}"
        else:
            authors_str = "Unknown Author"
        
        date_str = citation.publication_date or citation.date_accessed
        
        formatted = f"{authors_str}. ({date_str}). {citation.title}. "
        if citation.publisher:
            formatted += f"{citation.publisher}. "
        if citation.url and citation.url != "No URL provided":
            formatted += f"Retrieved from {citation.url}"
        
        return formatted
    
    def _format_mla(self, citation: CitationData) -> str:
        """Format citation in MLA style"""
        authors_str = ""
        if citation.authors:
            authors_str = citation.authors[0]
            if len(citation.authors) > 1:
                authors_str += " et al."
        else:
            authors_str = "Unknown Author"
        
        formatted = f"{authors_str}. \"{citation.title}.\" Web. {citation.date_accessed}."
        if citation.url and citation.url != "No URL provided":
            formatted += f" <{citation.url}>."
        
        return formatted
    
    def _format_chicago(self, citation: CitationData) -> str:
        """Format citation in Chicago style"""
        authors_str = ""
        if citation.authors:
            authors_str = citation.authors[0]
        else:
            authors_str = "Unknown Author"
        
        formatted = f"{authors_str}. \"{citation.title}.\" Accessed {citation.date_accessed}."
        if citation.url and citation.url != "No URL provided":
            formatted += f" {citation.url}."
        
        return formatted
    
    def _list_citations(self) -> str:
        """List all stored citations"""
        if not self._citations:
            return "No citations stored."
        
        result = "Stored Citations:\n"
        for citation_id, citation in self._citations.items():
            result += f"- {citation_id}: {citation.title}\n"
        
        return result
    
    def _generate_bibliography(self, style: str = "APA") -> str:
        """Generate a complete bibliography"""
        if not self._citations:
            return "No citations available for bibliography."
        
        bibliography = f"Bibliography ({style.upper()} Style):\n\n"
        
        for citation_id, citation in self._citations.items():
            formatted_citation = self._format_citation(citation_id, style)
            bibliography += f"{formatted_citation}\n\n"
        
        return bibliography
    
    def _track_usage(self, citation_id: str) -> str:
        """Track citation usage"""
        if not citation_id:
            return "Error: Citation ID is required for usage tracking"
            
        if citation_id not in self._citations:
            return f"Citation with ID {citation_id} not found"
        
        self._citation_usage[citation_id] = self._citation_usage.get(citation_id, 0) + 1
        return f"Citation {citation_id} usage tracked. Total uses: {self._citation_usage[citation_id]}"
    
    def _generate_citation_id(self, title: str, url: str) -> str:
        """Generate a unique citation ID"""
        combined = f"{title}{url}{datetime.now().isoformat()}"
        return hashlib.md5(combined.encode()).hexdigest()[:8]