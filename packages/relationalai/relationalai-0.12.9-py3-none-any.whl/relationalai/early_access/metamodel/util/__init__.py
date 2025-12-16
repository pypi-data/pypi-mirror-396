import warnings

from relationalai.semantics.metamodel.util import (NameCache, OrderedSet, FrozenOrderedSet, ordered_set, rewrite_list,
                                                   rewrite_set, filter_by_type, group_by, frozen, flatten_tuple, Printer,
                                                   split_by)

__all__ = ['NameCache', 'OrderedSet', 'FrozenOrderedSet', 'ordered_set', 'rewrite_list', 'rewrite_set', 'filter_by_type',
           'group_by', 'frozen', 'flatten_tuple', 'Printer', 'split_by']

warnings.warn(
    "relationalai.early_access.metamodel.util is deprecated, "
    "Please migrate to relationalai.semantics.metamodel.util",
    DeprecationWarning,
    stacklevel=2,
)
