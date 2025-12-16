from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/ip-name-servers.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ip_name_servers = resolve('ip_name_servers')
    l_0_without_priority_ns = resolve('without_priority_ns')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.filters['list']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'list' found.")
    try:
        t_3 = environment.filters['rejectattr']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'rejectattr' found.")
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
    if t_5((undefined(name='ip_name_servers') if l_0_ip_name_servers is missing else l_0_ip_name_servers)):
        pass
        l_0_without_priority_ns = (t_2(context.eval_ctx, t_3(context, (undefined(name='ip_name_servers') if l_0_ip_name_servers is missing else l_0_ip_name_servers), 'priority', 'arista.avd.defined')) + t_2(context.eval_ctx, t_4(context, (undefined(name='ip_name_servers') if l_0_ip_name_servers is missing else l_0_ip_name_servers), 'priority', 'arista.avd.defined', 0)))
        context.vars['without_priority_ns'] = l_0_without_priority_ns
        context.exported_vars.add('without_priority_ns')
        for l_1_name_server in t_1(t_1((undefined(name='without_priority_ns') if l_0_without_priority_ns is missing else l_0_without_priority_ns), 'ip_address'), sort_key='vrf', ignore_case=False):
            l_1_name_server_cli = missing
            _loop_vars = {}
            pass
            l_1_name_server_cli = 'ip name-server'
            _loop_vars['name_server_cli'] = l_1_name_server_cli
            if t_5(environment.getattr(l_1_name_server, 'vrf')):
                pass
                l_1_name_server_cli = str_join(((undefined(name='name_server_cli') if l_1_name_server_cli is missing else l_1_name_server_cli), ' vrf ', environment.getattr(l_1_name_server, 'vrf'), ))
                _loop_vars['name_server_cli'] = l_1_name_server_cli
            l_1_name_server_cli = str_join(((undefined(name='name_server_cli') if l_1_name_server_cli is missing else l_1_name_server_cli), ' ', environment.getattr(l_1_name_server, 'ip_address'), ))
            _loop_vars['name_server_cli'] = l_1_name_server_cli
            yield str((undefined(name='name_server_cli') if l_1_name_server_cli is missing else l_1_name_server_cli))
            yield '\n'
        l_1_name_server = l_1_name_server_cli = missing
        for l_1_name_server in t_1(t_1(t_1(t_4(context, t_4(context, (undefined(name='ip_name_servers') if l_0_ip_name_servers is missing else l_0_ip_name_servers), 'priority', 'arista.avd.defined'), 'priority', 'ne', 0), 'ip_address'), sort_key='vrf', ignore_case=False), 'priority'):
            l_1_name_server_cli = missing
            _loop_vars = {}
            pass
            l_1_name_server_cli = 'ip name-server'
            _loop_vars['name_server_cli'] = l_1_name_server_cli
            if t_5(environment.getattr(l_1_name_server, 'vrf')):
                pass
                l_1_name_server_cli = str_join(((undefined(name='name_server_cli') if l_1_name_server_cli is missing else l_1_name_server_cli), ' vrf ', environment.getattr(l_1_name_server, 'vrf'), ))
                _loop_vars['name_server_cli'] = l_1_name_server_cli
            l_1_name_server_cli = str_join(((undefined(name='name_server_cli') if l_1_name_server_cli is missing else l_1_name_server_cli), ' ', environment.getattr(l_1_name_server, 'ip_address'), ' priority ', environment.getattr(l_1_name_server, 'priority'), ))
            _loop_vars['name_server_cli'] = l_1_name_server_cli
            yield str((undefined(name='name_server_cli') if l_1_name_server_cli is missing else l_1_name_server_cli))
            yield '\n'
        l_1_name_server = l_1_name_server_cli = missing

blocks = {}
debug_info = '7=43&9=45&17=48&18=52&19=54&20=56&22=58&23=60&26=63&27=67&28=69&29=71&31=73&32=75'