// Lists appointments belonging to the authenticated client across companies.
query "client/appointments" verb=GET {
  api_group = "Agenda"
  auth = "user"

  input {
  }

  stack {
    db.get user {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "role", "account_id"]
    } as $client

    precondition ($client != null && $client.role == "client" && $client.account_id == null) {
      error_type = "accessdenied"
      error = "An authenticated client is required."
    }

    db.query appointment {
      join = {
        account: {
          table: "account",
          type: "inner",
          where: $db.appointment.account_id == $db.account.id
        }
        professional: {
          table: "professional",
          type: "inner",
          where: $db.appointment.professional_id == $db.professional.id
        }
      }
      eval = {
        company_name: $db.account.name,
        public_identifier: $db.account.public_identifier,
        professional_name: $db.professional.name
      }
      where = $db.appointment.client_id == $client.id
      sort = {starts_at: "desc"}
      return = {type: "list"}
    } as $appointments
  }

  response = ```
    $appointments|map:{
      id: $$.id,
      company_name: $$.company_name,
      public_identifier: $$.public_identifier,
      professional_id: $$.professional_id,
      professional_name: $$.professional_name,
      service_id: $$.service_id,
      service_name: $$.service_name,
      service_duration_minutes: $$.service_duration_minutes,
      service_price_cents: $$.service_price_cents,
      starts_at: $$.starts_at,
      ends_at: $$.ends_at,
      status: $$.status,
      is_late_cancellation: $$.is_late_cancellation
    }
  ```
  guid = "0UknAvsMX3cB6_1-SlfLrnaw5Pc"
}
