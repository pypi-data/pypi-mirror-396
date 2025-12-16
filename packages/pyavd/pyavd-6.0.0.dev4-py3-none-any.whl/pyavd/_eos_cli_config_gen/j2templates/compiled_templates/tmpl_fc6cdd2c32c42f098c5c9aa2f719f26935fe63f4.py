from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/agents.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_namespace = resolve('namespace')
    l_0_agents = resolve('agents')
    l_0_ns = missing
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
    l_0_ns = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), print_exclamation=False)
    context.vars['ns'] = l_0_ns
    context.exported_vars.add('ns')
    for l_1_agent in t_1((undefined(name='agents') if l_0_agents is missing else l_0_agents), sort_key='name', ignore_case=False):
        _loop_vars = {}
        pass
        if ((not environment.getattr((undefined(name='ns') if l_0_ns is missing else l_0_ns), 'print_exclamation')) and ((t_2(environment.getattr(l_1_agent, 'shutdown'), True) or t_2(environment.getattr(l_1_agent, 'shutdown_supervisor_active'), True)) or t_2(environment.getattr(l_1_agent, 'shutdown_supervisor_standby'), True))):
            pass
            yield '!\n'
            if not isinstance(l_0_ns, Namespace):
                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
            l_0_ns['print_exclamation'] = True
        if t_2(environment.getattr(l_1_agent, 'shutdown'), True):
            pass
            yield 'agent '
            yield str(environment.getattr(l_1_agent, 'name'))
            yield ' shutdown\n'
        if t_2(environment.getattr(l_1_agent, 'shutdown_supervisor_active'), True):
            pass
            yield 'agent '
            yield str(environment.getattr(l_1_agent, 'name'))
            yield ' shutdown supervisor active\n'
        if t_2(environment.getattr(l_1_agent, 'shutdown_supervisor_standby'), True):
            pass
            yield 'agent '
            yield str(environment.getattr(l_1_agent, 'name'))
            yield ' shutdown supervisor standby\n'
    l_1_agent = missing

blocks = {}
debug_info = '7=26&8=29&9=32&11=37&13=38&14=41&16=43&17=46&19=48&20=51'