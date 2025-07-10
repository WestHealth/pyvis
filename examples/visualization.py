"""
utils.visualization: network visualization routines.

This module contains some network visualization routines.

@author: Carlos Eduardo de Andrade <cea@research.att.com>

(c) Copyright 2025, AT&T Labs Research.
    AT&T Intellectual Property. All Rights Reserved.

Created on  Jan 24, 2024 by cea.
Modified on Jul 07, 2025 by cea.
"""

# from collections import defaultdict
from io import TextIOWrapper

import networkx as nx
import numpy as np
import pandas as pd

from ase_uni_rehoming.core.instance import Instance
from ase_uni_rehoming.core.solution import Solution
from ase_uni_rehoming.utils.units import add_units
from ase_uni_rehoming.utils.concat import concat_dataframes
from ase_uni_rehoming.utils.schemas.optimization_output import (
    VISUALIZATION_INSTANCE_NODES_PANDAS_SCHEMA,
    VISUALIZATION_INSTANCE_LINKS_PANDAS_SCHEMA,
    VISUALIZATION_SOLUTION_NODES_PANDAS_SCHEMA,
    VISUALIZATION_SOLUTION_LINKS_PANDAS_SCHEMA,
    VISUALIZATION_VALID_SWITCHES_PANDAS_SCHEMA
)
from ase_uni_rehoming.utils.third_party.pyvis.network import Network


###############################################################################
# Colors
###############################################################################

COLOR_UNI_NOT_MOVING = "DarkOliveGreen"
COLOR_UNI_NO_DIVERSE = "LimeGreen"
COLOR_UNI_DIVERSE = "Crimson"
COLOR_UNI_ASOD = "magenta"
COLOR_UNI_PPCOS = "orange"
COLOR_UNI_COLLECTOR_TYPE = "#FF2400" #"Scarlet"
COLOR_FBS = "MediumSpringGreen"
COLOR_UNI_NO_ACTIVE = "grey"
COLOR_SERVICE_PENDING_DISCONNECT = "grey"
COLOR_NTE_USED = "blue"
COLOR_NTE_EMPTY = "lightblue"
COLOR_EMUX = "gold"
COLOR_EMUX_EXTERNAL_LINKS = "Goldenrod"
COLOR_REMOTE_NODE = "Sienna"
COLOR_IPAG = "pink"
COLOR_INACTIVE = "grey"

SERVICE_SHAPE = "dot"
NTE_SHAPE = "square"
EMUX_SHAPE = "diamond"
IPAG_SHAPE = "triangle"
INACTIVE_SHAPE = "star"


###############################################################################

def color_switches(df_valid_switches: pd.DataFrame) -> pd.DataFrame:
    """
    Color the switches of the given dataframe.
    """

    # First, we merge some more usefull information.
    # Let us color the switches by their type.
    # TODO: add the configuration type here.
    df_valid_switches = (
        df_valid_switches
        [df_valid_switches["port_type"] == "uplink"]
        [[
            "node", "nte_node_sub_type", "nte_node_type", "load", "location",
            "num_non_co_located", "vlan", "room", "is_remote", "abf_eligible",
            "maximum_drops", "ip_type", "mgnt_ip", "reason_for_unknown",
            "role", "uni_collector_type"
        ]]
        .drop_duplicates()
        .rename(columns={
            "location": "switch_location"
        })
    )

    conditions = [
        (df_valid_switches["nte_node_type"]
            .str.contains("EMUX", case=False, na=False)),
        (df_valid_switches["nte_node_type"]
            .str.contains("IPAG", case=False, na=False))
    ]

    choices = ["EMUX", "IPAG"]
    df_valid_switches["base_type"] = \
        np.select(conditions, choices, default="NTE")

    colors = [COLOR_EMUX, COLOR_IPAG]
    df_valid_switches["switch_color"] = \
        np.select(conditions, colors, default=COLOR_NTE_USED)

    have_external_links = (
        (df_valid_switches["base_type"] != "IPAG")
        &
        (df_valid_switches["num_non_co_located"] > 0)
    )

    df_valid_switches.loc[have_external_links, "switch_color"] = \
        COLOR_EMUX_EXTERNAL_LINKS

    is_remote_switch = (
        (df_valid_switches["is_remote"])
        &
        (df_valid_switches["base_type"] != "IPAG")
    )

    df_valid_switches.loc[is_remote_switch, "switch_color"] = COLOR_REMOTE_NODE

    shapes = [EMUX_SHAPE, IPAG_SHAPE]
    df_valid_switches["shape"] = \
        np.select(conditions, shapes, default=NTE_SHAPE)

    return df_valid_switches


###############################################################################

