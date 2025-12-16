.. currentmodule:: {{modulename}}

:mod:`{{modulename}}`
{{ '=' * (modulename|count + 7 ) }}

.. automodule:: {{modulename}}

{% if submodules|count >0 %}
.. rubric:: Submodules

.. toctree::
    :maxdepth: 1
{% for sm in submodules %}
    {{ sm }}
{% endfor %}
{% endif %}


{% if classes|count >0 %}
.. rubric:: Classes

.. toctree::
    :hidden:
{% for c in classes %}
    {{ c }} <{{modulename}}-{{c}}.rst>
{% endfor %}

{% for c in classes|sort %}
.. autoclass:: {{ c }}
    :noindex:

    (:ref:`more info<{{modulename}}-{{c}}>`)


{% endfor %}

{% endif %}

{% if functions|count >0 %}
.. rubric:: Functions

{% for f in functions|sort %}
.. autofunction:: {{ f }}
{% endfor %}
{% endif %}


{% if exceptions|count >0 %}
.. rubric:: Exceptions

{% for o in other|sort %}
.. autoexception:: {{ o }}
{% endfor %}
{% endif %}


{% if other|count >0 %}
.. rubric:: Variables

{% for o in other|sort %}
.. data:: {{ o }}

{% endfor %}
{% endif %}