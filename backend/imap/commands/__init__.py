from imap.commands import append, copy, expunge, fetch, idle, login, move, search, select, store

COMMAND_HANDLERS = {
    "LOGIN": login.handle,
    "SELECT": select.handle,
    "FETCH": fetch.handle,
    "SEARCH": search.handle,
    "STORE": store.handle,
    "EXPUNGE": expunge.handle,
    "COPY": copy.handle,
    "MOVE": move.handle,
    "APPEND": append.handle,
    "IDLE": idle.handle,
}
