"""Module for calculating stresses in reinforced concrete beams."""


def calculate_steel_stresses(
    neutral_axis_depth: float,
    steel_depths: list[float],
    yield_stress: float,
    elastic_modulus: float = 200000,
    concrete_strain: float = 0.003,
) -> list[float]:
    """
    Calculate stresses (fs) on each steel bar aside from the far end which will yield.
    
    The far end steel (typically the deepest reinforcement) is assumed to yield,
    and stresses for other steel bars are calculated using strain compatibility.
    
    Args:
        neutral_axis_depth: Depth of neutral axis from compression face (c)
        steel_depths: List of effective depths (d) for each steel layer from compression face
                     The last element should be the far end steel that yields
        yield_stress: Yield stress of steel (fy)
        elastic_modulus: Modulus of elasticity of steel (Es). Defaults to 200000 MPa.
        concrete_strain: Strain at extreme compression fiber (εc). Defaults to 0.003.
    
    Returns:
        List of stresses (fs) for each steel bar. The last element will be yield_stress
        (for the far end steel that yields).
    
    Example:
        >>> c = 100  # mm
        >>> depths = [50, 100, 150]  # mm
        >>> fy = 400  # MPa
        >>> stresses = calculate_steel_stresses(c, depths, fy)
    """
    stresses = []
    
    # Calculate stress for each steel layer
    for i, d in enumerate(steel_depths):
        if i == len(steel_depths) - 1:
            # Far end steel yields
            stresses.append(yield_stress)
        else:
            # Calculate strain using compatibility: εs = εc * (d - c) / c
            if neutral_axis_depth > 0:
                strain = concrete_strain * (d - neutral_axis_depth) / neutral_axis_depth
            else:
                strain = 0.0
            
            # Calculate stress: fs = Es * εs (if elastic) or fy (if yielded)
            if strain >= yield_stress / elastic_modulus:
                # Steel has yielded
                stresses.append(yield_stress)
            else:
                # Steel is elastic
                stresses.append(elastic_modulus * strain)
    
    return stresses


def calculate_compression_block_height(
    far_end_depth: float,
    yield_stress: float,
    elastic_modulus: float = 200000,
    concrete_strain: float = 0.003,
) -> float:
    """
    Calculate compression block height (C) using stress/strain ratio and proportion.
    
    Assumes steel yields on the far end. Uses strain compatibility to find the
    neutral axis depth (C).
    
    Args:
        far_end_depth: Effective depth of far end steel from compression face (d)
        yield_stress: Yield stress of steel (fy)
        elastic_modulus: Modulus of elasticity of steel (Es). Defaults to 200000 MPa.
        concrete_strain: Strain at extreme compression fiber (εc). Defaults to 0.003.
    
    Returns:
        Compression block height (C), which is the neutral axis depth from compression face.
    
    Example:
        >>> d = 500  # mm
        >>> fy = 400  # MPa
        >>> c = calculate_compression_block_height(d, fy)
    """
    # Calculate yield strain
    yield_strain = yield_stress / elastic_modulus
    
    # From strain compatibility: εs = εc * (d - c) / c
    # When steel yields: fy/Es = εc * (d - c) / c
    # Solving for c: c = εc * d / (εc + fy/Es)
    if concrete_strain + yield_strain > 0:
        compression_block_height = (concrete_strain * far_end_depth) / (
            concrete_strain + yield_strain
        )
    else:
        compression_block_height = 0.0
    
    return compression_block_height

