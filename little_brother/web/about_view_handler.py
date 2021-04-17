# -*- coding: utf-8 -*-

# Copyright (C) 2019-21  Marcus Rickert
#
# See https://github.com/marcus67/little_brother
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import flask

from little_brother import constants
from little_brother import git
from little_brother import settings
from little_brother.persistence.session_context import SessionContext
from little_brother.web.base_view_handler import BaseViewHandler
from python_base_app import tools
from python_base_app.base_web_server import BaseWebServer
from some_flask_helpers import blueprint_adapter

# Dummy function to trigger extraction by pybabel...
_ = lambda x: x

BLUEPRINT_ADAPTER = blueprint_adapter.BlueprintAdapter()


class AboutViewHandler(BaseViewHandler):

    def __init__(self, p_package, p_languages):

        super().__init__(p_blueprint_name=constants.ABOUT_BLUEPRINT_NAME, p_blueprint_adapter=BLUEPRINT_ADAPTER,
                         p_package=p_package)

        self._languages = p_languages

    @BLUEPRINT_ADAPTER.route_method("/about", endpoint="main_view")
    def about_view(self):

        with SessionContext(p_persistence=self.persistence) as session_context:
            request = flask.request

            with tools.TimingContext(lambda duration: self.measure(p_hostname=request.remote_addr,
                                                                   p_service=self.simplify_url(request.url_rule),
                                                                   p_duration=duration)):
                try:
                    page = flask.render_template(
                        constants.ABOUT_HTML_TEMPLATE,
                        rel_font_size=self.get_rel_font_size(),
                        settings=settings.settings,
                        extended_settings=settings.extended_settings,
                        git_metadata=git.git_metadata,
                        authentication=BaseWebServer.get_authentication_info(),
                        languages=sorted([(a_locale, a_language) for a_locale, a_language in self._languages.items()]),
                        navigation={
                            'current_view': constants.ABOUT_BLUEPRINT_NAME + "." + constants.ABOUT_VIEW_NAME}
                    )

                except Exception as e:
                    msg = "Exception '{exception}' while generating about page"
                    self._logger.exception(msg.format(exception=str(e)))

                    return flask.render_template(
                        constants.INTERNAL_ERROR_HTML_TEMPLATE,
                        rel_font_size=self.get_rel_font_size(),
                    )

                return page
