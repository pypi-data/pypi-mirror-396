"""
Solver Resources - Direct dcisionai_graph Integration

Exposes available solvers as MCP resources.
"""

import json
import logging
from mcp.types import Resource

logger = logging.getLogger(__name__)


def get_solver_resources() -> list[Resource]:
    """Get list of solver resources"""
    return [
        Resource(
            uri="dcisionai://solvers/list",
            name="Available Solvers",
            description="List of all available optimization solvers (SCIP, HiGHS, OR-Tools, DAME)",
            mimeType="application/json"
        )
    ]


async def read_solver_resource(uri: str) -> str:
    """
    Read solver resource
    
    Args:
        uri: Resource URI (e.g., dcisionai://solvers/list)
        
    Returns:
        Resource content as JSON string
    """
    if uri == "dcisionai://solvers/list":
        try:
            # Return static list of available solvers
            # TODO: Could dynamically query solver availability if needed
            solvers = [
                {
                    "name": "scip",
                    "type": "MILP",
                    "available": True,
                    "description": "SCIP - Solving Constraint Integer Programs (open-source)"
                },
                {
                    "name": "highs",
                    "type": "LP/MILP",
                    "available": True,
                    "description": "HiGHS - High-performance open-source linear programming solver"
                },
                {
                    "name": "ortools",
                    "type": "CP/MIP",
                    "available": True,
                    "description": "OR-Tools - Google's optimization tools (constraint programming)"
                },
                {
                    "name": "dame",
                    "type": "Heuristic",
                    "available": True,
                    "description": "DAME - DcisionAI's heuristic optimization solver"
                },
                {
                    "name": "ipopt",
                    "type": "NLP",
                    "available": True,
                    "description": "IPOPT - Interior Point Optimizer (nonlinear programming)"
                }
            ]
            
            return json.dumps({
                "solvers": solvers,
                "total": len(solvers)
            }, indent=2)
        except Exception as e:
            logger.error(f"Error reading solver resource: {e}", exc_info=True)
            return json.dumps({
                "error": str(e),
                "message": "Failed to load solver list"
            })
    else:
        return json.dumps({"error": f"Unknown resource URI: {uri}"})

