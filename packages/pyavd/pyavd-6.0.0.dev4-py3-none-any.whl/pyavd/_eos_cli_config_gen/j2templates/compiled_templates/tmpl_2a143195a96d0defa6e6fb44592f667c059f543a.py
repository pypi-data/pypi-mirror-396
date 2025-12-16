from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/monitor-connectivity.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_monitor_connectivity = resolve('monitor_connectivity')
    l_0_local_interfaces_cli = resolve('local_interfaces_cli')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_3((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity)):
        pass
        yield '!\nmonitor connectivity\n'
        if t_3(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'name_server_group')):
            pass
            yield '   name-server group '
            yield str(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'name_server_group'))
            yield '\n'
        if t_3(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'interval')):
            pass
            yield '   interval '
            yield str(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'interval'))
            yield '\n'
        if t_3(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'shutdown'), False):
            pass
            yield '   no shutdown\n'
        elif t_3(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'shutdown'), True):
            pass
            yield '   shutdown\n'
        for l_1_interface_set in t_2(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'interface_sets'), 'name'):
            _loop_vars = {}
            pass
            yield '   interface set '
            yield str(environment.getattr(l_1_interface_set, 'name'))
            yield ' '
            yield str(environment.getattr(l_1_interface_set, 'interfaces'))
            yield '\n'
        l_1_interface_set = missing
        if t_3(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'local_interfaces')):
            pass
            l_0_local_interfaces_cli = str_join(('local-interfaces ', environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'local_interfaces'), ))
            context.vars['local_interfaces_cli'] = l_0_local_interfaces_cli
            context.exported_vars.add('local_interfaces_cli')
            if t_1(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'address_only'), True):
                pass
                l_0_local_interfaces_cli = str_join(((undefined(name='local_interfaces_cli') if l_0_local_interfaces_cli is missing else l_0_local_interfaces_cli), ' address-only', ))
                context.vars['local_interfaces_cli'] = l_0_local_interfaces_cli
                context.exported_vars.add('local_interfaces_cli')
            yield '   '
            yield str((undefined(name='local_interfaces_cli') if l_0_local_interfaces_cli is missing else l_0_local_interfaces_cli))
            yield ' default\n'
        for l_1_host in t_2(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'hosts'), 'name'):
            l_1_local_interfaces_cli = l_0_local_interfaces_cli
            _loop_vars = {}
            pass
            yield '   !\n   host '
            yield str(environment.getattr(l_1_host, 'name'))
            yield '\n'
            if t_3(environment.getattr(l_1_host, 'description')):
                pass
                yield '      description\n      '
                yield str(environment.getattr(l_1_host, 'description'))
                yield '\n'
            if t_3(environment.getattr(l_1_host, 'local_interfaces')):
                pass
                l_1_local_interfaces_cli = str_join(('local-interfaces ', environment.getattr(l_1_host, 'local_interfaces'), ))
                _loop_vars['local_interfaces_cli'] = l_1_local_interfaces_cli
                if t_1(environment.getattr(l_1_host, 'address_only'), True):
                    pass
                    l_1_local_interfaces_cli = str_join(((undefined(name='local_interfaces_cli') if l_1_local_interfaces_cli is missing else l_1_local_interfaces_cli), ' address-only', ))
                    _loop_vars['local_interfaces_cli'] = l_1_local_interfaces_cli
                yield '      '
                yield str((undefined(name='local_interfaces_cli') if l_1_local_interfaces_cli is missing else l_1_local_interfaces_cli))
                yield '\n'
            if t_3(environment.getattr(l_1_host, 'ip')):
                pass
                yield '      ip '
                yield str(environment.getattr(l_1_host, 'ip'))
                yield '\n'
            if t_3(environment.getattr(l_1_host, 'icmp_echo_size')):
                pass
                yield '      icmp echo size '
                yield str(environment.getattr(l_1_host, 'icmp_echo_size'))
                yield '\n'
            if t_3(environment.getattr(l_1_host, 'url')):
                pass
                yield '      url '
                yield str(environment.getattr(l_1_host, 'url'))
                yield '\n'
        l_1_host = l_1_local_interfaces_cli = missing
        for l_1_vrf in t_2(environment.getattr((undefined(name='monitor_connectivity') if l_0_monitor_connectivity is missing else l_0_monitor_connectivity), 'vrfs'), 'name'):
            l_1_local_interfaces_cli = l_0_local_interfaces_cli
            _loop_vars = {}
            pass
            if t_3(environment.getattr(l_1_vrf, 'name')):
                pass
                yield '   !\n   vrf '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield '\n'
                for l_2_interface_set in t_2(environment.getattr(l_1_vrf, 'interface_sets'), 'name'):
                    _loop_vars = {}
                    pass
                    if (t_3(environment.getattr(l_2_interface_set, 'name')) and t_3(environment.getattr(l_2_interface_set, 'interfaces'))):
                        pass
                        yield '      interface set '
                        yield str(environment.getattr(l_2_interface_set, 'name'))
                        yield ' '
                        yield str(environment.getattr(l_2_interface_set, 'interfaces'))
                        yield '\n'
                l_2_interface_set = missing
                if t_3(environment.getattr(l_1_vrf, 'description')):
                    pass
                    yield '      description\n      '
                    yield str(environment.getattr(l_1_vrf, 'description'))
                    yield '\n'
                if t_3(environment.getattr(l_1_vrf, 'local_interfaces')):
                    pass
                    l_1_local_interfaces_cli = str_join(('local-interfaces ', environment.getattr(l_1_vrf, 'local_interfaces'), ))
                    _loop_vars['local_interfaces_cli'] = l_1_local_interfaces_cli
                    if t_1(environment.getattr(l_1_vrf, 'address_only'), True):
                        pass
                        l_1_local_interfaces_cli = str_join(((undefined(name='local_interfaces_cli') if l_1_local_interfaces_cli is missing else l_1_local_interfaces_cli), ' address-only', ))
                        _loop_vars['local_interfaces_cli'] = l_1_local_interfaces_cli
                    yield '      '
                    yield str((undefined(name='local_interfaces_cli') if l_1_local_interfaces_cli is missing else l_1_local_interfaces_cli))
                    yield ' default\n'
                for l_2_host in t_2(environment.getattr(l_1_vrf, 'hosts'), 'name'):
                    l_2_local_interfaces_cli = l_1_local_interfaces_cli
                    _loop_vars = {}
                    pass
                    if t_3(environment.getattr(l_2_host, 'name')):
                        pass
                        yield '      !\n      host '
                        yield str(environment.getattr(l_2_host, 'name'))
                        yield '\n'
                        if t_3(environment.getattr(l_2_host, 'description')):
                            pass
                            yield '         description\n         '
                            yield str(environment.getattr(l_2_host, 'description'))
                            yield '\n'
                        if t_3(environment.getattr(l_2_host, 'local_interfaces')):
                            pass
                            l_2_local_interfaces_cli = str_join(('local-interfaces ', environment.getattr(l_2_host, 'local_interfaces'), ))
                            _loop_vars['local_interfaces_cli'] = l_2_local_interfaces_cli
                            if t_1(environment.getattr(l_2_host, 'address_only'), True):
                                pass
                                l_2_local_interfaces_cli = str_join(((undefined(name='local_interfaces_cli') if l_2_local_interfaces_cli is missing else l_2_local_interfaces_cli), ' address-only', ))
                                _loop_vars['local_interfaces_cli'] = l_2_local_interfaces_cli
                            yield '         '
                            yield str((undefined(name='local_interfaces_cli') if l_2_local_interfaces_cli is missing else l_2_local_interfaces_cli))
                            yield '\n'
                        if t_3(environment.getattr(l_2_host, 'ip')):
                            pass
                            yield '         ip '
                            yield str(environment.getattr(l_2_host, 'ip'))
                            yield '\n'
                        if t_3(environment.getattr(l_2_host, 'icmp_echo_size')):
                            pass
                            yield '         icmp echo size '
                            yield str(environment.getattr(l_2_host, 'icmp_echo_size'))
                            yield '\n'
                        if t_3(environment.getattr(l_2_host, 'url')):
                            pass
                            yield '         url '
                            yield str(environment.getattr(l_2_host, 'url'))
                            yield '\n'
                l_2_host = l_2_local_interfaces_cli = missing
        l_1_vrf = l_1_local_interfaces_cli = missing

blocks = {}
debug_info = '7=31&10=34&11=37&13=39&14=42&16=44&18=47&21=50&22=54&24=59&25=61&26=64&27=66&29=70&31=72&33=77&34=79&36=82&38=84&39=86&40=88&41=90&43=93&45=95&46=98&48=100&49=103&51=105&52=108&55=111&56=115&58=118&59=120&60=123&61=126&64=131&66=134&68=136&69=138&70=140&71=142&73=145&75=147&76=151&78=154&79=156&81=159&83=161&84=163&85=165&86=167&88=170&90=172&91=175&93=177&94=180&96=182&97=185'