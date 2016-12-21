def strip_type(s):
    return s.split('://')[-1]


def get_type(s):
    parts = s.split('://')
    if len(parts) > 1:
        return parts[0]
    else:
        return 'unit'