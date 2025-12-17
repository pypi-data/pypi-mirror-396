"""
Converters for migrating from legacy format to ModelPack/DataPack.

This module provides adapter functions to convert the current loose dictionary
format to the new Pydantic-based ModelPack/DataPack schemas.

This enables gradual migration without breaking existing code.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from dcisionai_mcp_server.schemas.optimization_contracts import (
    ModelPack,
    DataPack,
    ClassificationResult,
    ProblemClass,
    SolverEngine,
    IndexSetDefinition,
    DecisionVariableSpec,
    ParameterSpec,
    ObjectiveSpec,
    ConstraintSpec,
    AssumptionSpec,
    ObjectiveSense,
    ConstraintSense,
    VariableDomain,
    Expression,
    ConstantNode,
    ParameterRefNode,
    VariableRefNode,
    SummationNode,
    BinaryOpNode,
    ExpressionNodeType,
    SetDataSpec,
    ParameterDataSpec,
    DataQualityReport,
)

logger = logging.getLogger(__name__)


def normalize_name(name: str) -> str:
    """
    Normalize variable/parameter names for consistent matching.
    
    Handles:
    - Case variations (camelCase, PascalCase, snake_case)
    - Whitespace
    - Common abbreviations
    """
    if not name:
        return ""
    
    # Convert to lowercase and replace spaces/underscores/hyphens
    normalized = name.lower().strip()
    normalized = normalized.replace(' ', '_').replace('-', '_')
    
    # Remove common prefixes/suffixes for matching
    # (Keep original for display, but normalize for matching)
    return normalized


def create_name_mapping(
    variables: List[Dict[str, Any]],
    parameters: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Create a mapping from normalized names to actual names.
    
    Returns:
        Dict mapping normalized_name -> actual_name
    """
    name_map = {}
    
    # Map variables
    for var in variables:
        actual_name = var.get('name', '')
        if actual_name:
            norm_name = normalize_name(actual_name)
            name_map[norm_name] = actual_name
            # Also map the actual name to itself
            name_map[actual_name] = actual_name
    
    # Map parameters
    for param in parameters:
        actual_name = param.get('name', '')
        if actual_name:
            norm_name = normalize_name(actual_name)
            name_map[norm_name] = actual_name
            # Also map the actual name to itself
            name_map[actual_name] = actual_name
    
    return name_map


def resolve_reference(
    ref_name: str,
    name_map: Dict[str, str],
    available_names: List[str],
    entity_type: str = "variable"
) -> Optional[str]:
    """
    Resolve a variable/parameter reference to its actual name.
    
    Args:
        ref_name: Reference name from objective/constraint
        name_map: Mapping from normalized to actual names
        available_names: List of actual available names
        entity_type: "variable" or "parameter"
    
    Returns:
        Resolved name if found, None otherwise
    """
    # Try exact match first
    if ref_name in available_names:
        return ref_name
    
    # Try normalized match
    norm_ref = normalize_name(ref_name)
    if norm_ref in name_map:
        resolved = name_map[norm_ref]
        if resolved in available_names:
            return resolved
    
    # Try fuzzy matching (handle common variations)
    # e.g., "project_allocation" vs "project_allocations" vs "projectAllocation"
    for available_name in available_names:
        norm_available = normalize_name(available_name)
        # Check if one contains the other (for pluralization, etc.)
        if norm_ref in norm_available or norm_available in norm_ref:
            # Check if they're similar enough (same base word)
            ref_words = set(norm_ref.split('_'))
            avail_words = set(norm_available.split('_'))
            # If they share significant words, consider it a match
            if ref_words & avail_words:  # Intersection
                return available_name
    
    logger.warning(f"Could not resolve {entity_type} reference '{ref_name}'")
    return None


