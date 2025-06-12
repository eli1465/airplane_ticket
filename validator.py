from datetime import datetime

def ticket_validator(ticket):
    try:
        if not isinstance(ticket.id, int) or ticket.id <= 0:
            return False
        if not str(ticket.seat_no).isdigit():
            return False
        start_dt = datetime.strptime(ticket.start, "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(ticket.end, "%Y-%m-%d %H:%M")
        if end_dt <= start_dt:
            return False
    except:
        return False
    return True