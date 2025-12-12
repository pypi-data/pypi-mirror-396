/**
 *
 * @file
 * Copyright 2025 Digitalwerk GmbH.
 *
 *     This Source Code Form is subject to the terms of the Mozilla
 *     Public License, v. 2.0. If a copy of the MPL was not distributed
 *     with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
 *
 * If it is not possible or desirable to put the notice in a particular file, then
 * You may include the notice in a location (such as a LICENSE file in a
 * relevant directory) where a recipient would be likely to look for such a notice.
 *
 * You may add additional accurate notices of copyright ownership.
 */

#include "decoder.h"
#include "streaming_types.h"
#include "sample_streams.h"
#include "future.h"
#include "graph_utils_compat.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>
#include <pybind11/native_enum.h>
#include <pybind11/functional.h>

#include <adtffiltersdk/filter.h>
#include <adtfsystemsdk/adtf_system.h>
#include <adtfstreaming3/testing/connect_pins.h>

#include <a_util/xml.h>

namespace py = pybind11;
using namespace std::literals;
using namespace adtf::ucom;
using namespace adtf::base;
using namespace adtf::streaming;

namespace adtf::python::MODULE_RELEASE_ABI_VERSION::detail
{
    class copyable_resolver final : public adtf::util::cMacroResolver
    {
    public:
        copyable_resolver() = default;
        copyable_resolver(const copyable_resolver& other)
        {
            SetValues(other.m_mapValues);
        }
    };

    std::string get_adtf_dir(const std::string& environment, copyable_resolver resolver = {})
    {
        using namespace a_util::xml;
        using namespace adtf::util;

        DOM xml;
        if (!xml.load(environment))
        {
            return {};
        }

        const auto parent_directory = cFilename(environment.c_str()).GetPath();
        const auto dir_macro = xml.getRoot().getChild("environment_directory_macro").getData();

        if (dir_macro == "ADTF_DIR")
        {
            return parent_directory.GetPtr();
        }

        resolver.SetValue(dir_macro.c_str(), parent_directory);
        if (DOMElementList macros; xml.getRoot().findNodes("macros/macro", macros))
        {
            for (const auto& macro : macros)
            {
                resolver.SetValue(macro.getChild("name").getData().c_str(),
                                  resolver.Resolve(macro.getChild("value").getData().c_str()).GetPtr());
            }
        }

        if (DOMElementList include_urls; xml.getRoot().findNodes("includes/include/url", include_urls))
        {
            for (const auto& url : include_urls)
            {
                cFilename absolute_path(resolver.Resolve(url.getData().c_str()).GetPtr());
                absolute_path = absolute_path.CreateAbsolutePath(parent_directory);
                cStringList files;
                cFileSystem::FindFiles(absolute_path, files);
                for (const auto file : files)
                {
                    if (const auto adtf_dir = get_adtf_dir(file.GetPtr(), resolver); !adtf_dir.empty())
                    {
                        return adtf_dir;
                    }
                }
            }
        }

        return {};
    }
} // namespace adtf::python::MODULE_RELEASE_ABI_VERSION::detail

