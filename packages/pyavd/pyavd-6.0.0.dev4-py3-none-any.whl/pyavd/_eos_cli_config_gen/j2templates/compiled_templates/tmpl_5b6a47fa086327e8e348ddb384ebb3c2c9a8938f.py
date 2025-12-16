from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/arp.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_arp = resolve('arp')
    l_0_persistent_cli = resolve('persistent_cli')
    l_0_with_vrf_non_default = resolve('with_vrf_non_default')
    l_0_without_vrf = resolve('without_vrf')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if ((t_2(environment.getattr(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'aging'), 'timeout_default')) or t_2(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'static_entries'))) or t_2(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'persistent'))):
        pass
        yield '!\n'
        if t_2(environment.getattr(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'persistent'), 'enabled'), True):
            pass
            l_0_persistent_cli = 'arp persistent'
            context.vars['persistent_cli'] = l_0_persistent_cli
            context.exported_vars.add('persistent_cli')
            if t_2(environment.getattr(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'persistent'), 'refresh_delay')):
                pass
                l_0_persistent_cli = str_join(((undefined(name='persistent_cli') if l_0_persistent_cli is missing else l_0_persistent_cli), ' refresh-delay ', environment.getattr(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'persistent'), 'refresh_delay'), ))
                context.vars['persistent_cli'] = l_0_persistent_cli
                context.exported_vars.add('persistent_cli')
            yield str((undefined(name='persistent_cli') if l_0_persistent_cli is missing else l_0_persistent_cli))
            yield '\n'
        if t_2(environment.getattr(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'aging'), 'timeout_default')):
            pass
            yield 'arp aging timeout default '
            yield str(environment.getattr(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'aging'), 'timeout_default'))
            yield '\n'
        if t_2(environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'static_entries')):
            pass
            l_0_with_vrf_non_default = []
            context.vars['with_vrf_non_default'] = l_0_with_vrf_non_default
            context.exported_vars.add('with_vrf_non_default')
            l_0_without_vrf = []
            context.vars['without_vrf'] = l_0_without_vrf
            context.exported_vars.add('without_vrf')
            for l_1_entry in environment.getattr((undefined(name='arp') if l_0_arp is missing else l_0_arp), 'static_entries'):
                _loop_vars = {}
                pass
                if ((not t_2(environment.getattr(l_1_entry, 'vrf'))) or t_2(environment.getattr(l_1_entry, 'vrf'), 'default')):
                    pass
                    context.call(environment.getattr((undefined(name='without_vrf') if l_0_without_vrf is missing else l_0_without_vrf), 'append'), l_1_entry, _loop_vars=_loop_vars)
                else:
                    pass
                    context.call(environment.getattr((undefined(name='with_vrf_non_default') if l_0_with_vrf_non_default is missing else l_0_with_vrf_non_default), 'append'), l_1_entry, _loop_vars=_loop_vars)
            l_1_entry = missing
            for l_1_entry in t_1((undefined(name='without_vrf') if l_0_without_vrf is missing else l_0_without_vrf), 'ipv4_address'):
                _loop_vars = {}
                pass
                yield 'arp '
                yield str(environment.getattr(l_1_entry, 'ipv4_address'))
                yield ' '
                yield str(environment.getattr(l_1_entry, 'mac_address'))
                yield ' arpa\n'
            l_1_entry = missing
            for l_1_entry in t_1(t_1((undefined(name='with_vrf_non_default') if l_0_with_vrf_non_default is missing else l_0_with_vrf_non_default), 'ipv4_address'), sort_key='vrf', ignore_case=False):
                _loop_vars = {}
                pass
                yield 'arp vrf '
                yield str(environment.getattr(l_1_entry, 'vrf'))
                yield ' '
                yield str(environment.getattr(l_1_entry, 'ipv4_address'))
                yield ' '
                yield str(environment.getattr(l_1_entry, 'mac_address'))
                yield ' arpa\n'
            l_1_entry = missing

blocks = {}
debug_info = '7=27&9=30&10=32&11=35&12=37&14=40&16=42&17=45&19=47&20=49&21=52&23=55&24=58&25=60&27=63&30=65&31=69&33=74&34=78'