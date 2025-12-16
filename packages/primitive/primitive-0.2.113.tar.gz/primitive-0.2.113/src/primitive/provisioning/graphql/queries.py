authorized_keys_query = """
query authorizedKeys($reservationId: ID!) {
    authorizedKeys(reservationId: $reservationId)
}
"""
