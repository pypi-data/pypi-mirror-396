from typing import Literal

from pydantic import BaseModel, Field, PositiveFloat


class _EnableMixin:
    enable: bool = True


class PenaltySetting(BaseModel):
    """Penalty factor settings.

    Attributes
    ----------
    override: PositiveFloat | None
        Overrides the automatically evaluated penalty factor.
    scaling: PositiveFloat
        Scales the automatically evaluated penalty factor.
    """

    override: PositiveFloat | None = None
    scaling: PositiveFloat = 1.0


class IndicatorFunctionConfig(BaseModel, _EnableMixin):
    """Configuration for indicator functions to implement inequality constraints.

    Attributes
    ----------
    penalty: PenaltySetting
        Custom penalty setting for indicator functions.
    method: Literal["const", "str"]
        Indicator function implementation method. Default: `"const"`
        Two options are available:

        - `"const"`: Applies a constant penalty for every constraint violation.
        - `"if"`: Applies the objective function only if all constraints are satisfied.
                  Automatically ensures objective to be negative.

    enable : bool
        Toggle to enable or disable this method. Default: True.
    """

    penalty: PenaltySetting = Field(
        default_factory=lambda: PenaltySetting(scaling=1),
        description="Penalty setting for indicator functions.",
    )
    method: Literal["if", "const"] = Field(
        default="const",
        description="Method of indicator function implementation. Constant Penalty "
        "(const) or conditional application of cost function (if).",
    )


class XYMixerConfig(BaseModel, _EnableMixin):
    """Configuration for XY-mixers to implement one-hot constraints.

    Attributes
    ----------
    trotter : int
        Number of trotter steps for XY-mixer implementation. Default: 1.
    types: list[Literal["even", "odd", "last"]]
        Mixer types in XY-ring-mixer. Default: `["even", "odd", "last"]`.
    enable : bool
        Toggle to enable or disable this method. Default: True.
    """

    trotter: int = Field(
        default=1,
        lt=1000,
        ge=1,
        description="Number of trotter steps for XY-mixer implementation.",
    )
    types: list[Literal["even", "odd", "last"]] = Field(
        default=["even", "odd", "last"],
        description='Mixer types in XY-ring-mixer. Default: `["even", "odd", "last"]`',
    )


class QuadraticPenaltyConfig(BaseModel, _EnableMixin):
    """Configuration for quadratic penalties.

    Adds penalty terms to the objective. Adds slack variables for inequality constraints
    if neccessaray.

    Attributes
    ----------
    penalty : PenaltySetting
        Custom penalty setting for quadratic penalty terms.
    enable : bool
        Toggle to enable or disable this method. Default: True.
    """

    penalty: PenaltySetting = Field(
        default_factory=lambda: PenaltySetting(scaling=2.0),
        description="Penalty setting for quadratic penalties.",
    )


class SetpackingAsOnehotConfig(BaseModel, _EnableMixin):
    """Configuration for set-packing to one-hot constraint transformation.

    Attributes
    ----------
    enable : bool
        Toggle to enable or disable this method. Default: True.
    """


class InequalityToEqualityConfig(BaseModel, _EnableMixin):
    """Configuration for inequality to equality constraint transformation.

    Attributes
    ----------
    max_slack : int
        Maximum number of slack bits to add for each constraint. Default: 10.
    enable : bool
        Toggle to enable or disable this method. Default: True.
    """

    max_slack: int = Field(
        default=10,
        description="Maximum number of slack bits to add for each constraint.",
    )


class PipelineParams(BaseModel):
    """Define the modular FlexQAOA Pipeline.

    Attributes
    ----------
    penalty : PenaltySetting
        General penalty factor settings.
    inequality_to_equality : InequalityToEqualityConfig
        Configuration of the "inequality to equality" transformation.
    setpacking_as_onehot : SetpackingAsOnehotConfig
        Configuration of the "setpacking to onehot" transformation.
    xy_mixer : XYMixerConfig
        Configuration of the XY-mixers.
    indicator_function : IndicatorFunctionConfig
        Configuration of the indicator functions.
    sp_quadratic_penalty : QuadraticPenaltyConfig
        Configuration of the setpacking quadratic penalty function.
    quadratic_penalty : QuadraticPenaltyConfig
        Configuration of the general quadratic penalty function.
    """

    penalty: PenaltySetting = Field(default_factory=lambda: PenaltySetting(scaling=2.0))
    inequality_to_equality: InequalityToEqualityConfig = Field(
        default_factory=InequalityToEqualityConfig
    )
    setpacking_as_onehot: SetpackingAsOnehotConfig = Field(
        default_factory=SetpackingAsOnehotConfig
    )
    xy_mixer: XYMixerConfig = Field(default_factory=XYMixerConfig)
    indicator_function: IndicatorFunctionConfig = Field(
        default_factory=IndicatorFunctionConfig
    )
    sp_quadratic_penalty: QuadraticPenaltyConfig = Field(
        default_factory=QuadraticPenaltyConfig
    )
    quadratic_penalty: QuadraticPenaltyConfig = Field(
        default_factory=QuadraticPenaltyConfig
    )
