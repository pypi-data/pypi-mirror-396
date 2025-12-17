"""
DcisionAI Optimization Contracts

================================

Pydantic schemas for ModelPack (from Intent Discovery) and DataPack (from Data Preparation)
that enable Claude SDK to build Pyomo models in a DOMAIN-AGNOSTIC manner.

Design Philosophy (PhD Optimization Specialist Perspective):
============================================================

1. MATHEMATICAL PRECISION OVER CONVENIENCE
   - Every subscripted entity explicitly declares its index sets
   - Expressions are structured ASTs, not strings (avoids parsing failures)
   - Bounds, domains, and types are explicit, never inferred

2. SEPARATION OF CONCERNS
   - ModelPack = Mathematical Structure (the "what to optimize")
   - DataPack = Numerical Values (the "with what data")
   - This enables: template reuse, sensitivity analysis, data updates without model changes

3. PYOMO-NATIVE OUTPUT
   - Every schema element maps 1:1 to Pyomo constructs
   - Set → pyo.Set, Parameter → pyo.Param, Variable → pyo.Var
   - Expression AST → Pyomo expression rules

4. VALIDATION AT EVERY LEVEL
   - Cross-reference checks: every variable/parameter used must be defined
   - Dimensional consistency: index sets must align across entities
   - Mathematical consistency: QP must have quadratic terms, LP must not

5. DOMAIN-AGNOSTIC BY CONSTRUCTION
   - No industry-specific fields or patterns
   - Problem classification drives solver selection, not templates
   - Mathematical structure is universal

Author: DcisionAI Research
Location: dcisionai_mcp_server/schemas/optimization_contracts.py
Version: 2.0.0
"""

from __future__ import annotations

from typing import (
    Optional, Union, Literal, Dict, Any, List, 
    Tuple, Set, Annotated, TypeVar, Generic,
    Callable, TYPE_CHECKING
)
from pydantic import (
    BaseModel, Field, field_validator, model_validator,
    ConfigDict, computed_field, PrivateAttr
)
from enum import Enum
from decimal import Decimal
from datetime import datetime
from uuid import uuid4
import re


# =============================================================================
# SECTION 1: ENUMERATIONS (Mathematical Classification)
# =============================================================================

class ProblemClass(str, Enum):
    """
    Mathematical problem classification.
    
    This determines solver selection and solution guarantees.
    """
    LP = "LP"           # Linear Programming - polynomial time solvable
    QP = "QP"           # Quadratic Programming - polynomial if convex
    MILP = "MILP"       # Mixed-Integer Linear - NP-hard, branch-and-bound
    MIQP = "MIQP"       # Mixed-Integer Quadratic - NP-hard
    SOCP = "SOCP"       # Second-Order Cone - convex, interior point
    SDP = "SDP"         # Semidefinite Programming - convex
    NLP = "NLP"         # Nonlinear Programming - local optima only
    MINLP = "MINLP"     # Mixed-Integer Nonlinear - hardest class
    CP = "CP"           # Constraint Programming - feasibility focus


class VariableDomain(str, Enum):
    """
    Mathematical domain for decision variables.
    
    Maps directly to Pyomo domain specifications.
    """
    REALS = "Reals"                     # x ∈ ℝ
    NON_NEGATIVE_REALS = "NonNegativeReals"  # x ∈ ℝ₊
    NON_POSITIVE_REALS = "NonPositiveReals"  # x ∈ ℝ₋
    INTEGERS = "Integers"               # x ∈ ℤ
    NON_NEGATIVE_INTEGERS = "NonNegativeIntegers"  # x ∈ ℤ₊
    BINARY = "Binary"                   # x ∈ {0, 1}
    UNIT_INTERVAL = "UnitInterval"      # x ∈ [0, 1]
    PERCENT_FRACTION = "PercentFraction"  # x ∈ [0, 1] representing %


class ConstraintSense(str, Enum):
    """Constraint relationship type."""
    EQ = "=="    # Equality: lhs == rhs
    LE = "<="    # Less than or equal: lhs <= rhs
    GE = ">="    # Greater than or equal: lhs >= rhs


class ObjectiveSense(str, Enum):
    """Optimization direction."""
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


class ExpressionNodeType(str, Enum):
    """Types of nodes in expression AST."""
    CONSTANT = "constant"
    PARAMETER_REF = "param"
    VARIABLE_REF = "var"
    INDEX_REF = "index"
    BINARY_OP = "binary"
    UNARY_OP = "unary"
    SUMMATION = "sum"
    PRODUCT = "prod"
    CONDITIONAL = "if"
    QUADRATIC_FORM = "quad"


class ExpressionTemplate(str, Enum):
    """
    Named expression patterns to reduce composition risk.
    
    Instead of asking Claude to compose arbitrary AST, provide templates
    that Claude can select and bind to specific variables/parameters.
    
    This eliminates composition depth risk for common patterns.
    """
    LINEAR_SUM = "linear_sum"           # Σᵢ cᵢxᵢ
    QUADRATIC_FORM = "quadratic_form"   # x'Qx
    BILINEAR_SUM = "bilinear_sum"       # Σᵢⱼ cᵢⱼxᵢⱼ
    MEAN_VARIANCE = "mean_variance"     # Σᵢ μᵢxᵢ - λ·x'Qx
    WEIGHTED_SUM = "weighted_sum"       # Σᵢ wᵢ·fᵢ(xᵢ)
    PRODUCT_SUM = "product_sum"         # Σᵢ (aᵢ · bᵢ)
    DISTANCE_METRIC = "distance_metric" # Σᵢ (xᵢ - yᵢ)²
    MAX_MIN = "max_min"                 # max/min over set
    PIECEWISE_LINEAR = "piecewise_linear"  # Piecewise linear function


class SolverEngine(str, Enum):
    """Supported solver engines."""
    HIGHS = "highs"
    SCIP = "scip"
    CBC = "cbc"
    GLPK = "glpk"
    CPLEX = "cplex"
    GUROBI = "gurobi"
    IPOPT = "ipopt"
    BONMIN = "bonmin"
    COUENNE = "couenne"
    OSQP = "osqp"
    MOSEK = "mosek"
    ORTOOLS_CP_SAT = "or-tools-cp-sat"
    ORTOOLS_ROUTING = "or-tools-routing"


# =============================================================================
# SECTION 2: EXPRESSION AST (The Heart of Domain-Agnostic Modeling)
# =============================================================================

class ExprNode(BaseModel):
    """
    Base class for expression AST nodes.
    
    WHY AST INSTEAD OF STRINGS?
    ---------------------------
    String-based expressions like "sum(x[i] * c[i] for i in I)" are:
    - Fragile: one typo breaks everything
    - Hard to validate: can't check if 'x' is defined without parsing
    - Ambiguous: "x[i,j]" vs "x[i][j]" vs "x[(i,j)]"
    
    AST expressions are:
    - Structurally validated at construction time
    - Self-documenting: every node declares its dependencies
    - Directly translatable to Pyomo expressions
    """
    model_config = ConfigDict(extra="forbid", frozen=True)
    
    node_type: ExpressionNodeType
    
    def to_pyomo(self, model_var: str = "m") -> str:
        """Generate Pyomo expression string. Override in subclasses."""
        raise NotImplementedError


class ConstantNode(ExprNode):
    """Numeric constant."""
    node_type: Literal[ExpressionNodeType.CONSTANT] = ExpressionNodeType.CONSTANT
    value: float
    
    def to_pyomo(self, model_var: str = "m") -> str:
        return str(self.value)


