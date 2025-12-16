from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/ipv6-neighbors.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ipv6_neighbor = resolve('ipv6_neighbor')
    l_0_persistent_cli = resolve('persistent_cli')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.filters['rejectattr']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'rejectattr' found.")
    try:
        t_3 = environment.filters['selectattr']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'selectattr' found.")
    try:
        t_4 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if (t_4(environment.getattr(environment.getattr((undefined(name='ipv6_neighbor') if l_0_ipv6_neighbor is missing else l_0_ipv6_neighbor), 'persistent'), 'enabled'), True) or t_4(environment.getattr((undefined(name='ipv6_neighbor') if l_0_ipv6_neighbor is missing else l_0_ipv6_neighbor), 'static_entries'))):
        pass
        yield '!\n'
        if t_4(environment.getattr(environment.getattr((undefined(name='ipv6_neighbor') if l_0_ipv6_neighbor is missing else l_0_ipv6_neighbor), 'persistent'), 'enabled'), True):
            pass
            l_0_persistent_cli = 'ipv6 neighbor persistent'
            context.vars['persistent_cli'] = l_0_persistent_cli
            context.exported_vars.add('persistent_cli')
            if t_4(environment.getattr(environment.getattr((undefined(name='ipv6_neighbor') if l_0_ipv6_neighbor is missing else l_0_ipv6_neighbor), 'persistent'), 'refresh_delay')):
                pass
                l_0_persistent_cli = str_join(((undefined(name='persistent_cli') if l_0_persistent_cli is missing else l_0_persistent_cli), ' refresh-delay ', environment.getattr(environment.getattr((undefined(name='ipv6_neighbor') if l_0_ipv6_neighbor is missing else l_0_ipv6_neighbor), 'persistent'), 'refresh_delay'), ))
                context.vars['persistent_cli'] = l_0_persistent_cli
                context.exported_vars.add('persistent_cli')
            yield str((undefined(name='persistent_cli') if l_0_persistent_cli is missing else l_0_persistent_cli))
            yield '\n'
        if t_4(environment.getattr((undefined(name='ipv6_neighbor') if l_0_ipv6_neighbor is missing else l_0_ipv6_neighbor), 'static_entries')):
            pass
            for l_1_neighbor in t_1(t_1(t_2(context, environment.getattr((undefined(name='ipv6_neighbor') if l_0_ipv6_neighbor is missing else l_0_ipv6_neighbor), 'static_entries'), 'vrf', 'arista.avd.defined'), 'interface'), 'ipv6_address'):
                _loop_vars = {}
                pass
                yield 'ipv6 neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ipv6_address'))
                yield ' '
                yield str(environment.getattr(l_1_neighbor, 'interface'))
                yield ' '
                yield str(environment.getattr(l_1_neighbor, 'mac_address'))
                yield '\n'
            l_1_neighbor = missing
            for l_1_neighbor in t_1(t_1(t_1(t_3(context, environment.getattr((undefined(name='ipv6_neighbor') if l_0_ipv6_neighbor is missing else l_0_ipv6_neighbor), 'static_entries'), 'vrf', 'arista.avd.defined'), 'interface'), 'ipv6_address'), sort_key='vrf', ignore_case=False):
                _loop_vars = {}
                pass
                yield 'ipv6 neighbor vrf '
                yield str(environment.getattr(l_1_neighbor, 'vrf'))
                yield ' '
                yield str(environment.getattr(l_1_neighbor, 'ipv6_address'))
                yield ' '
                yield str(environment.getattr(l_1_neighbor, 'interface'))
                yield ' '
                yield str(environment.getattr(l_1_neighbor, 'mac_address'))
                yield '\n'
            l_1_neighbor = missing

blocks = {}
debug_info = '7=37&9=40&10=42&11=45&12=47&14=50&16=52&17=54&18=58&20=65&21=69'