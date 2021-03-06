from webob.exc import HTTPNotFound
from iktomi.web import match
from cms34.front import VP_Query, VP_Response, view_handler
from .. import ResourceView

class VP_ThemesQuery(VP_Query):
    model = 'Theme'
    order_field = 'order'
    order_asc = True
    limit = 20


class V_Theme(ResourceView):

    name='theme'
    plugins = [VP_Response, VP_ThemesQuery]

    @classmethod
    def cases(cls, sections, section):
        return [match('/', name='index') | cls.h_index,
                sections.h_section(section)]

    @view_handler
    def h_index(self, env, data):
        return self.response.template('index', dict(theme=self.section))


class V_ThemesList(ResourceView):

    name='themes_list'
    plugins = [VP_Response, VP_ThemesQuery]

    @classmethod
    def cases(cls, sections, section):
        return [match('/', name='index') | cls.h_index,
                sections.h_section(section)]

    @view_handler
    def h_index(self, env, data):
        themes = env.sections.get_sections(
                                         parent_id=self.section.id,
                                         type='theme')

        dirs = env.sections.get_sections(
                                         parent_id=self.section.id,
                                         type='dir')
        groups = []
        for group in dirs:
            themes = env.sections.get_sections(
                                        parent_id=group.id,
                                        type='theme')
            groups.append((group, themes))
        return self.response.template('index', dict(themes=themes,
                                                    groups=groups))

    def breadcrumbs(self, children=[]):
        children = filter(lambda x: x[0].type=='theme', children)
        return ResourceView.breadcrumbs(self, children)

