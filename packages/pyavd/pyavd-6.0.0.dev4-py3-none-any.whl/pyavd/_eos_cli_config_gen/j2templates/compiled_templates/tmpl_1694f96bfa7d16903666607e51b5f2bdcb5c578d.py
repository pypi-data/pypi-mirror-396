from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/ip-extcommunity-lists.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ip_extcommunity_lists = resolve('ip_extcommunity_lists')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    pass
    for l_1_ip_extcommunity_list in t_1((undefined(name='ip_extcommunity_lists') if l_0_ip_extcommunity_lists is missing else l_0_ip_extcommunity_lists), sort_key='name', ignore_case=False):
        _loop_vars = {}
        pass
        yield '!\n'
        for l_2_entry in environment.getattr(l_1_ip_extcommunity_list, 'entries'):
            _loop_vars = {}
            pass
            yield 'ip extcommunity-list '
            yield str(environment.getattr(l_1_ip_extcommunity_list, 'name'))
            yield ' '
            yield str(environment.getattr(l_2_entry, 'type'))
            yield ' '
            yield str(environment.getattr(l_2_entry, 'extcommunities'))
            yield '\n'
        l_2_entry = missing
    l_1_ip_extcommunity_list = missing

blocks = {}
debug_info = '7=18&9=22&10=26'