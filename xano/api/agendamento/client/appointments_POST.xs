// Creates a client appointment after revalidating all booking rules.
query "client/appointments" verb=POST {
  api_group = "Agenda"
  auth = "user"

  input {
    text identifier
    int service_id
    int? professional_id?=null
    timestamp starts_at
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

    db.get account {
      field_name = "public_identifier"
      field_value = $input.identifier
    } as $account

    precondition ($account != null) {
      error_type = "notfound"
      error = "Company not found."
    }

    db.query service {
      where = $db.service.id == $input.service_id && $db.service.account_id == $account.id && $db.service.is_active == true
      return = {type: "single"}
    } as $service

    precondition ($service != null) {
      error_type = "notfound"
      error = "Service not found."
    }

    var $earliest_start {
      value = now|add_secs_to_timestamp:3600
    }

    var $latest_start {
      value = now|add_secs_to_timestamp:2592000
    }

    precondition ($input.starts_at >= $earliest_start && $input.starts_at <= $latest_start) {
      error_type = "inputerror"
      error = "appointment_time_out_of_range"
    }

    var $ends_at {
      value = $input.starts_at + ($service.duration_minutes * 60000)
    }

    db.transaction {
      stack {
        function.run "Agenda/find_available_professional" {
          input = {
            account_id       : $account.id
            service_id       : $service.id
            starts_at        : $input.starts_at
            duration_minutes : $service.duration_minutes
            professional_id  : $input.professional_id
          }
        } as $professional_id

        precondition ($professional_id != null) {
          error_type = "inputerror"
          error = "appointment_slot_unavailable"
        }

        db.add appointment {
          data = {
            account_id            : $account.id
            client_id             : $client.id
            professional_id       : $professional_id
            service_id            : $service.id
            starts_at             : $input.starts_at
            ends_at               : $ends_at
            status                : "agendado"
            is_late_cancellation  : false
            service_name          : $service.name
            service_duration_minutes: $service.duration_minutes
            service_price_cents   : $service.price_cents
          }
        } as $appointment
      }
    }
  }

  response = {
    id: $appointment.id
    identifier: $account.public_identifier
    company_name: $account.name
    professional_id: $appointment.professional_id
    service_id: $appointment.service_id
    service_name: $appointment.service_name
    service_duration_minutes: $appointment.service_duration_minutes
    service_price_cents: $appointment.service_price_cents
    starts_at: $appointment.starts_at
    ends_at: $appointment.ends_at
    status: $appointment.status
    is_late_cancellation: $appointment.is_late_cancellation
  }
  guid = "_egbB4gUCPAne_3wcyx3Jsv8308"
}
