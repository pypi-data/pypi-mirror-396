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
#pragma once
#include <adtfstreaming3/adtf_streaming3.h>
#include <adtfsystemsdk/services/session_intf.h>
#include <string>

namespace adtf::python::MODULE_RELEASE_ABI_VERSION::compat
{
    using namespace adtf::ucom;
    using namespace adtf::streaming;
    using namespace std::literals;

    inline std::string get_name(const INamedGraphObject& object)
    {
        std::string name;
        object.GetName(adtf_string_intf(name));
        return name;
    }

    template<typename Interface>
    bool has_interface(const INamedGraphObject& object)
    {
        return ucom_cast<const Interface*>(&object);
    }

    template<typename Interface>
    void get_data_binding_objects(std::vector<std::string>& objects,
                                  const adtf::streaming::ant::IDataBinding* pDataBinding,
                                  const std::string& prefix)
    {
        object_vector<IPin> oPins;
        pDataBinding->GetPins(oPins);
        for (const auto& pPin : oPins)
        {
            if (has_interface<Interface>(*pPin))
            {
                objects.emplace_back(prefix + get_name(*pPin));
            }
        }
    }

    template<typename Interface>
    void get_interface_binding_objects(std::vector<std::string>& objects,
                                       const adtf::streaming::ant::IInterfaceBinding* pInterfaceBinding,
                                       const std::string& prefix)
    {
        object_vector<const IBindingObject> oBindingObjects;
        pInterfaceBinding->GetBindingObjects(oBindingObjects);
        for (const auto& pBindingObject : oBindingObjects)
        {
            if (has_interface<Interface>(*pBindingObject))
            {
                objects.emplace_back(prefix + get_name(*pBindingObject));
            }
        }
    }

    template<typename Interface>
    void get_runner_objects(std::vector<std::string>& objects,
                            const adtf::streaming::ant::IRuntimeBehaviour* pRuntimeBehaviour,
                            const std::string& prefix)
    {
        object_vector<IRunner> oRunnerObjects;
        pRuntimeBehaviour->GetRunners(oRunnerObjects);
        for (const auto& pRunner : oRunnerObjects)
        {
            if (has_interface<Interface>(*pRunner))
            {
                objects.emplace_back(prefix + get_name(*pRunner));
            }
        }
    }

    template<typename Interface = INamedGraphObject>
    void get_objects(std::vector<std::string>& objects,
                     const adtf::streaming::ant::INamedGraphObject& oObject,
                     std::string prefix = ""s)
    {
        prefix.append(get_name(oObject));
        if (has_interface<Interface>(oObject))
        {
            objects.emplace_back(prefix);
        }
        prefix.append("."s);

        using namespace adtf::ucom;
        if (const auto pDataBinding = ucom_cast<const IDataBinding*>(&oObject))
        {
            get_data_binding_objects<Interface>(objects, pDataBinding, prefix);
        }

        if (const auto pInterfaceBinding = ucom_cast<const IInterfaceBinding*>(&oObject))
        {
            get_interface_binding_objects<Interface>(objects, pInterfaceBinding, prefix);
        }

        if (const auto pRuntimeBehaviour = ucom_cast<const IRuntimeBehaviour*>(&oObject))
        {
            get_runner_objects<Interface>(objects, pRuntimeBehaviour, prefix);
        }

        if (const auto pGraph = ucom_cast<const IGraph*>(&oObject))
        {
            object_vector<INamedGraphObject> oChildren;
            pGraph->GetNamedGraphObjects(oChildren);
            for (const auto& pChild : oChildren)
            {
                get_objects<Interface>(objects, *pChild, prefix);
            }
        }
    }

    template<typename Interface>
    std::vector<std::string> get_objects()
    {
        std::vector<std::string> objects;
        object_ptr<IFilterGraph> filter_graph;
        if (IS_OK(adtf::services::get_session_filter_graph(filter_graph)))
        {
            get_objects<Interface>(objects, *filter_graph);
        }
        return objects;
    }
} // namespace compat
