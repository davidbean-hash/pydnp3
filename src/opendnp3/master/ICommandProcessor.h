/*
 * -*- coding: utf-8 -*- {{{
 * vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
 *
 * Copyright 2018, Kisensum.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Neither Kisensum, nor any of its employees, nor any jurisdiction or
 * organization that has cooperated in the development of these materials,
 * makes any warranty, express or implied, or assumes any legal liability
 * or responsibility for the accuracy, completeness, or usefulness or any
 * information, apparatus, product, software, or process disclosed, or
 * represents that its use would not infringe privately owned rights.
 * Reference herein to any specific commercial product, process, or service
 * by trade name, trademark, manufacturer, or otherwise does not necessarily
 * constitute or imply its endorsement, recommendation, or favoring by Kisensum.
 * }}}
 */

#ifndef PYDNP3_OPENDNP3_MASTER_ICOMMANDPROCESSOR_H
#define PYDNP3_OPENDNP3_MASTER_ICOMMANDPROCESSOR_H

#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <Python.h>

#include <opendnp3/master/ICommandProcessor.h>

#ifdef PYDNP3_OPENDNP3

namespace py = pybind11;
using namespace std;

// Wrap a Python callable into a CommandCallbackT that casts ICommandTaskResult
// using return_value_policy::reference instead of the default copy policy.
// This avoids the pybind11::cast_error for non-copyable ICommandTaskResult.
opendnp3::CommandCallbackT WrapPythonCommandCallback(py::object callback)
{
    auto shared_cb = std::make_shared<py::object>(std::move(callback));
    return [shared_cb](const opendnp3::ICommandTaskResult& result) {
        py::gil_scoped_acquire acq;
        py::object py_result = py::cast(result, py::return_value_policy::reference);
        (*shared_cb)(py_result);
    };
}

namespace opendnp3 {
/**
* Overriding virtual functions from interface class ICommandProcessor.
*/
    class PyICommandProcessor : public ICommandProcessor {
    public:
        /* Inherit the constructors */
        using ICommandProcessor::ICommandProcessor;

        /* Trampoline for ICommandProcessor virtual functions */
        void SelectAndOperate(CommandSet&& commands,
                              const CommandCallbackT& callback,
                              const TaskConfig& config = TaskConfig::Default()) override {
            PYBIND11_OVERLOAD_PURE(
                void,
                ICommandProcessor,
                SelectAndOperate,
                commands, callback, config
            );
        }
        void DirectOperate(CommandSet&& commands,
                           const CommandCallbackT& callback,
                           const TaskConfig& config = TaskConfig::Default()) override {
            PYBIND11_OVERLOAD_PURE(
                void,
                ICommandProcessor,
                DirectOperate,
                commands, callback, config
            );
        }
        template <class T>
        void SelectAndOperate(const T& command,
                              uint16_t index,
                              const CommandCallbackT& callback,
                              const TaskConfig& config = TaskConfig::Default()) {
            PYBIND11_OVERLOAD(
                void,
                ICommandProcessor,
                SelectAndOperate,
                command, index, callback, config
            );
        }
        template <class T>
        void DirectOperate(const T& command,
                           uint16_t index,
                           const CommandCallbackT& callback,
                           const TaskConfig& config = TaskConfig::Default()) {
            PYBIND11_OVERLOAD(
                void,
                ICommandProcessor,
                DirectOperate,
                command, index, callback, config
            );
        }
    };
}

