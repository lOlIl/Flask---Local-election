import ldap

LDAP_BASE = """ define the BASE for LDAP search """
scope = ldap.SCOPE_SUBTREE

"""

    Function init_conn
    - initialization of LDAP connection

"""

def init_conn():
    try:
        con = ldap.initialize("""  my LDAP server """)
    except:
        con = ldap.initialize("""  my Backup LDAP server """)    
    con.simple_bind_s(""" bind to some DB """)
    return con

"""

    Function check_pw_ldap
    - check the LDAP connection
    - returns mail and the whole name
    - by ERROR: returns NOUSER or BADPW(if incorrect password sended)

"""

def check_pw_ldap(user,passwd):
    con = init_conn()
    user=user.encode('utf-8')
    result=con.search_s(LDAP_BASE, scope, "uid=%s" %user)
    if not result: 
        error='NOUSER'
    else:
        try:

            """
                Work with LDAP inputs 
            """

            con.simple_bind_s(""" check the password """)
            error = None
        except ldap.INVALID_CREDENTIALS:
            error = 'BADPW'
    con.unbind()
    if not error:
        return mail,surname
    else:    
        return error
