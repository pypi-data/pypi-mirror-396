from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/ip-community-lists.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ip_community_lists = resolve('ip_community_lists')
    try:
        t_1 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_2 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_2((undefined(name='ip_community_lists') if l_0_ip_community_lists is missing else l_0_ip_community_lists)):
        pass
        yield '\n### IP Community-lists\n\n#### IP Community-lists Summary\n\n| Name | Action | Communities / Regexp |\n| ---- | ------ | -------------------- |\n'
        for l_1_community_list in (undefined(name='ip_community_lists') if l_0_ip_community_lists is missing else l_0_ip_community_lists):
            _loop_vars = {}
            pass
            if t_2(environment.getattr(l_1_community_list, 'name')):
                pass
                for l_2_entry in environment.getattr(l_1_community_list, 'entries'):
                    _loop_vars = {}
                    pass
                    if t_2(environment.getattr(l_2_entry, 'action')):
                        pass
                        if t_2(environment.getattr(l_2_entry, 'regexp')):
                            pass
                            yield '| '
                            yield str(environment.getattr(l_1_community_list, 'name'))
                            yield ' | '
                            yield str(environment.getattr(l_2_entry, 'action'))
                            yield ' | '
                            yield str(environment.getattr(l_2_entry, 'regexp'))
                            yield ' |\n'
                        elif t_2(environment.getattr(l_2_entry, 'communities')):
                            pass
                            yield '| '
                            yield str(environment.getattr(l_1_community_list, 'name'))
                            yield ' | '
                            yield str(environment.getattr(l_2_entry, 'action'))
                            yield ' | '
                            yield str(t_1(context.eval_ctx, environment.getattr(l_2_entry, 'communities'), ', '))
                            yield ' |\n'
                l_2_entry = missing
        l_1_community_list = missing
        yield '\n#### IP Community-lists Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/ip-community-lists.j2', 'documentation/ip-community-lists.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=24&15=27&16=30&17=32&18=35&19=37&20=40&21=46&22=49&32=58'