def convert_classification_to_classification_result(
    classification_dict: Dict[str, Any]
) -> ClassificationResult:
    """Convert legacy classification dict to ClassificationResult."""
    
    # Map problem_type to ProblemClass
    problem_type = classification_dict.get('problem_type', 'unknown').upper()
    problem_class_map = {
        'LP': ProblemClass.LP,
        'QP': ProblemClass.QP,
        'MILP': ProblemClass.MILP,
        'MIQP': ProblemClass.MIQP,
        'NLP': ProblemClass.NLP,
        'MINLP': ProblemClass.MINLP,
    }
    
    # Try to infer from optimization_type
    opt_type = classification_dict.get('optimization_type', '').upper()
    if 'LINEAR' in opt_type and 'INTEGER' in opt_type:
        problem_class = ProblemClass.MILP
    elif 'LINEAR' in opt_type:
        problem_class = ProblemClass.LP
    elif 'QUADRATIC' in opt_type:
        problem_class = ProblemClass.QP
    else:
        problem_class = problem_class_map.get(problem_type, ProblemClass.LP)
    
    # Map solver recommendation
    solver_hint = classification_dict.get('recommended_solver', 'highs').lower()
    solver_map = {
        'highs': SolverEngine.HIGHS,
        'scip': SolverEngine.SCIP,
        'cbc': SolverEngine.CBC,
        'glpk': SolverEngine.GLPK,
    }
    recommended_solver = solver_map.get(solver_hint, SolverEngine.HIGHS)
    
    return ClassificationResult(
        problem_class=problem_class,
        is_convex=classification_dict.get('is_convex'),
        has_integer_variables=classification_dict.get('has_integer_variables', False),
        has_binary_variables=classification_dict.get('has_binary_variables', False),
        has_quadratic_objective=classification_dict.get('has_quadratic_objective', False),
        has_quadratic_constraints=classification_dict.get('has_quadratic_constraints', False),
        has_nonlinear_terms=classification_dict.get('has_nonlinear_terms', False),
        pattern=classification_dict.get('pattern'),
        domain=classification_dict.get('domain', 'unknown'),
        estimated_variables=classification_dict.get('estimated_variables'),
        estimated_constraints=classification_dict.get('estimated_constraints'),
        complexity_class=classification_dict.get('complexity_class', 'np_hard'),
        recommended_solver=recommended_solver,
        reasoning=classification_dict.get('reasoning', 'Classification from intent discovery'),
        confidence=classification_dict.get('confidence', 0.85)
    )


def convert_index_definitions_to_index_sets(
    index_definitions: Dict[str, Any]
) -> Dict[str, IndexSetDefinition]:
    """Convert legacy index_definitions to IndexSetDefinition dict."""
    index_sets = {}
    
    for symbol, idx_def in index_definitions.items():
        # Determine set type
        if 'values' in idx_def and idx_def['values']:
            set_type = "enumerated"
            elements = idx_def['values']
            cardinality = len(elements)
            range_start = None
            range_end = None
        elif 'range_start' in idx_def and 'range_end' in idx_def:
            set_type = "range"
            elements = None
            range_start = idx_def['range_start']
            range_end = idx_def['range_end']
            cardinality = idx_def.get('count', range_end - range_start + 1)
        else:
            # Default to range
            set_type = "range"
            elements = None
            range_start = 0
            range_end = idx_def.get('count', 1) - 1
            cardinality = idx_def.get('count', 1)
        
        # Extract name (use symbol if name not provided)
        name = idx_def.get('name', symbol.upper())
        
        index_sets[name] = IndexSetDefinition(
            name=name,
            index_symbol=symbol,
            description=idx_def.get('description', f'Index set for {symbol}'),
            set_type=set_type,
            elements=elements,
            range_start=range_start,
            range_end=range_end,
            cardinality=cardinality,
            extracted_from=idx_def.get('extracted_from')
        )
    
    return index_sets