namespace adtf::python::MODULE_RELEASE_ABI_VERSION
{
    class SystemThread
    {
    public:
        void create(const std::string environment,
                    const std::string session,
                    const std::string filtergraph,
                    const adtf::util::log::tLogLevel log_level,
                    std::function<void(std::exception_ptr)> startup_completed)
        {
            adtf::util::log::set_filtered_logging(log_level);
            const auto adtf_dir = detail::get_adtf_dir(environment);

            const auto ready_promise = std::make_shared<std::promise<bool>>();

            _state = std::make_shared<State>();
            _state->runtime_ready_or_error = ready_promise->get_future();

            _thread = std::thread(
                [environment, session, filtergraph, log_level, state = _state,
                 startup_completed = std::move(startup_completed), ready_promise, adtf_dir]() mutable -> void
                {
                    try
                    {
                        adtf::system::cADTFSystem system;
                        system.SetADTFCorePlugin((adtf_dir +
#ifdef _DEBUG
                                                  "/bin/debug"
#else
                                                  "/bin"
#endif
                                                  "/adtf_core.adtfplugin")
                                                     .c_str());
                        system.EnableLogging();
                        system.SetLoggingParameter(log_level, adtf_util::log::tLogLevel::None,
                                                   adtf_util::log::tLogLevel::None, 0);
                        system.EnableMacroResolver(true);
                        system.EnableSessionManagerCreation();

                        THROW_IF_FAILED(system.Launch(adtf::util::cCommandLine()));

                        object_ptr<adtf::services::ISessionManager> session_manager;
                        THROW_IF_FAILED(_runtime->GetObject(session_manager));
                        THROW_IF_FAILED(session_manager->SetEnvironmentFile(environment.c_str()));
                        THROW_IF_FAILED(session_manager->CreateSession(session.c_str()));
                        if (!filtergraph.empty())
                        {
                            object_ptr<adtf::services::ISession> session;
                            THROW_IF_FAILED(session_manager->GetCurrentSession(session));
                            THROW_IF_FAILED(session->SetActiveFilterGraph(filtergraph.c_str()));
                        }
                        THROW_IF_FAILED(system.Exec(adtf::base::tADTFRunLevel::RL_FilterGraph,
                                                    adtf::util::cCommandLine(),
                                                    [&startup_completed, &ready_promise]() -> void
                                                    {
                                                        startup_completed(nullptr);
                                                        ready_promise->set_value(true);
                                                    }));
                    }
                    catch (...)
                    {
                        startup_completed(std::current_exception());
                        ready_promise->set_value(false);
                    }

                    std::scoped_lock lock(state->finished_mutex);
                    if (state->shutdown_completed)
                    {
                        state->shutdown_completed();
                    }
                    state->finished = true;
                });
        }

        void destroy(std::function<void()> shutdown_completed)
        {
            if (!_state)
            {
                shutdown_completed();
                return;
            }

            std::scoped_lock lock(_state->finished_mutex);
            if (_state->finished)
            {
                shutdown_completed();
            }
            else
            {
                if (_state->runtime_ready_or_error.get())
                {
                    _state->shutdown_completed = std::move(shutdown_completed);
                    THROW_IF_FAILED(_runtime->SetRunLevel(IRuntime::RL_Shutdown, false));
                }
                else
                {
                    _state->finished = true;
                    shutdown_completed();
                }
            }
        }

        void join()
        {
            if (_thread.joinable())
            {
                _thread.join();
            }
        }

    private:
        std::thread _thread;

        struct State
        {
            std::future<bool> runtime_ready_or_error;

            std::mutex finished_mutex;
            bool finished = false;
            std::function<void()> shutdown_completed;
        };
        std::shared_ptr<State> _state;
    };

    class RunGuard : public std::enable_shared_from_this<RunGuard>
    {
    public:
        std::shared_ptr<RunGuard> enter()
        {
            py::gil_scoped_release gil_release;
            THROW_IF_FAILED(_runtime->SetRunLevel(tADTFRunLevel::RL_Running, true));
            return shared_from_this();
        }

        bool exit(const py::handle&, const py::handle& value, const py::handle&)
        {
            py::gil_scoped_release gil_release;
            THROW_IF_FAILED(_runtime->SetRunLevel(tADTFRunLevel::RL_FilterGraph, true));
            return false;
        }

        py::object aenter()
        {
            auto future = EventLoop().create_future();
            auto started = change_runlevel(tADTFRunLevel::RL_Running, future, py::cast(shared_from_this()));

            future.add_done_callback(
                [started = std::make_shared<std::future<void>>(std::move(started))](const Future& future)
                {
                    if (future.cancelled())
                    {
                        py::gil_scoped_release gil_release;
                        started->get();
                        THROW_IF_FAILED(_runtime->SetRunLevel(tADTFRunLevel::RL_FilterGraph, true));
                    }
                    else
                    {
                        py::gil_scoped_release gil_release;
                        started->get();
                    }
                });

            return future.get();
        }

