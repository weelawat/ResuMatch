"""
RAG (Retrieval-Augmented Generation) service for resume-job comparison and suggestions.
This service retrieves relevant context (resume, job description) and generates
actionable suggestions using an LLM with LangChain.
"""
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from src.app.config import settings


class SuggestionOutput(BaseModel):
    """Structured output model for suggestions."""
    strengths: List[str] = Field(description="List of 3-5 key strengths where the candidate's resume aligns well with the job requirements")
    weaknesses: List[str] = Field(description="List of 3-5 areas where the candidate's resume is missing or weak compared to the job requirements")
    suggestions: List[str] = Field(description="List of 5-7 specific, actionable suggestions to improve the resume for this particular job")
    keywords_to_add: List[str] = Field(description="List of important keywords from the job description that should be incorporated into the resume")
    overall_assessment: str = Field(description="A brief 2-3 sentence summary of the candidate's fit for this role")


class RAGService:
    """Service for generating AI-powered suggestions using RAG with LangChain."""
    
    def __init__(self):
        """Initialize the RAG service with LangChain components."""
        self.llm = None
        self.chain = None
        self.output_parser = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize LangChain components."""
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        model_name = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
        
        if not api_key:
            return

        # Initialize LangChain ChatOpenAI
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            max_tokens=2000,
            api_key=api_key
        )
        
        # Initialize output parser for structured responses
        self.output_parser = PydanticOutputParser(pydantic_object=SuggestionOutput)
        
        # Create prompt template using LangChain
        system_template = (
            "You are an expert career advisor and resume reviewer with years of experience "
            "in HR and recruitment. Your task is to analyze resumes against job descriptions "
            "and provide actionable, specific, and constructive feedback.\n\n"
            "You excel at:\n"
            "- Identifying alignment between candidate skills and job requirements\n"
            "- Spotting gaps and areas for improvement\n"
            "- Providing specific, actionable recommendations\n"
            "- Understanding industry terminology and keywords\n\n"
            "Always be constructive, professional, and specific in your feedback."
        )

        human_template = (
            "Analyze the following resume against the job posting and provide a comprehensive "
            "comparison with actionable suggestions.\n\n"
            "JOB TITLE: {job_title}\n\n"
            "JOB DESCRIPTION:\n{job_description}\n\n"
            "JOB REQUIREMENTS:\n{job_requirements}\n\n"
            "CURRENT MATCH SCORE: {match_score}\n\n"
            "RESUME CONTENT:\n{resume_text}\n\n"
            "{format_instructions}\n\n"
            "Please provide your analysis in the structured format specified above. "
            "Be specific and actionable in all your recommendations."
        )

        # Create prompt template
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        
        prompt = ChatPromptTemplate.from_messages([
            system_message_prompt,
            human_message_prompt
        ])
        
        # Create chain using LCEL (LangChain Expression Language)
        # This is the modern approach replacing LLMChain
        self.chain = prompt | self.llm
    
    def generate_suggestions(
        self,
        resume_text: str,
        job_title: str,
        job_description: str,
        job_requirements: Optional[str] = None,
        match_score: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Generate suggestions by comparing resume with job description using RAG with LangChain.
        
        Args:
            resume_text: The extracted text from the resume
            job_title: The job title
            job_description: The job description
            job_requirements: Optional job requirements
            match_score: Optional similarity score (0-100)
        
        Returns:
            Dictionary containing suggestions, strengths, weaknesses, and recommendations
        """
        if not self.chain:
            return self._generate_fallback_suggestions(
                resume_text, job_title, job_description, job_requirements, match_score
            )
        
        try:
            # Prepare input for the chain
            match_score_str = f"{match_score:.2f}%" if match_score is not None else "Not calculated"
            job_requirements_str = job_requirements or "Not specified"
            
            # Get format instructions from parser
            format_instructions = self.output_parser.get_format_instructions()
            
            # Run the chain using LCEL
            result = self.chain.invoke({
                "job_title": job_title,
                "job_description": job_description,
                "job_requirements": job_requirements_str,
                "match_score": match_score_str,
                "resume_text": resume_text,
                "format_instructions": format_instructions
            })
            
            # Extract text from result (LCEL returns AIMessage object)
            if hasattr(result, 'content'):
                result_text = result.content
            elif isinstance(result, dict):
                result_text = result.get('text', str(result))
            else:
                result_text = str(result)
            
            # Parse the structured output
            parsed_output = self.output_parser.parse(result_text)
            
            # Convert to dictionary format
            return {
                "strengths": parsed_output.strengths[:5],
                "weaknesses": parsed_output.weaknesses[:5],
                "suggestions": parsed_output.suggestions[:7],
                "keywords_to_add": parsed_output.keywords_to_add,
                "overall_assessment": parsed_output.overall_assessment,
                "match_score": match_score,
                "raw_response": result_text
            }
            
        except Exception as e:
            print(f"Error calling LLM chain: {e}")
            # Fallback to basic suggestions
            return self._generate_fallback_suggestions(
                resume_text, job_title, job_description, job_requirements, match_score
            )
    
    def _create_documents(
        self,
        resume_text: str,
        job_title: str,
        job_description: str,
        job_requirements: Optional[str] = None
    ) -> List[Document]:
        """
        Create LangChain Document objects for better context handling.
        This allows for future enhancements like document chunking, retrieval, etc.
        """
        documents = []
        
        # Create document for job description
        job_metadata = {
            "type": "job_description",
            "title": job_title
        }
        job_content = f"Title: {job_title}\n\nDescription: {job_description}"
        if job_requirements:
            job_content += f"\n\nRequirements: {job_requirements}"
        
        documents.append(Document(page_content=job_content, metadata=job_metadata))
        
        # Create document for resume
        resume_metadata = {
            "type": "resume",
            "title": "Candidate Resume"
        }
        documents.append(Document(page_content=resume_text, metadata=resume_metadata))
        
        return documents
    
    def _generate_fallback_suggestions(
        self,
        resume_text: str,
        job_title: str,
        job_description: str,
        job_requirements: Optional[str] = None,
        match_score: Optional[float] = None
    ) -> Dict[str, any]:
        """Generate basic suggestions when LLM is not available."""
        # Simple keyword-based analysis
        resume_lower = resume_text.lower()
        job_text = f"{job_title} {job_description} {job_requirements or ''}".lower()
        
        # Extract keywords from job description
        job_keywords = set(word for word in job_text.split() if len(word) > 4)
        resume_keywords = set(word for word in resume_lower.split() if len(word) > 4)
        
        missing_keywords = job_keywords - resume_keywords
        
        return {
            "strengths": [
                "Resume contains relevant keywords",
                "Professional experience is documented"
            ],
            "weaknesses": [
                "Some job-specific keywords may be missing",
                "Consider tailoring resume more to job requirements"
            ],
            "suggestions": [
                "Add missing keywords naturally into your resume",
                "Highlight relevant experience more prominently",
                "Quantify achievements where possible",
                "Align skills section with job requirements",
                "Customize summary/objective for this role"
            ],
            "keywords_to_add": list(missing_keywords)[:10],
            "overall_assessment": f"Based on keyword analysis, the resume has a {match_score or 0:.1f}% match score. Consider incorporating more job-specific terminology and highlighting relevant experience.",
            "match_score": match_score,
            "raw_response": "Fallback analysis (LLM not configured - add OPENAI_API_KEY to enable LangChain-powered suggestions)"
        }


# Singleton instance
_rag_service = None

def get_rag_service() -> RAGService:
    """Get or create the RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
