from django import template
from solo.models import SoloUser

register = template.Library()


# class IsSoloUser(template.Node):
#
#     def __init__(self, user):
#         self.site_user = user
#
#     def render(self, context):
#         user = SoloUser.objects.filter(user_id=self.site_user.id)
#         if user:
#             return True
#         return ''
#
#
# @register.tag
# def is_solo_user(parser, token):
#
#     bits = list(token.split_contents())
#     user = bits[1]
#
#     return IsSoloUser(user)


@register.filter
def is_solo_user(site_user_id):
    if not site_user_id:
        return ''
    user = SoloUser.objects.filter(user_id=site_user_id).first()
    if user:
        return True


@register.filter
def is_solo_admin(site_user_id):
    if not site_user_id:
        return ''
    user = SoloUser.objects.filter(user_id=site_user_id).first()
    if user.is_solo_admin:
        return True

