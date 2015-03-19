from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.geoa import ModelView as GeoModelView
from flask_security import current_user
from app.models.user import User
from app.models.user_address import UserAddress
from app.models.delivery import Delivery



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

class DeliveryModelView(SecureModelView):
    can_create = False
    column_display_pk = True

    def __init__(self, session, **kwargs):
        super(DeliveryModelView, self).__init__(Delivery, session, url='delivery', **kwargs)
