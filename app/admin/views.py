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
from app.models.maven_signup import MavenSignup, BraintreeResultError



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

class MavenSignupModelView(SecureModelView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    details_template = 'admin/maven_signup_details.html'

    def __init__(self, session, **kwargs):
        super(MavenSignupModelView, self).__init__(MavenSignup, session, url='maven_signup', **kwargs)

    # TODO: use POST
    @expose('/approve/<int:id>', methods=('GET',))
    def approve(self, id):
        try:
            maven_signup = MavenSignup.query.filter(MavenSignup.id==id).one()
            maven_signup.create_merchant()
            flash('Maven signup approved')
        except BraintreeResultError as ex:
            flash('Maven signup wasnt approved. ' + str(ex), 'error')
        except Exception as ex:
            flash('Error.' + str(ex), 'error')

        return redirect(url_for('.details_view', id=id))

    @action('approve', 'Approve', 'Approve?')
    def action_approve(self, ids):
        query = MavenSignup.query.filter(MavenSignup.id.in_(ids))
        count = 0
        for m in query.all():
            if m.approve():
                count += 1

        flash(ngettext('Record was successfully deleted.',
                       '%(count)s records were successfully deleted.',
                       count,
                       count=count))
