# -*- coding: utf-8 -*-
from functools import partial
from jinja2 import Markup
from iktomi.utils.storage import storage_cached_property, storage_method
from iktomi.cms.item_lock import ItemLock
from cms34.utils import cached_property
from ..common.environment import Environment as EnvironmentBase
from ..common.i18n.translation import get_translations
from .views import packer


class Context(EnvironmentBase.Context):
    import json

    @cached_property
    def top_menu(self):
        return self.env.top_menu(self.env)

    @cached_property
    def users(self):
        auth_model = self.env.auth_model
        return self.env.db.query(auth_model).filter_by(active=True).all()

    def preview_buttons(self, item, buttons=['edit'],
                        where='bottom', position='absolute', hidden=False):
        result = {}
        result['data-preview'] = 'buttons'
        result['data-preview-where'] = where
        result['data-preview-position'] = position
        if hidden:
            result['data-preview-hidden'] = 1
        for button in buttons:
            if button == 'edit':
                result['data-preview-edit'] = self.env.url_for_obj(item)
        result = ['%s="%s"' % (key, value) for key, value in result.items()]
        return Markup(' '.join(result))

    def preview_panel(self):
        return Markup(self.env.render_to_string('preview_panel'))


class Environment(EnvironmentBase):
    Context = Context

    def __init__(self, app, **kwargs):
        EnvironmentBase.__init__(self, app, **kwargs)
        self.streams = app.streams
        self.dashboard = app.dashboard
        self.top_menu = app.top_menu
        self.models_ = app.models

    @property
    def object_tray_model(self):
        return self.models.admin.ObjectTray

    @property
    def auth_model(self):
        return self.models.admin.AdminUser

    @property
    def edit_log_model(self):
        return self.models.admin.EditLog

    @storage_cached_property
    def item_lock(storage):
        return ItemLock(storage)

    @storage_method
    def get_edit_url(storage, x):
        return storage.streams.get_edit_url(storage, x)

    def get_template_vars(self):
        vars = EnvironmentBase.get_template_vars(self)
        vars.update(dict(
            user=getattr(self._root_storage, 'user', None),
            packed_js_tag=partial(packer.js_tag, self._root_storage),
            packed_css_tag=partial(packer.css_tag, self._root_storage),
            CMS34_STATIC_URL=self._root_storage.cfg.CMS34_STATIC_URL,
            CMS_STATIC_URL=self._root_storage.cfg.CMS_STATIC_URL,
        ))
        return vars

    @storage_method
    def root_for_stream(storage, stream):
        return storage.root.build_subreverse(stream.module_name,
                                             lang=storage.lang)

    @storage_method
    def url_for_obj(storage, obj, name='item', **kwargs):
        assert obj, "obj should be an instance of SQLAlchemy model." \
                    "Obj has type {}.".format(type(obj))
        streams = filter(lambda x: getattr(x.config, 'obj_endpoint', None),
                         storage.streams.values())
        for stream in streams:
            model = stream.get_model(storage)
            if isinstance(obj, model):
                return stream.url_for(storage, name, item=obj.id, **kwargs)
        else:
            raise Exception('Add obj_endpoint to stream')

    def get_translations(self, lang):
        return get_translations(self.cfg.I18N_TRANSLATIONS_DIR, lang,
                                ['admin', 'iktomi-forms'])
