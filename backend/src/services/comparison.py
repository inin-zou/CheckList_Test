from typing import List, Dict, Any
import logging
from src.services.vector_db import get_vector_db
from src.services.llm import get_llm_service

logger = logging.getLogger(__name__)


class ChecklistComparisonService:
    """Service for comparing user documents against checklist templates"""
    
    def __init__(self):
        self.vector_db = get_vector_db()
        self.llm = get_llm_service()
    
    async def compare_document_with_checklist(
        self,
        user_filename: str,
        checklist_filename: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """Compare a user document against a checklist template
        
        Args:
            user_filename: Name of the user document to validate
            checklist_filename: Name of the checklist template to compare against
            top_k: Number of relevant chunks to retrieve for comparison
            
        Returns:
            Dictionary containing comparison results with missing/non-compliant items
        """
        try:
            # Get all checklist items
            checklist_items = self._get_checklist_items(checklist_filename)
            
            if not checklist_items:
                return {
                    "status": "error",
                    "error": f"No checklist items found for '{checklist_filename}'"
                }
            
            # Check each checklist item against user document
            results = []
            for item in checklist_items:
                compliance_result = await self._check_item_compliance(
                    user_filename=user_filename,
                    checklist_item=item,
                    top_k=top_k
                )
                results.append(compliance_result)
            
            # Summarize results
            compliant_items = [r for r in results if r["compliant"]]
            non_compliant_items = [r for r in results if not r["compliant"]]
            
            return {
                "status": "success",
                "user_document": user_filename,
                "checklist_template": checklist_filename,
                "total_items": len(results),
                "compliant_count": len(compliant_items),
                "non_compliant_count": len(non_compliant_items),
                "compliance_rate": len(compliant_items) / len(results) if results else 0,
                "compliant_items": compliant_items,
                "non_compliant_items": non_compliant_items
            }
            
        except Exception as e:
            logger.error(f"Error comparing documents: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _get_checklist_items(self, checklist_filename: str) -> List[Dict[str, Any]]:
        """Retrieve all chunks from a checklist template
        
        Args:
            checklist_filename: Name of the checklist file
            
        Returns:
            List of checklist items (chunks) with their content and metadata
        """
        try:
            # Search for all chunks from this checklist file
            results = self.vector_db.search(
                query="*",  # Get all content
                collection_type="checklist",
                top_k=1000,  # Get up to 1000 chunks
                filters={"filename": checklist_filename}
            )
            
            items = []
            for result in results:
                items.append({
                    "content": result.get("content", ""),
                    "chunk_index": result.get("chunk_index", 0),
                    "metadata": result.get("metadata", {})
                })
            
            # Sort by chunk_index to maintain order
            items.sort(key=lambda x: x["chunk_index"])
            return items
            
        except Exception as e:
            logger.error(f"Error retrieving checklist items: {str(e)}")
            return []
    
    async def _check_item_compliance(
        self,
        user_filename: str,
        checklist_item: Dict[str, Any],
        top_k: int = 10
    ) -> Dict[str, Any]:
        """Check if a checklist item is compliant in the user document
        
        Args:
            user_filename: Name of the user document
            checklist_item: The checklist item to verify
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            Dictionary with compliance status and explanation
        """
        try:
            checklist_content = checklist_item["content"]
            
            # Search user document for relevant content
            user_results = self.vector_db.search(
                query=checklist_content,
                collection_type="user",
                top_k=top_k,
                filters={"filename": user_filename}
            )
            
            if not user_results:
                return {
                    "checklist_item": checklist_content[:200] + "..." if len(checklist_content) > 200 else checklist_content,
                    "compliant": False,
                    "reason": "No relevant content found in user document",
                    "confidence": 0.0
                }
            
            # Use LLM to determine compliance
            context = "\n\n".join([r["content"] for r in user_results[:5]])
            
            prompt = f"""You are a compliance verification assistant. Your task is to determine if the user document contains the required checklist item.

Checklist Requirement:
{checklist_content}

Relevant Content from User Document:
{context}

Analyze whether the user document satisfies the checklist requirement. Respond in JSON format:
{{
    "compliant": true/false,
    "reason": "Brief explanation of why it is or isn't compliant",
    "confidence": 0.0-1.0
}}
"""
            
            llm_response = await self.llm.generate(prompt)
            
            # Parse LLM response (simplified - in production, add robust JSON parsing)
            import json
            try:
                result = json.loads(llm_response)
                return {
                    "checklist_item": checklist_content[:200] + "..." if len(checklist_content) > 200 else checklist_content,
                    "compliant": result.get("compliant", False),
                    "reason": result.get("reason", "Unable to determine"),
                    "confidence": result.get("confidence", 0.0),
                    "relevant_content": user_results[0]["content"][:300] if user_results else ""
                }
            except json.JSONDecodeError:
                return {
                    "checklist_item": checklist_content[:200] + "..." if len(checklist_content) > 200 else checklist_content,
                    "compliant": False,
                    "reason": "Failed to parse LLM response",
                    "confidence": 0.0
                }
                
        except Exception as e:
            logger.error(f"Error checking item compliance: {str(e)}")
            return {
                "checklist_item": checklist_item.get("content", "")[:200],
                "compliant": False,
                "reason": f"Error: {str(e)}",
                "confidence": 0.0
            }
    
    async def get_compliance_report(
        self,
        user_filename: str,
        checklist_filename: str
    ) -> str:
        """Generate a human-readable compliance report
        
        Args:
            user_filename: Name of the user document
            checklist_filename: Name of the checklist template
            
        Returns:
            Formatted compliance report as a string
        """
        comparison = await self.compare_document_with_checklist(
            user_filename=user_filename,
            checklist_filename=checklist_filename
        )
        
        if comparison["status"] == "error":
            return f"Error generating report: {comparison['error']}"
        
        report = f"""COMPLIANCE REPORT
{'=' * 60}
User Document: {comparison['user_document']}
Checklist Template: {comparison['checklist_template']}
Total Items Checked: {comparison['total_items']}
Compliant: {comparison['compliant_count']}
Non-Compliant: {comparison['non_compliant_count']}
Compliance Rate: {comparison['compliance_rate']:.1%}

"""
        
        if comparison['non_compliant_items']:
            report += "NON-COMPLIANT ITEMS:\n" + "-" * 60 + "\n"
            for idx, item in enumerate(comparison['non_compliant_items'], 1):
                report += f"{idx}. {item['checklist_item']}\n"
                report += f"   Reason: {item['reason']}\n"
                report += f"   Confidence: {item['confidence']:.1%}\n\n"
        
        return report


# Global instance
_comparison_service = None

def get_comparison_service() -> ChecklistComparisonService:
    """Get or create the global comparison service instance"""
    global _comparison_service
    if _comparison_service is None:
        _comparison_service = ChecklistComparisonService()
    return _comparison_service