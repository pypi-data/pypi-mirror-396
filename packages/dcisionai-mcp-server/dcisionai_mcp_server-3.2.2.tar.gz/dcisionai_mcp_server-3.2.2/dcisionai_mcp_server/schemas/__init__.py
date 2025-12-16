"""
Optimization Contracts Schemas

Pydantic schemas for ModelPack and DataPack that enable domain-agnostic
optimization model building.
"""

from dcisionai_mcp_server.schemas.optimization_contracts import (
    # Enums
    ProblemClass,
    VariableDomain,
    ConstraintSense,
    ObjectiveSense,
    ExpressionNodeType,
    SolverEngine,
    
    # Expression AST
    ExprNode,
    ConstantNode,
    ParameterRefNode,
    VariableRefNode,
    IndexRefNode,
    BinaryOpNode,
    UnaryOpNode,
    SummationNode,
    DoubleSummationNode,
    QuadraticFormNode,
    ConditionalNode,
    Expression,
    expr_to_pyomo,
    
    # Expression Templates
    ExpressionTemplate,
    TemplatedExpression,
    
    # Index Sets
    IndexSetDefinition,
    
    # Variables
    BoundsSpec,
    DecisionVariableSpec,
    
    # Parameters
    ParameterSpec,
    
    # Objectives
    ObjectiveSpec,
    
    # Constraints
    ConstraintSpec,
    
    # Assumptions
    AssumptionSpec,
    
    # Classification
    ClassificationResult,
    MultiObjectiveConfig,
    
    # Model Pack
    ModelPack,
    
    # Data Pack
    SetDataSpec,
    ParameterDataSpec,
    DataQualityReport,
    DataPack,
)

__all__ = [
    # Enums
    "ProblemClass",
    "VariableDomain",
    "ConstraintSense",
    "ObjectiveSense",
    "ExpressionNodeType",
    "ExpressionTemplate",
    "SolverEngine",
    
    # Expression AST
    "ExprNode",
    "ConstantNode",
    "ParameterRefNode",
    "VariableRefNode",
    "IndexRefNode",
    "BinaryOpNode",
    "UnaryOpNode",
    "SummationNode",
    "DoubleSummationNode",
    "QuadraticFormNode",
    "ConditionalNode",
    "Expression",
    "expr_to_pyomo",
    
    # Expression Templates
    "ExpressionTemplate",
    "TemplatedExpression",
    
    # Index Sets
    "IndexSetDefinition",
    
    # Variables
    "BoundsSpec",
    "DecisionVariableSpec",
    
    # Parameters
    "ParameterSpec",
    
    # Objectives
    "ObjectiveSpec",
    
    # Constraints
    "ConstraintSpec",
    
    # Assumptions
    "AssumptionSpec",
    
    # Classification
    "ClassificationResult",
    "MultiObjectiveConfig",
    
    # Model Pack
    "ModelPack",
    
    # Data Pack
    "SetDataSpec",
    "ParameterDataSpec",
    "DataQualityReport",
    "DataPack",
]

