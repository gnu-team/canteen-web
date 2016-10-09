from rest_framework import permissions

class DjangoModelPermissionsWithView(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map['GET'] = self.perms_map['HEAD'] = ['%(app_label)s.view_%(model_name)s']
        super()
