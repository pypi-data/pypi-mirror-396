
lua=None
mlib=None
control=None
RE=None
relativeMode=False
useConsole=True

# the above variables will be set in __init__.py if correctly used.

def defaultModules():
    assert(mlib)
    return mlib, lua, control, RE
