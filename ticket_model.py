from validator import ticket_validator

class Ticket:
    def __init__(self, id, source, destination, seat_no, start, end, airline):
        self.id = id
        self.source = source
        self.destination = destination
        self.seat_no = seat_no
        self.start = start
        self.end = end
        self.airline = airline

    def validate(self):
        return ticket_validator(self)

    def to_tuple(self):
        return (self.id, self.source, self.destination, self.seat_no, self.start, self.end, self.airline)