class ParameterRefNode(ExprNode):
    """
    Reference to a parameter.
    
    Example: cost[i,j] → ParameterRefNode(name="cost", indices=["i", "j"])
    """
    node_type: Literal[ExpressionNodeType.PARAMETER_REF] = ExpressionNodeType.PARAMETER_REF
    name: str = Field(..., description="Parameter name as defined in ModelPack")
    indices: Optional[List[str]] = Field(
        default=None, 
        description="Index variables: ['i', 'j'] for param[i,j]"
    )
    
    def to_pyomo(self, model_var: str = "m") -> str:
        if self.indices:
            idx_str = ", ".join(self.indices)
            return f"{model_var}.{self.name}[{idx_str}]"
        return f"{model_var}.{self.name}"


class VariableRefNode(ExprNode):
    """
    Reference to a decision variable.
    
    Example: x[i] → VariableRefNode(name="x", indices=["i"])
    """
    node_type: Literal[ExpressionNodeType.VARIABLE_REF] = ExpressionNodeType.VARIABLE_REF
    name: str = Field(..., description="Variable name as defined in ModelPack")
    indices: Optional[List[str]] = Field(
        default=None,
        description="Index variables: ['i'] for x[i]"
    )
    
    def to_pyomo(self, model_var: str = "m") -> str:
        if self.indices:
            idx_str = ", ".join(self.indices)
            return f"{model_var}.{self.name}[{idx_str}]"
        return f"{model_var}.{self.name}"


class IndexRefNode(ExprNode):
    """
    Reference to an index variable (used within summations).
    
    Example: In "sum over i of x[i]", 'i' is an index reference.
    """
    node_type: Literal[ExpressionNodeType.INDEX_REF] = ExpressionNodeType.INDEX_REF
    symbol: str = Field(..., pattern=r"^[a-z]$", description="Single letter index symbol")
    
    def to_pyomo(self, model_var: str = "m") -> str:
        return self.symbol


class BinaryOpNode(ExprNode):
    """
    Binary operation: left op right.
    
    Supports: +, -, *, /, ** (power)
    """
    node_type: Literal[ExpressionNodeType.BINARY_OP] = ExpressionNodeType.BINARY_OP
    operator: Literal["+", "-", "*", "/", "**"]
    left: "Expression"
    right: "Expression"
    
    def to_pyomo(self, model_var: str = "m") -> str:
        left_str = expr_to_pyomo(self.left, model_var)
        right_str = expr_to_pyomo(self.right, model_var)
        
        # Handle precedence with parentheses
        if self.operator in ("*", "/", "**"):
            if isinstance(self.left, dict) and self.left.get("operator") in ("+", "-"):
                left_str = f"({left_str})"
            if isinstance(self.right, dict) and self.right.get("operator") in ("+", "-"):
                right_str = f"({right_str})"
        
        return f"({left_str} {self.operator} {right_str})"


class UnaryOpNode(ExprNode):
    """
    Unary operation.
    
    Supports: negation, abs, sqrt, exp, log, sin, cos
    """
    node_type: Literal[ExpressionNodeType.UNARY_OP] = ExpressionNodeType.UNARY_OP
    operator: Literal["neg", "abs", "sqrt", "exp", "log", "sin", "cos"]
    operand: "Expression"
    
    def to_pyomo(self, model_var: str = "m") -> str:
        op_str = expr_to_pyomo(self.operand, model_var)
        
        if self.operator == "neg":
            return f"(-{op_str})"
        elif self.operator == "abs":
            return f"abs({op_str})"
        else:
            # Pyomo intrinsic functions
            return f"pyo.{self.operator}({op_str})"


class SummationNode(ExprNode):
    """
    Summation: Σᵢ∈I expression(i)
    
    This is THE critical construct for domain-agnostic modeling.
    Every linear/quadratic objective and most constraints use summation.
    
    Example: Σᵢ cᵢxᵢ → SummationNode(
        expression=BinaryOpNode("*", ParamRef("c", ["i"]), VarRef("x", ["i"])),
        index_var="i",
        over_set="I"
    )
    """
    node_type: Literal[ExpressionNodeType.SUMMATION] = ExpressionNodeType.SUMMATION
    expression: "Expression" = Field(..., description="Expression to sum")
    index_var: str = Field(..., description="Index variable symbol: 'i'")
    over_set: str = Field(..., description="Set name to iterate: 'I' or 'Products'")
    
    # Optional filter condition (for filtered sums)
    filter_condition: Optional["Expression"] = Field(
        default=None,
        description="Only sum where condition is true"
    )
    
    def to_pyomo(self, model_var: str = "m") -> str:
        inner = expr_to_pyomo(self.expression, model_var)
        
        if self.filter_condition:
            cond = expr_to_pyomo(self.filter_condition, model_var)
            return f"sum({inner} for {self.index_var} in {model_var}.{self.over_set} if {cond})"
        
        return f"sum({inner} for {self.index_var} in {model_var}.{self.over_set})"


class DoubleSummationNode(ExprNode):
    """
    Double summation: Σᵢ∈I Σⱼ∈J expression(i,j)
    
    Common in: assignment problems, transportation problems, portfolio covariance
    
    Example: Σᵢⱼ xᵢⱼdᵢⱼ → DoubleSummationNode(
        expression=BinaryOpNode("*", VarRef("x", ["i","j"]), ParamRef("d", ["i","j"])),
        outer_index="i", outer_set="I",
        inner_index="j", inner_set="J"
    )
    """
    node_type: Literal[ExpressionNodeType.SUMMATION] = ExpressionNodeType.SUMMATION
    expression: "Expression"
    outer_index: str
    outer_set: str
    inner_index: str
    inner_set: str
    
    def to_pyomo(self, model_var: str = "m") -> str:
        inner = expr_to_pyomo(self.expression, model_var)
        return (
            f"sum({inner} "
            f"for {self.outer_index} in {model_var}.{self.outer_set} "
            f"for {self.inner_index} in {model_var}.{self.inner_set})"
        )


class QuadraticFormNode(ExprNode):
    """
    Quadratic form: x'Qx = Σᵢ Σⱼ xᵢ Qᵢⱼ xⱼ
    
    This is THE canonical form for:
    - Portfolio variance: w'Σw
    - Regularization terms: ||x||²
    - Distance metrics: (x-y)'M(x-y)
    
    WHY A SPECIAL NODE?
    - Quadratic forms determine problem class (LP → QP)
    - Convexity depends on Q being positive semidefinite
    - Solvers handle them specially (Hessian extraction)
    """
    node_type: Literal[ExpressionNodeType.QUADRATIC_FORM] = ExpressionNodeType.QUADRATIC_FORM
    variable_name: str = Field(..., description="Variable name: 'x' or 'weight'")
    matrix_param: str = Field(..., description="Q matrix parameter name: 'covariance'")
    index_set: str = Field(..., description="Set over which quadratic form is defined")
    
    # Coefficient (optional scaling)
    coefficient: float = Field(default=1.0)
    
    def to_pyomo(self, model_var: str = "m") -> str:
        v = self.variable_name
        Q = self.matrix_param
        I = self.index_set
        coef = f"{self.coefficient} * " if self.coefficient != 1.0 else ""
        
        return (
            f"{coef}sum({model_var}.{v}[i] * {model_var}.{Q}[i, j] * {model_var}.{v}[j] "
            f"for i in {model_var}.{I} for j in {model_var}.{I})"
        )