def create_instance_visualization_data(instance: Instance) \
    -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create data for the visualization of the given instance.

    Args:
        - instance: an instance to be visualized.

    Returns:
        A tuple with:
        - a dataframe for the nodes information (`df_services_switches`);
        - a dataframe for the links information (`df_links`).
    """

    # First, we merge some more usefull information.
    # Let us color the switches by their type.
    df_valid_switches = color_switches(instance.df_valid_switches)

    # Let's color the UNIs.
    df_services_switches = pd.merge(
        concat_dataframes([instance.df_services, instance.df_pending_disconn_services])
        [[
            "service", "diversity_type", "product_type", "uni_cos_category",
             "committed_information_rate", "service_status",
             "pending_disconnect", "original_committed_information_rate",
             "nte_location", "oversubscribed", "vlan", "room", "location",
             "is_movable", "is_active", "no_mobility_reasons",
             "uni_collector_type"
        ]].rename(columns={
            "vlan": "service_vlan",
            "room": "service_room",
            "uni_collector_type": "service_uni_collector_type"
        }),
        df_valid_switches.rename(columns={
            "vlan": "switch_vlan",
            "room": "switch_room",
            "uni_collector_type": "switch_uni_collector_type"
        }),
        how="left",
        left_on="nte_location",
        right_on="node"
    )

    df_services_switches["service_room"] = \
        df_services_switches["service_room"].fillna("No room info.")

    df_services_switches["service_vlan"] = \
        df_services_switches["service_vlan"].fillna("No VLAN info.")

    df_services_switches.rename(
        columns={"location": "service_location"},
        inplace=True
    )

    no_moving_uni_indices = ~df_services_switches["is_movable"]
    no_active_uni_indices = ~df_services_switches["is_active"]

    diverse_uni_indices = (
        df_services_switches["diversity_type"].str.upper() != "NON-DIVERSE UNI"
    )

    asod_indices = (
        df_services_switches["product_type"] == "SDN-ETHERNET"
    )

    fix_cos_categories = instance.configuration["fix_cos_categories"]
    ppcos_indices = (
        df_services_switches["uni_cos_category"]
        .str.upper()
        .isin(fix_cos_categories)
    )

    fix_uni_collector_types = instance.configuration["fix_uni_collector_types"]
    uni_collector_type_indices = (
        df_services_switches["service_uni_collector_type"]
        .str.upper()
        .isin(fix_uni_collector_types)
    )

    df_services_switches["color"] = COLOR_UNI_NO_DIVERSE
    df_services_switches.loc[no_moving_uni_indices, "color"] = COLOR_UNI_NOT_MOVING
    df_services_switches.loc[no_active_uni_indices, "color"] = COLOR_UNI_NO_ACTIVE
    df_services_switches.loc[asod_indices, "color"] = COLOR_UNI_ASOD
    df_services_switches.loc[ppcos_indices, "color"] = COLOR_UNI_PPCOS
    df_services_switches.loc[uni_collector_type_indices, "color"] = COLOR_UNI_COLLECTOR_TYPE
    df_services_switches.loc[diverse_uni_indices, "color"] = COLOR_UNI_DIVERSE
    df_services_switches.loc[
        df_services_switches["pending_disconnect"], "color"
    ] = COLOR_SERVICE_PENDING_DISCONNECT
    df_services_switches["service_base_type"] = "UNI"

    fbs_indices = df_services_switches["product_type"] == "FBS"
    df_services_switches.loc[fbs_indices, "service_base_type"] = "FBS"
    df_services_switches.loc[fbs_indices, "color"] = COLOR_FBS

    # Now, we build the links.
    df_links = (
        pd.merge(
            instance.original_df_links[[
                "start_node", "end_node", "link_type", "link_speed",
                "start_vlan", "end_vlan"
            ]],
            df_valid_switches[[
                "node", "nte_node_sub_type", "nte_node_type",
                "switch_color", "base_type", "load", "switch_location",
                "shape", "num_non_co_located", "is_remote", "abf_eligible",
                "maximum_drops", "room", "ip_type", "mgnt_ip",
                "reason_for_unknown", "role", "uni_collector_type"
            ]],
            left_on="start_node",
            right_on="node",
            how="left"
        )
        .rename(columns={
            "nte_node_type": "start_type",
            "nte_node_sub_type": "start_sub_type",
            "switch_color": "start_color",
            "base_type": "start_base_type",
            "load": "start_load",
            "switch_location": "start_location",
            "shape": "start_shape",
            "num_non_co_located": "start_num_non_co_located",
            "is_remote": "start_is_remote",
            "abf_eligible": "start_abf_eligible",
            "maximum_drops": "start_maximum_drops",
            "room": "start_room",
            "ip_type": "start_ip_type",
            "mgnt_ip": "start_mgnt_ip",
            "reason_for_unknown": "start_reason_for_unknown",
            "role": "start_role",
            "uni_collector_type": "start_uni_collector_type"
        })
        .drop(columns=["node"])
    )

    df_links = (
        pd.merge(
            df_links,
            df_valid_switches[[
                "node", "nte_node_sub_type", "nte_node_type",
                "switch_color", "base_type", "load", "switch_location",
                "shape", "num_non_co_located", "is_remote", "abf_eligible",
                "maximum_drops", "room", "ip_type", "mgnt_ip",
                "reason_for_unknown", "role", "uni_collector_type"
            ]],
            left_on="end_node",
            right_on="node",
            how="left"
        )
        .rename(columns={
            "nte_node_type": "end_type",
            "nte_node_sub_type": "end_sub_type",
            "switch_color": "end_color",
            "base_type": "end_base_type",
            "load": "end_load",
            "switch_location": "end_location",
            "shape": "end_shape",
            "num_non_co_located": "end_num_non_co_located",
            "is_remote": "end_is_remote",
            "abf_eligible": "end_abf_eligible",
            "maximum_drops": "end_maximum_drops",
            "room": "end_room",
            "ip_type": "end_ip_type",
            "mgnt_ip": "end_mgnt_ip",
            "reason_for_unknown": "end_reason_for_unknown",
            "role": "end_role",
            "uni_collector_type": "end_uni_collector_type"
        })
        .drop(columns=["node"])
    )

    # Before we return, let's enforce the correct data types.
    # NOTE: pending disconn UNIs have a lot of NaN values.
    # Therefore, we just zero them.
    for col, dtype in VISUALIZATION_INSTANCE_NODES_PANDAS_SCHEMA.items():
        if dtype == "int64":
            df_services_switches[col] = df_services_switches[col].fillna(0)
        df_services_switches[col] = df_services_switches[col].astype(dtype)  # type: ignore

    for col, dtype in VISUALIZATION_INSTANCE_LINKS_PANDAS_SCHEMA.items():
        if dtype == "int64":
            df_links[col] = df_links[col].fillna(0)
        df_links[col] = df_links[col].astype(dtype)  # type: ignore

    return df_services_switches, df_links


###############################################################################

def create_instance_visualization(*args) -> None:  # noqa: C901
    """
    Create a visualization for the given instance on HTML format.

    This function can be called with one of the following signatures:

    1. create_instance_visualization(instance: Instance, output_file: TextIOWrapper)
       - instance: an instance to be visualized.
       - output_file: a writable TextIOWrapper object where the visualization
         will be written.

    2. create_instance_visualization(
            df_nodes: pd.DataFrame,
            df_links: pd.DataFrame,
            output_file: TextIOWrapper
       )
       - df_nodes: a Pandas dataframe containing nodes data for visualization.
       - df_links: a Pandas dataframe containing links data for visualization.
       - output_file: a writable TextIOWrapper object where the visualization
         will be written.

    Args:
        *args: Variable length argument list. The function expects either:
           - An instance of `Instance` and a writable `TextIO` object.
           - Two pandas DataFrames (`df_nodes` and `df_links`)
             and a writable `TextIOWrapper` object.

    Raises:
        TypeError: If the provided arguments do not match any of
        the expected signatures.
    """

    instance = None

    if (
            len(args) == 3 and
            isinstance(args[0], pd.DataFrame) and
            isinstance(args[1], pd.DataFrame) and
            isinstance(args[2], TextIOWrapper)
    ):
        df_services_switches, df_links, output_file = args

    elif (
        len(args) == 2 and
        isinstance(args[0], Instance) and
        isinstance(args[1], TextIOWrapper)
    ):
        instance, output_file = args
        df_services_switches, df_links = \
            create_instance_visualization_data(instance)

    else:
        raise TypeError(
            "Invalid arguments provided to 'create_instance_visualization()'"
        )
    # end if

    string_columns = df_services_switches.select_dtypes(include="string").columns
    df_services_switches[string_columns] = \
        df_services_switches[string_columns].fillna("No info.")

    number_columns = df_services_switches.select_dtypes(include="number").columns
    df_services_switches[number_columns] = \
        df_services_switches[number_columns].fillna(0)

    string_columns = df_links.select_dtypes(include="string").columns
    df_links[string_columns] = df_links[string_columns].fillna("No info.")

    number_columns = df_links.select_dtypes(include="number").columns
    df_links[number_columns] = \
        df_links[number_columns].fillna(0)

    if instance is not None:
        fix_cos_categories = instance.configuration["fix_cos_categories"]
        fix_uni_collector_types = instance.configuration["fix_uni_collector_types"]
    else:
        fix_cos_categories = {"PPCOS-SES", "PPCOS"}
        fix_uni_collector_types = {"ENNI"}
    # end if

    # Let's draw the graph starting with UNI -> switch assigment.
    nodes = set()
    used_switches = set()
    graph: nx.MultiDiGraph = nx.MultiDiGraph()
    for row in df_services_switches.itertuples():
        service = str(row.service)
        service_diversity = str(row.diversity_type)
        original_service_cir = add_units(row.original_committed_information_rate)
        adjusted_service_cir = add_units(row.committed_information_rate)
        oversubscribed = row.oversubscribed
        service_color = row.color
        service_location = row.service_location
        service_base_type = row.service_base_type
        product_type = row.product_type
        uni_cos_category = row.uni_cos_category
        is_movable = row.is_movable
        no_mobility_reasons = str(row.no_mobility_reasons).strip()
        service_vlan = row.service_vlan
        service_room = row.service_room
        service_active = row.is_active
        service_status = row.service_status
        service_pending_disconnect = row.pending_disconnect
        service_uni_collector_type = row.service_uni_collector_type

        switch = str(row.node)
        switch_color = str(row.switch_color)
        switch_type = row.nte_node_sub_type
        switch_load = add_units(row.load)
        switch_location = row.switch_location
        switch_base_type = row.base_type
        switch_vlan = row.switch_vlan
        switch_room = row.switch_room
        # switch_shape = row.shape
        switch_num_non_co_located = row.num_non_co_located
        switch_abf_eligible = row.abf_eligible
        switch_maximum_drops = row.maximum_drops
        switch_ip_type = row.ip_type
        switch_mgnt_ip = row.mgnt_ip
        switch_role = row.role
        switch_uni_collector_type = row.switch_uni_collector_type

        if service not in nodes:
            if original_service_cir == adjusted_service_cir:
                label = f"{service}\nCIR: {original_service_cir}"
            else:
                label = f"{service}\nOriCIR: {original_service_cir}\n"\
                        f"AdjCIR: {adjusted_service_cir}"

            if len(no_mobility_reasons) > 0:
                no_mobility_reasons = f"No mob. reasons: {no_mobility_reasons}\n"

            title = (
                f"Service: {service}\n"
                f"Base type: {service_base_type}\n"
                f"Active: {'Yes' if service_active else 'No'}\n"
                f"Movable: {'Yes' if is_movable else 'No'}\n"
                f"{no_mobility_reasons}"
                f"Service status: {service_status}\n"
                f"Product type: {product_type}\n"
                f"Diversity: {service_diversity}\n"
                f"UNI Collector type: {service_uni_collector_type}\n"
                f"Original CIR: {original_service_cir}\n"
                f"Adjusted CIR: {adjusted_service_cir}\n"
                f"Oversubscribed: {'Yes' if oversubscribed else 'No'}\n"
                f"COS category: {uni_cos_category}\n"
                f"Location: {service_location}\n"
                f"Room: {service_room}\n"
                f"VLAN: {service_vlan}"
            )

            nodes.add(service)
            graph.add_node(
                service,
                label=label,
                title=title,
                color=service_color,
                diversity=service_diversity,
                uni_collector_type=service_uni_collector_type,
                original_service_cir=original_service_cir,
                adjusted_service_cir=adjusted_service_cir,
                oversubscribed=("Yes" if oversubscribed else "No"),
                is_movable=("Yes" if is_movable else "No"),
                vlan=service_vlan,
                room=service_room,
                location=service_location,
                base_type=service_base_type,
                product_type=product_type,
                uni_cos_category=uni_cos_category,
                shape=SERVICE_SHAPE,
                active=('Yes' if service_active else 'No'),
                status=service_status
            )

        if (not service_pending_disconnect):
            used_switches.add(switch)

            if switch not in nodes:
                nodes.add(switch)

                title = (
                    f"Switch: {switch}\n"
                    f"Base type: {switch_base_type}\n"
                    f"Switch type: {switch_type}\n"
                    # f"Diversity: {service_diversity}\n"
                    f"ABF eligible: {'Yes' if switch_abf_eligible else 'No'}\n"
                    f"IP type: {switch_ip_type}\n"
                    f"Management IP: {switch_mgnt_ip}\n"
                    f"Role: {switch_role}\n"
                    f"UNI Collector type: {switch_uni_collector_type}\n"
                    f"Load: {switch_load}\n"
                    f"Num. drop ports: {switch_maximum_drops}\n"
                    f"Num. remote incoming links: {switch_num_non_co_located}\n"
                    f"Oversubscribed: {'Yes' if oversubscribed else 'No'}\n"
                    f"Location: {switch_location}\n"
                    f"Room: {switch_room}\n"
                    f"VLAN: {switch_vlan}"
                )

                graph.add_node(
                    switch,
                    title=title,
                    label=f"{switch}\n{switch_type}\nLoad: {switch_load}",
                    color=switch_color,
                    switch_type=switch_type,
                    # diversity=service_diversity,
                    ip_type=switch_ip_type,
                    role=switch_role,
                    uni_collector_type=switch_uni_collector_type,
                    oversubscribed=("Yes" if oversubscribed else "No"),
                    vlan=switch_vlan,
                    room=switch_room,
                    load=switch_load,
                    location=switch_location,
                    base_type=switch_base_type,
                    shape=row.shape,
                    num_non_co_located=switch_num_non_co_located,
                    num_drop_ports=switch_maximum_drops
                )
            # end if switch not in nodes

            if (
                ("non-diverse" not in service_diversity.lower()) or \
                (product_type == "SDN-ETHERNET") or \
                (uni_cos_category in fix_cos_categories) or \
                (service_uni_collector_type in fix_uni_collector_types)
            ):
                graph.add_edge(
                    service, switch,
                    color=service_color,
                    dashes=True, weight=2.0
                )
            else:
                graph.add_edge(service, switch, color=switch_color)
            # end if non-diverse
        # end if service_discoon
    # end for

    for row in df_links.itertuples():
        start_base_type = str(row.start_base_type)
        start_location = str(row.start_location)
        start_is_remote = row.start_is_remote

        end_base_type = str(row.end_base_type)
        end_location = str(row.end_location)
        end_is_remote = row.end_is_remote

        # Don't plot external incoming links to local EMUXs.
        if (start_base_type == "EMUX") and (not start_is_remote) and \
           (end_base_type == "NTE") and (end_is_remote):
            continue

        start_node = str(row.start_node)
        start_type = str(row.start_type)
        start_sub_type = str(row.start_sub_type)
        start_color = str(row.start_color)
        start_load = add_units(row.start_load)
        start_vlan = str(row.start_vlan)
        start_room = str(row.start_room)
        start_shape = row.start_shape
        start_num_non_co_located = row.start_num_non_co_located
        start_abf_eligible = row.start_abf_eligible
        start_maximum_drops = row.start_maximum_drops
        start_ip_type = row.start_ip_type
        start_mgnt_ip = row.start_mgnt_ip
        # start_reason_for_unknown = row.start_reason_for_unknown
        start_role = row.start_role
        start_uni_collector_type = row.start_uni_collector_type

        end_node = str(row.end_node)
        end_type = str(row.end_type)
        end_sub_type = str(row.end_sub_type)
        end_color = str(row.end_color)
        end_load = add_units(row.end_load)
        end_vlan = str(row.end_vlan)
        end_room = str(row.end_room)
        end_shape = row.end_shape
        end_num_non_co_located = row.end_num_non_co_located
        end_abf_eligible = row.end_abf_eligible
        end_maximum_drops = row.end_maximum_drops
        end_ip_type = row.end_ip_type
        end_mgnt_ip = row.end_mgnt_ip
        # end_reason_for_unknown = row.end_reason_for_unknown
        end_role = row.end_role
        end_uni_collector_type = row.end_uni_collector_type

        link_type = str(row.link_type)
        link_speed = str(row.link_speed)

        if (not (("IPAG" in start_type) or ("EMUX" in start_type))) and \
           (start_node not in used_switches):
            start_color = COLOR_NTE_EMPTY

        if (not (("IPAG" in end_type) or ("EMUX" in end_type))) and \
           (end_node not in used_switches):
            end_color = COLOR_NTE_EMPTY

        start_type = start_type.upper()
        end_type = end_type.upper()

        edge_color = COLOR_NTE_USED
        if ("EMUX" in start_type) or ("EMUX" in end_type):
            edge_color = COLOR_EMUX

        if ("IPAG" in start_type) or ("IPAG" in end_type):
            edge_color = COLOR_IPAG

        if start_node not in nodes:
            nodes.add(start_node)

            title = (
                f"Switch: {start_node}\n"
                f"Base type: {start_base_type}\n"
                f"Switch type: {start_type}\n"
                f"ABF eligible: {'Yes' if start_abf_eligible else 'No'}\n"
                f"IP type: {start_ip_type}\n"
                f"Management IP: {start_mgnt_ip}\n"
                f"Role: {start_role}\n"
                f"UNI Collector type: {start_uni_collector_type}\n"
                # f"Diversity: {service_diversity}\n"
                f"Load: {start_load}\n"
                f"Num. drop ports: {start_maximum_drops}\n"
                f"Num. remote incoming links: {start_num_non_co_located}\n"
                # f"Oversubscribed: {'Yes' if oversubscribed else 'No'}\n"
                f"Location: {start_location}\n"
                f"Room: {start_room}\n"
                f"VLAN: {start_vlan}"
            )

            graph.add_node(
                start_node,
                title=title,
                label=f"{start_node}\n{start_sub_type}\nLoad: {start_load}",
                color=start_color,
                switch_type=start_type,
                ip_type=start_ip_type,
                role=start_role,
                uni_collector_type=start_uni_collector_type,
                load=start_load,
                base_type=start_base_type,
                location=start_location,
                vlan=start_vlan,
                room=start_room,
                shape=start_shape,
                num_non_co_located=start_num_non_co_located,
                num_drop_ports=start_maximum_drops
            )

        if end_node not in nodes:
            nodes.add(end_node)

            title = (
                f"Switch: {end_node}\n"
                f"Base type: {end_base_type}\n"
                f"Switch type: {end_type}\n"
                f"ABF eligible: {'Yes' if end_abf_eligible else 'No'}\n"
                f"IP type: {end_ip_type}\n"
                f"Management IP: {end_mgnt_ip}\n"
                f"Role: {end_role}\n"
                f"UNI Collector type: {end_uni_collector_type}\n"
                # f"Diversity: {service_diversity}\n"
                f"Load: {end_load}\n"
                f"Num. drop ports: {end_maximum_drops}\n"
                f"Num. remote incoming links: {end_num_non_co_located}\n"
                # f"Oversubscribed: {'Yes' if oversubscribed else 'No'}\n"
                f"Location: {end_location}\n"
                f"Room: {end_room}\n"
                f"VLAN: {end_vlan}"
            )

            graph.add_node(
                end_node,
                title=title,
                label=f"{end_node}\n{end_sub_type}\nLoad: {end_load}",
                color=end_color,
                switch_type=end_type,
                ip_type=end_ip_type,
                role=end_role,
                uni_collector_type=end_uni_collector_type,
                load=end_load,
                base_type=end_base_type,
                location=end_location,
                vlan=end_vlan,
                room=end_room,
                shape=end_shape,
                num_non_co_located=end_num_non_co_located,
                num_drop_ports=end_maximum_drops
            )

        # NOTE: in general, the start nodes are "high-level" switches.
        # Therefore, we invert the order of the edges.
        graph.add_edge(
            end_node, start_node,
            color=edge_color,
            link_speed=link_speed,
            # diversity="Non-Diverse UNI",
            label=f"{link_speed}\n{link_type}"
        )
    # end for

    # We also compute the number of used ports.
    nx.set_node_attributes(graph, 0, "num_used_ports")      # type: ignore
    nx.set_node_attributes(graph, 0, "num_free_ports")      # type: ignore
    nx.set_node_attributes(graph, 0, "num_external_links")  # type: ignore

    for node, data in graph.nodes(data=True):
        if data["base_type"] in ["UNI", "FBS"]:
            continue

        num_external_links = int(data["num_non_co_located"])
        num_used_ports = graph.in_degree(node) + num_external_links  # type: ignore
        num_free_ports = int(data["num_drop_ports"]) - num_used_ports

        graph.nodes[node]["num_used_ports"] = num_used_ports
        graph.nodes[node]["num_free_ports"] = num_free_ports
        graph.nodes[node]["num_external_links"] = num_external_links

        text = (
            f"\nUsed ports: {num_used_ports}"
            f"\nFree ports: {num_free_ports}"
        )
        graph.nodes[node]["label"] += text
        graph.nodes[node]["title"] += text
    # end for

    # This is the final visualizer.
    graph_visualizer = Network(
        directed=True,
        height="1200px",
        notebook=True,
        cdn_resources="in_line",
        neighborhood_highlight=True,
        filter_menu=True,
        select_menu=True
    )

    graph_visualizer.from_nx(graph)
    graph_visualizer.set_edge_smooth("dynamic")

    output_file.reconfigure(encoding="utf-8", errors="replace")
    graph_visualizer.write_html_on_stream(output_file)


###############################################################################

def create_solution_visualization_data(solution: Solution) \
    -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Create data for the visualization of the given solution.

    Args:
        - solution: a solution to be visualized.

    Returns:
        A tuple with:
        - a dataframe for the nodes information (`df_services_switches`);
        - a dataframe for the links information (`df_links`);
        - a dataframe with the valid switches info (`df_valid_switches`).
    """

    # First, we merge some more usefull information.
    # Let us color the switches by their type.

    # TODO: add the configuration type here.
    df_valid_switches = color_switches(solution.instance.df_valid_switches)

    # Get some information about the UNIs and merge with switch info.
    df_services_switches = solution.df_service_assignment.copy()

    # print("\n\n", df_services_switches, "\n\n")

    if "location" not in df_services_switches.columns:
        df_services_switches["location"] = solution.instance.location_name

    no_active_uni_indices = ~df_services_switches["is_active"]
    no_moving_uni_indices = df_services_switches["is_movable"] == "No"

    diverse_uni_indices = (
        df_services_switches["diversity_type"].str.upper() != "NON-DIVERSE UNI"
    )

    asod_indices = (
        df_services_switches["product_type"].str.upper() == "SDN-ETHERNET"
    )

    fix_cos_categories = solution.instance.configuration["fix_cos_categories"]
    ppcos_indices = (
        df_services_switches["uni_cos_category"].str.upper().isin(fix_cos_categories)
    )

    fix_uni_collector_types = solution.instance.configuration["fix_uni_collector_types"]
    uni_collector_type_indices = (
        df_services_switches["uni_collector_type"]
        .str.upper()
        .isin(fix_uni_collector_types)
    )

    df_services_switches["uni_color"] = COLOR_UNI_NO_DIVERSE
    df_services_switches.loc[no_moving_uni_indices, "uni_color"] = COLOR_UNI_NOT_MOVING
    df_services_switches.loc[no_active_uni_indices, "uni_color"] = COLOR_UNI_NO_ACTIVE
    df_services_switches.loc[asod_indices, "uni_color"] = COLOR_UNI_ASOD
    df_services_switches.loc[ppcos_indices, "uni_color"] = COLOR_UNI_PPCOS
    df_services_switches.loc[uni_collector_type_indices, "uni_color"] = COLOR_UNI_COLLECTOR_TYPE
    df_services_switches.loc[diverse_uni_indices, "uni_color"] = COLOR_UNI_DIVERSE
    df_services_switches.loc[
        df_services_switches["pending_disconnect"], "uni_color"
    ] = COLOR_SERVICE_PENDING_DISCONNECT

    df_services_switches.rename(
        columns={
            "location": "uni_location",
            "base_type": "service_base_type"
        },
        inplace=True
    )

    df_services_switches = pd.merge(
        df_services_switches.rename(columns={
            "vlan": "service_vlan",
            "room": "service_room",
            "uni_collector_type": "service_uni_collector_type"
        }),
        df_valid_switches.rename(columns={
            "vlan": "switch_vlan",
            "room": "switch_room",
            "uni_collector_type": "switch_uni_collector_type"
        }),
        how="left",
        left_on="target_switch",
        right_on="node"
    )

    df_services_switches.loc[
        df_services_switches["pending_disconnect"], "service_room"
    ] = "No room info."

    fbs_indices = df_services_switches["service_base_type"] == "FBS"
    df_services_switches.loc[fbs_indices, "uni_color"] = COLOR_FBS

    # Now, the switch -> switch links.
    df_links = (
        pd.merge(
            solution.df_links[solution.df_links["action"] != "Remove"]
            [[
                "start_node", "end_node", "link_type", "link_speed"
            ]],
            df_valid_switches[[
                "node", "nte_node_sub_type", "nte_node_type",
                "switch_color", "base_type", "switch_location",
                "shape", "vlan", "num_non_co_located", "abf_eligible",
                "maximum_drops", "room", "ip_type", "mgnt_ip",
                "reason_for_unknown", "role", "uni_collector_type"
            ]],
            left_on="start_node",
            right_on="node",
            how="left"
        )
        .rename(columns={
            "nte_node_type": "start_type",
            "nte_node_sub_type": "start_sub_type",
            "switch_color": "start_color",
            "base_type": "start_base_type",
            "switch_location": "start_location",
            "shape": "start_shape",
            "vlan": "start_vlan",
            "num_non_co_located": "start_num_non_co_located",
            "abf_eligible": "start_abf_eligible",
            "maximum_drops": "start_maximum_drops",
            "room": "start_room",
            "ip_type": "start_ip_type",
            "mgnt_ip": "start_mgnt_ip",
            "reason_for_unknown": "start_reason_for_unknown",
            "role": "start_role",
            "uni_collector_type": "start_uni_collector_type"
        })
        .drop(columns=["node"])
    )

    df_links = (
        pd.merge(
            df_links,
            df_valid_switches[[
                "node", "nte_node_sub_type", "nte_node_type",
                "switch_color", "base_type", "switch_location",
                "shape", "vlan", "num_non_co_located", "abf_eligible",
                "maximum_drops", "room", "ip_type", "mgnt_ip",
                "reason_for_unknown", "role", "uni_collector_type"
            ]],
            left_on="end_node",
            right_on="node",
            how="left"
        )
        .rename(columns={
            "nte_node_type": "end_type",
            "nte_node_sub_type": "end_sub_type",
            "switch_color": "end_color",
            "base_type": "end_base_type",
            "switch_location": "end_location",
            "shape": "end_shape",
            "vlan": "end_vlan",
            "num_non_co_located": "end_num_non_co_located",
            "abf_eligible": "end_abf_eligible",
            "maximum_drops": "end_maximum_drops",
            "room": "end_room",
            "ip_type": "end_ip_type",
            "mgnt_ip": "end_mgnt_ip",
            "reason_for_unknown": "end_reason_for_unknown",
            "role": "end_role",
            "uni_collector_type": "end_uni_collector_type"
        })
        .drop(columns=["node"])
    )

    # Before we move on, some integer columns may have NaN values,
    # e.g., pending disconnection UNIs. Therefore, we just zero them.

    # Before we return, let's enforce the correct data types
    for col, dtype in VISUALIZATION_SOLUTION_NODES_PANDAS_SCHEMA.items():
        if dtype == "int64":
            df_services_switches[col] = df_services_switches[col].fillna(0)
        df_services_switches[col] = df_services_switches[col].astype(dtype)  # type: ignore


    for col, dtype in VISUALIZATION_SOLUTION_LINKS_PANDAS_SCHEMA.items():
        df_links[col] = df_links[col].astype(dtype)  # type: ignore

    df_valid_switches = df_valid_switches[["node", "base_type"]]
    for col, dtype in VISUALIZATION_VALID_SWITCHES_PANDAS_SCHEMA.items():
        df_valid_switches[col] = df_valid_switches[col].astype(dtype)  # type: ignore

    return (
        df_services_switches,
        df_links,
        df_valid_switches
    )


