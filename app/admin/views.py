from flask import flash, redirect, url_for
from flask.helpers import flash
from flask_admin import expose
from flask_admin.babel import ngettext
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.geoa import ModelView as GeoModelView
from flask_admin.actions import action
from flask_security import current_user

from app.models.user import User
from app.models.user_address import UserAddress
from app.models.order import Order
from app.models.maven_account import MavenAccount



class SecureModelViewMixin(object):
    def is_accessible(self):
        return current_user.is_authenticated()

class SecureModelView(SecureModelViewMixin, ModelView):
    pass

class SecureGeoModelView(SecureModelViewMixin, GeoModelView):
    pass

class UserModelView(SecureModelView):
    def __init__(self, session, **kwargs):
        super(UserModelView, self).__init__(User, session, url='user', **kwargs)

class UserAddressModelView(SecureGeoModelView):
    def __init__(self, session, **kwargs):
        super(UserAddressModelView, self).__init__(UserAddress, session, url='user_address', **kwargs)

class OrderModelView(SecureModelView):
    can_create = False
    column_display_pk = True

    def __init__(self, session, **kwargs):
        super(OrderModelView, self).__init__(Order, session, url='order', **kwargs)

class MavenAccountModelView(SecureModelView):
    can_create = False
    can_edit = False
    can_delete = True
    can_view_details = True
    details_template = 'admin/maven_signup_details.html'

    def __init__(self, session, **kwargs):
        super(MavenAccountModelView, self).__init__(MavenAccount, session, url='maven_account', **kwargs)

    # TODO: use POST
    @expose('/approve/<int:id>', methods=('GET',))
    def approve(self, id):
        try:
            maven_signup = MavenAccount.query.filter(MavenAccount.id==id).one()
            maven_signup.approve()
            flash('Maven account approved')
        except Exception as ex:
            flash('Error.' + str(ex), 'error')

        return redirect(url_for('.details_view', id=id))

    @action('approve', 'Approve', 'Approve?')
    def action_approve(self, ids):
        query = MavenAccount.query.filter(MavenAccount.id.in_(ids))
        count = 0
        for m in query.all():
            if m.approve():
                count += 1

        flash(ngettext('Record was successfully deleted.',
                       '%(count)s records were successfully deleted.',
                       count,
                       count=count))
