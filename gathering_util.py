def chkNConv(instr):
    if isinstance(instr, str):
        return instr.encode(encoding='utf-8')
    elif isinstance(instr, unicode):
        return instr
    else:
        return u''