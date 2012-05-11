# Copyright (c) 2010-2012, GEM Foundation.
#
# EqCatalogueTool is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# EqCatalogueTool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with EqCatalogueTool. If not, see <http://www.gnu.org/licenses/>.

import eqcatalogue.models as db
from sqlalchemy import and_

class Event(object):

    def __init__(self, session):
        self.session = session

    def all(self):
        return self.session.query(db.Event).join(db.MagnitudeMeasure).join\
            (db.Origin)

    def before(self, time):
        return self.session.query(db.Event).join(db.MagnitudeMeasure).join\
            (db.Origin).filter(db.Origin.time < time)

    def after(self, time):
        return self.session.query(db.Event).join(db.MagnitudeMeasure).join\
            (db.Origin).filter(db.Origin.time > time)

    def between(self, time_lb, time_ub):
        return self.session.query(db.Event).join(db.MagnitudeMeasure).join\
            (db.Origin).filter(and_(db.Origin.time >= time_lb,
            db.Origin.time <= time_ub))