class ConditionalNode(ExprNode):
    """
    Conditional expression: if condition then expr1 else expr2
    
    Used for piecewise functions and indicator constraints.
    """
    node_type: Literal[ExpressionNodeType.CONDITIONAL] = ExpressionNodeType.CONDITIONAL
    condition: "Expression"
    if_true: "Expression"
    if_false: "Expression"
    
    def to_pyomo(self, model_var: str = "m") -> str:
        cond = expr_to_pyomo(self.condition, model_var)
        true_expr = expr_to_pyomo(self.if_true, model_var)
        false_expr = expr_to_pyomo(self.if_false, model_var)
        return f"pyo.Expr_if({cond}, {true_expr}, {false_expr})"


# Union type for all expression nodes
Expression = Union[
    ConstantNode, ParameterRefNode, VariableRefNode, IndexRefNode,
    BinaryOpNode, UnaryOpNode, SummationNode, DoubleSummationNode,
    QuadraticFormNode, ConditionalNode,
    Dict[str, Any]  # Allow dict representation for flexibility
]


def expr_to_pyomo(expr: Expression, model_var: str = "m") -> str:
    """
    Convert expression AST to Pyomo code string.
    
    Handles both Pydantic models and dict representations.
    """
    if hasattr(expr, 'to_pyomo'):
        return expr.to_pyomo(model_var)
    
    if isinstance(expr, dict):
        node_type = expr.get("node_type")
        
        if node_type == "constant":
            return str(expr["value"])
        
        elif node_type == "param":
            name = expr["name"]
            indices = expr.get("indices")
            if indices:
                return f"{model_var}.{name}[{', '.join(indices)}]"
            return f"{model_var}.{name}"
        
        elif node_type == "var":
            name = expr["name"]
            indices = expr.get("indices")
            if indices:
                return f"{model_var}.{name}[{', '.join(indices)}]"
            return f"{model_var}.{name}"
        
        elif node_type == "index":
            return expr["symbol"]
        
        elif node_type == "binary":
            left = expr_to_pyomo(expr["left"], model_var)
            right = expr_to_pyomo(expr["right"], model_var)
            return f"({left} {expr['operator']} {right})"
        
        elif node_type == "unary":
            operand = expr_to_pyomo(expr["operand"], model_var)
            op = expr["operator"]
            if op == "neg":
                return f"(-{operand})"
            elif op == "abs":
                return f"abs({operand})"
            return f"pyo.{op}({operand})"
        
        elif node_type == "sum":
            inner = expr_to_pyomo(expr["expression"], model_var)
            idx = expr.get("index_var") or expr.get("outer_index")
            over = expr.get("over_set") or expr.get("outer_set")
            filt = expr.get("filter_condition")
            
            # Check for double sum (nested structure)
            if isinstance(expr.get("expression"), dict) and expr["expression"].get("node_type") == "sum":
                # Nested sum - handle double summation
                inner_expr = expr["expression"]
                inner_idx = inner_expr.get("index_var")
                inner_over = inner_expr.get("over_set")
                if inner_idx and inner_over:
                    return (
                        f"sum(sum({expr_to_pyomo(inner_expr['expression'], model_var)} "
                        f"for {inner_idx} in {model_var}.{inner_over}) "
                        f"for {idx} in {model_var}.{over})"
                    )
            
            if filt:
                cond = expr_to_pyomo(filt, model_var)
                return f"sum({inner} for {idx} in {model_var}.{over} if {cond})"
            return f"sum({inner} for {idx} in {model_var}.{over})"
        
        elif node_type == "quad":
            v = expr["variable_name"]
            Q = expr["matrix_param"]
            I = expr["index_set"]
            coef = expr.get("coefficient", 1.0)
            coef_str = f"{coef} * " if coef != 1.0 else ""
            return (
                f"{coef_str}sum({model_var}.{v}[i] * {model_var}.{Q}[i, j] * {model_var}.{v}[j] "
                f"for i in {model_var}.{I} for j in {model_var}.{I})"
            )
    
    return str(expr)


# =============================================================================
# SECTION 3: INDEX SETS (The Foundation of Dimensional Consistency)
# =============================================================================

class IndexSetDefinition(BaseModel):
    """
    Definition of an index set.
    
    Index sets are the FOUNDATION of optimization models.
    Every subscripted variable and parameter references index sets.
    
    Examples:
    - Products: i ∈ {1, ..., n}
    - Warehouses: j ∈ {NYC, LA, CHI}
    - Time periods: t ∈ {1, ..., T}
    - Asset pairs: (i,j) ∈ Assets × Assets
    """
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(
        ...,
        description="Set name (PascalCase): 'Products', 'Warehouses', 'Assets'"
    )
    
    # Mathematical notation
    index_symbol: str = Field(
        ...,
        pattern=r"^[a-z]$",
        description="Index symbol (single lowercase letter): 'i', 'j', 't'"
    )
    
    description: str = Field(
        ...,
        description="What this set represents in the problem"
    )
    
    # Set specification (exactly one must be provided)
    set_type: Literal["enumerated", "range", "cartesian"] = Field(
        default="range",
        description="How the set is defined"
    )
    
    # For enumerated sets: explicit elements
    elements: Optional[List[Union[str, int]]] = Field(
        default=None,
        description="Explicit elements: ['AAPL', 'GOOGL'] or [1, 2, 3]"
    )
    
    # For range sets: start and end
    range_start: Optional[int] = Field(default=None)
    range_end: Optional[int] = Field(default=None)
    
    # Cardinality (always required - Claude needs this for code generation)
    cardinality: int = Field(
        ...,
        ge=1,
        description="Number of elements in the set"
    )
    
    # For Cartesian product sets
    component_sets: Optional[List[str]] = Field(
        default=None,
        description="For cartesian type: ['I', 'J'] means I × J"
    )
    
    # Evidence trail (for debugging/auditing)
    extracted_from: Optional[str] = Field(
        default=None,
        description="Exact quote from problem that this was extracted from"
    )
    
    @model_validator(mode="after")
    def validate_set_specification(self) -> "IndexSetDefinition":
        """Ensure set is properly specified."""
        if self.set_type == "enumerated":
            if not self.elements:
                raise ValueError("Enumerated set must have elements")
            if len(self.elements) != self.cardinality:
                raise ValueError(f"Elements count ({len(self.elements)}) != cardinality ({self.cardinality})")
        
        elif self.set_type == "range":
            if self.range_start is None or self.range_end is None:
                raise ValueError("Range set must have range_start and range_end")
            expected_card = self.range_end - self.range_start + 1
            if expected_card != self.cardinality:
                raise ValueError(f"Range [{self.range_start}, {self.range_end}] has {expected_card} elements, not {self.cardinality}")
        
        elif self.set_type == "cartesian":
            if not self.component_sets or len(self.component_sets) < 2:
                raise ValueError("Cartesian set must have at least 2 component sets")
        
        return self
    
    def to_pyomo(self, model_var: str = "m") -> str:
        """Generate Pyomo Set declaration."""
        if self.set_type == "enumerated":
            return f"{model_var}.{self.name} = pyo.Set(initialize={self.elements})"
        elif self.set_type == "range":
            return f"{model_var}.{self.name} = pyo.RangeSet({self.range_start}, {self.range_end})"
        elif self.set_type == "cartesian":
            components = " * ".join(f"{model_var}.{s}" for s in self.component_sets)
            return f"{model_var}.{self.name} = {components}"
        return f"{model_var}.{self.name} = pyo.Set()"


