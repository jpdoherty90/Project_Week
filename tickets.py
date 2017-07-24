def new_ticket(event_id, seller_id, seat, price):
    event = Event.objects.get(id=event_id)
    seller = Seller.objects.get(id=seller_id)
    Ticket.objects.create(event=event, seller=seller, seat=seat, price=price)
