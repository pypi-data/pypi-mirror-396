from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/ip-name-server-groups.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ip_name_server_groups = resolve('ip_name_server_groups')
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
    for l_1_name_server_group in t_2((undefined(name='ip_name_server_groups') if l_0_ip_name_server_groups is missing else l_0_ip_name_server_groups), sort_key='name', ignore_case=False):
        l_1_flattened_name_servers = missing
        _loop_vars = {}
        pass
        yield '!\nip name-server group '
        yield str(environment.getattr(l_1_name_server_group, 'name'))
        yield '\n'
        l_1_flattened_name_servers = []
        _loop_vars['flattened_name_servers'] = l_1_flattened_name_servers
        for l_2_vrf in t_1(environment.getattr(l_1_name_server_group, 'vrfs'), []):
            _loop_vars = {}
            pass
            for l_3_name_server in environment.getattr(l_2_vrf, 'name_servers'):
                l_3_server = missing
                _loop_vars = {}
                pass
                l_3_server = {'vrf': environment.getattr(l_2_vrf, 'name'), 'ip_address': environment.getattr(l_3_name_server, 'ip_address')}
                _loop_vars['server'] = l_3_server
                if t_3(environment.getattr(l_3_name_server, 'priority')):
                    pass
                    context.call(environment.getattr((undefined(name='server') if l_3_server is missing else l_3_server), 'update'), {'priority': environment.getattr(l_3_name_server, 'priority')}, _loop_vars=_loop_vars)
                context.call(environment.getattr((undefined(name='flattened_name_servers') if l_1_flattened_name_servers is missing else l_1_flattened_name_servers), 'append'), (undefined(name='server') if l_3_server is missing else l_3_server), _loop_vars=_loop_vars)
            l_3_name_server = l_3_server = missing
        l_2_vrf = missing
        if ((not (undefined(name='flattened_name_servers') if l_1_flattened_name_servers is missing else l_1_flattened_name_servers)) and t_3(environment.getattr(l_1_name_server_group, 'name_servers'))):
            pass
            l_1_flattened_name_servers = environment.getattr(l_1_name_server_group, 'name_servers')
            _loop_vars['flattened_name_servers'] = l_1_flattened_name_servers
        for l_2_server in t_2(t_2(t_2((undefined(name='flattened_name_servers') if l_1_flattened_name_servers is missing else l_1_flattened_name_servers), 'ip_address'), sort_key='vrf', ignore_case=False), 'priority', default_value='0'):
            l_2_name_server_cli = missing
            _loop_vars = {}
            pass
            l_2_name_server_cli = str_join(('name-server vrf ', environment.getattr(l_2_server, 'vrf'), ' ', environment.getattr(l_2_server, 'ip_address'), ))
            _loop_vars['name_server_cli'] = l_2_name_server_cli
            if t_3(environment.getattr(l_2_server, 'priority')):
                pass
                l_2_name_server_cli = str_join(((undefined(name='name_server_cli') if l_2_name_server_cli is missing else l_2_name_server_cli), ' priority ', environment.getattr(l_2_server, 'priority'), ))
                _loop_vars['name_server_cli'] = l_2_name_server_cli
            yield '   '
            yield str((undefined(name='name_server_cli') if l_2_name_server_cli is missing else l_2_name_server_cli))
            yield '\n'
        l_2_server = l_2_name_server_cli = missing
        if t_3(environment.getattr(l_1_name_server_group, 'dns_domain')):
            pass
            yield '   dns domain '
            yield str(environment.getattr(l_1_name_server_group, 'dns_domain'))
            yield '\n'
        for l_2_domain in t_2(environment.getattr(l_1_name_server_group, 'ip_domain_lists')):
            _loop_vars = {}
            pass
            yield '   ip domain-list '
            yield str(l_2_domain)
            yield '\n'
        l_2_domain = missing
    l_1_name_server_group = l_1_flattened_name_servers = missing

blocks = {}
debug_info = '6=30&8=35&10=37&11=39&12=42&13=46&14=48&15=50&17=51&21=54&22=56&24=58&25=62&26=64&27=66&29=69&31=72&32=75&34=77&35=81'