""" Module to handle data sources in Plotly traces and layout. """
# pylint: disable=all

from collections.abc import Mapping
from copy import deepcopy

constants = {
    "TRACE_SRC_ATTRIBUTES":
    ['node.color', 'link.color', 'error_x.array',
     'error_x.arrayminus', 'error_y.array', 'error_y.arrayminus',
     'error_z.array', 'error_z.arrayminus', 'locations', 'lat', 'lon',
     'marker.color', 'marker.size', 'textposition', 'values',
     'labels', 'parents', 'ids', 'x', 'y', 'z', 'measure',
     'node.label', 'node.groups', 'node.x', 'node.y', 'link.source',
     'link.target', 'link.value', 'link.label', 'i', 'j', 'k', 'open',
     'high', 'low', 'close', 'a', 'b', 'c', 'u', 'v', 'w', 'starts.x',
     'starts.y', 'starts.z', 'header.values', 'cells.values', 'r',
     'theta', 'header.fill.color', 'header.font.color',
              'header.font.size', 'cells.fill.color', 'cells.font.color',
              'cells.font.size', 'columnwidth', 'columnorder', 'intensity',
              'facecolor', 'vertexcolor', 'text', 'groups',
              'transforms[].target'],
    "LAYOUT_SRC_ATTRIBUTES": ['meta', 'tickvals', 'ticktext'], }


def transpose(original_array):
    """ Transpose a 2D array or convert a 1D array to a 2D array. """

    # if we want to transpose a uni dimensional array
    if all(not isinstance(a, list) for a in original_array):
        return [[a] for a in original_array]

    longest = len(
        original_array[0]) if isinstance(
        original_array[0],
        list) else 1
    for a in original_array:
        length = len(a) if isinstance(a, list) else 1
        if length > longest:
            longest = length

    new_array = [[] for _ in range(longest)]
    for outer in original_array:
        if not isinstance(outer, list):
            outer = [outer]
        for inner_index in range(longest):
            value = outer[inner_index] if inner_index < len(outer) else None
            new_array[inner_index].append(value)
    return new_array


def special_table_case(trace_type, src_attribute_path):
    """
    Check if the trace type and attribute path
    indicate a special case for tables.
    """

    return (
        trace_type == 'table' and
        any(src_attribute_path.endswith(a) for a in [
            'header.valuessrc', 'header.font.colorsrc', 'header.font.sizesrc',
            'header.fill.colorsrc', 'columnwidthsrc'
        ])
    )


def maybe_transpose_data(data, src_attribute_path, trace_type):
    """
    Transpose data if necessary based on the
    attribute path and trace type.
    """

    if not data or (isinstance(data, list) and len(data) == 0):
        return None

    is_transposable_2d = (
        src_attribute_path.endswith('zsrc') and
        trace_type in ['contour', 'contourgl', 'heatmap', 'heatmapgl', 'surface', 'carpet', 'contourcarpet'])  # noqa: E501
    if is_transposable_2d:
        return transpose(data)

    if (special_table_case(trace_type, src_attribute_path) and
            isinstance(data, list) and
            isinstance(data[0], list) and len(data) == 1):
        return data[0]

    return data


def get_attrs_path(container, allowed_attributes):
    """
    Recursively search for attributes in a container
    that match allowed attrs.
    """

    src_attributes = {}

    def recursive_search(container, path=''):
        if not isinstance(container, Mapping):
            return
        if isinstance(container, list):
            for idx, value in enumerate(container):
                recursive_search(value, f"{path}[{idx}]")
            return
        for key, value in container.items():
            new_path = f"{path}.{key}" if path else key
            if new_path.replace(
                    r'\[\d+\]', '[]') in allowed_attributes and isinstance(
                    value, list):
                src_attributes[new_path] = value
            recursive_search(value, new_path)
    recursive_search(container)
    return src_attributes


def get_src_attr(container, attr, src_converters=None):
    """ Get the source attribute from a container. """

    key = attr + 'src'
    src_property = nested_property(container, key).getVal()
    value = src_converters.to_src(src_property, container.get(
        'type')) if src_converters else src_property
    return {
        'key': key,
        'value': value,
        'originalValue': value,
        'attr': attr,
    }


def get_adjusted_src_attr(src_attr):
    """ Adjust the source attribute for specific cases. """

    if (isinstance(src_attr['value'], list) and len(src_attr['value']) == 1 and
            src_attr['attr'] in ['x', 'y']):
        return {**src_attr, 'value': src_attr['value'][0] or None}
    return src_attr


def get_column_names(src_array, data_source_options):
    """ Get the column names for a given source array. """

    names = []
    for src in src_array:
        columns = [dso for dso in data_source_options if dso['value'] == src]
        if len(columns) == 1:
            names.append(columns[0].get('columnName') or columns[0].get('label'))  # noqa: E501
        else:
            names.append('')
    return ' - '.join(names)


