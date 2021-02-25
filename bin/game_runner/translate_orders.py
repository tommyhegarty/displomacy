def new_order(command,new,conflict,target,unit_type,owner):
    to_return={
        "command":command,
        "new":new,
        "conflict":conflict,
        "target":target,
        "unit_type":unit_type,
        "owner":owner
    }
    return to_return