        py::object aexit(const py::handle& type, const py::handle& value, const py::handle& trace)
        {
            auto future = EventLoop().create_future();
            auto stopped = change_runlevel(tADTFRunLevel::RL_FilterGraph, future, py::cast(false));

            future.add_done_callback(
                [stopped = std::make_shared<std::future<void>>(std::move(stopped))](const Future& future)
                {
                    py::gil_scoped_release gil_release;
                    stopped->get();
                });

            return future.get();
        }

    private:
        std::future<void> change_runlevel(tADTFRunLevel runlevel, Future future, py::object future_result)
        {
            return std::async(
                std::launch::async,
                [runlevel, future = std::move(future), future_result = std::move(future_result)]() mutable -> void
                {
                    const auto result = _runtime->SetRunLevel(runlevel, true);

                    py::gil_scoped_acquire gil_lock;
                    auto loop = future.loop();
                    loop.schedule()(std::function<void()>(
                        [future = std::move(future), future_result = std::move(future_result), result]() mutable -> void
                        {
                            if (!future.cancelled())
                            {
                                if (IS_OK(result))
                                {
                                    future.set_result(future_result);
                                }
                                else
                                {
                                    try
                                    {
                                        throw result;
                                    }
                                    catch (...)
                                    {
                                        future.set_exception(std::current_exception());
                                    }
                                }
                            }
                        }));
                });
        }
    };

    class Session final : public std::enable_shared_from_this<Session>, private IRuntimeHook
    {
    public:
        Session(const std::string& environment,
                const std::string& session,
                const std::string& filtergraph,
                adtf::util::log::tLogLevel log_level):
            _environment(environment), _session(session), _filtergraph(filtergraph), _log_level(log_level)
        {
        }
        Session(const Session&) = delete;
        Session(Session&&) = delete;
        Session& operator=(const Session&) = delete;
        Session& operator=(Session&&) = delete;

        ~Session() = default;

        std::shared_ptr<Session> enter()
        {
            if (_session_active)
            {
                throw std::logic_error(
                    "There is already another ADTF session active. Each process can only have one session at a "
                    "time. Use destroy() to explicitly release a previous session.");
            }

            try
            {
                py::gil_scoped_release gil_release;

                _state = std::make_shared<State>();
                auto startup_completed = std::make_shared<std::promise<void>>();
                auto future = startup_completed->get_future();

                _state->system_thread.create(
                    _environment, _session, _filtergraph, _log_level,
                    [this, startup_completed = std::move(startup_completed)](std::exception_ptr error) mutable -> void
                    {
                        if (error)
                        {
                            startup_completed->set_exception(error);
                        }
                        else
                        {
                            _runtime->RegisterHook(*this);
                            startup_completed->set_value();
                        }
                    });

                future.get();

                _session_active = true;
            }
            catch (...)
            {
                _state->system_thread.join();
                _state.reset();
                throw;
            }

            return shared_from_this();
        }

        bool exit(const py::handle&, const py::handle& value, const py::handle&)
        {
            if (_state)
            {
                py::gil_scoped_release gil_release;
                _state->system_thread.destroy([]() {});
                _state->system_thread.join();
                _state.reset();
                _session_active = false;
            }

            return false;
        }

        py::object aenter()
        {
            if (_session_active)
            {
                throw std::logic_error("There is already another ADTF session active. Each process can only have one "
                                       "active session at a time.");
            }

            EventLoop loop;
            auto future = loop.create_future();
            auto python_future = future.get();

            future.add_done_callback(
                [_this = shared_from_this()](const Future& future)
                {
                    if (future.cancelled())
                    {
                        _this->exit(py::none(), py::none(), py::none());
                    }
                    else if (!future.exception().is_none())
                    {
                        _this->_state->system_thread.join();
                        _this->_state.reset();
                        _session_active = false;
                    }
                });

            _state = std::make_shared<State>();
            _state->system_thread.create(
                _environment, _session, _filtergraph, _log_level,
                [this, future = std::move(future)](std::exception_ptr error) mutable -> void
                {
                    if (!error)
                    {
                        _runtime->RegisterHook(*this);
                    }

                    py::gil_scoped_acquire gil_lock;

                    auto loop = future.loop();
                    loop.schedule()(std::function<void()>(
                        [error, future = std::move(future), _this = shared_from_this()]() mutable -> void
                        {
                            if (!future.cancelled())
                            {
                                if (error)
                                {
                                    future.set_exception(error);
                                }
                                else
                                {
                                    future.set_result(py::cast(_this));
                                }
                            }
                        }));
                });

            _session_active = true;

            return python_future;
        }

