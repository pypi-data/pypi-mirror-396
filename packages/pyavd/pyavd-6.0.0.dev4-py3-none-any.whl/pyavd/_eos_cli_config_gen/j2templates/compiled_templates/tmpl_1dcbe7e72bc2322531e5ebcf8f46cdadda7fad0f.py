from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/ip-nat-part2.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ip_nat = resolve('ip_nat')
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
        t_3 = environment.filters['groupby']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'groupby' found.")
    try:
        t_4 = environment.filters['selectattr']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'selectattr' found.")
    try:
        t_5 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_5((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat)):
        pass
        yield '!\n'
        for (l_1_pool_type, l_1_pools) in t_3(environment, t_2(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'pools'), sort_key='name', ignore_case=False), 'type', default='ip-port'):
            _loop_vars = {}
            pass
            if (l_1_pool_type == 'ip-port'):
                pass
                for l_2_pool in t_4(context, l_1_pools, 'prefix_length', 'arista.avd.defined'):
                    _loop_vars = {}
                    pass
                    yield 'ip nat pool '
                    yield str(environment.getattr(l_2_pool, 'name'))
                    yield ' prefix-length '
                    yield str(environment.getattr(l_2_pool, 'prefix_length'))
                    yield '\n'
                    for l_3_range in t_4(context, t_4(context, t_1(environment.getattr(l_2_pool, 'ranges'), []), 'first_ip', 'arista.avd.defined'), 'last_ip', 'arista.avd.defined'):
                        _loop_vars = {}
                        pass
                        if (not (t_5(environment.getattr(l_3_range, 'first_port')) and t_5(environment.getattr(l_3_range, 'last_port')))):
                            pass
                            yield '   range '
                            yield str(environment.getattr(l_3_range, 'first_ip'))
                            yield ' '
                            yield str(environment.getattr(l_3_range, 'last_ip'))
                            yield '\n'
                    l_3_range = missing
                    for l_3_range in t_4(context, t_4(context, t_4(context, t_4(context, t_1(environment.getattr(l_2_pool, 'ranges'), []), 'first_ip', 'arista.avd.defined'), 'last_ip', 'arista.avd.defined'), 'first_port', 'arista.avd.defined'), 'last_port', 'arista.avd.defined'):
                        _loop_vars = {}
                        pass
                        yield '   range '
                        yield str(environment.getattr(l_3_range, 'first_ip'))
                        yield ' '
                        yield str(environment.getattr(l_3_range, 'last_ip'))
                        yield ' '
                        yield str(environment.getattr(l_3_range, 'first_port'))
                        yield ' '
                        yield str(environment.getattr(l_3_range, 'last_port'))
                        yield '\n'
                    l_3_range = missing
                    if t_5(environment.getattr(l_2_pool, 'utilization_log_threshold')):
                        pass
                        yield '   utilization threshold '
                        yield str(environment.getattr(l_2_pool, 'utilization_log_threshold'))
                        yield ' action log\n'
                l_2_pool = missing
            if (l_1_pool_type == 'port-only'):
                pass
                for l_2_pool in l_1_pools:
                    _loop_vars = {}
                    pass
                    yield 'ip nat pool '
                    yield str(environment.getattr(l_2_pool, 'name'))
                    yield ' port-only\n'
                    for l_3_range in t_4(context, t_4(context, t_1(environment.getattr(l_2_pool, 'ranges'), []), 'first_port', 'arista.avd.defined'), 'last_port', 'arista.avd.defined'):
                        _loop_vars = {}
                        pass
                        yield '   port range '
                        yield str(environment.getattr(l_3_range, 'first_port'))
                        yield ' '
                        yield str(environment.getattr(l_3_range, 'last_port'))
                        yield '\n'
                    l_3_range = missing
                l_2_pool = missing
        l_1_pool_type = l_1_pools = missing
        if t_5(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization')):
            pass
            yield 'ip nat synchronization\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'description')):
                pass
                yield '   description '
                yield str(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'description'))
                yield '\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'expiry_interval')):
                pass
                yield '   expiry-interval '
                yield str(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'expiry_interval'))
                yield '\n'
            if t_1(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'shutdown'), False):
                pass
                yield '   shutdown\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'peer_address')):
                pass
                yield '   peer-address '
                yield str(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'peer_address'))
                yield '\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'local_interface')):
                pass
                yield '   local-interface '
                yield str(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'local_interface'))
                yield '\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range')):
                pass
                if (t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'first_port')) and t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'last_port'))):
                    pass
                    yield '   port-range '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'first_port'))
                    yield ' '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'last_port'))
                    yield '\n'
                if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_nat') if l_0_ip_nat is missing else l_0_ip_nat), 'synchronization'), 'port_range'), 'split_disabled'), False):
                    pass
                    yield '   port-range split disabled\n'

blocks = {}
debug_info = '7=42&9=45&10=48&11=50&12=54&14=58&19=61&20=64&24=69&30=73&32=82&33=85&37=88&38=90&39=94&40=96&41=100&46=107&48=110&49=113&51=115&52=118&54=120&57=123&58=126&60=128&61=131&63=133&64=135&66=138&68=142'