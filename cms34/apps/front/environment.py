# -*- coding: utf-8 -*-
from iktomi.utils import cached_property
from iktomi.utils.storage import (storage_cached_property,
                                  storage_method,
                                  storage_property)
from jinja2 import Markup
from ..common.i18n.translation import get_translations
from ..common.environment import Environment as EnvironmentBase
from ..common.replace_tags import replace_tags
from cms34.resources.search.models import search_index_dispatcher


class Context(EnvironmentBase.Context):
    def css_tag(self, filename, media='all'):
        url = self.env.url_for_static('css/{}'.format(filename))
        return Markup('<link rel="stylesheet" type="text/css" ' \
                      'media="{}" href="{}"/>'.format(media, url))

    def js_tag(self, filename):
        url = self.env.url_for_static('js/{}'.format(filename))
        return Markup('<script type="text/javascript" src="{}">' \
                      '</script>'.format(url))

    def preview_buttons(self, item, buttons=['edit'],
                        where='bottom', position='absolute', hidden=False):
        if not getattr(self.env.cfg, 'PREVIEW', False):
            return u''
        parent_env = self.env.parent_env
        parent_env._push(models=self.env.models, lang=self.env.lang)
        try:
            result = parent_env.context.preview_buttons(item, buttons,
                                                        where=where,
                                                        position=position,
                                                        hidden=hidden, )
        finally:
            parent_env._pop()
        return result


class Environment(EnvironmentBase):
    Context = Context

    @cached_property
    def models(self):
        return self.app.front_models

    @cached_property
    def shared_models(self):
        return self.app.shared_models

    @cached_property
    def flood_models(self):
        return self.app.flood_models

    @cached_property
    def indices(self):
        return search_index_dispatcher(self)

    def get_template_vars(self):
        result = EnvironmentBase.get_template_vars(self)
        result.update(dict(
            replace_tags=replace_tags,
            lang=self._root_storage.lang,
        ))
        return result

    def url_for_obj(self, obj, default=None):
        raise NotImplementedError

    @cached_property
    def cached_db(self):
        return self.app.cached_db_maker()

    def get_translations(self, lang):
        return get_translations(
            self.cfg.I18N_TRANSLATIONS_DIR,
            lang,
            ['front', 'admin', 'iktomi-forms', 'iktomi-cms']
        )
