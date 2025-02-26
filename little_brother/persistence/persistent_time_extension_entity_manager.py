# -*- coding: utf-8 -*-

# Copyright (C) 2019-2024  Marcus Rickert
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

import datetime

from sqlalchemy.sql.expression import and_

from little_brother.persistence.base_entity_manager import BaseEntityManager
from little_brother.persistence.persistent_time_extension import TimeExtension
from little_brother.persistence.session_context import SessionContext
from python_base_app import tools


class TimeExtensionEntityManager(BaseEntityManager):

    def __init__(self):
        super().__init__(p_entity_class=TimeExtension)

    @classmethod
    def get_active_time_extensions(cls, p_session_context: SessionContext,
                                   p_reference_datetime) -> dict[str, TimeExtension]:

        session = p_session_context.get_session()

        result = session.query(TimeExtension).filter(
            and_(
                (p_reference_datetime >= TimeExtension.reference_datetime),
                (p_reference_datetime < TimeExtension.end_datetime)
            )
        ).all()

        return {play_time.username: play_time for play_time in result}

    @classmethod
    def set_time_extension(cls, p_session_context: SessionContext, p_username, p_reference_datetime,
                           p_start_datetime, p_time_delta):

        session = p_session_context.get_session()
        result = session.query(TimeExtension).filter(
            and_(
                (p_reference_datetime >= TimeExtension.reference_datetime),
                (p_reference_datetime < TimeExtension.end_datetime),
                (p_username == TimeExtension.username)
            )
        ).all()

        if len(result) == 0:
            time_extension = TimeExtension()
            session.add(time_extension)
            time_extension.username = p_username
            time_extension.reference_datetime = p_reference_datetime
            time_extension.start_datetime = p_start_datetime
            time_extension.end_datetime = p_start_datetime + datetime.timedelta(minutes=p_time_delta)
            session.commit()

        elif len(result) == 1:
            time_extension = result.pop()
            new_end_datetime = time_extension.end_datetime + datetime.timedelta(minutes=p_time_delta)

            if new_end_datetime <= time_extension.start_datetime or p_time_delta == 0:
                session.delete(time_extension)
                session.commit()

            else:
                time_extension.end_datetime = new_end_datetime
                session.commit()

    def set_time_extension_for_session(self, p_session_context: SessionContext, p_user_name, p_delta_extension,
                                       p_session_active, p_session_end_datetime, p_reference_time=None):

        if p_reference_time is None:
            p_reference_time = tools.get_current_time()

        start_datetime = p_reference_time

        if p_session_active:
            if p_session_end_datetime is not None:
                if p_session_end_datetime > start_datetime:
                    start_datetime = p_session_end_datetime

                else:
                    msg = "Session end time {end_time} is sooner than " \
                          "reference time {ref_time} for time extension start"
                    self._logger.warn(msg.format(end_time=tools.get_time_as_string(p_session_end_datetime),
                                                 ref_time=tools.get_time_as_string(p_reference_time)))

            else:
                msg = "Cannot retrieve session end time for active session. " \
                      "Using reference time for time extension start"
                self._logger.warn(msg)

        self.set_time_extension(
            p_session_context=p_session_context,
            p_username=p_user_name,
            p_reference_datetime=p_reference_time,
            p_start_datetime=start_datetime,
            p_time_delta=p_delta_extension
        )

    def delete_historic_entries(self, p_session_context: SessionContext, p_history_length_in_days: int):

        self.delete_generic_historic_entries(p_session_context=p_session_context,
                                             p_history_length_in_days=p_history_length_in_days,
                                             p_reference_time_column=TimeExtension.reference_datetime)
