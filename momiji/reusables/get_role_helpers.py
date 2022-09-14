def get_role_by_id(roles, lookup_id):
    for role in roles:
        if role.id == lookup_id:
            return role
    return None


def get_role_by_name(roles, lookup_name):
    for role in roles:
        if role.name == lookup_name:
            return role
    return None


def get_role_by_name_case_insensitive(roles, lookup_name):
    for role in roles:
        if role.name.lower() == lookup_name.lower():
            return role
    return None
