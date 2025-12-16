# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from dataclasses import dataclass
from enum import Enum

from ._parameters import Parameter, Parameters
from ._examples import Example, Examples


@dataclass(frozen=True)
class Requirement:
    """
    Args:
        code: A unique identifier of the requirement
        display_name: A human-readable name of the requirement
        message: A basic description of the requirement
        path: Relative path in documentation
        compatibility: Compatibility of the requirement
        tags: Tags of the requirement
        parameters: Parameters of the requirement
    """
    code: str
    version: str | None = None
    display_name: str | None = None
    message: str | None = None
    path: str | None = None
    compatibility: str | None = None
    tags: tuple[str, ...] = ()
    parameters: tuple[Parameter, ...] = ()
    examples: tuple[Example, ...] = ()

class Requirements(Requirement, Enum):
    """
    An enumeration of all requirements.
    """
    VM_MDL_001 = (
        "VM.MDL.001",
        "1.0.0",
        "material-mdl-source-asset",
        "MDL material source assets must be properly referenced and accessible to ensure material loading and rendering.",
        "capabilities/materials/requirements/material-mdl-source-asset.html",
        "Open USD",
        ("correctness",),
        (),
        (),
    )
    VM_D_001 = (
        "VM.D.001",
        "1.0.0",
        "material-duplicates",
        "Using fewer materials can result in better performance.",
        "capabilities/materials/requirements/material-duplicates.html",
        "Open USD",
        ("performance",),
        (),
        (),
    )
    VM_PS_001 = (
        "VM.PS.001",
        "1.0.0",
        "material-preview-surface",
        "Material attributes must comply with the UsdPreviewSurface specification to ensure consistent rendering and viewer compatibility.",
        "capabilities/materials/requirements/material-preview-surface.html",
        "Open USD",
        ("correctness",),
        (),
        (),
    )
    VM_BIND_001 = (
        "VM.BIND.001",
        "1.0.0",
        "material-bind-scope",
        "Material bindings must use appropriate scope to ensure proper material assignment and inheritance.",
        "capabilities/materials/requirements/material-bind-scope.html",
        "Open USD",
        ("correctness",),
        (),
        (),
    )
    VM_MDL_002 = (
        "VM.MDL.002",
        "1.0.0",
        "material-mdl-schema",
        "MDL Shaders must standard OpenUSD shader source attributes to ensure compatibility.",
        "capabilities/materials/requirements/material-mdl-schema.html",
        "Kit-107.0+",
        ("correctness",),
        (),
        (),
    )
    JT_ART_003 = (
        "JT.ART.003",
        "1.0.0",
        "articulation-not-on-kinematic-body",
        "In PhysX based simulators, like Omniverse Isaac Sim, Articulations are not allowed on kinematic bodies.",
        "capabilities/physics_bodies/physics_joints/requirements/articulation-not-on-kinematic-body.html",
        "PhysX",
        ("limitation",),
        (),
        (),
    )
    JT_003 = (
        "JT.003",
        "1.0.0",
        "joint-no-multiple-body-targets",
        "Body0 and Body1 relationships must not have more than one target.",
        "capabilities/physics_bodies/physics_joints/requirements/joint-no-multiple-body-targets.html",
        "OpenUSD",
        ("correctness",),
        (),
        (),
    )
    JT_002 = (
        "JT.002",
        "1.0.0",
        "joint-body-target-exists",
        "Targets set to Body0 and Body1 relationships must exist.",
        "capabilities/physics_bodies/physics_joints/requirements/joint-body-target-exists.html",
        "OpenUSD",
        ("correctness",),
        (),
        (),
    )
    JT_ART_002 = (
        "JT.ART.002",
        "1.0.0",
        "articulation-no-nesting",
        "Articulation roots cannot be nested.",
        "capabilities/physics_bodies/physics_joints/requirements/articulation-no-nesting.html",
        "OpenUSD",
        ("correctness",),
        (),
        (),
    )
    JT_001 = (
        "JT.001",
        "1.0.0",
        "joint-capability",
        "Rigid bodies which are not free floating should be connected using joints.",
        "capabilities/physics_bodies/physics_joints/requirements/joint-capability.html",
        "OpenUSD",
        ("essential",),
        (),
        (),
    )
    JT_ART_001 = (
        "JT.ART.001",
        "1.0.0",
        "articulation",
        "For stable and fast simulations of kinematic chains, an asset should define an articulation.",
        "capabilities/physics_bodies/physics_joints/requirements/articulation.html",
        "OpenUSD",
        ("high-quality",),
        (),
        (),
    )
    JT_ART_004 = (
        "JT.ART.004",
        "1.0.0",
        "articulation-not-on-static-body",
        "Articulations are not allowed on static bodies.",
        "capabilities/physics_bodies/physics_joints/requirements/articulation-not-on-static-body.html",
        "OpenUSD",
        ("correctness",),
        (),
        (),
    )
    UN_007 = (
        "UN.007",
        "1.0.0",
        "meters-per-unit-1",
        "Stage must specify metersPerUnit = 1.0 to define the linear unit scale",
        "capabilities/core/units/requirements/meters-per-unit-1.html",
        "core-usd",
        ("essential",),
        (),
        (
            Examples.NO_METERSPERUNIT_SPECIFIED_NOK,
            Examples.METERSPERUNIT_NOT_SET_TO_1_0_NOK,
            Examples.METERSPERUNIT_1_0_OK,
        ),
    )
    UN_006 = (
        "UN.006",
        "1.0.0",
        "upaxis-z",
        "Stage must specify upAxis = \"Z\" to define the orientation of the stage",
        "capabilities/core/units/requirements/upaxis-z.html",
        "core-usd",
        ("essential",),
        (),
        (),
    )
    UN_005 = (
        "UN.005",
        "1.0.0",
        "timecodes-per-second",
        "Stage must specify timeCodesPerSecond, if timesamples are present in the stage.",
        "capabilities/core/units/requirements/timecodes-per-second.html",
        "core-usd",
        ("correctness",),
        (),
        (),
    )
    UN_004 = (
        "UN.004",
        "1.0.0",
        "corrective-transforms",
        "Must apply corrective transforms for different units",
        "capabilities/core/units/requirements/corrective-transforms.html",
        "core-usd",
        ("correctness",),
        (),
        (),
    )
    UN_001 = (
        "UN.001",
        "1.0.0",
        "upaxis",
        "Stage must specify upAxis to define the orientation of the stage",
        "capabilities/core/units/requirements/upaxis.html",
        "core-usd",
        ("essential",),
        (),
        (),
    )
    UN_002 = (
        "UN.002",
        "1.0.0",
        "meters-per-unit",
        "Stage must specify metersPerUnit to define the linear unit scale",
        "capabilities/core/units/requirements/meters-per-unit.html",
        "core-usd",
        ("essential",),
        (),
        (),
    )
    UN_003 = (
        "UN.003",
        "1.0.0",
        "kilograms-per-unit",
        "Stage must specify kilogramsPerUnit to define the mass unit scale, if physics objects are present in the stage.",
        "capabilities/core/units/requirements/kilograms-per-unit.html",
        "core-usd",
        ("correctness",),
        (),
        (),
    )
    RB_006 = (
        "RB.006",
        "1.0.0",
        "rigid-body-no-nesting",
        "In PhysX based simulators, like Omniverse Isaac Sim, Rigid bodies can not be nested unless xformOp reset xform stack is used.",
        "capabilities/physics_bodies/physics_rigid_bodies/requirements/rigid-body-no-nesting.html",
        "PhysX",
        ("limitation",),
        (),
        (),
    )
    RB_COL_002 = (
        "RB.COL.002",
        "1.0.0",
        "static-collider",
        "If an asset is expected to be static (no movement happens), it can not contain a rigid body, only a Collider body.",
        "capabilities/physics_bodies/physics_rigid_bodies/requirements/static-collider.html",
        "OpenUSD",
        ("correctness",),
        (),
        (),
    )
    RB_009 = (
        "RB.009",
        "1.0.0",
        "rigid-body-schema-no-skew-matrix",
        "Rigid bodies have to be UsdGeomXformable prims without skew matrix.",
        "capabilities/physics_bodies/physics_rigid_bodies/requirements/rigid-body-schema-no-skew-matrix.html",
        "OpenUSD",
        ("correctness",),
        (),
        (),
    )
    RB_COL_004 = (
        "RB.COL.004",
        "1.0.0",
        "collider-non-uniform-scale",
        "The collision shape scale must be uniform for the following geometries: Sphere, Capsule, Cylinder, Cone \u0026 Points.",
        "capabilities/physics_bodies/physics_rigid_bodies/requirements/collider-non-uniform-scale.html",
        "OpenUSD",
        ("correctness",),
        (),
        (),
    )
    RB_003 = (
        "RB.003",
        "1.0.0",
        "rigid-body-schema-application",
        "Rigid bodies have to be UsdGeomXformable prims.",
        "capabilities/physics_bodies/physics_rigid_bodies/requirements/rigid-body-schema-application.html",
        "OpenUSD",
        ("correctness",),
        (),
        (),
    )
    RB_COL_003 = (
        "RB.COL.003",
        "1.0.0",
        "collider-mesh",
        "The Mesh Collision API can only be assigned to Mesh Prims.",
        "capabilities/physics_bodies/physics_rigid_bodies/requirements/collider-mesh.html",
        "OpenUSD",
        ("correctness",),
        (),
        (),
    )
    RB_001 = (
        "RB.001",
        "1.0.0",
        "rigid-body-capability",
        "Assets must contain at least one rigid body",
        "capabilities/physics_bodies/physics_rigid_bodies/requirements/rigid-body-capability.html",
        "OpenUSD",
        ("essential",),
        (),
        (),
    )
    RB_007 = (
        "RB.007",
        "1.0.0",
        "rigid-body-mass",
        "Rigid bodies _or_ their descendent collision shapes should have a mass \u0026 their other inertial properties explicitly specified.",
        "capabilities/physics_bodies/physics_rigid_bodies/requirements/rigid-body-mass.html",
        "OpenUSD",
        ("high-quality",),
        (),
        (),
    )
    RB_COL_001 = (
        "RB.COL.001",
        "1.0.0",
        "collider-capability",
        "Colliding Gprims must apply the Collision API.",
        "capabilities/physics_bodies/physics_rigid_bodies/requirements/collider-capability.html",
        "OpenUSD",
        ("essential",),
        (),
        (),
    )
    RB_005 = (
        "RB.005",
        "1.0.0",
        "rigid-body-no-instancing",
        "Rigid bodies cannot be part of a scene graph instance.",
        "capabilities/physics_bodies/physics_rigid_bodies/requirements/rigid-body-no-instancing.html",
        "OpenUSD",
        ("correctness",),
        (),
        (),
    )
    AA_002 = (
        "AA.002",
        "1.0.0",
        "supported-file-types",
        "Asset must use only supported file types",
        "capabilities/core/atomic_asset/requirements/supported-file-types.html",
        "OpenUSD",
        ("essential",),
        (),
        (),
    )
    AA_OV_001 = (
        "AA.OV.001",
        "1.0.0",
        "ov-usdz-udim-limitation",
        "Texture UDIMs are not supported in USDZ files in NVIDIA Omniverse",
        "capabilities/core/atomic_asset/requirements/ov-usdz-udim-limitation.html",
        "kit",
        ("limitation",),
        (),
        (),
    )
    AA_001 = (
        "AA.001",
        "1.0.0",
        "anchored-asset-paths",
        "Asset references should use anchored paths",
        "capabilities/core/atomic_asset/requirements/anchored-asset-paths.html",
        "core-usd",
        ("essential",),
        (),
        (),
    )
    SL_003 = (
        "SL.003",
        "1.0.0",
        "semantic-label-schema",
        "Semantic labels must use the SemanticsLabelsAPI schema",
        "capabilities/semantic_labels/requirements/semantic-label-schema.html",
        "open-usd",
        ("correctness",),
        (),
        (),
    )
    SL_NV_002 = (
        "SL.NV.002",
        "1.0.0",
        "semantic-label-time",
        "Semantic label attributes must not contain time samples",
        "capabilities/semantic_labels/requirements/semantic-label-time.html",
        "rtx",
        ("limitation",),
        (),
        (),
    )
    SL_001 = (
        "SL.001",
        "1.0.0",
        "semantic-label-capability",
        "All geometry prims must be semantically labeled.",
        "capabilities/semantic_labels/requirements/semantic-label-capability.html",
        "core-usd",
        ("essential",),
        (),
        (),
    )
    SL_QCODE_001 = (
        "SL.QCODE.001",
        "1.0.0",
        "semantic-label-qcode-valid",
        "If the Wikidata ontology is used, Q-Codes must be valid, properly formatted, and retrievable from wikidata.org.",
        "capabilities/semantic_labels/requirements/semantic-label-qcode-valid.html",
        "nvidia-omniverse",
        ("correctness",),
        (),
        (),
    )
    HI_005 = (
        "HI.005",
        "1.0.0",
        "xform-common-api-usage",
        "Transformations on prims representing objects or groups that require placement should conform to the UsdGeomXformCommonAPI.",
        "capabilities/hierarchy/requirements/xform-common-api-usage.html",
        "OpenUSD",
        ("correctness",),
        (),
        (),
    )
    HI_011 = (
        "HI.011",
        "1.0.0",
        "many-children",
        "Avoid large numbers of child prims under a parent xform",
        "capabilities/hierarchy/requirements/many-children.html",
        "OpenUSD",
        ("performance",),
        (),
        (
            Examples.MANY_CHILDREN_UNDER_A_SINGLE_PRIM_NOK,
            Examples.CHILDREN_DISTRIBUTED_AMONG_MULTIPLE_PRIMS_OK,
        ),
    )
    HI_003 = (
        "HI.003",
        "1.0.0",
        "root-is-xformable",
        "The root prim of the asset hierarchy must be transformable",
        "capabilities/hierarchy/requirements/root-is-xformable.html",
        "hierarchy-usd",
        ("essential",),
        (),
        (),
    )
    HI_004 = (
        "HI.004",
        "1.0.0",
        "stage-has-default-prim",
        "Stage must specify a default prim to define the root entry point.",
        "capabilities/hierarchy/requirements/stage-has-default-prim.html",
        "OpenUSD",
        ("essential",),
        (),
        (),
    )
    HI_008 = (
        "HI.008",
        "1.0.0",
        "logical-geometry-grouping",
        "Geometry should be grouped in a way that is logical for the object\u0027s structure.",
        "capabilities/hierarchy/requirements/logical-geometry-grouping.html",
        "OpenUSD",
        ("correctness",),
        (),
        (),
    )
    HI_001 = (
        "HI.001",
        "1.0.0",
        "hierarchy-has-root",
        "Prim hierarchy must have a single root prim.",
        "capabilities/hierarchy/requirements/hierarchy-has-root.html",
        "OpenUSD",
        ("essential",),
        (),
        (),
    )
    HI_012 = (
        "HI.012",
        "1.0.0",
        "empty-leaves",
        "Avoid empty leaf nodes in scene hierarchy",
        "capabilities/hierarchy/requirements/empty-leaves.html",
        "OpenUSD",
        ("performance",),
        (),
        (
            Examples.UNNECESSARY_EMPTY_LEAF_PRIMS_NOK,
            Examples.PRIM_HIERARCHY_WITHOUT_UNNECESSARY_LEAF_PRIMS_OK,
        ),
    )
    HI_010 = (
        "HI.010",
        "1.0.0",
        "intentional-origin-positioning",
        "Origins of prims representing objects or groups that require placement should be positioned intentionally",
        "capabilities/hierarchy/requirements/intentional-origin-positioning.html",
        "Core USD",
        ("essential",),
        (),
        (),
    )
    HI_009 = (
        "HI.009",
        "1.0.0",
        "kinematic-chain-hierarchy",
        "For articulated assets without joint definitions, the prim hierarchy should reflect the kinematic chain.",
        "capabilities/hierarchy/requirements/kinematic-chain-hierarchy.html",
        "OpenUSD",
        ("correctness",),
        (),
        (),
    )
    HI_006 = (
        "HI.006",
        "1.0.0",
        "placeable-posable-are-xformable",
        "Prims representing objects or groups that require placement (including the asset root) shall be xformable.",
        "capabilities/hierarchy/requirements/placeable-posable-are-xformable.html",
        "OpenUSD",
        ("essential",),
        (),
        (),
    )
    NVM_004 = (
        "NVM.004",
        "1.0.0",
        "material-binding",
        "Attributes must be on bound materials",
        "capabilities/nonvisual_sensors/nonvisual_materials/requirements/material-binding.html",
        "rtx",
        ("correctness",),
        (),
        (),
    )
    NVM_003 = (
        "NVM.003",
        "1.0.0",
        "material-coating",
        "Materials must specify surface coating",
        "capabilities/nonvisual_sensors/nonvisual_materials/requirements/material-coating.html",
        "rtx",
        ("correctness",),
        (),
        (),
    )
    NVM_006 = (
        "NVM.006",
        "1.0.0",
        "material-time",
        "Properties must not be time-varying",
        "capabilities/nonvisual_sensors/nonvisual_materials/requirements/material-time.html",
        "rtx",
        ("correctness",),
        (),
        (),
    )
    NVM_005 = (
        "NVM.005",
        "1.0.0",
        "material-consistency",
        "Properties must be consistent with visual materials",
        "capabilities/nonvisual_sensors/nonvisual_materials/requirements/material-consistency.html",
        "rtx",
        ("correctness",),
        (),
        (),
    )
    NVM_002 = (
        "NVM.002",
        "1.0.0",
        "material-base",
        "Materials must specify a base material type",
        "capabilities/nonvisual_sensors/nonvisual_materials/requirements/material-base.html",
        "rtx",
        ("correctness",),
        (),
        (),
    )
    NVM_001 = (
        "NVM.001",
        "1.0.0",
        "material-attributes",
        "Materials must specify additional \"non-visual\" material attributes",
        "capabilities/nonvisual_sensors/nonvisual_materials/requirements/material-attributes.html",
        "rtx",
        ("essential",),
        (),
        (),
    )
    DC_001 = (
        "DC.001",
        "1.0.0",
        "dense-caption-capability",
        "The Root Prim must inlcude documentation metadata that describes the 3D Asset.",
        "capabilities/dense_captions/requirements/dense-caption-capability.html",
        "core-usd",
        ("essential",),
        (),
        (),
    )
    DC_002 = (
        "DC.002",
        "1.0.0",
        "additional-dense-captions",
        "Prims representing sub-objects or parts within the asset should be documented with additional dense captions.",
        "capabilities/dense_captions/requirements/additional-dense-captions.html",
        "core-usd",
        ("high-quality",),
        (),
        (),
    )
    VG_008 = (
        "VG.008",
        "1.0.0",
        "usdgeom-mesh-coincident",
        "Meshes should not share the exact same space",
        "capabilities/geometry/requirements/usdgeom-mesh-coincident.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_014 = (
        "VG.014",
        "1.0.0",
        "usdgeom-mesh-topology",
        "Mesh topology must be valid",
        "capabilities/geometry/requirements/usdgeom-mesh-topology.html",
        "Core USD",
        ("correctness",),
        (),
        (),
    )
    VG_005 = (
        "VG.005",
        "1.0.0",
        "usdgeom-boundable-size",
        "Meshes should maintain appropriate scale and boundary volumes",
        "capabilities/geometry/requirements/usdgeom-boundable-size.html",
        "RTX",
        ("performance",),
        (),
        (),
    )
    VG_028 = (
        "VG.028",
        "1.0.0",
        "usdgeom-mesh-normals-must-be-valid",
        "Mesh normals values must be valid to produce correct shading.",
        "capabilities/geometry/requirements/usdgeom-mesh-normals-must-be-valid.html",
        "Core USD",
        ("correctness",),
        (),
        (
            Examples.TRIANGLE_WITH_INCONSISTENT_WINDING_ORDER_AND_NORMALS_NOK,
        ),
    )
    VG_009 = (
        "VG.009",
        "1.0.0",
        "usdgeom-mesh-primvar-indexing",
        "Use indexed primvars when values are repeated",
        "capabilities/geometry/requirements/usdgeom-mesh-primvar-indexing.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_030 = (
        "VG.030",
        "1.0.0",
        "usdgeom-zero-extent",
        "Boundable geometry should have non-zero extents in at least one dimension.Zero extent geometry wastes memory and may cause simulation problems.",
        "capabilities/geometry/requirements/usdgeom-zero-extent.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_004 = (
        "VG.004",
        "1.0.0",
        "usdgeom-mesh-empty-spaces",
        "Use efficient mesh boundaries for performance",
        "capabilities/geometry/requirements/usdgeom-mesh-empty-spaces.html",
        "RTX",
        ("performance",),
        (),
        (),
    )
    VG_007 = (
        "VG.007",
        "1.0.0",
        "usdgeom-mesh-manifold",
        "Mesh geometry must be manifold",
        "capabilities/geometry/requirements/usdgeom-mesh-manifold.html",
        "Core USD",
        ("correctness",),
        (),
        (
            Examples.NON_MANIFOLD_EDGE_DUE_TO_INCONSISTENT_WINDING_NOK,
            Examples.MANIFOLD_MESH_OK,
        ),
    )
    VG_001 = (
        "VG.001",
        "1.0.0",
        "at-least-one-imageable-geometry",
        "Assets must contain at least one imageable geometry prim.",
        "capabilities/geometry/requirements/at-least-one-imageable-geometry.html",
        "core-usd",
        ("essential",),
        (),
        (),
    )
    VG_020 = (
        "VG.020",
        "1.0.0",
        "usdgeom-pointbased-points-precision",
        "The values of `points` must not exceed the limit at which a given precision can be represented using 32-bit floats.",
        "capabilities/geometry/requirements/usdgeom-pointbased-points-precision.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_024 = (
        "VG.024",
        "1.0.0",
        "identical-mesh-consistency",
        "Repeated occurrences of identically shaped objects should have identical mesh connectivity",
        "capabilities/geometry/requirements/identical-mesh-consistency.html",
        "Core USD",
        ("correctness",),
        (),
        (),
    )
    VG_003 = (
        "VG.003",
        "1.0.0",
        "usdgeom-mesh-internal-geometry",
        "Only include geometry that contributes to visualization or simulation",
        "capabilities/geometry/requirements/usdgeom-mesh-internal-geometry.html",
        "OpenUSD",
        ("performance",),
        (),
        (),
    )
    VG_RTX_002 = (
        "VG.RTX.002",
        "1.0.0",
        "usdgeom-mesh-count",
        "Use appropriate mesh count for scene",
        "capabilities/geometry/requirements/usdgeom-mesh-count.html",
        "RTX",
        ("performance",),
        (),
        (),
    )
    VG_029 = (
        "VG.029",
        "1.0.0",
        "usdgeom-mesh-winding-order",
        "The winding order of faces in a mesh must correctly represent the orientation (front/back) of the face.",
        "capabilities/geometry/requirements/usdgeom-mesh-winding-order.html",
        "Core USD",
        ("correctness",),
        (),
        (
            Examples.INCONSISTENT_WINDING_ORDER_NOK,
        ),
    )
    VG_017 = (
        "VG.017",
        "1.0.0",
        "usdgeom-mesh-primitive-tessellation",
        "Avoid tessellating primitive shapes",
        "capabilities/geometry/requirements/usdgeom-mesh-primitive-tessellation.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_010 = (
        "VG.010",
        "1.0.0",
        "usdgeom-mesh-subdivision",
        "Do not subdivide meshes with Normals.",
        "capabilities/geometry/requirements/usdgeom-mesh-subdivision.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_RTX_001 = (
        "VG.RTX.001",
        "1.0.0",
        "usdgeom-boundable-size-rtx-limit",
        "World space bounds must not exceed RTX limit.",
        "capabilities/geometry/requirements/usdgeom-boundable-size-rtx-limit.html",
        "RTX",
        ("limitation",),
        (),
        (),
    )
    VG_031 = (
        "VG.031",
        "1.0.0",
        "usdgeom-mesh-non-opaque-must-have-thickness",
        "Meshes made from non opaque materials shall have thickness",
        "capabilities/geometry/requirements/usdgeom-mesh-non-opaque-must-have-thickness.html",
        "Core USD",
        ("correctness",),
        (),
        (),
    )
    VG_027 = (
        "VG.027",
        "1.0.0",
        "usdgeom-mesh-normals-exist",
        "All non-subdivided meshes must have normals.",
        "capabilities/geometry/requirements/usdgeom-mesh-normals-exist.html",
        "Core USD",
        ("correctness",),
        (),
        (),
    )
    VG_015 = (
        "VG.015",
        "1.0.0",
        "usdgeom-mesh-identical-timesamples",
        "Use time samples only when attribute values change",
        "capabilities/geometry/requirements/usdgeom-mesh-identical-timesamples.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_018 = (
        "VG.018",
        "1.0.0",
        "usdgeom-mesh-unused-topology",
        "Mesh topology should be without unused vertices, edges, or faces.",
        "capabilities/geometry/requirements/usdgeom-mesh-unused-topology.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_021 = (
        "VG.021",
        "1.0.0",
        "usdgeom-mesh-vertex-count",
        "Use appropriate vertex count for geometry",
        "capabilities/geometry/requirements/usdgeom-mesh-vertex-count.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_002 = (
        "VG.002",
        "1.0.0",
        "usdgeom-extent",
        "Boundable geometry primitives should have valid extent values.",
        "capabilities/geometry/requirements/usdgeom-extent.html",
        "OpenUSD",
        ("performance",),
        (),
        (),
    )
    VG_MESH_001 = (
        "VG.MESH.001",
        "1.0.0",
        "geom-shall-be-mesh",
        "All geometry shall be represented as non-subdivided mesh primitives using the UsdGeomMesh schema.",
        "capabilities/geometry/requirements/geom-shall-be-mesh.html",
        "Core USD",
        ("essential",),
        (),
        (),
    )
    VG_019 = (
        "VG.019",
        "1.0.0",
        "usdgeom-mesh-zero-area-faces",
        "Faces should have non-zero area.Faces where all vertices are co-linear or coincident waste memory and can cause rendering artifacts.",
        "capabilities/geometry/requirements/usdgeom-mesh-zero-area-faces.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_023 = (
        "VG.023",
        "1.0.0",
        "mesh-xform-positioning",
        "Meshes should be positioned using xform ops, not by embedding positions into point positions.",
        "capabilities/geometry/requirements/mesh-xform-positioning.html",
        "Core USD",
        ("correctness",),
        (),
        (),
    )
    VG_032 = (
        "VG.032",
        "1.0.0",
        "usdgeom-mesh-lamina-faces",
        "Faces should not be lamina.Lamina faces are those that share all the same vertices. This means there are two or more identical overlapping faces. This is wasteful, and can also cause rendering artifacts if the faces have different materials. They can be created in a variety of ways, for example accidentally duplicating faces on a mesh, merging objects with coincident faces and then merging vertices, or modeling operations like booleans on meshes that have coincident faces.",
        "capabilities/geometry/requirements/usdgeom-mesh-lamina-faces.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_012 = (
        "VG.012",
        "1.0.0",
        "usdgeom-mesh-small",
        "Combine small meshes into larger ones where appropriate",
        "capabilities/geometry/requirements/usdgeom-mesh-small.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_025 = (
        "VG.025",
        "1.0.0",
        "asset-at-origin",
        "Geometry shall be defined as such that the asset is correctly positioned and oriented at the origin (0,0,0).",
        "capabilities/geometry/requirements/asset-at-origin.html",
        "Core USD",
        ("essential",),
        (
            Parameters.TRANSFORM_TOLERANCE,
        ),
        (),
    )
    VG_006 = (
        "VG.006",
        "1.0.0",
        "usdgeom-mesh-overlap",
        "Meshes should not overlap unnecessarily",
        "capabilities/geometry/requirements/usdgeom-mesh-overlap.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_022 = (
        "VG.022",
        "1.0.0",
        "usdgeom-mesh-duplicate",
        "Meshes should use instancing if they are identical apart from their world space location",
        "capabilities/geometry/requirements/usdgeom-mesh-duplicate.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_013 = (
        "VG.013",
        "1.0.0",
        "usdgeom-mesh-tessellation-density",
        "Use appropriate tessellation density for geometry",
        "capabilities/geometry/requirements/usdgeom-mesh-tessellation-density.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_011 = (
        "VG.011",
        "1.0.0",
        "usdgeom-mesh-primvar-usage",
        "Only include primvars that are actively used",
        "capabilities/geometry/requirements/usdgeom-mesh-primvar-usage.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    VG_016 = (
        "VG.016",
        "1.0.0",
        "usdgeom-mesh-colocated-points",
        "Each vertex position should be unique",
        "capabilities/geometry/requirements/usdgeom-mesh-colocated-points.html",
        "Core USD",
        ("performance",),
        (),
        (),
    )
    