        py::object aexit(const py::handle& type, const py::handle& value, const py::handle& trace)
        {
            auto future = EventLoop().create_future();
            auto python_future = future.get();

            future.add_done_callback(
                [_this = shared_from_this()](const Future& future)
                {
                    py::gil_scoped_release gil_release;
                    _this->_state->system_thread.join();
                    _this->_state.reset();
                    _session_active = false;
                });

            _state->system_thread.destroy(
                [future = std::move(future)]() mutable -> void
                {
                    py::gil_scoped_acquire gil_lock;

                    auto loop = future.loop();
                    loop.schedule()(std::function<void()>(
                        [future = std::move(future)]() mutable -> void
                        {
                            if (!future.cancelled())
                            {
                                future.set_result(py::cast(false));
                            }
                        }));
                });

            return python_future;
        }

        tResult RuntimeHook(const tHookInfo& hook_info, const iobject_ptr<IObject>&) override
        {
            if (hook_info.idHook == IRuntime::tRuntimeHookId::RHI_RunLevelPreIncrement &&
                hook_info.ui32Param1 == tADTFRunLevel::RL_Running)
            {
                for (const auto& sample_stream : _state->sample_streams)
                {
                    RETURN_IF_FAILED(sample_stream->SetState(IFilter::tFilterState::State_Running));
                }
            }
            if (hook_info.idHook == IRuntime::tRuntimeHookId::RHI_RunLevelPreDecrement &&
                hook_info.ui32Param1 == tADTFRunLevel::RL_Running)
            {
                for (const auto& sample_stream : _state->sample_streams)
                {
                    RETURN_IF_FAILED(sample_stream->SetState(IFilter::tFilterState::State_Ready));
                }
            }

            if (hook_info.idHook == IRuntime::tRuntimeHookId::RHI_RunLevelPreDecrement &&
                hook_info.ui32Param1 == tADTFRunLevel::RL_FilterGraph)
            {
                for (const auto& sample_stream : _state->sample_streams)
                {
                    object_ptr<IInPin> pin;
                    if (IS_OK(sample_stream->FindPin("input", pin)))
                    {
                        pin->Disconnect();
                    }
                    sample_stream->SetState(IFilter::tFilterState::State_Shutdown);
                }
                _state->sample_streams.clear();
                _runtime->UnregisterHook(*this);
            }
            RETURN_NOERROR;
        }

        std::vector<std::string> graph_objects_names()
        {
            check_state();
            return compat::get_objects<INamedGraphObject>();
        }

        std::vector<std::string> output_pin_names()
        {
            check_state();
            return compat::get_objects<IOutPin>();
        }

        std::shared_ptr<RunGuard> run()
        {
            check_state();
            return std::make_shared<RunGuard>();
        }

        std::shared_ptr<StreamReader>
            open_stream(const std::string& pin, std::optional<StreamReader::Requests> requests, Items items)
        {
            check_state();
            if (_runtime->GetRunLevel() == tADTFRunLevel::RL_Running)
            {
                THROW_ERROR_DESC(ERR_INVALID_STATE, "Session is already running.");
            }

            const auto last_slash = pin.find_last_of('.');
            if (last_slash == std::string::npos)
            {
                throw std::invalid_argument("invalid pin");
            }
            const auto object_name = pin.substr(0, last_slash);
            const auto pin_name = pin.substr(last_slash + 1);

            object_ptr<IStreamingGraph> streaming_graph;
            THROW_IF_FAILED(adtf::services::get_session_streaming_graph(streaming_graph));
            object_ptr<INamedGraphObject> graph_object;
            THROW_IF_FAILED(get_named_graph_object_from_graph(*streaming_graph, object_name.c_str(), graph_object));

            const auto stream = std::make_shared<StreamReader>(items, std::move(requests));
            THROW_IF_FAILED(stream->SetState(IFilter::tFilterState::State_Initialized));
            connect(*graph_object, pin_name, *stream, "input");
            THROW_IF_FAILED(stream->SetState(IFilter::tFilterState::State_Ready));
            _state->sample_streams.emplace_back(stream);
            return stream;
        }

