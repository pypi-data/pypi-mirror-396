
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import jneqsim.neqsim.process.util.example
import jneqsim.neqsim.process.util.fielddevelopment
import jneqsim.neqsim.process.util.fire
import jneqsim.neqsim.process.util.monitor
import jneqsim.neqsim.process.util.optimization
import jneqsim.neqsim.process.util.report
import jneqsim.neqsim.process.util.scenario
import typing


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.process.util")``.

    example: jneqsim.neqsim.process.util.example.__module_protocol__
    fielddevelopment: jneqsim.neqsim.process.util.fielddevelopment.__module_protocol__
    fire: jneqsim.neqsim.process.util.fire.__module_protocol__
    monitor: jneqsim.neqsim.process.util.monitor.__module_protocol__
    optimization: jneqsim.neqsim.process.util.optimization.__module_protocol__
    report: jneqsim.neqsim.process.util.report.__module_protocol__
    scenario: jneqsim.neqsim.process.util.scenario.__module_protocol__
