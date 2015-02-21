from flask_admin.contrib.sqla import ModelView
from flask_security import current_user
from flask_admin.contrib.geoa import ModelView as GeoModelView
from app.models.category import Category
from app.models.establishment import Establishment, EstablishmentLocation
from app.models.user import User
from app.models.delivery import Delivery



class SecureModelVideoMixin(object):
    def is_accessible(self):
        return current_user.is_authenticated()

class SecureModelView(SecureModelVideoMixin, ModelView):
    pass

class SecureGeoModelView(SecureModelVideoMixin, GeoModelView):
    pass

class CategoryModelView(SecureModelView):
    column_list = ('name', 'image')
    column_searchable_list = ('name',)
    form_columns = ('name', 'image')

    def __init__(self, session, **kwargs):
        super(CategoryModelView, self).__init__(Category, session, url='category', **kwargs)


class EstablishmentModelView(SecureModelView):
    column_searchable_list = ('name',)

    def __init__(self, session, **kwargs):
        super(EstablishmentModelView, self).__init__(Establishment, session, url='establishment', **kwargs)

class UserModelView(SecureModelView):
    def __init__(self, session, **kwargs):
        super(UserModelView, self).__init__(User, session, url='user', **kwargs)

class DeliveryModelView(SecureModelView):
    can_create = False
    column_display_pk = True

    def __init__(self, session, **kwargs):
        super(DeliveryModelView, self).__init__(Delivery, session, url='delivery', **kwargs)


class EstablishmentLocationModelView(SecureGeoModelView):
    def __init__(self, session, **kwargs):
        super(EstablishmentLocationModelView, self).__init__(EstablishmentLocation, session, url='establishment_location', **kwargs)
