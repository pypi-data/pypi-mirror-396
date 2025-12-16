# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations

from abc import abstractmethod
from functools import cache, cached_property
from typing import Any, Protocol, final, runtime_checkable

from pxr import Sdf, Usd

from ._base_rule_checker import BaseRuleChecker
from ._issues import Issue, IssueSeverity

__all__ = [
    "UsdValidatorAdapter",
    "ValidatorErrorProtocol",
    "ValidatorErrorSiteProtocol",
    "ValidatorProtocol",
]


@runtime_checkable
class ValidatorErrorSiteProtocol(Protocol):
    """
    Temporary protocol for backward compatibility with UsdValidation.
    """

    def GetPrim(self) -> Usd.Prim | None: ...
    def GetProperty(self) -> Usd.Property | None: ...
    def GetPrimSpec(self) -> Sdf.PrimSpec | None: ...
    def GetPropertySpec(self) -> Sdf.PropertySpec | None: ...
    def GetLayer(self) -> Sdf.Layer | None: ...
    def GetStage(self) -> Usd.Stage | None: ...


@runtime_checkable
class ValidatorErrorProtocol(Protocol):
    """
    Temporary protocol for backward compatibility with UsdValidation.
    """

    def GetMessage(self) -> str: ...
    def GetSites(self) -> list[ValidatorErrorSiteProtocol]: ...


@runtime_checkable
class ValidatorProtocol(Protocol):
    """
    Temporary protocol for backward compatibility with UsdValidation.
    """

    def Validate(self, obj: Any) -> list[ValidatorErrorProtocol]: ...
    def GetMetadata(self) -> Any: ...


class UsdValidatorAdapterMeta(type):
    """
    Metaclass for UsdValidatorAdapter.
    """

    @cache
    def __contains__(cls, validator_name: str) -> bool:
        """
        Returns
            True if the validator is registered or loadable from a plugin. False otherwise.
        """
        try:
            from pxr import UsdValidation
        except ImportError:
            return False
        else:
            registry = UsdValidation.ValidationRegistry()
            if registry.HasValidator(validator_name):
                return True
            elif registry.GetValidatorMetadata(validator_name) is not None:
                return True
            else:
                return False


class UsdValidatorAdapter(BaseRuleChecker, metaclass=UsdValidatorAdapterMeta):

    @classmethod
    @abstractmethod
    def validator_name(cls) -> str: ...

    @final
    @classmethod
    @cache
    def is_implemented(cls) -> bool:
        return cls.validator_name() in UsdValidatorAdapter

    @final
    @classmethod
    def _base_validator(cls) -> ValidatorProtocol | None:
        """
        Returns
            Gets the registered validator or load it from a plugin. None if not registered or not loadable.
        """
        try:
            from pxr import UsdValidation
        except ImportError:
            return None
        else:
            registry = UsdValidation.ValidationRegistry()
            return registry.GetOrLoadValidatorByName(cls.validator_name())

    @final
    @classmethod
    def GetDescription(cls) -> str:
        validator = cls._base_validator()
        if validator is None:
            return super().GetDescription()
        return validator.GetMetadata().doc

    @final
    @cached_property
    def base_validator(self) -> ValidatorProtocol | None:
        """
        Returns:
            The underlying validator implementation, or None if the validator is not implemented.
        """
        return self._base_validator()

    @final
    def _AddValidatorError(self, error: ValidatorErrorProtocol) -> None:
        issue: Issue = self.transform(error)
        self._issues.append(issue)

    @final
    def _Validate(self, obj: Any) -> None:
        if self.base_validator is None:
            raise ValueError(f"Validator {self.validator_name()} not implemented")
        errors: list[ValidatorErrorProtocol] = list(self.base_validator.Validate(obj))
        for error in errors:
            self._AddValidatorError(error)

    @final
    def CheckStage(self, stage: Usd.Stage) -> None:
        self._Validate(stage)

    @final
    def CheckLayer(self, layer: Sdf.Layer) -> None:
        self._Validate(layer)

    @final
    def CheckPrim(self, prim: Usd.Prim) -> None:
        self._Validate(prim)

    def transform(self, error: ValidatorErrorProtocol) -> Issue:
        """
        Transforms a validator error into an issue.

        Args:
            error (ValidatorErrorProtocol): The validator error to transform.

        Returns:
            The issue corresponding to the validator error.
        """
        at: Usd.Stage | Sdf.Layer | Usd.Prim | Sdf.Spec | None = None
        for site in error.GetSites():
            at = (
                site.GetPrim()
                or site.GetProperty()
                or site.GetPrimSpec()
                or site.GetPropertySpec()
                or site.GetLayer()
                or site.GetStage()
            )
            if at is not None:
                break
        return Issue(
            message=error.GetMessage(),
            severity=IssueSeverity.FAILURE,
            rule=self.__class__,
            at=at,
        )
