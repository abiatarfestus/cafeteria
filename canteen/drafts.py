# def validate_seat(value):
#     """
#     Validate whether the seat is open
#     """
#     selected_seat = Seat.objects.get(id=value)
#     if selected_seat.reserved:
#         raise ValidationError(
#             _(f"The selected seat is already reserved."),
#             params={'value': value},
#         )

# def validate_customer(value):
#     """
#     Validate whether the customer has no active/pending reservation
#     """
#     active_reservations = Reservation.objects.filter(Q(status="PENDING") | Q(status="ACCEPTED")).select_related("customer")
#     print(f"ACTIVE RESERVATIONS: {active_reservations}")
#     reservists = [reservation.customer.id for reservation in active_reservations]
#     print(f"RESERVISTS: {reservists}")
#     if value in reservists:
#         raise ValidationError(
#             _(f"The customer already has an active reservation."),
#             params={'value': value},
#         )

#  def save(self, *args, **kwargs):
    #     selected_seat = Seat.objects.get(id=self.seat.id)
    #     active_reservations = Reservation.objects.filter(Q(status="PENDING") | Q(status="ACCEPTED")).select_related("customer")
    #     print(f"ACTIVE RESERVATIONS: {active_reservations}")
    #     reservists = [reservation.customer for reservation in active_reservations]
    #     print(f"RESERVISTS: {reservists}")
    #     if selected_seat.reserved:
    #         return  # The seat you want is already reserved || remove this by showing open seats only
    #     elif self.customer in reservists:
    #         return # You already have a pending resevation || remove this by disabling reservation when already waiting
    #     super(Reservation, self).save(*args, **kwargs)

    
    # <div class="form-check form-check-inline">
    #     <input class="form-check-input" type="radio" name="inlineRadioOptions" id="delivery-yes" value="Yes">
    #     <label class="form-check-label" for="delivery-yes">Yes</label>
    #     </div>
    #     <div class="form-check form-check-inline">
    #     <input class="form-check-input" type="radio" name="inlineRadioOptions" id="delivery-no" value="No">
    #     <label class="form-check-label" for="delivery-no">No</label>
    # </div>

    
#     <br>
#     <div class="form-field">
#         <input class="form-control" type="text" name="address" placeholder="Delivery address...">
#     </div>
# </div>