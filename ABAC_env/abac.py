resources = {
    'admin_page':       {'required_role': 'Admin',      'required_clearance': 5},
    'engineering_page': {'required_department': 'Engineering', 'required_clearance': 3},
    'general_page':     {'required_clearance': 1} 
}

def check_access(user_attrs, resource):
    """Return True if user_attrs satisfy the policy for resource, else False."""
    policy = resources.get(resource, {})
    role_req = policy.get('required_role')
    if role_req and user_attrs.get('role') != role_req:
        return False
    dept_req = policy.get('required_department')
    if dept_req and user_attrs.get('department') != dept_req:
        return False
    clearance_req = policy.get('required_clearance')
    if clearance_req and user_attrs.get('clearance', 0) < clearance_req:
        return False
    return True