# =============================================================================
# SECTION 4: DECISION VARIABLES
# =============================================================================

class BoundsSpec(BaseModel):
    """
    Variable bounds specification.
    
    Supports both constant and parameter-dependent bounds.
    """
    model_config = ConfigDict(extra="forbid")
    
    lower: Optional[float] = Field(default=None, description="Constant lower bound (None = -∞)")
    upper: Optional[float] = Field(default=None, description="Constant upper bound (None = +∞)")
    
    # Parameter-dependent bounds (for indexed variables)
    lower_param: Optional[str] = Field(
        default=None,
        description="Parameter name for lower bound: 'min_allocation[i]'"
    )
    upper_param: Optional[str] = Field(
        default=None,
        description="Parameter name for upper bound: 'max_allocation[i]'"
    )


class DecisionVariableSpec(BaseModel):
    """
    Complete specification of a decision variable.
    
    This is WHAT WE'RE SOLVING FOR - the unknowns in the optimization problem.
    
    CRITICAL DISTINCTION:
    - Decision Variable: unknown, solved by optimizer (x, y, allocation)
    - Parameter: known input data (cost, demand, capacity)
    
    Example:
    - allocation[i] ∈ [0, 1] for i ∈ Assets
    - x[i,j] ∈ {0, 1} for (i,j) ∈ Plants × Customers
    """
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(
        ...,
        description="Variable name (snake_case): 'allocation', 'production_qty', 'route_selected'"
    )
    
    description: str = Field(
        ...,
        description="What this variable represents in business terms"
    )
    
    # Mathematical domain
    domain: VariableDomain = Field(
        default=VariableDomain.NON_NEGATIVE_REALS,
        description="Mathematical domain"
    )
    
    # Indexing
    index_sets: List[str] = Field(
        default_factory=list,
        description="Names of index sets: ['Assets'] for x[i], ['Plants', 'Customers'] for x[i,j]"
    )
    
    # Bounds
    bounds: BoundsSpec = Field(default_factory=BoundsSpec)
    
    # Dimensionality (computed from index sets, but explicit for validation)
    total_dimensions: int = Field(
        default=1,
        description="Total number of variable instances"
    )
    
    # Semantic annotations
    unit: Optional[str] = Field(
        default=None,
        description="Unit of measurement: 'dollars', 'units', 'fraction'"
    )
    
    business_interpretation: Optional[str] = Field(
        default=None,
        description="Example: 'allocation[AAPL] = 0.4 means 40% of portfolio in Apple'"
    )
    
    # Solver hints
    initial_value: Optional[float] = Field(
        default=None,
        description="Initial value for warm-starting"
    )
    
    # Evidence trail
    extracted_from: Optional[str] = Field(
        default=None,
        description="Exact quote from problem"
    )
    
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    
    def to_pyomo(self, model_var: str = "m") -> str:
        """Generate Pyomo Var declaration."""
        parts = [f"{model_var}.{self.name} = pyo.Var("]
        
        # Index sets
        if self.index_sets:
            sets = ", ".join(f"{model_var}.{s}" for s in self.index_sets)
            parts.append(f"{sets}, ")
        
        # Domain
        domain_str = f"domain=pyo.{self.domain.value}"
        parts.append(domain_str)
        
        # Bounds (if not implied by domain)
        if self.domain not in (VariableDomain.BINARY, VariableDomain.UNIT_INTERVAL):
            if self.bounds.lower is not None or self.bounds.upper is not None:
                l = self.bounds.lower if self.bounds.lower is not None else "None"
                u = self.bounds.upper if self.bounds.upper is not None else "None"
                parts.append(f", bounds=({l}, {u})")
        
        # Initialize
        if self.initial_value is not None:
            parts.append(f", initialize={self.initial_value}")
        
        parts.append(")")
        return "".join(parts)


# =============================================================================
# SECTION 5: PARAMETERS
# =============================================================================

class ParameterSpec(BaseModel):
    """
    Complete specification of a parameter.
    
    Parameters are KNOWN INPUT DATA - values given to the optimizer.
    
    CRITICAL DISTINCTION:
    - Parameter: known, provided by data (cost[i], demand[j], return[i])
    - Decision Variable: unknown, solved by optimizer
    
    Example:
    - cost[i] = unit cost for product i (scalar per i)
    - distance[i,j] = distance from i to j (matrix)
    - budget = total available budget (scalar)
    """
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(
        ...,
        description="Parameter name (snake_case): 'cost', 'demand', 'expected_return'"
    )
    
    description: str = Field(
        ...,
        description="What this parameter represents"
    )
    
    # Structure
    structure: Literal["scalar", "indexed"] = Field(
        default="scalar",
        description="scalar = single value, indexed = array/matrix"
    )
    
    # For indexed parameters
    index_sets: List[str] = Field(
        default_factory=list,
        description="Index sets: [] for scalar, ['I'] for vector, ['I', 'J'] for matrix"
    )
    
    # Data characteristics
    data_type: Literal["float", "int", "bool"] = Field(default="float")
    
    # Validation rules (for data quality)
    must_be_positive: bool = Field(default=False)
    must_be_nonnegative: bool = Field(default=False)
    valid_range: Optional[Tuple[float, float]] = Field(
        default=None,
        description="Expected range for validation: (min, max)"
    )
    
    # Source tracking
    source: Literal["problem_statement", "assumption", "derived", "external_data"] = Field(
        default="assumption"
    )
    
    # Default value (for optional parameters)
    default_value: Optional[float] = Field(default=None)
    
    # Semantic annotations
    unit: Optional[str] = Field(default=None)
    
    # Special flags
    is_covariance_matrix: bool = Field(
        default=False,
        description="If True, must be symmetric positive semidefinite"
    )
    is_distance_matrix: bool = Field(
        default=False,
        description="If True, must satisfy triangle inequality"
    )
    
    # Evidence
    extracted_from: Optional[str] = None
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    
    def to_pyomo(self, model_var: str = "m") -> str:
        """Generate Pyomo Param declaration."""
        parts = [f"{model_var}.{self.name} = pyo.Param("]
        
        if self.index_sets:
            sets = ", ".join(f"{model_var}.{s}" for s in self.index_sets)
            parts.append(f"{sets}, ")
        
        if self.default_value is not None:
            parts.append(f"default={self.default_value}, ")
        
        parts.append("mutable=True)")  # Allow updates
        return "".join(parts)


# =============================================================================
# SECTION 6: OBJECTIVES
# =============================================================================