def convert_variables_to_decision_variable_specs(
    variables: List[Dict[str, Any]],
    index_sets: Dict[str, IndexSetDefinition]
) -> List[DecisionVariableSpec]:
    """Convert legacy variables to DecisionVariableSpec list."""
    var_specs = []
    
    for var in variables:
        # Map domain
        domain_str = var.get('domain', 'nonnegative').lower()
        domain_map = {
            'nonnegative': VariableDomain.NON_NEGATIVE_REALS,
            'nonpositive': VariableDomain.NON_POSITIVE_REALS,
            'reals': VariableDomain.REALS,
            'binary': VariableDomain.BINARY,
            'integer': VariableDomain.INTEGERS,
            'nonnegative_integers': VariableDomain.NON_NEGATIVE_INTEGERS,
            'unit_interval': VariableDomain.UNIT_INTERVAL,
        }
        domain = domain_map.get(domain_str, VariableDomain.NON_NEGATIVE_REALS)
        
        # Extract index sets
        indices = var.get('indices', [])
        index_set_names = []
        for idx_symbol in indices:
            # Find corresponding index set name
            for set_name, set_def in index_sets.items():
                if set_def.index_symbol == idx_symbol:
                    index_set_names.append(set_name)
                    break
        
        # Extract bounds
        bounds_dict = var.get('bounds', {})
        from dcisionai_mcp_server.schemas.optimization_contracts import BoundsSpec
        bounds = BoundsSpec(
            lower=bounds_dict.get('lower'),
            upper=bounds_dict.get('upper'),
            lower_param=bounds_dict.get('lower_param'),
            upper_param=bounds_dict.get('upper_param')
        )
        
        var_specs.append(DecisionVariableSpec(
            name=var.get('name', 'unknown'),
            description=var.get('description', ''),
            domain=domain,
            index_sets=index_set_names,
            bounds=bounds,
            total_dimensions=var.get('total_dimensions', 1),
            unit=var.get('unit'),
            business_interpretation=var.get('business_interpretation'),
            initial_value=var.get('initial_value'),
            extracted_from=var.get('extracted_from'),
            confidence=var.get('confidence', 0.9)
        ))
    
    return var_specs


def convert_parameters_to_parameter_specs(
    parameters: List[Dict[str, Any]],
    index_sets: Dict[str, IndexSetDefinition]
) -> List[ParameterSpec]:
    """Convert legacy parameters to ParameterSpec list."""
    param_specs = []
    
    for param in parameters:
        # Determine structure
        indices = param.get('indices', [])
        structure = "scalar" if not indices else "indexed"
        
        # Extract index sets
        index_set_names = []
        for idx_symbol in indices:
            for set_name, set_def in index_sets.items():
                if set_def.index_symbol == idx_symbol:
                    index_set_names.append(set_name)
                    break
        
        param_specs.append(ParameterSpec(
            name=param.get('name', 'unknown'),
            description=param.get('description', ''),
            structure=structure,
            index_sets=index_set_names,
            data_type=param.get('data_type', 'float'),
            must_be_positive=param.get('must_be_positive', False),
            must_be_nonnegative=param.get('must_be_nonnegative', False),
            valid_range=param.get('valid_range'),
            source=param.get('source', 'assumption'),
            default_value=param.get('value'),
            unit=param.get('unit'),
            is_covariance_matrix=param.get('is_covariance_matrix', False),
            is_distance_matrix=param.get('is_distance_matrix', False),
            extracted_from=param.get('extracted_from'),
            confidence=param.get('confidence', 0.9)
        ))
    
    return param_specs


def parse_formula_to_ast(formula_text: str, variables: List[str], parameters: List[str]) -> Expression:
    """
    Parse formula string to AST expression.
    
    This is a simplified parser that handles common cases.
    For complex formulas, LLM should generate AST directly.
    """
    # For now, return a simple structure that can be converted
    # In Phase 3, LLM should generate AST directly
    
    # Try to detect simple patterns
    if formula_text.startswith('sum(') or 'sum(' in formula_text:
        # Simple summation - create SummationNode
        # Extract variable and parameter references
        # This is a placeholder - full implementation would parse properly
        return {
            "node_type": "sum",
            "expression": {
                "node_type": "binary",
                "operator": "*",
                "left": {"node_type": "param", "name": parameters[0] if parameters else "cost", "indices": ["i"]},
                "right": {"node_type": "var", "name": variables[0] if variables else "x", "indices": ["i"]}
            },
            "index_var": "i",
            "over_set": "I"
        }
    
    # Default: return as dict (will be converted by expr_to_pyomo)
    return {"node_type": "constant", "value": 0.0}


