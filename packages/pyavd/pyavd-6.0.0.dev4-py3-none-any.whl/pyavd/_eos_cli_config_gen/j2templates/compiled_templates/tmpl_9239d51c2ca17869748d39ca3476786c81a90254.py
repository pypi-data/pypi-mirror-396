from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/aaa-authorization-default-role.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_aaa_authorization = resolve('aaa_authorization')
    try:
        t_1 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_1(environment.getattr(environment.getattr((undefined(name='aaa_authorization') if l_0_aaa_authorization is missing else l_0_aaa_authorization), 'policy'), 'local_default_role')):
        pass
        yield 'aaa authorization policy local default-role '
        yield str(environment.getattr(environment.getattr((undefined(name='aaa_authorization') if l_0_aaa_authorization is missing else l_0_aaa_authorization), 'policy'), 'local_default_role'))
        yield '\n'

blocks = {}
debug_info = '7=18&8=21'