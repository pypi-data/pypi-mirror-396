from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/vlan-interfaces.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_vlan_interfaces = resolve('vlan_interfaces')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['arista.avd.hide_passwords']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.hide_passwords' found.")
    try:
        t_3 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_4 = environment.filters['indent']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'indent' found.")
    try:
        t_5 = environment.filters['list']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'list' found.")
    try:
        t_6 = environment.filters['rejectattr']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No filter named 'rejectattr' found.")
    try:
        t_7 = environment.filters['selectattr']
    except KeyError:
        @internalcode
        def t_7(*unused):
            raise TemplateRuntimeError("No filter named 'selectattr' found.")
    try:
        t_8 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_8(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    for l_1_vlan_interface in t_3((undefined(name='vlan_interfaces') if l_0_vlan_interfaces is missing else l_0_vlan_interfaces), 'name'):
        l_1_with_vrf_dest = resolve('with_vrf_dest')
        l_1_without_vrf_dest = resolve('without_vrf_dest')
        l_1_sorted_ipv6_dhcp_relay_destinations = resolve('sorted_ipv6_dhcp_relay_destinations')
        l_1_ip_attached_host_route_export_cli = resolve('ip_attached_host_route_export_cli')
        l_1_ipv6_attached_host_route_export_cli = resolve('ipv6_attached_host_route_export_cli')
        l_1_host_proxy_cli = resolve('host_proxy_cli')
        l_1_interface_ip_nat = resolve('interface_ip_nat')
        l_1_hide_passwords = resolve('hide_passwords')
        l_1_isis_auth_cli = resolve('isis_auth_cli')
        l_1_both_key_ids = resolve('both_key_ids')
        _loop_vars = {}
        pass
        yield '!\ninterface '
        yield str(environment.getattr(l_1_vlan_interface, 'name'))
        yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'traffic_policy'), 'input')):
            pass
            yield '   traffic-policy input '
            yield str(environment.getattr(environment.getattr(l_1_vlan_interface, 'traffic_policy'), 'input'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'traffic_policy'), 'output')):
            pass
            yield '   traffic-policy output '
            yield str(environment.getattr(environment.getattr(l_1_vlan_interface, 'traffic_policy'), 'output'))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'description')):
            pass
            yield '   description '
            yield str(environment.getattr(l_1_vlan_interface, 'description'))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'shutdown'), True):
            pass
            yield '   shutdown\n'
        elif t_8(environment.getattr(l_1_vlan_interface, 'shutdown'), False):
            pass
            yield '   no shutdown\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'mtu')):
            pass
            yield '   mtu '
            yield str(environment.getattr(l_1_vlan_interface, 'mtu'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'logging'), 'event'), 'link_status'), True):
            pass
            yield '   logging event link-status\n'
        elif t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'logging'), 'event'), 'link_status'), False):
            pass
            yield '   no logging event link-status\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'pvlan_mapping')):
            pass
            yield '   pvlan mapping '
            yield str(environment.getattr(l_1_vlan_interface, 'pvlan_mapping'))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'no_autostate'), True):
            pass
            yield '   no autostate\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'vrf')):
            pass
            yield '   vrf '
            yield str(environment.getattr(l_1_vlan_interface, 'vrf'))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ip_proxy_arp'), True):
            pass
            yield '   ip proxy-arp\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'arp_gratuitous_accept'), True):
            pass
            yield '   arp gratuitous accept\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ip_address')):
            pass
            yield '   ip address '
            yield str(environment.getattr(l_1_vlan_interface, 'ip_address'))
            yield '\n'
            if t_8(environment.getattr(l_1_vlan_interface, 'ip_address_secondaries')):
                pass
                for l_2_ip_address_secondary in t_3(environment.getattr(l_1_vlan_interface, 'ip_address_secondaries')):
                    _loop_vars = {}
                    pass
                    yield '   ip address '
                    yield str(l_2_ip_address_secondary)
                    yield ' secondary\n'
                l_2_ip_address_secondary = missing
        if t_8(environment.getattr(l_1_vlan_interface, 'ip_verify_unicast_source_reachable_via')):
            pass
            yield '   ip verify unicast source reachable-via '
            yield str(environment.getattr(l_1_vlan_interface, 'ip_verify_unicast_source_reachable_via'))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ip_directed_broadcast'), True):
            pass
            yield '   ip directed-broadcast\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'arp_aging_timeout')):
            pass
            yield '   arp aging timeout '
            yield str(environment.getattr(l_1_vlan_interface, 'arp_aging_timeout'))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'arp_cache_dynamic_capacity')):
            pass
            yield '   arp cache dynamic capacity '
            yield str(environment.getattr(l_1_vlan_interface, 'arp_cache_dynamic_capacity'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'ipv6_nd_cache'), 'expire')):
            pass
            yield '   ipv6 nd cache expire '
            yield str(environment.getattr(environment.getattr(l_1_vlan_interface, 'ipv6_nd_cache'), 'expire'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'ipv6_nd_cache'), 'dynamic_capacity')):
            pass
            yield '   ipv6 nd cache dynamic capacity '
            yield str(environment.getattr(environment.getattr(l_1_vlan_interface, 'ipv6_nd_cache'), 'dynamic_capacity'))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'arp_monitor_mac_address'), True):
            pass
            yield '   arp monitor mac-address\n'
        if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'ipv6_nd_cache'), 'refresh_always'), True):
            pass
            yield '   ipv6 nd cache refresh always\n'
        if ((t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'bfd'), 'interval')) and t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'bfd'), 'min_rx'))) and t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'bfd'), 'multiplier'))):
            pass
            yield '   bfd interval '
            yield str(environment.getattr(environment.getattr(l_1_vlan_interface, 'bfd'), 'interval'))
            yield ' min-rx '
            yield str(environment.getattr(environment.getattr(l_1_vlan_interface, 'bfd'), 'min_rx'))
            yield ' multiplier '
            yield str(environment.getattr(environment.getattr(l_1_vlan_interface, 'bfd'), 'multiplier'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'bfd'), 'echo'), True):
            pass
            yield '   bfd echo\n'
        elif t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'bfd'), 'echo'), False):
            pass
            yield '   no bfd echo\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ip_dhcp_relay_all_subnets'), True):
            pass
            yield '   ip dhcp relay all-subnets\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_dhcp_relay_all_subnets'), True):
            pass
            yield '   ipv6 dhcp relay all-subnets\n'
        for l_2_ip_helper in t_3(environment.getattr(l_1_vlan_interface, 'ip_helpers'), 'ip_helper'):
            l_2_ip_helper_cli = missing
            _loop_vars = {}
            pass
            l_2_ip_helper_cli = str_join(('ip helper-address ', environment.getattr(l_2_ip_helper, 'ip_helper'), ))
            _loop_vars['ip_helper_cli'] = l_2_ip_helper_cli
            if t_8(environment.getattr(l_2_ip_helper, 'vrf')):
                pass
                l_2_ip_helper_cli = str_join(((undefined(name='ip_helper_cli') if l_2_ip_helper_cli is missing else l_2_ip_helper_cli), ' vrf ', environment.getattr(l_2_ip_helper, 'vrf'), ))
                _loop_vars['ip_helper_cli'] = l_2_ip_helper_cli
            if t_8(environment.getattr(l_2_ip_helper, 'source_interface')):
                pass
                l_2_ip_helper_cli = str_join(((undefined(name='ip_helper_cli') if l_2_ip_helper_cli is missing else l_2_ip_helper_cli), ' source-interface ', environment.getattr(l_2_ip_helper, 'source_interface'), ))
                _loop_vars['ip_helper_cli'] = l_2_ip_helper_cli
            yield '   '
            yield str((undefined(name='ip_helper_cli') if l_2_ip_helper_cli is missing else l_2_ip_helper_cli))
            yield '\n'
        l_2_ip_helper = l_2_ip_helper_cli = missing
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_dhcp_relay_destinations')):
            pass
            l_1_with_vrf_dest = t_3(t_3(t_7(context, environment.getattr(l_1_vlan_interface, 'ipv6_dhcp_relay_destinations'), 'vrf', 'arista.avd.defined'), 'address'), 'vrf')
            _loop_vars['with_vrf_dest'] = l_1_with_vrf_dest
            l_1_without_vrf_dest = t_3(t_6(context, environment.getattr(l_1_vlan_interface, 'ipv6_dhcp_relay_destinations'), 'vrf', 'arista.avd.defined'), 'address')
            _loop_vars['without_vrf_dest'] = l_1_without_vrf_dest
            l_1_sorted_ipv6_dhcp_relay_destinations = (t_5(context.eval_ctx, (undefined(name='without_vrf_dest') if l_1_without_vrf_dest is missing else l_1_without_vrf_dest)) + t_5(context.eval_ctx, (undefined(name='with_vrf_dest') if l_1_with_vrf_dest is missing else l_1_with_vrf_dest)))
            _loop_vars['sorted_ipv6_dhcp_relay_destinations'] = l_1_sorted_ipv6_dhcp_relay_destinations
        for l_2_destination in t_1((undefined(name='sorted_ipv6_dhcp_relay_destinations') if l_1_sorted_ipv6_dhcp_relay_destinations is missing else l_1_sorted_ipv6_dhcp_relay_destinations), []):
            l_2_destination_cli = missing
            _loop_vars = {}
            pass
            l_2_destination_cli = str_join(('ipv6 dhcp relay destination ', environment.getattr(l_2_destination, 'address'), ))
            _loop_vars['destination_cli'] = l_2_destination_cli
            if t_8(environment.getattr(l_2_destination, 'vrf')):
                pass
                l_2_destination_cli = str_join(((undefined(name='destination_cli') if l_2_destination_cli is missing else l_2_destination_cli), ' vrf ', environment.getattr(l_2_destination, 'vrf'), ))
                _loop_vars['destination_cli'] = l_2_destination_cli
            if t_8(environment.getattr(l_2_destination, 'local_interface')):
                pass
                l_2_destination_cli = str_join(((undefined(name='destination_cli') if l_2_destination_cli is missing else l_2_destination_cli), ' local-interface ', environment.getattr(l_2_destination, 'local_interface'), ))
                _loop_vars['destination_cli'] = l_2_destination_cli
            elif t_8(environment.getattr(l_2_destination, 'source_address')):
                pass
                l_2_destination_cli = str_join(((undefined(name='destination_cli') if l_2_destination_cli is missing else l_2_destination_cli), ' source-address ', environment.getattr(l_2_destination, 'source_address'), ))
                _loop_vars['destination_cli'] = l_2_destination_cli
            if t_8(environment.getattr(l_2_destination, 'link_address')):
                pass
                l_2_destination_cli = str_join(((undefined(name='destination_cli') if l_2_destination_cli is missing else l_2_destination_cli), ' link-address ', environment.getattr(l_2_destination, 'link_address'), ))
                _loop_vars['destination_cli'] = l_2_destination_cli
            yield '   '
            yield str((undefined(name='destination_cli') if l_2_destination_cli is missing else l_2_destination_cli))
            yield '\n'
        l_2_destination = l_2_destination_cli = missing
        if t_8(environment.getattr(l_1_vlan_interface, 'dhcp_server_ipv4'), True):
            pass
            yield '   dhcp server ipv4\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'dhcp_server_ipv6'), True):
            pass
            yield '   dhcp server ipv6\n'
        if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'ip_attached_host_route_export'), 'enabled'), True):
            pass
            l_1_ip_attached_host_route_export_cli = 'ip attached-host route export'
            _loop_vars['ip_attached_host_route_export_cli'] = l_1_ip_attached_host_route_export_cli
            if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'ip_attached_host_route_export'), 'distance')):
                pass
                l_1_ip_attached_host_route_export_cli = str_join(((undefined(name='ip_attached_host_route_export_cli') if l_1_ip_attached_host_route_export_cli is missing else l_1_ip_attached_host_route_export_cli), ' ', environment.getattr(environment.getattr(l_1_vlan_interface, 'ip_attached_host_route_export'), 'distance'), ))
                _loop_vars['ip_attached_host_route_export_cli'] = l_1_ip_attached_host_route_export_cli
            yield '   '
            yield str((undefined(name='ip_attached_host_route_export_cli') if l_1_ip_attached_host_route_export_cli is missing else l_1_ip_attached_host_route_export_cli))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'ipv6_attached_host_route_export'), 'enabled'), True):
            pass
            l_1_ipv6_attached_host_route_export_cli = 'ipv6 attached-host route export'
            _loop_vars['ipv6_attached_host_route_export_cli'] = l_1_ipv6_attached_host_route_export_cli
            if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'ipv6_attached_host_route_export'), 'distance')):
                pass
                l_1_ipv6_attached_host_route_export_cli = str_join(((undefined(name='ipv6_attached_host_route_export_cli') if l_1_ipv6_attached_host_route_export_cli is missing else l_1_ipv6_attached_host_route_export_cli), ' ', environment.getattr(environment.getattr(l_1_vlan_interface, 'ipv6_attached_host_route_export'), 'distance'), ))
                _loop_vars['ipv6_attached_host_route_export_cli'] = l_1_ipv6_attached_host_route_export_cli
            if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'ipv6_attached_host_route_export'), 'prefix_length')):
                pass
                l_1_ipv6_attached_host_route_export_cli = str_join(((undefined(name='ipv6_attached_host_route_export_cli') if l_1_ipv6_attached_host_route_export_cli is missing else l_1_ipv6_attached_host_route_export_cli), ' prefix-length ', environment.getattr(environment.getattr(l_1_vlan_interface, 'ipv6_attached_host_route_export'), 'prefix_length'), ))
                _loop_vars['ipv6_attached_host_route_export_cli'] = l_1_ipv6_attached_host_route_export_cli
            yield '   '
            yield str((undefined(name='ipv6_attached_host_route_export_cli') if l_1_ipv6_attached_host_route_export_cli is missing else l_1_ipv6_attached_host_route_export_cli))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ip_igmp'), True):
            pass
            yield '   ip igmp\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ip_igmp_version')):
            pass
            yield '   ip igmp version '
            yield str(environment.getattr(l_1_vlan_interface, 'ip_igmp_version'))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ip_igmp_querier_address_virtual'), True):
            pass
            yield '   ip igmp querier address virtual\n'
        if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'ip_igmp_host_proxy'), 'enabled'), True):
            pass
            l_1_host_proxy_cli = 'ip igmp host-proxy'
            _loop_vars['host_proxy_cli'] = l_1_host_proxy_cli
            yield '   '
            yield str((undefined(name='host_proxy_cli') if l_1_host_proxy_cli is missing else l_1_host_proxy_cli))
            yield '\n'
            if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'ip_igmp_host_proxy'), 'groups')):
                pass
                for l_2_proxy_group in environment.getattr(environment.getattr(l_1_vlan_interface, 'ip_igmp_host_proxy'), 'groups'):
                    _loop_vars = {}
                    pass
                    if (t_8(environment.getattr(l_2_proxy_group, 'exclude')) or t_8(environment.getattr(l_2_proxy_group, 'include'))):
                        pass
                        if t_8(environment.getattr(l_2_proxy_group, 'include')):
                            pass
                            for l_3_include_source in environment.getattr(l_2_proxy_group, 'include'):
                                _loop_vars = {}
                                pass
                                yield '   '
                                yield str((undefined(name='host_proxy_cli') if l_1_host_proxy_cli is missing else l_1_host_proxy_cli))
                                yield ' '
                                yield str(environment.getattr(l_2_proxy_group, 'group'))
                                yield ' include '
                                yield str(environment.getattr(l_3_include_source, 'source'))
                                yield '\n'
                            l_3_include_source = missing
                        if t_8(environment.getattr(l_2_proxy_group, 'exclude')):
                            pass
                            for l_3_exclude_source in environment.getattr(l_2_proxy_group, 'exclude'):
                                _loop_vars = {}
                                pass
                                yield '   '
                                yield str((undefined(name='host_proxy_cli') if l_1_host_proxy_cli is missing else l_1_host_proxy_cli))
                                yield ' '
                                yield str(environment.getattr(l_2_proxy_group, 'group'))
                                yield ' exclude '
                                yield str(environment.getattr(l_3_exclude_source, 'source'))
                                yield '\n'
                            l_3_exclude_source = missing
                    elif t_8(environment.getattr(l_2_proxy_group, 'group')):
                        pass
                        yield '   '
                        yield str((undefined(name='host_proxy_cli') if l_1_host_proxy_cli is missing else l_1_host_proxy_cli))
                        yield ' '
                        yield str(environment.getattr(l_2_proxy_group, 'group'))
                        yield '\n'
                l_2_proxy_group = missing
            if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'ip_igmp_host_proxy'), 'access_lists')):
                pass
                for l_2_access_list in environment.getattr(environment.getattr(l_1_vlan_interface, 'ip_igmp_host_proxy'), 'access_lists'):
                    _loop_vars = {}
                    pass
                    yield '   '
                    yield str((undefined(name='host_proxy_cli') if l_1_host_proxy_cli is missing else l_1_host_proxy_cli))
                    yield ' access-list '
                    yield str(environment.getattr(l_2_access_list, 'name'))
                    yield '\n'
                l_2_access_list = missing
            if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'ip_igmp_host_proxy'), 'report_interval')):
                pass
                yield '   '
                yield str((undefined(name='host_proxy_cli') if l_1_host_proxy_cli is missing else l_1_host_proxy_cli))
                yield ' report-interval '
                yield str(environment.getattr(environment.getattr(l_1_vlan_interface, 'ip_igmp_host_proxy'), 'report_interval'))
                yield '\n'
            if t_8(environment.getattr(environment.getattr(l_1_vlan_interface, 'ip_igmp_host_proxy'), 'version')):
                pass
                yield '   '
                yield str((undefined(name='host_proxy_cli') if l_1_host_proxy_cli is missing else l_1_host_proxy_cli))
                yield ' version '
                yield str(environment.getattr(environment.getattr(l_1_vlan_interface, 'ip_igmp_host_proxy'), 'version'))
                yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_enable'), True):
            pass
            yield '   ipv6 enable\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_address')):
            pass
            yield '   ipv6 address '
            yield str(environment.getattr(l_1_vlan_interface, 'ipv6_address'))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_address_link_local')):
            pass
            yield '   ipv6 address '
            yield str(environment.getattr(l_1_vlan_interface, 'ipv6_address_link_local'))
            yield ' link-local\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_nd_ra_disabled'), True):
            pass
            yield '   ipv6 nd ra disabled\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_nd_managed_config_flag'), True):
            pass
            yield '   ipv6 nd managed-config-flag\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_nd_other_config_flag'), True):
            pass
            yield '   ipv6 nd other-config-flag\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_nd_prefixes')):
            pass
            for l_2_prefix in t_3(environment.getattr(l_1_vlan_interface, 'ipv6_nd_prefixes'), 'ipv6_prefix'):
                l_2_ipv6_nd_prefix_cli = missing
                _loop_vars = {}
                pass
                l_2_ipv6_nd_prefix_cli = str_join(('ipv6 nd prefix ', environment.getattr(l_2_prefix, 'ipv6_prefix'), ))
                _loop_vars['ipv6_nd_prefix_cli'] = l_2_ipv6_nd_prefix_cli
                if t_8(environment.getattr(l_2_prefix, 'valid_lifetime')):
                    pass
                    l_2_ipv6_nd_prefix_cli = str_join(((undefined(name='ipv6_nd_prefix_cli') if l_2_ipv6_nd_prefix_cli is missing else l_2_ipv6_nd_prefix_cli), ' ', environment.getattr(l_2_prefix, 'valid_lifetime'), ))
                    _loop_vars['ipv6_nd_prefix_cli'] = l_2_ipv6_nd_prefix_cli
                    if t_8(environment.getattr(l_2_prefix, 'preferred_lifetime')):
                        pass
                        l_2_ipv6_nd_prefix_cli = str_join(((undefined(name='ipv6_nd_prefix_cli') if l_2_ipv6_nd_prefix_cli is missing else l_2_ipv6_nd_prefix_cli), ' ', environment.getattr(l_2_prefix, 'preferred_lifetime'), ))
                        _loop_vars['ipv6_nd_prefix_cli'] = l_2_ipv6_nd_prefix_cli
                if t_8(environment.getattr(l_2_prefix, 'no_autoconfig_flag'), True):
                    pass
                    l_2_ipv6_nd_prefix_cli = str_join(((undefined(name='ipv6_nd_prefix_cli') if l_2_ipv6_nd_prefix_cli is missing else l_2_ipv6_nd_prefix_cli), ' no-autoconfig', ))
                    _loop_vars['ipv6_nd_prefix_cli'] = l_2_ipv6_nd_prefix_cli
                yield '   '
                yield str((undefined(name='ipv6_nd_prefix_cli') if l_2_ipv6_nd_prefix_cli is missing else l_2_ipv6_nd_prefix_cli))
                yield '\n'
            l_2_prefix = l_2_ipv6_nd_prefix_cli = missing
        if t_8(environment.getattr(l_1_vlan_interface, 'access_group_in')):
            pass
            yield '   ip access-group '
            yield str(environment.getattr(l_1_vlan_interface, 'access_group_in'))
            yield ' in\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'access_group_out')):
            pass
            yield '   ip access-group '
            yield str(environment.getattr(l_1_vlan_interface, 'access_group_out'))
            yield ' out\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_access_group_in')):
            pass
            yield '   ipv6 access-group '
            yield str(environment.getattr(l_1_vlan_interface, 'ipv6_access_group_in'))
            yield ' in\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_access_group_out')):
            pass
            yield '   ipv6 access-group '
            yield str(environment.getattr(l_1_vlan_interface, 'ipv6_access_group_out'))
            yield ' out\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'multicast')):
            pass
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'multicast'), 'ipv4'), 'boundaries')):
                pass
                for l_2_boundary in t_3(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'multicast'), 'ipv4'), 'boundaries'), 'boundary'):
                    l_2_boundary_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_boundary_cli = str_join(('multicast ipv4 boundary ', environment.getattr(l_2_boundary, 'boundary'), ))
                    _loop_vars['boundary_cli'] = l_2_boundary_cli
                    if t_8(environment.getattr(l_2_boundary, 'out'), True):
                        pass
                        l_2_boundary_cli = str_join(((undefined(name='boundary_cli') if l_2_boundary_cli is missing else l_2_boundary_cli), ' out', ))
                        _loop_vars['boundary_cli'] = l_2_boundary_cli
                    yield '   '
                    yield str((undefined(name='boundary_cli') if l_2_boundary_cli is missing else l_2_boundary_cli))
                    yield '\n'
                l_2_boundary = l_2_boundary_cli = missing
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'multicast'), 'ipv6'), 'boundaries')):
                pass
                for l_2_boundary in t_3(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'multicast'), 'ipv6'), 'boundaries'), 'boundary'):
                    _loop_vars = {}
                    pass
                    yield '   multicast ipv6 boundary '
                    yield str(environment.getattr(l_2_boundary, 'boundary'))
                    yield ' out\n'
                l_2_boundary = missing
            if t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'multicast'), 'ipv4'), 'source_route_export'), 'enabled'), True):
                pass
                if t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'multicast'), 'ipv4'), 'source_route_export'), 'administrative_distance')):
                    pass
                    yield '   multicast ipv4 source route export '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'multicast'), 'ipv4'), 'source_route_export'), 'administrative_distance'))
                    yield '\n'
                else:
                    pass
                    yield '   multicast ipv4 source route export\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'multicast'), 'ipv6'), 'source_route_export'), 'enabled'), True):
                pass
                if t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'multicast'), 'ipv6'), 'source_route_export'), 'administrative_distance')):
                    pass
                    yield '   multicast ipv6 source route export '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'multicast'), 'ipv6'), 'source_route_export'), 'administrative_distance'))
                    yield '\n'
                else:
                    pass
                    yield '   multicast ipv6 source route export\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'multicast'), 'ipv4'), 'static'), True):
                pass
                yield '   multicast ipv4 static\n'
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'multicast'), 'ipv6'), 'static'), True):
                pass
                yield '   multicast ipv6 static\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ip_nat')):
            pass
            l_1_interface_ip_nat = environment.getattr(l_1_vlan_interface, 'ip_nat')
            _loop_vars['interface_ip_nat'] = l_1_interface_ip_nat
            template = environment.get_template('eos/interface-ip-nat.j2', 'eos/vlan-interfaces.j2')
            gen = template.root_render_func(template.new_context(context.get_all(), True, {'both_key_ids': l_1_both_key_ids, 'host_proxy_cli': l_1_host_proxy_cli, 'interface_ip_nat': l_1_interface_ip_nat, 'ip_attached_host_route_export_cli': l_1_ip_attached_host_route_export_cli, 'ipv6_attached_host_route_export_cli': l_1_ipv6_attached_host_route_export_cli, 'isis_auth_cli': l_1_isis_auth_cli, 'sorted_ipv6_dhcp_relay_destinations': l_1_sorted_ipv6_dhcp_relay_destinations, 'vlan_interface': l_1_vlan_interface, 'with_vrf_dest': l_1_with_vrf_dest, 'without_vrf_dest': l_1_without_vrf_dest}))
            try:
                for event in gen:
                    yield event
            finally: gen.close()
        if t_8(environment.getattr(l_1_vlan_interface, 'ntp_serve')):
            pass
            if environment.getattr(l_1_vlan_interface, 'ntp_serve'):
                pass
                yield '   ntp serve\n'
            else:
                pass
                yield '   no ntp serve\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ospf_cost')):
            pass
            yield '   ip ospf cost '
            yield str(environment.getattr(l_1_vlan_interface, 'ospf_cost'))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ospf_network_point_to_point'), True):
            pass
            yield '   ip ospf network point-to-point\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ospf_authentication')):
            pass
            if (environment.getattr(l_1_vlan_interface, 'ospf_authentication') == 'simple'):
                pass
                yield '   ip ospf authentication\n'
            elif (environment.getattr(l_1_vlan_interface, 'ospf_authentication') == 'message-digest'):
                pass
                yield '   ip ospf authentication message-digest\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ospf_authentication_key')):
            pass
            yield '   ip ospf authentication-key '
            yield str(t_1(environment.getattr(l_1_vlan_interface, 'ospf_authentication_key_type'), '7'))
            yield ' '
            yield str(t_2(environment.getattr(l_1_vlan_interface, 'ospf_authentication_key'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ospf_area')):
            pass
            yield '   ip ospf area '
            yield str(environment.getattr(l_1_vlan_interface, 'ospf_area'))
            yield '\n'
        for l_2_ospf_message_digest_key in t_3(environment.getattr(l_1_vlan_interface, 'ospf_message_digest_keys'), 'id'):
            _loop_vars = {}
            pass
            if (t_8(environment.getattr(l_2_ospf_message_digest_key, 'hash_algorithm')) and t_8(environment.getattr(l_2_ospf_message_digest_key, 'key'))):
                pass
                yield '   ip ospf message-digest-key '
                yield str(environment.getattr(l_2_ospf_message_digest_key, 'id'))
                yield ' '
                yield str(environment.getattr(l_2_ospf_message_digest_key, 'hash_algorithm'))
                yield ' '
                yield str(t_1(environment.getattr(l_2_ospf_message_digest_key, 'key_type'), '7'))
                yield ' '
                yield str(t_2(environment.getattr(l_2_ospf_message_digest_key, 'key'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
                yield '\n'
        l_2_ospf_message_digest_key = missing
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_ospf_network_point_to_point'), True):
            pass
            yield '   ipv6 ospf network point-to-point\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_ospf_area')):
            pass
            yield '   ipv6 ospf area '
            yield str(environment.getattr(l_1_vlan_interface, 'ipv6_ospf_area'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'service_policy'), 'pbr'), 'input')):
            pass
            yield '   service-policy type pbr input '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'service_policy'), 'pbr'), 'input'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'sparse_mode'), True):
            pass
            yield '   pim ipv4 sparse-mode\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'bidirectional'), True):
            pass
            yield '   pim ipv4 bidirectional\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'border_router'), True):
            pass
            yield '   pim ipv4 border-router\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'hello'), 'interval')):
            pass
            yield '   pim ipv4 hello interval '
            yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'hello'), 'interval'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'hello'), 'count')):
            pass
            yield '   pim ipv4 hello count '
            yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'hello'), 'count'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'dr_priority')):
            pass
            yield '   pim ipv4 dr-priority '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'dr_priority'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'neighbor_filter')):
            pass
            yield '   pim ipv4 neighbor filter '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'neighbor_filter'))
            yield '\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'bfd'), True):
            pass
            yield '   pim ipv4 bfd\n'
        if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'local_interface')):
            pass
            yield '   pim ipv4 local-interface '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'pim'), 'ipv4'), 'local_interface'))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'isis_enable')):
            pass
            yield '   isis enable '
            yield str(environment.getattr(l_1_vlan_interface, 'isis_enable'))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'isis_bfd'), True):
            pass
            yield '   isis bfd\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'isis_metric')):
            pass
            yield '   isis metric '
            yield str(environment.getattr(l_1_vlan_interface, 'isis_metric'))
            yield '\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'isis_passive'), True):
            pass
            yield '   isis passive\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'isis_network_point_to_point'), True):
            pass
            yield '   isis network point-to-point\n'
        if (t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'mode')) and (((environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'mode') in ['md5', 'text']) or ((environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'mode') == 'sha') and t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'sha'), 'key_id')))) or (((environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'mode') == 'shared-secret') and t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'shared_secret'), 'profile'))) and t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'shared_secret'), 'algorithm'))))):
            pass
            l_1_isis_auth_cli = str_join(('isis authentication mode ', environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'mode'), ))
            _loop_vars['isis_auth_cli'] = l_1_isis_auth_cli
            if (environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'mode') == 'sha'):
                pass
                l_1_isis_auth_cli = str_join(((undefined(name='isis_auth_cli') if l_1_isis_auth_cli is missing else l_1_isis_auth_cli), ' key-id ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'sha'), 'key_id'), ))
                _loop_vars['isis_auth_cli'] = l_1_isis_auth_cli
            elif (environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'mode') == 'shared-secret'):
                pass
                l_1_isis_auth_cli = str_join(((undefined(name='isis_auth_cli') if l_1_isis_auth_cli is missing else l_1_isis_auth_cli), ' profile ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'shared_secret'), 'profile'), ' algorithm ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'shared_secret'), 'algorithm'), ))
                _loop_vars['isis_auth_cli'] = l_1_isis_auth_cli
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'rx_disabled'), True):
                pass
                l_1_isis_auth_cli = str_join(((undefined(name='isis_auth_cli') if l_1_isis_auth_cli is missing else l_1_isis_auth_cli), ' rx-disabled', ))
                _loop_vars['isis_auth_cli'] = l_1_isis_auth_cli
            yield '   '
            yield str((undefined(name='isis_auth_cli') if l_1_isis_auth_cli is missing else l_1_isis_auth_cli))
            yield '\n'
        else:
            pass
            if (t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'mode')) and (((environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'mode') in ['md5', 'text']) or ((environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'mode') == 'sha') and t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'sha'), 'key_id')))) or (((environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'mode') == 'shared-secret') and t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'shared_secret'), 'profile'))) and t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'shared_secret'), 'algorithm'))))):
                pass
                l_1_isis_auth_cli = str_join(('isis authentication mode ', environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'mode'), ))
                _loop_vars['isis_auth_cli'] = l_1_isis_auth_cli
                if (environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'mode') == 'sha'):
                    pass
                    l_1_isis_auth_cli = str_join(((undefined(name='isis_auth_cli') if l_1_isis_auth_cli is missing else l_1_isis_auth_cli), ' key-id ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'sha'), 'key_id'), ))
                    _loop_vars['isis_auth_cli'] = l_1_isis_auth_cli
                elif (environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'mode') == 'shared-secret'):
                    pass
                    l_1_isis_auth_cli = str_join(((undefined(name='isis_auth_cli') if l_1_isis_auth_cli is missing else l_1_isis_auth_cli), ' profile ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'shared_secret'), 'profile'), ' algorithm ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'shared_secret'), 'algorithm'), ))
                    _loop_vars['isis_auth_cli'] = l_1_isis_auth_cli
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'rx_disabled'), True):
                    pass
                    l_1_isis_auth_cli = str_join(((undefined(name='isis_auth_cli') if l_1_isis_auth_cli is missing else l_1_isis_auth_cli), ' rx-disabled', ))
                    _loop_vars['isis_auth_cli'] = l_1_isis_auth_cli
                yield '   '
                yield str((undefined(name='isis_auth_cli') if l_1_isis_auth_cli is missing else l_1_isis_auth_cli))
                yield ' level-1\n'
            if (t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'mode')) and (((environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'mode') in ['md5', 'text']) or ((environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'mode') == 'sha') and t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'sha'), 'key_id')))) or (((environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'mode') == 'shared-secret') and t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'shared_secret'), 'profile'))) and t_8(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'shared_secret'), 'algorithm'))))):
                pass
                l_1_isis_auth_cli = str_join(('isis authentication mode ', environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'mode'), ))
                _loop_vars['isis_auth_cli'] = l_1_isis_auth_cli
                if (environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'mode') == 'sha'):
                    pass
                    l_1_isis_auth_cli = str_join(((undefined(name='isis_auth_cli') if l_1_isis_auth_cli is missing else l_1_isis_auth_cli), ' key-id ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'sha'), 'key_id'), ))
                    _loop_vars['isis_auth_cli'] = l_1_isis_auth_cli
                elif (environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'mode') == 'shared-secret'):
                    pass
                    l_1_isis_auth_cli = str_join(((undefined(name='isis_auth_cli') if l_1_isis_auth_cli is missing else l_1_isis_auth_cli), ' profile ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'shared_secret'), 'profile'), ' algorithm ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'shared_secret'), 'algorithm'), ))
                    _loop_vars['isis_auth_cli'] = l_1_isis_auth_cli
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'rx_disabled'), True):
                    pass
                    l_1_isis_auth_cli = str_join(((undefined(name='isis_auth_cli') if l_1_isis_auth_cli is missing else l_1_isis_auth_cli), ' rx-disabled', ))
                    _loop_vars['isis_auth_cli'] = l_1_isis_auth_cli
                yield '   '
                yield str((undefined(name='isis_auth_cli') if l_1_isis_auth_cli is missing else l_1_isis_auth_cli))
                yield ' level-2\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'isis_authentication')):
            pass
            l_1_both_key_ids = []
            _loop_vars['both_key_ids'] = l_1_both_key_ids
            if t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'key_ids')):
                pass
                for l_2_auth_key in t_3(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'key_ids'), 'id'):
                    _loop_vars = {}
                    pass
                    if (((t_8(environment.getattr(l_2_auth_key, 'id')) and t_8(environment.getattr(l_2_auth_key, 'algorithm'))) and t_8(environment.getattr(l_2_auth_key, 'key_type'))) and t_8(environment.getattr(l_2_auth_key, 'key'))):
                        pass
                        context.call(environment.getattr((undefined(name='both_key_ids') if l_1_both_key_ids is missing else l_1_both_key_ids), 'append'), environment.getattr(l_2_auth_key, 'id'), _loop_vars=_loop_vars)
                        if t_8(environment.getattr(l_2_auth_key, 'rfc_5310'), True):
                            pass
                            yield '   isis authentication key-id '
                            yield str(environment.getattr(l_2_auth_key, 'id'))
                            yield ' algorithm '
                            yield str(environment.getattr(l_2_auth_key, 'algorithm'))
                            yield ' rfc-5310 key '
                            yield str(environment.getattr(l_2_auth_key, 'key_type'))
                            yield ' '
                            yield str(environment.getattr(l_2_auth_key, 'key'))
                            yield '\n'
                        else:
                            pass
                            yield '   isis authentication key-id '
                            yield str(environment.getattr(l_2_auth_key, 'id'))
                            yield ' algorithm '
                            yield str(environment.getattr(l_2_auth_key, 'algorithm'))
                            yield ' key '
                            yield str(environment.getattr(l_2_auth_key, 'key_type'))
                            yield ' '
                            yield str(environment.getattr(l_2_auth_key, 'key'))
                            yield '\n'
                l_2_auth_key = missing
            for l_2_auth_key in t_3(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'key_ids'), 'id'):
                _loop_vars = {}
                pass
                if ((((t_8(environment.getattr(l_2_auth_key, 'id')) and (environment.getattr(l_2_auth_key, 'id') not in (undefined(name='both_key_ids') if l_1_both_key_ids is missing else l_1_both_key_ids))) and t_8(environment.getattr(l_2_auth_key, 'algorithm'))) and t_8(environment.getattr(l_2_auth_key, 'key_type'))) and t_8(environment.getattr(l_2_auth_key, 'key'))):
                    pass
                    if t_8(environment.getattr(l_2_auth_key, 'rfc_5310'), True):
                        pass
                        yield '   isis authentication key-id '
                        yield str(environment.getattr(l_2_auth_key, 'id'))
                        yield ' algorithm '
                        yield str(environment.getattr(l_2_auth_key, 'algorithm'))
                        yield ' rfc-5310 key '
                        yield str(environment.getattr(l_2_auth_key, 'key_type'))
                        yield ' '
                        yield str(environment.getattr(l_2_auth_key, 'key'))
                        yield ' level-1\n'
                    else:
                        pass
                        yield '   isis authentication key-id '
                        yield str(environment.getattr(l_2_auth_key, 'id'))
                        yield ' algorithm '
                        yield str(environment.getattr(l_2_auth_key, 'algorithm'))
                        yield ' key '
                        yield str(environment.getattr(l_2_auth_key, 'key_type'))
                        yield ' '
                        yield str(environment.getattr(l_2_auth_key, 'key'))
                        yield ' level-1\n'
            l_2_auth_key = missing
            for l_2_auth_key in t_3(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'key_ids'), 'id'):
                _loop_vars = {}
                pass
                if ((((t_8(environment.getattr(l_2_auth_key, 'id')) and (environment.getattr(l_2_auth_key, 'id') not in (undefined(name='both_key_ids') if l_1_both_key_ids is missing else l_1_both_key_ids))) and t_8(environment.getattr(l_2_auth_key, 'algorithm'))) and t_8(environment.getattr(l_2_auth_key, 'key_type'))) and t_8(environment.getattr(l_2_auth_key, 'key'))):
                    pass
                    if t_8(environment.getattr(l_2_auth_key, 'rfc_5310'), True):
                        pass
                        yield '   isis authentication key-id '
                        yield str(environment.getattr(l_2_auth_key, 'id'))
                        yield ' algorithm '
                        yield str(environment.getattr(l_2_auth_key, 'algorithm'))
                        yield ' rfc-5310 key '
                        yield str(environment.getattr(l_2_auth_key, 'key_type'))
                        yield ' '
                        yield str(environment.getattr(l_2_auth_key, 'key'))
                        yield ' level-2\n'
                    else:
                        pass
                        yield '   isis authentication key-id '
                        yield str(environment.getattr(l_2_auth_key, 'id'))
                        yield ' algorithm '
                        yield str(environment.getattr(l_2_auth_key, 'algorithm'))
                        yield ' key '
                        yield str(environment.getattr(l_2_auth_key, 'key_type'))
                        yield ' '
                        yield str(environment.getattr(l_2_auth_key, 'key'))
                        yield ' level-2\n'
            l_2_auth_key = missing
            if (t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'key_type')) and t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'key'))):
                pass
                yield '   isis authentication key '
                yield str(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'key_type'))
                yield ' '
                yield str(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'both'), 'key'))
                yield '\n'
            else:
                pass
                if (t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'key_type')) and t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'key'))):
                    pass
                    yield '   isis authentication key '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'key_type'))
                    yield ' '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_1'), 'key'))
                    yield ' level-1\n'
                if (t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'key_type')) and t_8(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'key'))):
                    pass
                    yield '   isis authentication key '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'key_type'))
                    yield ' '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_vlan_interface, 'isis_authentication'), 'level_2'), 'key'))
                    yield ' level-2\n'
        if t_8(environment.getattr(l_1_vlan_interface, 'ip_address_virtual')):
            pass
            yield '   ip address virtual '
            yield str(environment.getattr(l_1_vlan_interface, 'ip_address_virtual'))
            yield '\n'
            if t_8(environment.getattr(l_1_vlan_interface, 'ip_address_virtual_secondaries')):
                pass
                for l_2_ip_address_virtual_secondary in t_3(environment.getattr(l_1_vlan_interface, 'ip_address_virtual_secondaries')):
                    _loop_vars = {}
                    pass
                    yield '   ip address virtual '
                    yield str(l_2_ip_address_virtual_secondary)
                    yield ' secondary\n'
                l_2_ip_address_virtual_secondary = missing
        for l_2_ipv6_address_virtual in t_3(environment.getattr(l_1_vlan_interface, 'ipv6_address_virtuals')):
            _loop_vars = {}
            pass
            yield '   ipv6 address virtual '
            yield str(l_2_ipv6_address_virtual)
            yield '\n'
        l_2_ipv6_address_virtual = missing
        if t_8(environment.getattr(l_1_vlan_interface, 'ip_virtual_router_addresses')):
            pass
            for l_2_ip_virtual_router_address in t_3(environment.getattr(l_1_vlan_interface, 'ip_virtual_router_addresses')):
                _loop_vars = {}
                pass
                yield '   ip virtual-router address '
                yield str(l_2_ip_virtual_router_address)
                yield '\n'
            l_2_ip_virtual_router_address = missing
        if t_8(environment.getattr(l_1_vlan_interface, 'ipv6_virtual_router_addresses')):
            pass
            for l_2_ipv6_virtual_router_address in t_3(environment.getattr(l_1_vlan_interface, 'ipv6_virtual_router_addresses')):
                _loop_vars = {}
                pass
                yield '   ipv6 virtual-router address '
                yield str(l_2_ipv6_virtual_router_address)
                yield '\n'
            l_2_ipv6_virtual_router_address = missing
        if t_8(environment.getattr(l_1_vlan_interface, 'vrrp_ids')):
            pass
            def t_9(fiter):
                for l_2_vrid in fiter:
                    if t_8(environment.getattr(l_2_vrid, 'id')):
                        yield l_2_vrid
            for l_2_vrid in t_9(t_3(environment.getattr(l_1_vlan_interface, 'vrrp_ids'), 'id')):
                l_2_delay_cli = resolve('delay_cli')
                l_2_peer_auth_cli = resolve('peer_auth_cli')
                _loop_vars = {}
                pass
                if t_8(environment.getattr(l_2_vrid, 'priority_level')):
                    pass
                    yield '   vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' priority-level '
                    yield str(environment.getattr(l_2_vrid, 'priority_level'))
                    yield '\n'
                if t_8(environment.getattr(environment.getattr(l_2_vrid, 'advertisement'), 'interval')):
                    pass
                    yield '   vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' advertisement interval '
                    yield str(environment.getattr(environment.getattr(l_2_vrid, 'advertisement'), 'interval'))
                    yield '\n'
                if (t_8(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'enabled'), True) and (t_8(environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'delay'), 'minimum')) or t_8(environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'delay'), 'reload')))):
                    pass
                    l_2_delay_cli = str_join(('vrrp ', environment.getattr(l_2_vrid, 'id'), ' preempt delay', ))
                    _loop_vars['delay_cli'] = l_2_delay_cli
                    if t_8(environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'delay'), 'minimum')):
                        pass
                        l_2_delay_cli = str_join(((undefined(name='delay_cli') if l_2_delay_cli is missing else l_2_delay_cli), ' minimum ', environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'delay'), 'minimum'), ))
                        _loop_vars['delay_cli'] = l_2_delay_cli
                    if t_8(environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'delay'), 'reload')):
                        pass
                        l_2_delay_cli = str_join(((undefined(name='delay_cli') if l_2_delay_cli is missing else l_2_delay_cli), ' reload ', environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'delay'), 'reload'), ))
                        _loop_vars['delay_cli'] = l_2_delay_cli
                    yield '   '
                    yield str((undefined(name='delay_cli') if l_2_delay_cli is missing else l_2_delay_cli))
                    yield '\n'
                elif t_8(environment.getattr(environment.getattr(l_2_vrid, 'preempt'), 'enabled'), False):
                    pass
                    yield '   no vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' preempt\n'
                if t_8(environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'timers'), 'delay'), 'reload')):
                    pass
                    yield '   vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' timers delay reload '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_2_vrid, 'timers'), 'delay'), 'reload'))
                    yield '\n'
                if t_8(environment.getattr(l_2_vrid, 'peer_authentication')):
                    pass
                    l_2_peer_auth_cli = str_join(('vrrp ', environment.getattr(l_2_vrid, 'id'), ' peer authentication', ))
                    _loop_vars['peer_auth_cli'] = l_2_peer_auth_cli
                    if (environment.getattr(environment.getattr(l_2_vrid, 'peer_authentication'), 'mode') == 'ietf-md5'):
                        pass
                        l_2_peer_auth_cli = str_join(((undefined(name='peer_auth_cli') if l_2_peer_auth_cli is missing else l_2_peer_auth_cli), ' ietf-md5 key-string', ))
                        _loop_vars['peer_auth_cli'] = l_2_peer_auth_cli
                    else:
                        pass
                        l_2_peer_auth_cli = str_join(((undefined(name='peer_auth_cli') if l_2_peer_auth_cli is missing else l_2_peer_auth_cli), ' text', ))
                        _loop_vars['peer_auth_cli'] = l_2_peer_auth_cli
                    if t_8(environment.getattr(environment.getattr(l_2_vrid, 'peer_authentication'), 'key_type')):
                        pass
                        l_2_peer_auth_cli = str_join(((undefined(name='peer_auth_cli') if l_2_peer_auth_cli is missing else l_2_peer_auth_cli), ' ', environment.getattr(environment.getattr(l_2_vrid, 'peer_authentication'), 'key_type'), ))
                        _loop_vars['peer_auth_cli'] = l_2_peer_auth_cli
                    l_2_peer_auth_cli = str_join(((undefined(name='peer_auth_cli') if l_2_peer_auth_cli is missing else l_2_peer_auth_cli), ' ', t_2(environment.getattr(environment.getattr(l_2_vrid, 'peer_authentication'), 'key'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)), ))
                    _loop_vars['peer_auth_cli'] = l_2_peer_auth_cli
                    yield '   '
                    yield str((undefined(name='peer_auth_cli') if l_2_peer_auth_cli is missing else l_2_peer_auth_cli))
                    yield '\n'
                if t_8(environment.getattr(environment.getattr(l_2_vrid, 'ipv4'), 'address')):
                    pass
                    yield '   vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' ipv4 '
                    yield str(environment.getattr(environment.getattr(l_2_vrid, 'ipv4'), 'address'))
                    yield '\n'
                for l_3_secondary_ip in t_3(environment.getattr(environment.getattr(l_2_vrid, 'ipv4'), 'secondary_addresses')):
                    _loop_vars = {}
                    pass
                    yield '   vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' ipv4 '
                    yield str(l_3_secondary_ip)
                    yield ' secondary\n'
                l_3_secondary_ip = missing
                if t_8(environment.getattr(environment.getattr(l_2_vrid, 'ipv4'), 'version')):
                    pass
                    yield '   vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' ipv4 version '
                    yield str(environment.getattr(environment.getattr(l_2_vrid, 'ipv4'), 'version'))
                    yield '\n'
                for l_3_ipv6_address in t_3(environment.getattr(environment.getattr(l_2_vrid, 'ipv6'), 'addresses')):
                    _loop_vars = {}
                    pass
                    yield '   vrrp '
                    yield str(environment.getattr(l_2_vrid, 'id'))
                    yield ' ipv6 '
                    yield str(l_3_ipv6_address)
                    yield '\n'
                l_3_ipv6_address = missing
                for l_3_tracked_obj in t_3(environment.getattr(l_2_vrid, 'tracked_object'), 'name'):
                    l_3_tracked_obj_cli = resolve('tracked_obj_cli')
                    _loop_vars = {}
                    pass
                    if t_8(environment.getattr(l_3_tracked_obj, 'name')):
                        pass
                        l_3_tracked_obj_cli = str_join(('vrrp ', environment.getattr(l_2_vrid, 'id'), ' tracked-object ', environment.getattr(l_3_tracked_obj, 'name'), ))
                        _loop_vars['tracked_obj_cli'] = l_3_tracked_obj_cli
                        if t_8(environment.getattr(l_3_tracked_obj, 'decrement')):
                            pass
                            l_3_tracked_obj_cli = str_join(((undefined(name='tracked_obj_cli') if l_3_tracked_obj_cli is missing else l_3_tracked_obj_cli), ' decrement ', environment.getattr(l_3_tracked_obj, 'decrement'), ))
                            _loop_vars['tracked_obj_cli'] = l_3_tracked_obj_cli
                        elif t_8(environment.getattr(l_3_tracked_obj, 'shutdown'), True):
                            pass
                            l_3_tracked_obj_cli = str_join(((undefined(name='tracked_obj_cli') if l_3_tracked_obj_cli is missing else l_3_tracked_obj_cli), ' shutdown', ))
                            _loop_vars['tracked_obj_cli'] = l_3_tracked_obj_cli
                        yield '   '
                        yield str((undefined(name='tracked_obj_cli') if l_3_tracked_obj_cli is missing else l_3_tracked_obj_cli))
                        yield '\n'
                l_3_tracked_obj = l_3_tracked_obj_cli = missing
            l_2_vrid = l_2_delay_cli = l_2_peer_auth_cli = missing
        if t_8(environment.getattr(l_1_vlan_interface, 'eos_cli')):
            pass
            yield '   '
            yield str(t_4(environment.getattr(l_1_vlan_interface, 'eos_cli'), 3, False))
            yield '\n'
    l_1_vlan_interface = l_1_with_vrf_dest = l_1_without_vrf_dest = l_1_sorted_ipv6_dhcp_relay_destinations = l_1_ip_attached_host_route_export_cli = l_1_ipv6_attached_host_route_export_cli = l_1_host_proxy_cli = l_1_interface_ip_nat = l_1_hide_passwords = l_1_isis_auth_cli = l_1_both_key_ids = missing