def convert_objectives_to_objective_specs(
    objectives: List[Dict[str, Any]],
    variables: List[str],
    parameters: List[str],
    name_map: Optional[Dict[str, str]] = None
) -> List[ObjectiveSpec]:
    """Convert legacy objectives to ObjectiveSpec list."""
    obj_specs = []
    
    if name_map is None:
        name_map = {}
    
    for obj in objectives:
        # Map direction
        direction = obj.get('direction', 'minimize').lower()
        sense = ObjectiveSense.MINIMIZE if direction == 'minimize' else ObjectiveSense.MAXIMIZE
        
        # Resolve variable references
        raw_var_refs = obj.get('uses_variables', [])
        resolved_vars = []
        unresolved_vars = []
        for var_ref in raw_var_refs:
            resolved = resolve_reference(var_ref, name_map, variables, "variable")
            if resolved:
                resolved_vars.append(resolved)
            else:
                unresolved_vars.append(var_ref)
        
        # Resolve parameter references
        raw_param_refs = obj.get('uses_parameters', [])
        resolved_params = []
        unresolved_params = []
        for param_ref in raw_param_refs:
            resolved = resolve_reference(param_ref, name_map, parameters, "parameter")
            if resolved:
                resolved_params.append(resolved)
            else:
                unresolved_params.append(param_ref)
        
        # Log warnings for unresolved references
        if unresolved_vars:
            logger.warning(
                f"Objective '{obj.get('name', 'unknown')}' references undefined variables: {unresolved_vars}. "
                f"Available variables: {variables}"
            )
        if unresolved_params:
            logger.warning(
                f"Objective '{obj.get('name', 'unknown')}' references undefined parameters: {unresolved_params}. "
                f"Available parameters: {parameters}"
            )
        
        # Parse expression (for now, use formula_text if available)
        formula_text = obj.get('formula_text') or obj.get('mathematical_intent', '')
        expression = parse_formula_to_ast(formula_text, resolved_vars, resolved_params)
        
        obj_specs.append(ObjectiveSpec(
            name=obj.get('name', 'objective'),
            description=obj.get('description', ''),
            sense=sense,
            expression=expression,
            mathematical_intent=obj.get('mathematical_intent', ''),
            uses_variables=resolved_vars,  # Use resolved names
            uses_parameters=resolved_params,  # Use resolved names
            is_linear=obj.get('is_linear', True),
            is_quadratic=obj.get('is_quadratic', False),
            priority=obj.get('priority', 1),
            weight=obj.get('weight', 1.0)
        ))
    
    return obj_specs


def convert_constraints_to_constraint_specs(
    constraints: List[Dict[str, Any]],
    variables: List[str],
    parameters: List[str],
    name_map: Optional[Dict[str, str]] = None
) -> List[ConstraintSpec]:
    """Convert legacy constraints to ConstraintSpec list."""
    const_specs = []
    
    if name_map is None:
        name_map = {}
    
    for const in constraints:
        # Map sense
        const_type = const.get('type', 'inequality').lower()
        if const_type == 'equality':
            sense = ConstraintSense.EQ
        elif '>=' in const.get('formula_text', ''):
            sense = ConstraintSense.GE
        else:
            sense = ConstraintSense.LE
        
        # Resolve variable references
        raw_var_refs = const.get('uses_variables', [])
        resolved_vars = []
        unresolved_vars = []
        for var_ref in raw_var_refs:
            resolved = resolve_reference(var_ref, name_map, variables, "variable")
            if resolved:
                resolved_vars.append(resolved)
            else:
                unresolved_vars.append(var_ref)
        
        # Resolve parameter references
        raw_param_refs = const.get('uses_parameters', [])
        resolved_params = []
        unresolved_params = []
        for param_ref in raw_param_refs:
            resolved = resolve_reference(param_ref, name_map, parameters, "parameter")
            if resolved:
                resolved_params.append(resolved)
            else:
                unresolved_params.append(param_ref)
        
        # Log warnings for unresolved references
        if unresolved_vars:
            logger.warning(
                f"Constraint '{const.get('name', 'unknown')}' references undefined variables: {unresolved_vars}. "
                f"Available variables: {variables}"
            )
        if unresolved_params:
            logger.warning(
                f"Constraint '{const.get('name', 'unknown')}' references undefined parameters: {unresolved_params}. "
                f"Available parameters: {parameters}"
            )
        
        # Parse expressions
        formula_text = const.get('formula_text', '')
        # For now, create simple expressions
        # In Phase 3, LLM should generate AST directly
        lhs = parse_formula_to_ast(formula_text, resolved_vars, resolved_params)
        rhs = ConstantNode(value=const.get('rhs_value', 0.0))
        
        const_specs.append(ConstraintSpec(
            name=const.get('name', 'constraint'),
            description=const.get('description', ''),
            sense=sense,
            lhs=lhs,
            rhs=rhs,
            scope="indexed" if const.get('applies_to', '').startswith('for_each') else "global",
            index_sets=const.get('index_sets', []),
            index_vars=const.get('index_vars', []),
            mathematical_intent=const.get('mathematical_intent', ''),
            uses_variables=resolved_vars,  # Use resolved names
            uses_parameters=resolved_params,  # Use resolved names
            is_hard=const.get('rigidity', 'hard') == 'hard',
            extracted_from=const.get('extracted_from'),
            confidence=const.get('confidence', 0.9)
        ))
    
    return const_specs


