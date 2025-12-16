.. _api-index:

=================
API index
=================

.. rubric:: All modules

.. toctree::
    :maxdepth: 1
{% for module, module_fname in all_modules | sort %}
    {{module}}
{% endfor %}


.. rubric:: All classes

.. hlist::
    :columns: 2
{% for classname, _ in all_classes | sort %}
    * :class:`{{ modulename }}.{{ classname }}`
{% endfor %}