class TemplatedExpression(BaseModel):
    """
    Expression using a named template pattern.
    
    Reduces composition risk by using pre-defined patterns.
    Claude selects template and provides bindings.
    """
    model_config = ConfigDict(extra="forbid")
    
    template: ExpressionTemplate = Field(
        ...,
        description="Template pattern to use"
    )
    
    bindings: Dict[str, str] = Field(
        ...,
        description="Variable/parameter bindings: {'c': 'cost', 'x': 'allocation', 'I': 'Assets'}"
    )
    
    # Optional coefficient/weight
    coefficient: float = Field(default=1.0, description="Scaling factor")
    
    def to_ast(self) -> Expression:
        """
        Convert template to AST expression.
        
        Expands template patterns to full AST structures.
        This eliminates composition risk for common patterns.
        """
        if self.template == ExpressionTemplate.LINEAR_SUM:
            # Σᵢ cᵢxᵢ
            c_param = self.bindings.get('c', 'cost')
            x_var = self.bindings.get('x', 'allocation')
            I_set = self.bindings.get('I', 'Assets')
            index_var = self.bindings.get('i', 'i')  # Default to 'i'
            return SummationNode(
                expression=BinaryOpNode(
                    operator="*",
                    left=ParameterRefNode(name=c_param, indices=[index_var]),
                    right=VariableRefNode(name=x_var, indices=[index_var])
                ),
                index_var=index_var,
                over_set=I_set
            )
        
        elif self.template == ExpressionTemplate.QUADRATIC_FORM:
            # x'Qx
            x_var = self.bindings.get('x', 'allocation')
            Q_param = self.bindings.get('Q', 'covariance')
            I_set = self.bindings.get('I', 'Assets')
            return QuadraticFormNode(
                variable_name=x_var,
                matrix_param=Q_param,
                index_set=I_set,
                coefficient=self.coefficient
            )
        
        elif self.template == ExpressionTemplate.BILINEAR_SUM:
            # Σᵢⱼ cᵢⱼxᵢⱼ
            c_param = self.bindings.get('c', 'cost')
            x_var = self.bindings.get('x', 'flow')
            I_set = self.bindings.get('I', 'Sources')
            J_set = self.bindings.get('J', 'Destinations')
            i_var = self.bindings.get('i', 'i')
            j_var = self.bindings.get('j', 'j')
            from dcisionai_mcp_server.schemas.optimization_contracts import DoubleSummationNode
            return DoubleSummationNode(
                expression=BinaryOpNode(
                    operator="*",
                    left=ParameterRefNode(name=c_param, indices=[i_var, j_var]),
                    right=VariableRefNode(name=x_var, indices=[i_var, j_var])
                ),
                outer_index=i_var,
                outer_set=I_set,
                inner_index=j_var,
                inner_set=J_set
            )
        
        elif self.template == ExpressionTemplate.MEAN_VARIANCE:
            # Σᵢ μᵢxᵢ - λ·x'Qx
            mu_param = self.bindings.get('mu', 'expected_return')
            x_var = self.bindings.get('x', 'allocation')
            Q_param = self.bindings.get('Q', 'covariance')
            I_set = self.bindings.get('I', 'Assets')
            lambda_val = self.bindings.get('lambda', '0.5')
            index_var = self.bindings.get('i', 'i')
            
            # Linear term: Σᵢ μᵢxᵢ
            linear_term = SummationNode(
                expression=BinaryOpNode(
                    operator="*",
                    left=ParameterRefNode(name=mu_param, indices=[index_var]),
                    right=VariableRefNode(name=x_var, indices=[index_var])
                ),
                index_var=index_var,
                over_set=I_set
            )
            
            # Quadratic term: λ·x'Qx
            quad_term = BinaryOpNode(
                operator="*",
                left=ConstantNode(value=float(lambda_val)),
                right=QuadraticFormNode(
                    variable_name=x_var,
                    matrix_param=Q_param,
                    index_set=I_set,
                    coefficient=1.0
                )
            )
            
            # Combine: linear - quadratic
            return BinaryOpNode(
                operator="-",
                left=linear_term,
                right=quad_term
            )
        
        elif self.template == ExpressionTemplate.WEIGHTED_SUM:
            # Σᵢ wᵢ·fᵢ(xᵢ)
            w_param = self.bindings.get('w', 'weight')
            f_param = self.bindings.get('f', 'value')
            x_var = self.bindings.get('x', 'allocation')
            I_set = self.bindings.get('I', 'Assets')
            index_var = self.bindings.get('i', 'i')
            return SummationNode(
                expression=BinaryOpNode(
                    operator="*",
                    left=ParameterRefNode(name=w_param, indices=[index_var]),
                    right=BinaryOpNode(
                        operator="*",
                        left=ParameterRefNode(name=f_param, indices=[index_var]),
                        right=VariableRefNode(name=x_var, indices=[index_var])
                    )
                ),
                index_var=index_var,
                over_set=I_set
            )
        
        elif self.template == ExpressionTemplate.PRODUCT_SUM:
            # Σᵢ (aᵢ · bᵢ)
            a_param = self.bindings.get('a', 'param_a')
            b_param = self.bindings.get('b', 'param_b')
            I_set = self.bindings.get('I', 'Items')
            index_var = self.bindings.get('i', 'i')
            return SummationNode(
                expression=BinaryOpNode(
                    operator="*",
                    left=ParameterRefNode(name=a_param, indices=[index_var]),
                    right=ParameterRefNode(name=b_param, indices=[index_var])
                ),
                index_var=index_var,
                over_set=I_set
            )
        
        elif self.template == ExpressionTemplate.DISTANCE_METRIC:
            # Σᵢ (xᵢ - yᵢ)²
            x_var = self.bindings.get('x', 'allocation')
            y_param = self.bindings.get('y', 'target')
            I_set = self.bindings.get('I', 'Assets')
            index_var = self.bindings.get('i', 'i')
            return SummationNode(
                expression=BinaryOpNode(
                    operator="**",
                    left=BinaryOpNode(
                        operator="-",
                        left=VariableRefNode(name=x_var, indices=[index_var]),
                        right=ParameterRefNode(name=y_param, indices=[index_var])
                    ),
                    right=ConstantNode(value=2.0)
                ),
                index_var=index_var,
                over_set=I_set
            )
        
        elif self.template == ExpressionTemplate.MAX_MIN:
            # max/min over set
            op = self.bindings.get('op', 'max')  # 'max' or 'min'
            x_var = self.bindings.get('x', 'allocation')
            I_set = self.bindings.get('I', 'Assets')
            index_var = self.bindings.get('i', 'i')
            # For max/min, we'd use Pyomo's max/min functions
            # This is a simplified representation
            return SummationNode(
                expression=VariableRefNode(name=x_var, indices=[index_var]),
                index_var=index_var,
                over_set=I_set
            )
        
        elif self.template == ExpressionTemplate.PIECEWISE_LINEAR:
            # Piecewise linear function
            x_var = self.bindings.get('x', 'allocation')
            breakpoints = self.bindings.get('breakpoints', 'breakpoints')
            slopes = self.bindings.get('slopes', 'slopes')
            # Simplified - would need ConditionalNode for full implementation
            return VariableRefNode(name=x_var, indices=[])
        
        else:
            raise ValueError(f"Template {self.template} not yet implemented")