###############################################################################

def create_solution_visualization(*args) -> None:  # noqa: C901
    """
    Create a visualization for the given solution on HTML format.

    This function can be called with one of the following signatures:

    1. create_instance_visualization(solution: Solution, output_file: TextIOWrapper)
       - solution: an solution to be visualized.
       - output_file: a writable TextIOWrapper object where the visualization
         will be written.

    2. create_instance_visualization(
            df_nodes: pd.DataFrame,
            df_links: pd.DataFrame,
            df_valid_switches: pd.DataFrame,
            df_switches_to_be_decommissioned: pd.DataFrame,
            output_file: TextIOWrapper
       )
       - df_nodes: a Pandas dataframe containing nodes data for visualization.
       - df_links: a Pandas dataframe containing links data for visualization.
       - df_valid_switches: a Pandas dataframe containing valid switches data
         for visualization.
       - df_switches_to_be_decommissioned: a Pandas dataframe containing
         the list of switches to be decommissioned.
       - output_file: a writable TextIOWrapper object where the visualization
         will be written.

    Args:
        *args: Variable length argument list. The function expects either:
           - An instance of `Instance` and a writable `TextIO` object.
           - Four pandas DataFrames (`df_nodes`, `df_links`, `df_valid_switches`,
             and `df_switches_to_be_decommissioned`) and
             a writable `TextIOWrapper` object.

    Raises:
        TypeError: If the provided arguments do not match any of
        the expected signatures.
    """

    solution = None

    if (
            len(args) == 5 and
            isinstance(args[0], pd.DataFrame) and
            isinstance(args[1], pd.DataFrame) and
            isinstance(args[2], pd.DataFrame) and
            isinstance(args[3], pd.DataFrame) and
            isinstance(args[4], TextIOWrapper)
    ):
        (
            df_services_switches, df_links, df_valid_switches,
            df_switches_to_be_decommissioned, output_file
        ) = args

    elif (
        len(args) == 2 and
        isinstance(args[0], Solution) and
        isinstance(args[1], TextIOWrapper)
    ):
        solution, output_file = args
        df_services_switches, df_links, df_valid_switches = \
            create_solution_visualization_data(solution)

        df_switches_to_be_decommissioned = \
            solution.df_switches_to_be_decommissioned

    else:
        raise TypeError(
            "Invalid arguments provided to 'create_solution_visualization()'"
        )
    # end if

    string_columns = df_services_switches.select_dtypes(include="string").columns
    df_services_switches[string_columns] = \
        df_services_switches[string_columns].fillna("No info.")

    number_columns = df_services_switches.select_dtypes(include="number").columns
    df_services_switches[number_columns] = \
        df_services_switches[number_columns].fillna(0)

    string_columns = df_links.select_dtypes(include="string").columns
    df_links[string_columns] = df_links[string_columns].fillna("No info.")

    number_columns = df_links.select_dtypes(include="number").columns
    df_links[number_columns] = \
        df_links[number_columns].fillna(0)

    string_columns = df_valid_switches.select_dtypes(include="string").columns
    df_valid_switches[string_columns] = \
        df_valid_switches[string_columns].fillna("No info.")

    string_columns = df_switches_to_be_decommissioned.select_dtypes(include="string").columns
    df_switches_to_be_decommissioned[string_columns] = \
        df_switches_to_be_decommissioned[string_columns].fillna("No info.")

    number_columns = df_switches_to_be_decommissioned.select_dtypes(include="number").columns
    df_switches_to_be_decommissioned[number_columns] = \
        df_switches_to_be_decommissioned[number_columns].fillna(0)

    if solution is not None:
        fix_cos_categories = solution.instance.configuration["fix_cos_categories"]
        fix_uni_collector_types = solution.instance.configuration["fix_uni_collector_types"]
    else:
        fix_cos_categories = {"PPCOS-SES", "PPCOS"}
        fix_uni_collector_types = {"ENNI"}
    # end if

    # Let's draw the graph starting with UNI -> switch assigment.
    nodes = set()
    used_switches = set()
    graph: nx.MultiDiGraph = nx.MultiDiGraph()
    for row in df_services_switches.itertuples():
        service = str(row.service)
        service_diversity = str(row.diversity_type)
        original_service_cir = add_units(row.original_committed_information_rate)
        adjusted_service_cir = add_units(row.committed_information_rate)
        oversubscribed = row.oversubscribed
        service_color = row.uni_color
        service_location = row.uni_location
        product_type = row.product_type
        service_base_type = row.service_base_type
        service_cos_category = row.uni_cos_category
        is_movable = row.is_movable
        no_mobility_reasons = str(row.no_mobility_reasons).strip()
        service_vlan = row.service_vlan
        service_room = row.service_room
        service_active = row.is_active
        service_pending_disconnect = row.pending_disconnect
        service_status = row.service_status
        service_uni_collector_type = row.service_uni_collector_type

        switch = str(row.node)
        switch_color = str(row.switch_color)
        switch_type = row.nte_node_sub_type
        switch_load = add_units(row.load)
        switch_location = row.switch_location
        switch_base_type = row.base_type
        # switch_shape = row.shape
        switch_vlan = row.switch_vlan
        switch_room = row.switch_room
        switch_num_non_co_located = row.num_non_co_located
        switch_abf_eligible = row.abf_eligible
        switch_maximum_drops = row.maximum_drops
        switch_ip_type = row.ip_type
        switch_mgnt_ip = row.mgnt_ip
        switch_role = row.role
        switch_uni_collector_type = row.switch_uni_collector_type

        if (switch != "nan") and (switch != "<NA>"):
            used_switches.add(switch)

        if service not in nodes:
            if original_service_cir == adjusted_service_cir:
                label = f"{service}\nCIR: {original_service_cir}"
            else:
                label = f"{service}\nOriCIR: {original_service_cir}\n"\
                        f"AdjCIR: {adjusted_service_cir}"

            if len(no_mobility_reasons) > 0:
                no_mobility_reasons = f"No mob. reasons: {no_mobility_reasons}\n"

            title = (
                f"Service: {service}\n"
                f"Base type: {service_base_type}\n"
                f"Active: {'Yes' if service_active else 'No'}\n"
                f"Movable: {'Yes' if is_movable else 'No'}\n"
                f"{no_mobility_reasons}"
                f"Service status: {service_status}\n"
                f"Product type: {product_type}\n"
                f"Diversity: {service_diversity}\n"
                f"UNI Collector type: {service_uni_collector_type}\n"
                f"Original CIR: {original_service_cir}\n"
                f"Adjusted CIR: {adjusted_service_cir}\n"
                f"Oversubscribed: {'Yes' if oversubscribed else 'No'}\n"
                f"COS category: {service_cos_category}\n"
                f"Location: {service_location}\n"
                f"Room: {service_room}\n"
                f"VLAN: {service_vlan}"
            )

            nodes.add(service)
            graph.add_node(
                service,
                title=title,
                label=label,
                color=service_color,
                diversity=service_diversity,
                uni_collector_type=service_uni_collector_type,
                original_cir=original_service_cir,
                adjusted_cir=adjusted_service_cir,
                oversubscribed=("Yes" if oversubscribed else "No"),
                is_movable=("Yes" if is_movable else "No"),
                vlan=service_vlan,
                room=service_room,
                base_type=service_base_type,
                location=service_location,
                product_type=product_type,
                shape=SERVICE_SHAPE,
                status=service_status
            )
        # end if

        if (
            (not service_pending_disconnect)
            and
            (switch != "nan")
            and
            (switch != "<NA>")
        ):

            if switch not in nodes:
                nodes.add(switch)

                title = (
                    f"Switch: {switch}\n"
                    f"Base type: {switch_base_type}\n"
                    f"Switch type: {switch_type}\n"
                    f"Diversity: {service_diversity}\n"
                    f"ABF eligible: {'Yes' if switch_abf_eligible else 'No'}\n"
                    f"IP type: {switch_ip_type}\n"
                    f"Management IP: {switch_mgnt_ip}\n"
                    f"Role: {switch_role}\n"
                    f"UNI Collector type: {switch_uni_collector_type}\n"
                    f"Load: {switch_load}\n"
                    f"Num. drop ports: {switch_maximum_drops}\n"
                    f"Num. remote incoming links: {switch_num_non_co_located}\n"
                    f"Oversubscribed: {'Yes' if oversubscribed else 'No'}\n"
                    f"Location: {switch_location}\n"
                    f"Room: {switch_room}\n"
                    f"VLAN: {switch_vlan}"
                )

                graph.add_node(
                    switch,
                    title=title,
                    label=f"{switch}\n{switch_type}",
                    color=switch_color,
                    switch_type=switch_type,
                    # diversity=service_diversity,
                    ip_type=switch_ip_type,
                    role=switch_role,
                    uni_collector_type=switch_uni_collector_type,
                    load=switch_load,
                    oversubscribed=("Yes" if oversubscribed else "No"),
                    vlan=switch_vlan,
                    room=switch_room,
                    base_type=switch_base_type,
                    location=switch_location,
                    shape=row.shape,
                    num_non_co_located=switch_num_non_co_located,
                    num_drop_ports=switch_maximum_drops
                )
            # end if new switch

            if (
                ("non-diverse" not in service_diversity.lower()) or
                (product_type == "SDN-ETHERNET") or
                (service_cos_category in fix_cos_categories) or
                (service_uni_collector_type in fix_uni_collector_types)
            ):
                graph.add_edge(
                    service, switch,
                    color=service_color,
                    dashes=True, weight=2.0
                )
            else:
                graph.add_edge(service, switch, color=switch_color)
            # end if diverse
        # end if no-disconnect
    # end for

    # Now, the switch -> switch links.
    for row in df_links.itertuples():
        start_node = str(row.start_node)
        start_type = str(row.start_type)
        start_sub_type = str(row.start_sub_type)
        start_color = str(row.start_color)
        start_base_type = str(row.start_base_type)
        start_location = str(row.start_location)
        start_shape = row.start_shape
        start_vlan = row.start_vlan
        start_room = str(row.start_room)
        start_num_non_co_located = row.start_num_non_co_located
        start_abf_eligible = row.start_abf_eligible
        start_maximum_drops = row.start_maximum_drops
        start_ip_type = row.start_ip_type
        start_mgnt_ip = row.start_mgnt_ip
        # start_reason_for_unknown = row.start_reason_for_unknown
        start_role = row.start_role
        start_uni_collector_type = row.start_uni_collector_type

        end_node = str(row.end_node)
        end_type = str(row.end_type)
        end_sub_type = str(row.end_sub_type)
        end_color = str(row.end_color)
        end_base_type = str(row.end_base_type)
        end_location = str(row.end_location)
        end_shape = row.end_shape
        end_vlan = row.end_vlan
        end_room = str(row.end_room)
        end_num_non_co_located = row.end_num_non_co_located
        end_abf_eligible = row.end_abf_eligible
        end_maximum_drops = row.end_maximum_drops
        end_ip_type = row.end_ip_type
        end_mgnt_ip = row.end_mgnt_ip
        # end_reason_for_unknown = row.end_reason_for_unknown
        end_role = row.end_role
        end_uni_collector_type = row.end_uni_collector_type

        link_type = str(row.link_type)
        link_speed = str(row.link_speed)

        if (not (("IPAG" in start_type) or ("EMUX" in start_type))) and \
           (start_node not in used_switches):
            start_color = COLOR_NTE_EMPTY

        if (not (("IPAG" in end_type) or ("EMUX" in end_type))) and \
           (end_node not in used_switches):
            end_color = COLOR_NTE_EMPTY

        start_type = start_type.upper()
        end_type = end_type.upper()

        edge_color = COLOR_NTE_USED
        if ("EMUX" in start_type) or ("EMUX" in end_type):
            edge_color = COLOR_EMUX

        if ("IPAG" in start_type) or ("IPAG" in end_type):
            edge_color = COLOR_IPAG

        if start_node not in nodes:
            nodes.add(start_node)

            title = (
                f"Switch: {start_node}\n"
                f"Base type: {start_base_type}\n"
                f"Switch type: {start_type}\n"
                f"ABF eligible: {'Yes' if start_abf_eligible else 'No'}\n"
                f"IP type: {start_ip_type}\n"
                f"Management IP: {start_mgnt_ip}\n"
                f"Role: {start_role}\n"
                f"UNI Collector type: {start_uni_collector_type}\n"
                # f"Diversity: {service_diversity}\n"
                # f"Load: {start_load}\n"
                f"Num. drop ports: {start_maximum_drops}\n"
                f"Num. remote incoming links: {start_num_non_co_located}\n"
                # f"Oversubscribed: {'Yes' if oversubscribed else 'No'}\n"
                f"Location: {start_location}\n"
                f"Room: {start_room}\n"
                f"VLAN: {start_vlan}"
            )

            graph.add_node(
                start_node,
                title=title,
                label=f"{start_node}\n{start_sub_type}",
                color=start_color,
                switch_type=start_type,
                ip_type=start_ip_type,
                role=start_role,
                uni_collector_type=start_uni_collector_type,
                base_type=start_base_type,
                location=start_location,
                shape=start_shape,
                vlan=start_vlan,
                room=start_room,
                num_non_co_located=start_num_non_co_located,
                num_drop_ports=start_maximum_drops
            )

        if end_node not in nodes:
            nodes.add(end_node)

            title = (
                f"Switch: {end_node}\n"
                f"Base type: {end_base_type}\n"
                f"Switch type: {end_type}\n"
                f"ABF eligible: {'Yes' if end_abf_eligible else 'No'}\n"
                f"IP type: {end_ip_type}\n"
                f"Management IP: {end_mgnt_ip}\n"
                f"Role: {end_role}\n"
                f"UNI Collector type: {end_uni_collector_type}\n"
                # f"Diversity: {service_diversity}\n"
                # f"Load: {end_load}\n"
                f"Num. drop ports: {end_maximum_drops}\n"
                f"Num. remote incoming links: {end_num_non_co_located}\n"
                # f"Oversubscribed: {'Yes' if oversubscribed else 'No'}\n"
                f"Location: {end_location}\n"
                f"Room: {end_room}\n"
                f"VLAN: {end_vlan}"
            )

            graph.add_node(
                end_node,
                title=title,
                label=f"{end_node}\n{end_sub_type}",
                color=end_color,
                switch_type=end_type,
                ip_type=end_ip_type,
                role=end_role,
                uni_collector_type=end_uni_collector_type,
                base_type=end_base_type,
                location=end_location,
                shape=end_shape,
                vlan=end_vlan,
                room=end_room,
                num_non_co_located=end_num_non_co_located,
                num_drop_ports=end_maximum_drops
            )

        # NOTE: in general, the start nodes are "high-level" switches.
        # Therefore, we invert the order of the edges.
        graph.add_edge(
            end_node, start_node,
            color=edge_color,
            link_speed=link_speed,
            # diversity="Non-Diverse UNI",
            label=f"{link_speed}\n{link_type}",
            link_type=link_type
        )
    # end for

    for row in df_switches_to_be_decommissioned.itertuples():
        switch = row.switch
        switch_type = row.nte_node_sub_type
        switch_base_type = row.base_type
        switch_room = row.room

        label = f"{switch}\n{switch_type}\nNOT USED"
        graph.add_node(
            switch,
            title=label,
            label=label,
            color=COLOR_INACTIVE,
            switch_type=switch_type,
            base_type=switch_base_type,
            diversity="",
            shape=INACTIVE_SHAPE,
            num_non_co_located=0,
            num_drop_ports=0,
            room=switch_room
        )
    # end for

    # # With the graph ready, let us mark all switches that are in the path
    # # of UNIs with diversity requirements.
    # diverse_unis = (
    #     df_services_switches[
    #         ~ (df_services_switches["diversity_type"] == "NON-DIVERSE UNI")
    #         &
    #         ~ (df_services_switches["diversity_type"] == "NON-DIVERSE FBS")
    #         &
    #         ~ (df_services_switches["pending_disconnect"])
    #     ]
    #     [["service", "diversity_type"]]
    # )

    # diversity_types = defaultdict(set)
    # for row in diverse_unis.itertuples():
    #     service = str(row.service)
    #     diversity = row.diversity_type

    #     dfs_edges = nx.edge_dfs(
    #         graph, source=service, orientation="original"
    #     )

    #     for edge in dfs_edges:
    #         node = graph.nodes[edge[1]]
    #         node["diversity"] = diversity
    #         diversity_types[edge[1]].add(diversity)

    #         for key in graph[edge[0]][edge[1]].keys():
    #             graph[edge[0]][edge[1]][key]["diversity"] = diversity
    #     # end for
    # # end for

    # for node_name, div_types in diversity_types.items():
    #     node = graph.nodes[node_name]
    #     div_types = "; ".join(div_types)
    #     node["title"] += f"\nDiversity: {div_types}"
    # # end if

    # We also compute the load in each switch.
    nx.set_node_attributes(graph, 0, "load")  # type: ignore
    for nte in df_valid_switches[df_valid_switches["base_type"] == "NTE"]["node"]:
        if nte not in graph:
            continue

        neighbors = set(graph.predecessors(nte))
        load = int(
            df_services_switches[
                df_services_switches["service"].isin(neighbors)
            ]
            ["committed_information_rate"]
            .sum()
        )

        graph.nodes[nte]["load"] = load
        graph.nodes[nte]["label"] += f"\nLoad: {add_units(load)}"
        graph.nodes[nte]["title"] += f"\nLoad: {add_units(load)}"
    # end for

    for emux in df_valid_switches[df_valid_switches["base_type"] == "EMUX"]["node"]:
        if emux not in graph:
            continue

        neighbors = set(graph.predecessors(emux))
        load = int(
            df_services_switches[
                df_services_switches["service"].isin(neighbors)
            ]
            ["committed_information_rate"]
            .sum()
        )

        for node in neighbors:
            data = graph.nodes[node]
            if data["base_type"] == "NTE":
                load += data["load"]
        # end for

        graph.nodes[emux]["load"] = load
        graph.nodes[emux]["label"] += f"\nLoad: {add_units(load)}"
        graph.nodes[emux]["title"] += f"\nLoad: {add_units(load)}"
    # end for

    for ipag in df_valid_switches[df_valid_switches["base_type"] == "IPAG"]["node"]:
        if ipag not in graph:
            continue
        load = 0
        for node in set(graph.predecessors(ipag)):
            load += graph.nodes[node]["load"]
        # end for

        graph.nodes[ipag]["label"] += f"\nLoad: {add_units(load)}"
        graph.nodes[ipag]["title"] += f"\nLoad: {add_units(load)}"
    # end for

    # We also compute the number of used ports.
    nx.set_node_attributes(graph, 0, "used_ports")          # type: ignore
    nx.set_node_attributes(graph, 0, "num_free_ports")      # type: ignore
    nx.set_node_attributes(graph, 0, "num_external_links")  # type: ignore

    for node, data in graph.nodes(data=True):
        if data["base_type"] in ["UNI", "FBS"]:
            continue

        num_external_links = int(data["num_non_co_located"])
        num_used_ports = graph.in_degree(node) + num_external_links  # type: ignore
        num_free_ports = int(data["num_drop_ports"]) - num_used_ports

        graph.nodes[node]["used_ports"] = num_used_ports
        graph.nodes[node]["num_free_ports"] = num_free_ports
        graph.nodes[node]["num_external_links"] = num_external_links

        text = (
            f"\nUsed ports: {num_used_ports}"
            f"\nFree ports: {num_free_ports}"
        )
        graph.nodes[node]["label"] += text
        graph.nodes[node]["title"] += text
    # end for

    # This is the final visualizer.
    graph_visualizer = Network(
        directed=True,
        height="1200px",
        notebook=True,
        cdn_resources="in_line",
        neighborhood_highlight=True,
        filter_menu=True,
        select_menu=True
    )

    graph_visualizer.from_nx(graph)
    graph_visualizer.set_edge_smooth("dynamic")

    output_file.reconfigure(encoding="utf-8", errors="replace")
    graph_visualizer.write_html_on_stream(output_file)
