def merge_mongo_and_queries(*filters):
    return merge_mongo_queries("$and", *filters)


def merge_mongo_or_queries(*filters):
    return merge_mongo_queries("$or", *filters)


def merge_mongo_queries(token, *filters):
    q = None
    for f in filters:
        if f is None:
            continue
        elif token in f and q is None:
            assert isinstance(f[token], list), (
                "[Db] Expected f[token] to be a list in mongo queries"
            )
            q = f[token]
        elif token in f and q is not None:
            q += f[token]
        elif q is not None:
            # "$and" not in f
            q.append(f)
        else:
            # "$and" not in f and q is None
            q = [f]
    if q is None:
        return None
    if len(q) == 1:
        return q[0]
    return {token: q}


def build_mongo_find_query(nested_dict: dict) -> dict:
    """Build find query from nested_dicts"""

    def _build(may_be_dict: dict, prefix=None):
        key_val_pairs = []

        def get_key(k):
            if prefix is None:
                return k
            return prefix + "." + k

        if (
            type(may_be_dict) == list
            and len(may_be_dict) > 0
            and isinstance(may_be_dict[0], dict)
        ):
            for item in may_be_dict:
                child_key_val_paris = _build(item, prefix)
                key_val_pairs += child_key_val_paris
            return key_val_pairs

        if type(may_be_dict) != dict:
            return may_be_dict

        for key, val in may_be_dict.items():
            if key[0] == "$":
                if prefix is None:
                    key_val_pairs.append((key, _build(val)))
                else:
                    key_val_pairs.append((prefix, (key, _build(val))))
            elif type(val) == dict:
                if prefix is None:
                    child_key_val_paris = _build(val, key)
                else:
                    child_key_val_paris = _build(val, get_key(key))
                key_val_pairs += child_key_val_paris
            else:
                key_val_pairs.append((get_key(key), _build(val)))
        return key_val_pairs

    def build_key_val_pairs(may_be_tuple_list) -> dict:
        _dict = {}
        if isinstance(may_be_tuple_list, tuple):
            if isinstance(may_be_tuple_list[1], list):
                _dict[may_be_tuple_list[0]] = [
                    build_key_val_pairs(i) for i in may_be_tuple_list[1]
                ]
            else:
                _dict[may_be_tuple_list[0]] = build_key_val_pairs(may_be_tuple_list[1])
            return _dict
        elif isinstance(may_be_tuple_list, list):
            for item in may_be_tuple_list:
                new_dict = build_key_val_pairs(item)
                for k, v in new_dict.items():
                    if k in _dict and str(_dict[k]) != str(v):
                        raise AssertionError(
                            f"[Db] Looks like you have a value contradiction on key: {k}"
                        )
                    _dict[k] = v
            return _dict
        else:
            return may_be_tuple_list

    tuples = _build(nested_dict)
    return build_key_val_pairs(tuples)
