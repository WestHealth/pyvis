#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
visualize_instance.py: create a visualization for the given instance.

Usage:
    visualize_instance.py -i <instance_folder> -o <output_file>

Arguments:
    -i --instance_folder <arg>  Instance folder.
    -o --output_file <arg>      Output file (HTML).

Created on  Feb 06, 2024 by cea.
Modified on Jul 03, 2025 by cea.
"""

from pathlib import Path

import docopt
import pandas as pd

from ase_uni_rehoming.core.instance import Instance
from ase_uni_rehoming.utils.config import load_configuration
from ase_uni_rehoming.utils.visualization import (
    create_instance_visualization, create_instance_visualization_data
)

###############################################################################

if __name__ == "__main__":
    args = docopt.docopt(__doc__)

    instance_folder = Path(args["--instance_folder"])
    location_name = instance_folder.name

    config_file = instance_folder / "algorithm_configuration.csv"
    config = load_configuration(pd.read_csv(config_file, low_memory=False))

    uni_file = instance_folder / "unis.csv"
    df_unis = pd.read_csv(uni_file, low_memory=False)

    fbs_file = instance_folder / "fbss.csv"
    df_fbss = pd.read_csv(fbs_file, low_memory=False)

    links_file = instance_folder / "links.csv"
    df_links = pd.read_csv(links_file, low_memory=False)

    switches_port_link_counting_file = instance_folder / "port_link_counting.csv"
    df_switches_port_link_counting = \
        pd.read_csv(switches_port_link_counting_file, low_memory=False)

    switch_types_file = instance_folder / "switches_info.csv"
    df_switch_types = pd.read_csv(switch_types_file, low_memory=False)

    abs_eligibility_file = instance_folder / "abs_eligibility.csv"
    df_abs_eligibility = pd.read_csv(abs_eligibility_file, low_memory=False)

    vlans_file = instance_folder / "vlan_cluster.csv"
    df_vlans = pd.read_csv(vlans_file, low_memory=False)

    associated_costs_file = instance_folder / "associated_costs.csv"
    df_associated_costs = pd.read_csv(associated_costs_file, low_memory=False)

    multiplexing_ratios_file = instance_folder / "multiplexing_ratios.csv"
    df_multiplexing_ratios = pd.read_csv(multiplexing_ratios_file, low_memory=False)

    empty_emuxs_file = instance_folder / "empty_emuxs.csv"
    df_empty_emuxs = pd.read_csv(empty_emuxs_file, low_memory=False)

    switch_ips_file = instance_folder / "switch_ips.csv"
    df_switch_ips = pd.read_csv(switch_ips_file, low_memory=False)

    try:
        rooms_file = instance_folder / "rooms.csv"
        df_rooms = pd.read_csv(rooms_file, low_memory=False).astype(str)
    except Exception:
        df_rooms = pd.DataFrame(columns=["location", "node", "room"]).astype(str)

    ipag_types = set()
    with open(instance_folder / "ipag_types.txt", "r", encoding="utf8") as fm:
        for line in fm.readlines():
            ipag_types.add(line.strip())

    port_technologies_to_include = set()
    with open(instance_folder / "port_technologies_to_include.txt", "r",
            encoding="utf8") as fm:
        for line in fm.readlines():
            port_technologies_to_include.add(line.strip())

    config["port_technologies_to_include"] = sorted(port_technologies_to_include)

    instance = Instance()
    instance.build(
        location_name=location_name,
        df_unis=df_unis,
        df_fbss=df_fbss,
        df_links=df_links,
        df_switches_port_link_counting=df_switches_port_link_counting,
        df_switch_types=df_switch_types,
        df_vlans=df_vlans,
        df_abs_eligibility=df_abs_eligibility,
        df_associated_costs=df_associated_costs,
        df_multiplexing_ratios=df_multiplexing_ratios,
        df_empty_emuxs=df_empty_emuxs,
        df_rooms=df_rooms,
        df_switch_ips=df_switch_ips,
        ipag_types=ipag_types,
        configuration=config
    )

    df_nodes, df_links = create_instance_visualization_data(instance)

    with open(Path(args["--output_file"]), "w") as hd:
        create_instance_visualization(df_nodes, df_links, hd)
