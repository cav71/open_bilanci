# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.inclusion_tag("bilanci/_indicatori_parameter_list.html", takes_context=True)

def bilancio_indicatori_parameter_list(context, parameter_list, territorio_slug, selected_parameters):

    return {
        'parameter_list': parameter_list,
        'territorio_slug':territorio_slug,
        'selected_parameters': selected_parameters,

    }