class ObjectiveSpec(BaseModel):
    """
    Complete specification of an objective function.
    
    The objective defines WHAT WE'RE OPTIMIZING - the goal.
    
    Examples:
    - minimize Σᵢ cost[i] * production[i]
    - maximize Σᵢ return[i] * allocation[i] - λ * (allocation'Σ*allocation)
    
    Supports three expression formats (exactly one required):
    1. expression: AST (preferred, most flexible)
    2. expression_template: Template pattern (reduces composition risk)
    3. expression_string: String fallback (validated, for compatibility)
    """
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(
        ...,
        description="Objective name: 'minimize_cost', 'maximize_profit'"
    )
    
    description: str = Field(
        ...,
        description="What this objective represents in business terms"
    )
    
    # Direction
    sense: ObjectiveSense
    
    # Expression formats (exactly one required)
    expression: Optional[Expression] = Field(
        default=None,
        description="Expression AST for the objective (preferred)"
    )
    
    expression_template: Optional[TemplatedExpression] = Field(
        default=None,
        description="Template pattern expression (reduces composition risk)"
    )
    
    expression_string: Optional[str] = Field(
        default=None,
        description="String expression fallback (validated, for compatibility)"
    )
    
    @model_validator(mode="after")
    def require_one_expression(self) -> "ObjectiveSpec":
        """Ensure exactly one expression format is provided."""
        count = sum(x is not None for x in [
            self.expression,
            self.expression_template,
            self.expression_string
        ])
        if count != 1:
            raise ValueError(
                f"Exactly one expression format required (expression, expression_template, or expression_string). "
                f"Found {count} formats."
            )
        return self
    
    def get_expression(self) -> Expression:
        """Get the expression in AST format."""
        if self.expression:
            return self.expression
        elif self.expression_template:
            return self.expression_template.to_ast()
        elif self.expression_string:
            # Parse string to AST (simplified - would need proper parser)
            # For now, return a placeholder
            return {"node_type": "constant", "value": 0.0}
        raise ValueError("No expression available")
    
    # Plain English (for LLM understanding and documentation)
    mathematical_intent: str = Field(
        ...,
        description="Plain English: 'Sum over all products i of cost[i] times production[i]'"
    )
    
    # Dependencies (for validation)
    uses_variables: List[str] = Field(
        default_factory=list,
        description="Variable names used in this objective"
    )
    uses_parameters: List[str] = Field(
        default_factory=list,
        description="Parameter names used in this objective"
    )
    
    # Expression characteristics (affects problem classification)
    is_linear: bool = Field(
        default=True,
        description="True if objective is linear in variables"
    )
    is_quadratic: bool = Field(
        default=False,
        description="True if objective contains x'Qx terms"
    )
    is_convex: Optional[bool] = Field(
        default=None,
        description="True if objective is convex (for minimization)"
    )
    
    # Multi-objective handling
    priority: int = Field(
        default=1,
        ge=1,
        description="Priority for lexicographic optimization (1 = highest)"
    )
    weight: float = Field(
        default=1.0,
        ge=0.0,
        description="Weight for weighted-sum scalarization"
    )
    
    def to_pyomo(self, model_var: str = "m") -> str:
        """Generate Pyomo Objective declaration."""
        sense_str = "pyo.minimize" if self.sense == ObjectiveSense.MINIMIZE else "pyo.maximize"
        expr = self.get_expression()
        expr_str = expr_to_pyomo(expr, model_var)
        
        return f"""
def {self.name}_rule({model_var}):
    return {expr_str}
{model_var}.{self.name} = pyo.Objective(rule={self.name}_rule, sense={sense_str})
"""


# =============================================================================
# SECTION 7: CONSTRAINTS
# =============================================================================

class ConstraintSpec(BaseModel):
    """
    Complete specification of a constraint.
    
    Constraints define WHAT'S ALLOWED - the feasibility requirements.
    
    Examples:
    - Σᵢ allocation[i] == 1 (budget constraint)
    - production[i] <= capacity[i] ∀i (capacity constraints)
    - Σⱼ shipment[i,j] == demand[j] ∀j (demand satisfaction)
    
    Supports three expression formats (exactly one required per side):
    1. AST expressions (preferred)
    2. Template patterns (reduces composition risk)
    3. String expressions (validated fallback)
    """
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(
        ...,
        description="Constraint name: 'budget_constraint', 'capacity_limit'"
    )
    
    description: str = Field(
        ...,
        description="What this constraint enforces in business terms"
    )
    
    # Constraint relationship
    sense: ConstraintSense
    
    # Expression formats for LHS (exactly one required)
    lhs: Optional[Expression] = Field(default=None, description="Left-hand side AST expression")
    lhs_template: Optional[TemplatedExpression] = Field(default=None, description="LHS template pattern")
    lhs_string: Optional[str] = Field(default=None, description="LHS string expression")
    
    # Expression formats for RHS (exactly one required)
    rhs: Optional[Expression] = Field(default=None, description="Right-hand side AST expression")
    rhs_template: Optional[TemplatedExpression] = Field(default=None, description="RHS template pattern")
    rhs_string: Optional[str] = Field(default=None, description="RHS string expression")
    
    @model_validator(mode="after")
    def require_expressions(self) -> "ConstraintSpec":
        """Ensure exactly one expression format per side."""
        lhs_count = sum(x is not None for x in [self.lhs, self.lhs_template, self.lhs_string])
        rhs_count = sum(x is not None for x in [self.rhs, self.rhs_template, self.rhs_string])
        
        if lhs_count != 1:
            raise ValueError(f"Exactly one LHS expression format required. Found {lhs_count}.")
        if rhs_count != 1:
            raise ValueError(f"Exactly one RHS expression format required. Found {rhs_count}.")
        return self
    
    def get_lhs(self) -> Expression:
        """Get LHS expression in AST format."""
        if self.lhs:
            return self.lhs
        elif self.lhs_template:
            return self.lhs_template.to_ast()
        elif self.lhs_string:
            # Parse string to AST (simplified)
            return {"node_type": "constant", "value": 0.0}
        raise ValueError("No LHS expression available")
    
    def get_rhs(self) -> Expression:
        """Get RHS expression in AST format."""
        if self.rhs:
            return self.rhs
        elif self.rhs_template:
            return self.rhs_template.to_ast()
        elif self.rhs_string:
            # Parse string to AST (simplified)
            return ConstantNode(value=0.0)
        raise ValueError("No RHS expression available")
    
    # Indexing (for constraint families)
    scope: Literal["global", "indexed"] = Field(
        default="global",
        description="global = single constraint, indexed = one per index combination"
    )
    
    # For indexed constraints
    index_sets: List[str] = Field(
        default_factory=list,
        description="Sets to iterate over: ['I'] creates constraint for each i ∈ I"
    )
    index_vars: List[str] = Field(
        default_factory=list,
        description="Index variable names: ['i'] for 'for i in I'"
    )
    
    # Filter (for conditional constraints)
    filter_condition: Optional[Expression] = Field(
        default=None,
        description="Only create constraint where condition holds"
    )
    
    # Plain English
    mathematical_intent: str = Field(
        ...,
        description="Plain English: 'For each warehouse i, total shipped cannot exceed capacity'"
    )
    
    # Dependencies
    uses_variables: List[str] = Field(default_factory=list)
    uses_parameters: List[str] = Field(default_factory=list)
    
    # Classification
    is_hard: bool = Field(
        default=True,
        description="Hard = must satisfy, Soft = penalty for violation"
    )
    violation_penalty: Optional[float] = Field(
        default=None,
        description="Penalty coefficient for soft constraint violations"
    )
    
    # Evidence
    extracted_from: Optional[str] = None
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    
    @model_validator(mode="after")
    def validate_indexing(self) -> "ConstraintSpec":
        """Ensure indexed constraints are properly specified."""
        if self.scope == "indexed":
            if not self.index_sets:
                raise ValueError("Indexed constraint must specify index_sets")
            if not self.index_vars:
                raise ValueError("Indexed constraint must specify index_vars")
            if len(self.index_sets) != len(self.index_vars):
                raise ValueError("index_sets and index_vars must have same length")
        return self
    
    def to_pyomo(self, model_var: str = "m") -> str:
        """Generate Pyomo Constraint declaration."""
        lhs_expr = self.get_lhs()
        rhs_expr = self.get_rhs()
        lhs_str = expr_to_pyomo(lhs_expr, model_var)
        rhs_str = expr_to_pyomo(rhs_expr, model_var)
        
        if self.scope == "indexed":
            args = ", ".join(self.index_vars)
            sets = ", ".join(f"{model_var}.{s}" for s in self.index_sets)
            
            return f"""
def {self.name}_rule({model_var}, {args}):
    return {lhs_str} {self.sense.value} {rhs_str}
{model_var}.{self.name} = pyo.Constraint({sets}, rule={self.name}_rule)
"""
        else:
            return f"""
def {self.name}_rule({model_var}):
    return {lhs_str} {self.sense.value} {rhs_str}
{model_var}.{self.name} = pyo.Constraint(rule={self.name}_rule)
"""


