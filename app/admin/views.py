from flask.ext.admin.contrib.sqla import ModelView

from app import current_user

from app.models.category import Category
from app.models.establishment import Establishment



class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated()

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