def convert_assumptions_to_assumption_specs(
    assumptions: List[Dict[str, Any]]
) -> List[AssumptionSpec]:
    """Convert legacy assumptions to AssumptionSpec list."""
    return [
        AssumptionSpec(
            name=ass.get('parameter', f'assumption_{i}'),
            description=ass.get('description', ''),
            assumption_type=ass.get('assumption_type', 'implicit'),
            affects_parameter=ass.get('parameter'),
            assumed_value=ass.get('value'),
            value_range=ass.get('value_range'),
            generation_strategy=ass.get('generation_strategy'),
            sensitivity=ass.get('sensitivity', 'medium'),
            reason_needed=ass.get('reasoning', 'Required for optimization'),
            confidence=ass.get('confidence', 0.7)
        )
        for i, ass in enumerate(assumptions)
    ]


def convert_intent_to_model_pack(intent_dict: Dict[str, Any]) -> ModelPack:
    """
    Convert legacy intent discovery output to ModelPack.
    
    Handles multiple input formats:
    1. Direct format: intent_dict has 'decision_variables', 'objectives', etc. at top level
    2. Step format: intent_dict has 'step3_entities', 'step4_objectives', etc.
    3. Final spec format: intent_dict has 'final_specification' with nested structure
    """
    # Handle step format (from graph result)
    if 'step3_entities' in intent_dict or 'step4_objectives' in intent_dict:
        # Extract from step format
        step3 = intent_dict.get('step3_entities', {})
        step4 = intent_dict.get('step4_objectives', {})
        step5 = intent_dict.get('step5_constraints', {})
        step2 = intent_dict.get('step2_assumptions', {})
        step1 = intent_dict.get('step1_classification', {})
        
        # Extract from step results (handle multiple possible structures)
        # Try 'result' first, then direct keys, then 'entities' for step3
        entities_result = step3.get('result', {})
        if not entities_result and 'entities' in step3:
            # Some formats have entities directly
            entities_result = step3.get('entities', {})
        
        if isinstance(entities_result, dict):
            index_definitions = entities_result.get('index_definitions', {})
            variables = entities_result.get('decision_variables', [])
            parameters = entities_result.get('parameters', [])
        else:
            index_definitions = {}
            variables = []
            parameters = []
        
        # Extract objectives (can be list or nested in dict)
        objectives_result = step4.get('result', {})
        if isinstance(objectives_result, dict) and 'objectives' in objectives_result:
            objectives = objectives_result['objectives']
        elif 'objectives' in step4:
            objectives = step4['objectives']
        else:
            objectives = []
        
        # Ensure objectives is a list
        if not isinstance(objectives, list):
            objectives = []
        
        # Extract constraints (can be list or nested in dict)
        constraints_result = step5.get('result', {})
        if isinstance(constraints_result, dict) and 'constraints' in constraints_result:
            constraints = constraints_result['constraints']
        elif 'constraints' in step5:
            constraints = step5['constraints']
        else:
            constraints = []
        
        # Ensure constraints is a list
        if not isinstance(constraints, list):
            constraints = []
        
        # Extract assumptions
        assumptions_result = step2.get('result', {})
        if isinstance(assumptions_result, dict):
            assumptions = assumptions_result.get('assumptions', [])
        elif 'assumptions' in step2:
            assumptions = step2.get('assumptions', [])
        else:
            assumptions = []
        
        # Extract classification
        classification_dict = step1.get('result', {})
        if not classification_dict and 'classification' in step1:
            classification_dict = step1.get('classification', {})
    else:
        # Direct format or final_spec format
        if 'final_specification' in intent_dict:
            final_spec = intent_dict['final_specification']
            classification_dict = final_spec.get('classification', {})
            index_definitions = final_spec.get('index_definitions', {})
            variables = final_spec.get('decision_variables', [])
            parameters = final_spec.get('parameters', [])
            objectives = final_spec.get('objectives', [])
            constraints = final_spec.get('constraints', [])
            assumptions = final_spec.get('assumptions', [])
        else:
            # Direct format
            classification_dict = intent_dict.get('classification', {})
            index_definitions = intent_dict.get('index_definitions', {})
            variables = intent_dict.get('decision_variables', [])
            parameters = intent_dict.get('parameters', [])
            objectives = intent_dict.get('objectives', [])
            constraints = intent_dict.get('constraints', [])
            assumptions = intent_dict.get('assumptions', [])
    
    # Convert classification
    classification = convert_classification_to_classification_result(classification_dict)
    
    # Convert index sets
    index_sets = convert_index_definitions_to_index_sets(index_definitions)
    
    # Convert variables
    var_specs = convert_variables_to_decision_variable_specs(variables, index_sets)
    var_names = [v.name for v in var_specs]
    
    # Convert parameters
    param_specs = convert_parameters_to_parameter_specs(parameters, index_sets)
    param_names = [p.name for p in param_specs]
    
    # Create name mapping for reference resolution
    name_map = create_name_mapping(variables, parameters)
    
    # Convert objectives with name resolution
    obj_specs = convert_objectives_to_objective_specs(
        objectives, 
        var_names, 
        param_names,
        name_map=name_map
    )
    
    # Convert constraints with name resolution
    const_specs = convert_constraints_to_constraint_specs(
        constraints, 
        var_names, 
        param_names,
        name_map=name_map
    )
    
    # Convert assumptions
    assumption_specs = convert_assumptions_to_assumption_specs(assumptions)
    
    # Create ModelPack
    model_pack = ModelPack(
        problem_description=intent_dict.get('problem_description', ''),
        classification=classification,
        index_sets=index_sets,
        variables=var_specs,
        parameters=param_specs,
        objectives=obj_specs,
        constraints=const_specs,
        assumptions=assumption_specs,
        matched_template=intent_dict.get('matched_template'),
        template_match_score=intent_dict.get('template_match_score')
    )
    
    return model_pack


