from django import template

register=template.Library()

@register.inclusion_tag("components/dashboard/sidebar/link_and_icon.html")
def sidebar_link(link_name, icon_name,url_name):
    return{
        'link_name':link_name,
        'icon_name':icon_name,
        'url_name':url_name,
        
    }