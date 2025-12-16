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

import contextlib
import json
import logging
from typing import TYPE_CHECKING, cast

import numpy as np
import qm
from boulderopalscaleupsdk.device.controller.quantum_machines import QuaProgram
from boulderopalscaleupsdk.protobuf.v1 import agent_pb2
from google.protobuf.struct_pb2 import Struct
from pydantic.main import IncEx
from qm.jobs.running_qm_job import RunningQmJob

from boulderopalscaleup.controllers import Controller

if TYPE_CHECKING:
    from iqcc_cloud_client.qmm_cloud import (
        CloudJob,
        CloudQuantumMachine,
        CloudQuantumMachinesManager,
    )

    from boulderopalscaleup.client import QctrlScaleUpClient

# Import IQCC Cloud classes if available
with contextlib.suppress(ImportError):
    from iqcc_cloud_client.qmm_cloud import (
        CloudJob,
        CloudQuantumMachine,
        CloudQuantumMachinesManager,
    )

LOG = logging.getLogger(__name__)


class OPX1000Controller(Controller):
    def __init__(self, qmm: "qm.QuantumMachinesManager | CloudQuantumMachinesManager"):
        self.qmm = qmm

    async def run_program(
        self,
        program_request: agent_pb2.RunProgramRequest,
        client: "QctrlScaleUpClient",
    ) -> agent_pb2.RunProgramResponse:
        LOG.info("Running experiment task %s", program_request)

        qua_program = QuaProgram.loads(program_request.program)

        # Defined as IncEx so linter is happy.
        # Exclude fields that are not supported by QOP 3.5
        exclude_fields: IncEx = cast(
            IncEx,
            {
                "qm_version": True,
                "controllers": {
                    "__all__": {
                        "fems": {
                            "__all__": {
                                "analog_outputs": {
                                    "__all__": {
                                        "filter": {
                                            "feedback": True,
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        )
        config = qua_program.config.root.model_dump_json(exclude=exclude_fields, exclude_none=True)

        qm_instance = self._initialize_qm(client, config)

        LOG.info("Executing program.")
        match qm_instance:
            case CloudQuantumMachine():
                qm_job = qm_instance.execute(
                    qm.Program(program=qua_program.program),
                    options={"timeout": 600},
                )
            case _:
                qm_job = qm_instance.execute(
                    qm.Program(program=qua_program.program),
                )

        LOG.info("Handling results.")
        measurement_data = self._fetch_job_results(qm_job)

        def _convert(array):
            return np.asarray(array).astype(float).tolist()

        raw_data = {k: _convert(v) for k, v in measurement_data.items()}

        raw_data_struct = Struct()
        raw_data_struct.update(raw_data)
        return agent_pb2.RunProgramResponse(raw_data=raw_data_struct)

    async def run_mixer_calibration(
        self,
        calibration_request: agent_pb2.RunQuantumMachinesMixerCalibrationRequest,  # noqa: ARG002
        client: "QctrlScaleUpClient",  # noqa: ARG002
    ) -> agent_pb2.RunQuantumMachinesMixerCalibrationResponse:
        """
        Run a mixer calibration on the device.
        """

        # No-op for OPX1000 because it does not need mixer calibration
        return agent_pb2.RunQuantumMachinesMixerCalibrationResponse(
            success=True,
        )

    def _initialize_qm(
        self,
        client: "QctrlScaleUpClient",  # noqa: ARG002
        config_json: str,
    ) -> qm.QuantumMachine | CloudQuantumMachine:
        """
        Initialize a Quantum Machine from a config JSON string and export the config.
        """
        LOG.info("Initializing QM.")
        qua_config = json.loads(config_json)
        return self.qmm.open_qm(config=qua_config, close_other_machines=True)  # type: ignore[return-value]

    def _fetch_job_results(self, job: RunningQmJob | CloudJob):
        def _format(data):
            if (
                type(data) is np.ndarray
                and data.ndim > 0
                and type(data[0]) is np.void
                and len(data.dtype.names or []) == 1
            ):
                data = data["value"]
            return data

        result_handles = job.result_handles
        result_handles.wait_for_all_values()

        results = {}
        for data in list(result_handles.keys()):
            if hasattr(result_handles, data) and data != "__fridge_info":
                results[data] = _format(result_handles.get(data).fetch_all())  # type: ignore[union-attr]

        return results