def get_plotly_data_sources(data, layout, original_data_sources):
    """ Extract data sources from Plotly data and layout. """

    data_sources = deepcopy(original_data_sources)
    update = {'layout': {}, 'traces': []}
    unsynced_attrs = []

    attrs = []
    for index, trace in enumerate(data):
        for attr, value in get_attrs_path(
                trace, constants['TRACE_SRC_ATTRIBUTES']).items():
            attrs.append({'attr': attr, 'value': value,
                         'index': index, 'trace': True})
    for attr, value in get_attrs_path(
            layout, constants['LAYOUT_SRC_ATTRIBUTES']).items():
        attrs.append({'attr': attr, 'value': value, 'layout': True})

    for _attr in attrs:
        attr, value, trace, layout, index = _attr.get('attr'), _attr.get(
            'value'), _attr.get(
            'trace', False), _attr.get(
            'layout', False), _attr.get(
            'index', None)
        container = data[index] if trace else layout
        src_attr = get_src_attr(container, attr)
        attr_data = maybe_transpose_data(
            value, src_attr['key'],
            container.get('type'))
        if isinstance(src_attr['value'], list):
            for idx, key in enumerate(src_attr['value']):
                data_sources[key] = attr_data[idx]
        if isinstance(src_attr['value'], str) and src_attr['value']:
            data_sources[src_attr['value']] = attr_data
        if not src_attr['value']:
            unsynced_attrs.append(_attr)

    for _attr in unsynced_attrs:
        attr, value, trace, layout, index = _attr.get('attr'), _attr.get(
            'value'), _attr.get(
            'trace', False), _attr.get(
            'layout', False), _attr.get(
            'index', None)

        def update_attr(attr, value):
            if layout and 'meta.columnNames' in attr:
                return
            if trace:
                while len(update['traces']) <= index:
                    update['traces'].append({})
                update['traces'][index][attr] = value
            if layout:
                update['layout'][attr] = value

        container = data[index] if trace else layout
        src_attr = get_src_attr(container, attr)
        src_attr['value'] = []

        def in_data_sources(arr):
            for k, v in data_sources.items():
                if arr == v:
                    return True, k
            return False, None

        def generate_key():
            k = 1
            while f"{attr}_{k}" in data_sources:
                k += 1
            return f"{attr}_{k}"

        attr_data = maybe_transpose_data(
            value, src_attr['key'],
            container.get('type'))
        update_attr(attr, attr_data)
        attr_data = attr_data if isinstance(
            attr_data, list) and isinstance(
            attr_data[0],
            list) else [attr_data]
        for d in attr_data:
            if not d:
                continue
            found, key = in_data_sources(d)
            if found:
                src_attr['value'].append(key)
            else:
                k = generate_key()
                data_sources[k] = d
                src_attr['value'].append(k)
        src_attr['value'] = get_adjusted_src_attr(src_attr)['value']
        update_attr(src_attr['key'], src_attr['value'])
        update_attr(
            f"meta.columnNames.{attr}",
            get_column_names(
                [src_attr['value']]
                if isinstance(src_attr['value'],
                              str) else src_attr['value'],
                [{'value': name, 'label': name}
                 for name in data_sources.keys()])
            if src_attr['value'] else None)
    return data_sources, update


def nested_property(container, prop_str):
    """ Create a nested property object to get/set values in a container. """
    # Only supports dot notation and [index] for arrays
    def parse_prop_str(prop_str):
        import re
        parts = []
        for part in prop_str.split('.'):
            matches = re.findall(r'([^\[\]]+)|\[(\d+)\]', part)
            for m in matches:
                if m[0]:
                    parts.append(m[0])
                elif m[1]:
                    parts.append(int(m[1]))
        return parts

    parts = parse_prop_str(prop_str)

    def getVal():
        cur = container
        for part in parts:
            if isinstance(part, int):
                if isinstance(cur, list) and part < len(cur):
                    cur = cur[part]
                else:
                    return None
            else:
                if isinstance(cur, dict) and part in cur:
                    cur = cur[part]
                else:
                    return None
        return cur

    def setVal(val):
        cur = container
        for part in parts[:-1]:
            if isinstance(part, int):
                while len(cur) <= part:
                    cur.append({})
                cur = cur[part]
            else:
                if part not in cur:
                    cur[part] = {}
                cur = cur[part]
        last = parts[-1]
        if isinstance(last, int):
            while len(cur) <= last:
                cur.append(None)
            cur[last] = val
        else:
            cur[last] = val
    return type(
        'NestedProperty', (),
        {'getVal': staticmethod(getVal),
         'setVal': staticmethod(setVal),
         'astr': prop_str, 'parts': parts, 'obj': container})()