        static void stop_active()
        {
            if (!_runtime)
            {
                THROW_ERROR_DESC(ERR_INVALID_STATE, "no active session");
            }

            if (_runtime->GetRunLevel() == tADTFRunLevel::RL_Running)
            {
                _runtime->SetRunLevel(tADTFRunLevel::RL_FilterGraph, false);
            }
        }

    private:
        void check_state()
        {
            if (!_state)
            {
                throw std::runtime_error("The session is not active, you need to enter its context first.");
            }
        }

        void connect(IObject& source,
                     const std::string& output_pin,
                     StreamReader& destination,
                     const std::string& input_pin)
        {
            auto source_binding = ucom_cast<IDataBinding*>(&source);
            if (!source_binding)
            {
                THROW_ERROR_DESC(ERR_INVALID_ARG, "Source does not implement IDataBinding");
            }

            object_ptr<IOutPin> output;
            if (const auto result = source_binding->FindPin(output_pin.c_str(), output); IS_FAILED(result))
            {
                if (const auto dynamic_binding = ucom_cast<IDynamicDataBinding*>(&source))
                {
                    const object_ptr<IStreamType> type = make_object_ptr<stream_type_anonymous<>>();
                    THROW_IF_FAILED(dynamic_binding->RequestPin(output_pin.c_str(), type, output));
                }
                else
                {
                    throw ADTF_BASE_ANNOTATE_RESULT(result);
                }
            }

            object_ptr<IInPin> input;
            THROW_IF_FAILED(destination.FindPin(input_pin.c_str(), input));

            THROW_IF_FAILED(adtf::streaming::testing::connect_pins(output, input, true));
        }

        struct State
        {
            SystemThread system_thread;
            std::vector<std::shared_ptr<StreamReader>> sample_streams;
        };

        const std::string _environment;
        const std::string _session;
        const std::string _filtergraph;
        const adtf::util::log::tLogLevel _log_level;

        std::shared_ptr<State> _state;

        static inline bool _session_active = false;
    };

    void add_session_bindings(py::module& m)
    {
        using namespace adtf::system::testing;

        py::register_exception_translator(
            [](std::exception_ptr p)
            {
                try
                {
                    if (p)
                    {
                        std::rethrow_exception(p);
                    }
                }
                catch (const tResult& result)
                {
                    throw std::runtime_error(adtf::util::to_string(result).GetPtr());
                }
            });

        add_streaming_types_bindings(m);
        add_sample_streams_bindings(m);

        py::native_enum<adtf::util::log::tLogLevel>(m, "LogLevel", "enum.Enum")
            .value("NONE", adtf::util::log::tLogLevel::None)
            .value("ERROR", adtf::util::log::tLogLevel::Error)
            .value("WARNING", adtf::util::log::tLogLevel::Warning)
            .value("INFO", adtf::util::log::tLogLevel::Info)
            .value("DETAIL", adtf::util::log::tLogLevel::Detail)
            .value("DUMP", adtf::util::log::tLogLevel::Dump)
            .value("DEBUG", adtf::util::log::tLogLevel::Debug)
            .value("ALL", adtf::util::log::tLogLevel::All)
            .finalize();

        py::class_<RunGuard, py::smart_holder>(m, "RunGuard")
            .def("__enter__", &RunGuard::enter,
                 "Enter the context and raise the runlevel to RL_Running(5). Must be called within the :class:Session "
                 "context")
            .def("__exit__", &RunGuard::exit, "Leave the context and decrease the runlevel to RL_FilterGraph(4).")
            .def("__aenter__", &RunGuard::aenter,
                 "Enter the context and raise the runlevel to RL_Running(5). Must be called within the :class:Session "
                 "context")
            .def("__aexit__", &RunGuard::aexit, "Leave the context and decrease the runlevel to RL_FilterGraph(4).")
            .doc() = R"doc(Context manager controlling the run level of an ADTF session.

A :class:`RunGuard` is created via :meth:`Session.run` and is used to
start and stop execution of the active ADTF session:

- Entering the context (sync or async) raises the ADTF runlevel to
  ``RL_Running`` (5) and starts processing in the underlying filtergraph.
- Leaving the context lowers the runlevel back to ``RL_FilterGraph`` (4),
  pausing execution while keeping the session initialized.

Typical usage (synchronous):

    with session.run():
        # ADTF is running
        ...

or asynchronous:

    async with session.run():
        # ADTF startup and shutdown is happening asynchronously without blocking the event loop.
        ...

The session itself remains active and must still be managed via the
:class:`Session` context (``with Session(...) as session:``).)doc";