blocks = {}
debug_info = '7=60&9=74&10=76&11=79&13=81&14=84&16=86&17=89&19=91&21=94&24=97&25=100&27=102&29=105&32=108&33=111&35=113&38=116&39=119&41=121&44=124&47=127&48=130&49=132&50=134&51=138&55=141&56=144&58=146&61=149&62=152&64=154&65=157&67=159&68=162&70=164&71=167&73=169&76=172&79=175&82=178&84=184&86=187&89=190&92=193&95=196&96=200&97=202&98=204&100=206&101=208&103=211&105=214&106=216&107=218&108=220&110=222&111=226&112=228&113=230&115=232&116=234&117=236&118=238&120=240&121=242&123=245&125=248&128=251&131=254&132=256&133=258&134=260&136=263&138=265&139=267&140=269&141=271&143=273&144=275&146=278&148=280&151=283&152=286&154=288&157=291&158=293&159=296&160=298&161=300&162=303&163=305&164=307&165=311&168=318&169=320&170=324&173=331&174=334&178=339&179=341&180=345&183=350&184=353&186=357&187=360&190=364&193=367&194=370&196=372&197=375&199=377&202=380&205=383&208=386&209=388&210=392&211=394&212=396&213=398&214=400&217=402&218=404&220=407&223=410&224=413&226=415&227=418&229=420&230=423&232=425&233=428&235=430&236=432&237=434&238=438&239=440&240=442&242=445&245=448&246=450&247=454&250=457&251=459&252=462&257=467&258=469&259=472&264=477&267=480&271=483&272=485&273=487&275=493&276=495&282=501&283=504&285=506&288=509&289=511&291=514&295=517&296=520&298=524&299=527&301=529&302=532&304=535&307=544&310=547&311=550&313=552&314=555&316=557&319=560&322=563&325=566&326=569&328=571&329=574&331=576&332=579&334=581&335=584&337=586&340=589&341=592&343=594&344=597&346=599&349=602&350=605&352=607&355=610&358=613&364=615&365=617&366=619&367=621&368=623&370=625&371=627&373=630&375=634&381=636&382=638&383=640&384=642&385=644&387=646&388=648&390=651&392=653&398=655&399=657&400=659&401=661&402=663&404=665&405=667&407=670&410=672&411=674&412=676&413=678&414=681&418=683&419=684&420=687&422=698&427=707&428=710&433=712&434=715&436=726&440=735&441=738&446=740&447=743&449=754&453=763&454=766&456=772&457=775&459=779&460=782&464=786&465=789&466=791&467=793&468=797&472=800&473=804&475=807&476=809&477=813&480=816&481=818&482=822&485=825&486=827&487=836&488=839&490=843&491=846&493=850&496=852&497=854&498=856&500=858&501=860&503=863&504=865&505=868&507=870&508=873&510=877&511=879&512=881&513=883&515=887&517=889&518=891&520=893&521=896&523=898&524=901&526=905&527=909&529=914&530=917&532=921&533=925&535=930&536=934&537=936&538=938&539=940&540=942&541=944&543=947&548=951&549=954'