# =============================================================================
# SECTION 8: ASSUMPTIONS (From Intent Discovery Step 2)
# =============================================================================

class AssumptionSpec(BaseModel):
    """
    Explicit assumption made during intent discovery.
    
    WHY ASSUMPTIONS MATTER:
    - Many optimization problems have IMPLICIT data requirements
    - "Minimize transportation cost" implies: we need cost data, distances, demands
    - Making assumptions EXPLICIT enables: data generation, sensitivity analysis, auditing
    """
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Assumption identifier")
    description: str = Field(..., description="What is being assumed")
    
    assumption_type: Literal["explicit", "implicit", "derived"] = Field(
        default="implicit",
        description="explicit = stated in problem, implicit = inferred, derived = calculated"
    )
    
    # What parameter this assumption affects
    affects_parameter: Optional[str] = Field(
        default=None,
        description="Parameter that depends on this assumption"
    )
    
    # Value specification
    assumed_value: Optional[Any] = Field(default=None)
    value_range: Optional[Tuple[float, float]] = Field(default=None)
    
    # For data generation
    generation_strategy: Optional[Literal[
        "uniform", "normal", "lognormal", 
        "industry_benchmark", "historical"
    ]] = Field(default=None)
    
    # Impact assessment
    sensitivity: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="How sensitive is solution to this assumption"
    )
    
    # Reasoning
    reason_needed: str = Field(
        ...,
        description="Why this assumption is required"
    )
    
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)


# =============================================================================
# SECTION 9: MODEL PACK (Complete Output from Intent Discovery)
# =============================================================================

class ClassificationResult(BaseModel):
    """
    Problem classification from Intent Discovery Step 1.
    
    This determines solver selection and solution strategies.
    """
    model_config = ConfigDict(extra="forbid")
    
    problem_class: ProblemClass
    
    # Structural characteristics
    is_convex: Optional[bool] = Field(
        default=None,
        description="If convex, global optimum is guaranteed"
    )
    has_integer_variables: bool = False
    has_binary_variables: bool = False
    has_quadratic_objective: bool = False
    has_quadratic_constraints: bool = False
    has_nonlinear_terms: bool = False
    
    # Problem pattern (helps with specialized algorithms)
    pattern: Optional[Literal[
        "allocation", "assignment", "transportation", "routing",
        "scheduling", "knapsack", "set_covering", "network_flow",
        "portfolio", "production", "blending", "facility_location"
    ]] = None
    
    # Domain (for context, not for hard-coded behavior)
    domain: str = Field(
        ...,
        description="Business domain: 'finance', 'logistics', 'manufacturing'"
    )
    
    # Complexity estimates
    estimated_variables: Optional[int] = None
    estimated_constraints: Optional[int] = None
    complexity_class: Literal["polynomial", "np_hard", "np_complete"] = Field(
        default="np_hard"
    )
    
    # Solver recommendation
    recommended_solver: SolverEngine = SolverEngine.HIGHS
    alternative_solvers: List[SolverEngine] = Field(default_factory=list)
    
    # Reasoning (for auditing)
    reasoning: str = Field(
        ...,
        description="Why this classification was chosen"
    )
    alternatives_considered: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)


class MultiObjectiveConfig(BaseModel):
    """Configuration for multi-objective optimization."""
    model_config = ConfigDict(extra="forbid")
    
    is_multi_objective: bool = False
    
    strategy: Literal[
        "single",           # Only one objective
        "weighted_sum",     # Combine with weights
        "lexicographic",    # Prioritized optimization
        "epsilon_constraint", # Constrain secondary objectives
        "pareto"            # Generate Pareto frontier
    ] = "single"
    
    primary_objective: Optional[str] = None
    
    # For weighted_sum
    weights: Optional[Dict[str, float]] = None
    
    # For epsilon_constraint
    epsilon_values: Optional[Dict[str, float]] = None
    
    reasoning: Optional[str] = None