        py::class_<Session, py::smart_holder>(m, "Session")
            .def(py::init<std::string, std::string, std::string, adtf::util::log::tLogLevel>(), py::arg("environment"),
                 py::arg("session"), py::arg("filtergraph") = ""s,
                 py::arg("log_level") = adtf::util::log::tLogLevel::Warning)
            .def("__enter__", &Session::enter, "Enter the session context and raise the runlevel to RL_FilterGraph(4).")
            .def("__exit__", &Session::exit,
                 "Leave the context and decrease the runlevel to RL_Shutdown(0) and release all resources.")
            .def("__aenter__", &Session::aenter,
                 "Enter the session context and raise the runlevel to RL_FilterGraph(4).")
            .def("__aexit__", &Session::aexit,
                 "Leave the context and decrease the runlevel to RL_Shutdown(0) and release all resources.")
            .def_property_readonly("graph_object_names", &Session::graph_objects_names,
                                   "A list of all graph object names within the filtergraph of the session. Must be "
                                   "called in the context of :class:Session.")
            .def_property_readonly("output_pin_names", &Session::output_pin_names,
                                   "A list of all output pin names within the filtergraph of the session. Must be "
                                   "called in the context of :class:Session.")
            .def("run", &Session::run, "Create a new :class:RunGuard. Must be called in the context of :class:Session.")
            .def("open_stream", &Session::open_stream,
                 "Create a new :class:StreamReader attached to the given output pin within the ADTF filter graph. Must "
                 "be called in the context of :class:Session. Must not be called in the context of :class:RunGuard.",
                 py::arg("pin_name"), py::arg("requests") = std::nullopt, py::arg("items") = Items::ALL)
            .def_static("stop_active", &Session::stop_active)
            .doc() = R"doc(Represents a single ADTF session (environment + session file).

A :class:`Session` owns the underlying ADTF runtime for a given environment
and session configuration. It is both a synchronous and asynchronous context
manager and enforces that only one session is active per process.

Construction
------------
Session(environment: str, session: str, filtergraph: str = "", log_level: LogLevel = LogLevel.WARNING)

- ``environment``: Path to the ADTF ``.adtfenvironment`` file.
- ``session``:     Path to the ADTF ``.adtfsession`` file.
- ``filtergraph``: Optional name of the filter graph to activate in the session.
- ``log_level``:   ADTF log level to use for this session.

Context management
------------------
Using a session synchronously:

    with adtf.Session("my.adtfenvironment", "my.adtfsession") as session:
        # ADTF runtime is initialized (runlevel RL_FilterGraph)
        with session.run():
            # ADTF is running (runlevel RL_Running)
            ...

Asynchronously (e.g. with asyncio):

    async with adtf.Session("my.adtfenvironment", "my.adtfsession") as session:
        async with session.run():
            ...

Entering the session context initializes and launches the ADTF system up to
runlevel ``RL_FilterGraph`` (4). Leaving the context completely shuts down and
releases the session. Only one session context may be active at a time.

Accessing data
--------------
Once inside a session context you can:

- Inspect available graph objects via :attr:`Session.graph_objects`.
- Get all output pins via :attr:`Session.output_pin_names`.
- Open one or more streams using :meth:`Session.open_stream`, which returns
  :class:`StreamReader` objects yielding :class:`Sample`, :class:`StreamType`
  and :class:`Trigger` items via the context of :class:ProcessingScope.)doc";
    }
} // namespace adtf::python::MODULE_RELEASE_ABI_VERSION