def convert_data_pack_to_data_pack(data_dict: Dict[str, Any], model_id: str) -> DataPack:
    """
    Convert legacy data_pack dict to DataPack.
    
    Args:
        data_dict: Legacy data_pack dictionary
        model_id: ModelPack ID this data corresponds to
    """
    # Convert set data
    set_data = {}
    sets_dict = data_dict.get('sets', {})
    for set_name, elements in sets_dict.items():
        set_data[set_name] = SetDataSpec(
            set_name=set_name,
            elements=elements if isinstance(elements, list) else list(elements),
            cardinality=len(elements) if isinstance(elements, list) else 1
        )
    
    # Convert parameter data
    parameter_data = {}
    params_dict = data_dict.get('parameters', {})
    records = data_dict.get('records', [])
    metadata = data_dict.get('metadata', {})
    
    # Process scalar parameters from metadata
    for param_name, value in metadata.items():
        if isinstance(value, (int, float)):
            parameter_data[param_name] = ParameterDataSpec(
                parameter_name=param_name,
                scalar_value=float(value),
                source="provided"
            )
    
    # Process indexed parameters from records
    # This is simplified - full implementation would handle complex indexing
    for record in records:
        for key, value in record.items():
            if key not in parameter_data and isinstance(value, (int, float)):
                # Create indexed parameter entry
                if key not in parameter_data:
                    parameter_data[key] = ParameterDataSpec(
                        parameter_name=key,
                        indexed_values={},
                        source="provided"
                    )
                # Add indexed value (simplified - would need proper indexing)
                if parameter_data[key].indexed_values is None:
                    parameter_data[key].indexed_values = {}
                record_id = record.get('id', str(len(parameter_data[key].indexed_values)))
                parameter_data[key].indexed_values[record_id] = float(value)
    
    # Create DataPack
    data_pack = DataPack(
        model_id=model_id,
        set_data=set_data,
        parameter_data=parameter_data,
        quality_report=DataQualityReport(
            overall_score=1.0,
            completeness=1.0,
            consistency=1.0,
            validity=1.0
        ),
        data_source=data_dict.get('data_source', 'generated')
    )
    
    return data_pack