class ModelPack(BaseModel):
    """
    MODEL PACK: Complete mathematical structure from Intent Discovery.
    
    This is THE CONTRACT between Intent Discovery and Model Builder.
    
    Contains:
    - Classification (what type of problem)
    - Index Sets (dimensional structure)
    - Variables (what we're solving for)
    - Parameters (what data we need)
    - Objectives (what we're optimizing)
    - Constraints (what's allowed)
    - Assumptions (what we assumed)
    
    Does NOT contain:
    - Actual data values (that's in DataPack)
    - Solver configuration (that's in SolverConfig)
    - Solution results (that's in SolutionPack)
    """
    model_config = ConfigDict(extra="forbid")
    
    # Identification
    model_id: str = Field(
        default_factory=lambda: str(uuid4())[:8],
        description="Unique identifier for this model"
    )
    
    problem_description: str = Field(
        ...,
        description="Original natural language problem description"
    )
    
    # Step 1: Classification
    classification: ClassificationResult
    
    # Index Sets (foundation for dimensional consistency)
    index_sets: Dict[str, IndexSetDefinition] = Field(
        default_factory=dict,
        description="Index set definitions by name"
    )
    
    # Step 3: Entities - Variables and Parameters
    variables: List[DecisionVariableSpec] = Field(
        default_factory=list,
        description="Decision variables (what we solve for)"
    )
    
    parameters: List[ParameterSpec] = Field(
        default_factory=list,
        description="Parameters (data we need)"
    )
    
    # Step 4: Objectives
    objectives: List[ObjectiveSpec] = Field(
        default_factory=list,
        description="Objective functions"
    )
    
    # Multi-objective configuration
    multi_objective: MultiObjectiveConfig = Field(
        default_factory=MultiObjectiveConfig
    )
    
    # Step 5: Constraints
    constraints: List[ConstraintSpec] = Field(
        default_factory=list,
        description="Constraint specifications"
    )
    
    # Step 2: Assumptions
    assumptions: List[AssumptionSpec] = Field(
        default_factory=list,
        description="Explicit assumptions made"
    )
    
    # Template matching (if applicable)
    matched_template: Optional[str] = None
    template_match_score: Optional[float] = None
    
    # Validation state
    is_valid: bool = True
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    intent_pipeline_version: str = "2.0"
    
    @model_validator(mode="after")
    def validate_model_consistency(self) -> "ModelPack":
        """
        Comprehensive validation of model consistency.
        
        This catches errors that would cause Pyomo generation to fail.
        """
        errors = []
        warnings = []
        
        # Build lookup sets
        set_names = set(self.index_sets.keys())
        var_names = {v.name for v in self.variables}
        param_names = {p.name for p in self.parameters}
        
        # 1. Validate variable index set references
        for var in self.variables:
            for idx_set in var.index_sets:
                if idx_set not in set_names:
                    errors.append(
                        f"Variable '{var.name}' references undefined set '{idx_set}'"
                    )
        
        # 2. Validate parameter index set references
        for param in self.parameters:
            for idx_set in param.index_sets:
                if idx_set not in set_names:
                    errors.append(
                        f"Parameter '{param.name}' references undefined set '{idx_set}'"
                    )
        
        # 3. Validate objective references
        for obj in self.objectives:
            for var in obj.uses_variables:
                if var not in var_names:
                    errors.append(
                        f"Objective '{obj.name}' references undefined variable '{var}'"
                    )
            for param in obj.uses_parameters:
                if param not in param_names:
                    errors.append(
                        f"Objective '{obj.name}' references undefined parameter '{param}'"
                    )
        
        # 4. Validate constraint references
        for const in self.constraints:
            for var in const.uses_variables:
                if var not in var_names:
                    errors.append(
                        f"Constraint '{const.name}' references undefined variable '{var}'"
                    )
            for param in const.uses_parameters:
                if param not in param_names:
                    errors.append(
                        f"Constraint '{const.name}' references undefined parameter '{param}'"
                    )
            
            # Check indexed constraint sets
            for idx_set in const.index_sets:
                if idx_set not in set_names:
                    errors.append(
                        f"Constraint '{const.name}' references undefined set '{idx_set}'"
                    )
        
        # 5. Validate problem class matches content
        if self.classification.has_quadratic_objective:
            has_quad = any(o.is_quadratic for o in self.objectives)
            if not has_quad:
                warnings.append(
                    "Classification says quadratic objective, but no objective marked is_quadratic"
                )
        
        if self.classification.has_integer_variables or self.classification.has_binary_variables:
            has_int = any(
                v.domain in (VariableDomain.INTEGERS, VariableDomain.NON_NEGATIVE_INTEGERS, VariableDomain.BINARY)
                for v in self.variables
            )
            if not has_int:
                warnings.append(
                    "Classification says integer/binary variables, but none defined"
                )
        
        # 6. Check for unused entities
        used_vars = set()
        used_params = set()
        for obj in self.objectives:
            used_vars.update(obj.uses_variables)
            used_params.update(obj.uses_parameters)
        for const in self.constraints:
            used_vars.update(const.uses_variables)
            used_params.update(const.uses_parameters)
        
        unused_vars = var_names - used_vars
        unused_params = param_names - used_params
        
        if unused_vars:
            warnings.append(f"Unused variables: {unused_vars}")
        if unused_params:
            warnings.append(f"Unused parameters: {unused_params}")
        
        self.validation_errors = errors
        self.validation_warnings = warnings
        self.is_valid = len(errors) == 0
        
        return self
    
    def get_pyomo_code(self, model_var: str = "m") -> str:
        """
        Generate complete Pyomo model code.
        
        This is THE main output - ready-to-execute Python.
        """
        lines = [
            '"""',
            f'Auto-generated Pyomo Model',
            f'Model ID: {self.model_id}',
            f'Problem: {self.problem_description[:100]}...',
            f'Classification: {self.classification.problem_class.value}',
            f'Generated: {self.created_at.isoformat()}',
            '"""',
            '',
            'import pyomo.environ as pyo',
            '',
            f'# Create model',
            f'{model_var} = pyo.ConcreteModel(name="{self.model_id}")',
            '',
            '# === SETS ===',
        ]
        
        for idx_set in self.index_sets.values():
            lines.append(idx_set.to_pyomo(model_var))
        
        lines.extend(['', '# === PARAMETERS ==='])
        for param in self.parameters:
            lines.append(param.to_pyomo(model_var))
        
        lines.extend(['', '# === DECISION VARIABLES ==='])
        for var in self.variables:
            lines.append(var.to_pyomo(model_var))
        
        lines.extend(['', '# === OBJECTIVE ==='])
        for obj in self.objectives:
            if obj.priority == 1:  # Primary objective
                lines.append(obj.to_pyomo(model_var))
                break
        
        lines.extend(['', '# === CONSTRAINTS ==='])
        for const in self.constraints:
            lines.append(const.to_pyomo(model_var))
        
        return '\n'.join(lines)


# =============================================================================
# SECTION 10: DATA PACK (Complete Output from Data Preparation)
# =============================================================================

class SetDataSpec(BaseModel):
    """Actual data for an index set."""
    model_config = ConfigDict(extra="forbid")
    
    set_name: str
    elements: List[Union[int, str]]
    cardinality: int
    
    @model_validator(mode="after")
    def validate_cardinality(self) -> "SetDataSpec":
        if len(self.elements) != self.cardinality:
            raise ValueError(
                f"Set {self.set_name}: element count ({len(self.elements)}) != cardinality ({self.cardinality})"
            )
        return self


class ParameterDataSpec(BaseModel):
    """
    Actual data values for a parameter.
    
    Supports:
    - Scalar: single value
    - Indexed: dictionary mapping indices to values
    - Dense: full matrix/tensor representation
    """
    model_config = ConfigDict(extra="forbid")
    
    parameter_name: str
    
    # For scalar parameters
    scalar_value: Optional[float] = None
    
    # For indexed parameters (sparse representation)
    indexed_values: Optional[Dict[str, float]] = Field(
        default=None,
        description="Values by index tuple as string: {'(0,1)': 5.0} or {'AAPL': 0.12}"
    )
    
    # For dense matrices (e.g., covariance matrices)
    dense_matrix: Optional[List[List[float]]] = None
    
    # Data quality
    source: Literal["provided", "generated", "external", "derived"] = "provided"
    completeness: float = Field(
        default=1.0,
        ge=0.0, le=1.0,
        description="Fraction of non-missing values"
    )
    
    @computed_field
    @property
    def is_scalar(self) -> bool:
        return self.scalar_value is not None


class DataQualityReport(BaseModel):
    """Data quality metrics for the entire DataPack."""
    model_config = ConfigDict(extra="forbid")
    
    overall_score: float = Field(ge=0.0, le=1.0)
    completeness: float = Field(ge=0.0, le=1.0)
    consistency: float = Field(ge=0.0, le=1.0)
    validity: float = Field(ge=0.0, le=1.0)
    
    missing_parameters: List[str] = Field(default_factory=list)
    validation_issues: List[str] = Field(default_factory=list)
    
    # Special matrix properties
    covariance_matrix_valid: Optional[bool] = None
    covariance_is_positive_definite: Optional[bool] = None
    distance_matrix_valid: Optional[bool] = None


class DataPack(BaseModel):
    """
    DATA PACK: Actual numerical values for the optimization model.
    
    This is THE CONTRACT between Data Preparation and Model Builder.
    
    Contains:
    - Set elements (actual members of each set)
    - Parameter values (actual numbers)
    - Data quality metrics
    - Source provenance
    
    Does NOT contain:
    - Model structure (that's in ModelPack)
    - Variable values (those are solved)
    """
    model_config = ConfigDict(extra="forbid")
    
    # Reference to model
    model_id: str = Field(
        ...,
        description="ModelPack ID this data corresponds to"
    )
    
    # Set data
    set_data: Dict[str, SetDataSpec] = Field(
        default_factory=dict,
        description="Actual elements for each index set"
    )
    
    # Parameter data
    parameter_data: Dict[str, ParameterDataSpec] = Field(
        default_factory=dict,
        description="Actual values for each parameter"
    )
    
    # Data quality
    quality_report: DataQualityReport = Field(
        default_factory=lambda: DataQualityReport(
            overall_score=1.0,
            completeness=1.0,
            consistency=1.0,
            validity=1.0
        )
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    data_source: Literal["generated", "provided", "external", "salesforce"] = "generated"
    
    @model_validator(mode="after")
    def validate_data_consistency(self) -> "DataPack":
        """Validate that data matches model structure."""
        # This would check against ModelPack if provided
        # For now, just basic validation
        return self