void bind_ICommandProcessor(py::module &m)
{
    // ----- class: opendnp3::ICommandProcessor -----
    py::class_<opendnp3::ICommandProcessor,
               opendnp3::PyICommandProcessor,
               std::shared_ptr<opendnp3::ICommandProcessor>>cls(m, "ICommandProcessor",
        "Interface used to dispatch SELECT / OPERATE / DIRECT OPERATE from application code to a master.");

    cls.def(py::init<>());

    const char* selectAndOperate_singleCommand =
    "   Select and operate a single command. \n"
    ":param command: Command to operate \n"
    ":param index: in dex of the command \n"
    ":param callback: callback that will be invoked upon completion or failure \n"
    ":param config: optional configuration that controls normal callbacks and allows the user to be specified for SA";

    cls.def(
        "SelectAndOperate",
        [](opendnp3::ICommandProcessor &self,
           const opendnp3::ControlRelayOutputBlock &command,
           uint16_t index,
           py::object callback,
           const opendnp3::TaskConfig &config) {
            self.SelectAndOperate(command, index, WrapPythonCommandCallback(std::move(callback)), config);
        },
        py::arg("command"), py::arg("index"), py::arg("callback"), py::arg("config") = opendnp3::TaskConfig::Default()
    );

    cls.def(
        "SelectAndOperate",
        [](opendnp3::ICommandProcessor &self,
           const opendnp3::AnalogOutputInt16 &command,
           uint16_t index,
           py::object callback,
           const opendnp3::TaskConfig &config) {
            self.SelectAndOperate(command, index, WrapPythonCommandCallback(std::move(callback)), config);
        },
        py::arg("command"), py::arg("index"), py::arg("callback"), py::arg("config") = opendnp3::TaskConfig::Default()
    );

    cls.def(
        "SelectAndOperate",
        [](opendnp3::ICommandProcessor &self,
           const opendnp3::AnalogOutputInt32 &command,
           uint16_t index,
           py::object callback,
           const opendnp3::TaskConfig &config) {
            self.SelectAndOperate(command, index, WrapPythonCommandCallback(std::move(callback)), config);
        },
        py::arg("command"), py::arg("index"), py::arg("callback"), py::arg("config") = opendnp3::TaskConfig::Default()
    );

    cls.def(
        "SelectAndOperate",
        [](opendnp3::ICommandProcessor &self,
           const opendnp3::AnalogOutputFloat32 &command,
           uint16_t index,
           py::object callback,
           const opendnp3::TaskConfig &config) {
            self.SelectAndOperate(command, index, WrapPythonCommandCallback(std::move(callback)), config);
        },
        py::arg("command"), py::arg("index"), py::arg("callback"), py::arg("config") = opendnp3::TaskConfig::Default()
    );

    cls.def(
        "SelectAndOperate",
        [](opendnp3::ICommandProcessor &self,
           const opendnp3::AnalogOutputDouble64 &command,
           uint16_t index,
           py::object callback,
           const opendnp3::TaskConfig &config) {
            self.SelectAndOperate(command, index, WrapPythonCommandCallback(std::move(callback)), config);
        },
        selectAndOperate_singleCommand,
        py::arg("command"), py::arg("index"), py::arg("callback"), py::arg("config") = opendnp3::TaskConfig::Default()
    );

    const char* directOperate_singleCommand =
    "   Direct operate a single command. \n"
    ":param command: Command to operate \n"
    ":param index: in dex of the command \n"
    ":param callback: callback that will be invoked upon completion or failure \n"
    ":param config: optional configuration that controls normal callbacks and allows the user to be specified for SA";

    cls.def(
        "DirectOperate",
        [](opendnp3::ICommandProcessor &self,
           const opendnp3::ControlRelayOutputBlock &command,
           uint16_t index,
           py::object callback,
           const opendnp3::TaskConfig &config) {
            self.DirectOperate(command, index, WrapPythonCommandCallback(std::move(callback)), config);
        },
        py::arg("command"), py::arg("index"), py::arg("callback"), py::arg("config") = opendnp3::TaskConfig::Default()
    );

    cls.def(
        "DirectOperate",
        [](opendnp3::ICommandProcessor &self,
           const opendnp3::AnalogOutputInt16 &command,
           uint16_t index,
           py::object callback,
           const opendnp3::TaskConfig &config) {
            self.DirectOperate(command, index, WrapPythonCommandCallback(std::move(callback)), config);
        },
        py::arg("command"), py::arg("index"), py::arg("callback"), py::arg("config") = opendnp3::TaskConfig::Default()
    );

    cls.def(
        "DirectOperate",
        [](opendnp3::ICommandProcessor &self,
           const opendnp3::AnalogOutputInt32 &command,
           uint16_t index,
           py::object callback,
           const opendnp3::TaskConfig &config) {
            self.DirectOperate(command, index, WrapPythonCommandCallback(std::move(callback)), config);
        },
        py::arg("command"), py::arg("index"), py::arg("callback"), py::arg("config") = opendnp3::TaskConfig::Default()
    );

    cls.def(
        "DirectOperate",
        [](opendnp3::ICommandProcessor &self,
           const opendnp3::AnalogOutputFloat32 &command,
           uint16_t index,
           py::object callback,
           const opendnp3::TaskConfig &config) {
            self.DirectOperate(command, index, WrapPythonCommandCallback(std::move(callback)), config);
        },
        py::arg("command"), py::arg("index"), py::arg("callback"), py::arg("config") = opendnp3::TaskConfig::Default()
    );

    cls.def(
        "DirectOperate",
        [](opendnp3::ICommandProcessor &self,
           const opendnp3::AnalogOutputDouble64 &command,
           uint16_t index,
           py::object callback,
           const opendnp3::TaskConfig &config) {
            self.DirectOperate(command, index, WrapPythonCommandCallback(std::move(callback)), config);
        },
        directOperate_singleCommand,
        py::arg("command"), py::arg("index"), py::arg("callback"), py::arg("config") = opendnp3::TaskConfig::Default()
    );

    const char* selectAndOperate_commandSet =
	"   Select and operate a set of commands. \n"
	":param commands: Set of command headers \n"
	":param callback: callback that will be invoked upon completion or failure \n"
	":param config: optional configuration that controls normal callbacks and allows the user to be specified for SA";

    cls.def(
        "SelectAndOperate",
        [](opendnp3::ICommandProcessor &self,
           opendnp3::CommandSet& commands,
           py::object callback,
           const opendnp3::TaskConfig& config) {
            self.SelectAndOperate(std::move(commands), WrapPythonCommandCallback(std::move(callback)), config);
        },
        selectAndOperate_commandSet,
        py::arg("commands"), py::arg("callback"), py::arg("config") = opendnp3::TaskConfig::Default()
    );

    const char* directOperate_commandSet =
    "   Direct operate a set of commands. \n"
    ":param commands: Set of command headers \n"
    ":param callback: callback that will be invoked upon completion or failure \n"
    ":param config: optional configuration that controls normal callbacks and allows the user to be specified for SA";

    cls.def(
        "DirectOperate",
        [](opendnp3::ICommandProcessor &self,
           opendnp3::CommandSet& commands,
           py::object callback,
           const opendnp3::TaskConfig& config) {
            self.DirectOperate(std::move(commands), WrapPythonCommandCallback(std::move(callback)), config);
        },
        directOperate_commandSet,
        py::arg("commands"), py::arg("callback"), py::arg("config") = opendnp3::TaskConfig::Default()
    );
}

#endif // PYDNP3_OPENDNP3
#endif
