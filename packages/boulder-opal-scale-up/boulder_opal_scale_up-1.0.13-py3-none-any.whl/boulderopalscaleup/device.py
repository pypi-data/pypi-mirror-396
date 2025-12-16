# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.


from typing import Literal, overload

from boulderopalscaleupsdk.common.dtypes import ISO8601DatetimeUTCLike
from boulderopalscaleupsdk.device.controller import (
    QBLOXControllerInfo,
    QuantumMachinesControllerInfo,
)
from boulderopalscaleupsdk.device.defcal import DefCalData
from boulderopalscaleupsdk.device.processor import SuperconductingProcessor
from boulderopalscaleupsdk.experiments.classifiers import (
    Classifier,
    LinearIQClassifier,
    LinearNDClassifier,
)
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from rich.console import Console

DeviceName = str


@dataclass
class Defcal:
    gate: str
    addr: str | tuple[str, ...]
    program: str

    def show(self) -> None:
        console = Console()
        console.is_jupyter = False
        console.print(self.program)


@dataclass
class DeviceData:
    qpu: SuperconductingProcessor
    controller_info: QBLOXControllerInfo | QuantumMachinesControllerInfo
    _defcals: dict[tuple[str, tuple[str, ...]], DefCalData]
    _iq_classifiers: dict[str, LinearIQClassifier]
    _leakage_classifiers: dict[tuple[str, str], LinearNDClassifier]
    _enabled_qubits: list[str]

    def get_defcal(self, gate: str, addr: str | tuple[str, ...]) -> Defcal:
        """
        Get the defcal for a specific gate and address alias.
        """
        if self._defcals == {}:
            raise ValueError("No defcal data available.")
        _addr = (addr,) if isinstance(addr, str) else tuple(i for i in sorted(addr))
        defcal = self._defcals.get((gate, _addr))
        if defcal is None:
            raise KeyError(f"No defcal data found for gate '{gate}' and address '{_addr}'.")
        return Defcal(gate=gate, addr=_addr, program=defcal.program)

    @overload
    def get_classifier(
        self,
        dtype: Literal["linear_iq"],
        addr: str | tuple[str],
    ) -> LinearIQClassifier: ...

    @overload
    def get_classifier(
        self,
        dtype: Literal["linear_nd"],
        addr: tuple[str, str],
    ) -> LinearNDClassifier: ...

    def get_classifier(
        self,
        dtype: Literal["linear_iq", "linear_nd"],
        addr: str | tuple[str, ...],
    ) -> Classifier:
        """
        Get a classifier for an address alias of a specific type.
        """
        _addr = (addr,) if isinstance(addr, str) else tuple(i for i in sorted(addr))
        classifier: Classifier | None
        match dtype:
            case "linear_iq":
                if len(_addr) != 1:
                    raise ValueError(f"Invalid address '{addr}' for '{dtype}' classifier.")
                classifier = self._iq_classifiers.get(_addr[0])
            case "linear_nd":
                if len(_addr) != 2:
                    raise ValueError(f"Invalid address '{addr}' for '{dtype}' classifier.")
                classifier = self._leakage_classifiers.get(_addr)
            case _:
                raise ValueError(f"Unsupported classifier dtype '{dtype}'.")

        if classifier is None:
            raise KeyError(f"No classifier found of type '{dtype}' and address '{addr}'.")
        return classifier

    def get_enabled_qubits(self) -> list[str] | Literal["all"]:
        match self._enabled_qubits:
            case []:
                return "all"
            case _:
                return self._enabled_qubits


class DeviceSummary(BaseModel):
    id: str
    organization_id: str
    name: str
    provider: str
    updated_at: ISO8601DatetimeUTCLike
    created_at: ISO8601DatetimeUTCLike

    def __str__(self):
        return f'DeviceSummary(name="{self.name}", id="{self.id}")'
