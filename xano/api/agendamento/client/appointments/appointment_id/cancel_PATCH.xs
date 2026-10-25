// Cancels a future appointment owned by the authenticated client.
query "client/appointments/{appointment_id}/cancel" verb=PATCH {
  api_group = "Agenda"
  auth = "user"

  input {
    int appointment_id
    bool confirm_late_cancellation?=false
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
      where = $db.appointment.id == $input.appointment_id && $db.appointment.client_id == $client.id
      return = {type: "single"}
    } as $appointment

    precondition ($appointment != null) {
      error_type = "notfound"
      error = "Appointment not found."
    }

    var $now_timestamp {
      value = now|add_secs_to_timestamp:0
    }

    var $late_cancellation_deadline {
      value = now|add_secs_to_timestamp:28800
    }

    precondition ($appointment.status == "agendado" && $appointment.starts_at > $now_timestamp) {
      error_type = "inputerror"
      error = "appointment_cannot_be_cancelled"
    }

    var $is_late_cancellation {
      value = $appointment.starts_at < $late_cancellation_deadline
    }

    precondition (!$is_late_cancellation || $input.confirm_late_cancellation) {
      error_type = "inputerror"
      error = "late_cancellation_confirmation_required"
    }

    db.edit appointment {
      field_name = "id"
      field_value = $appointment.id
      data = {
        status: "cancelado"
        is_late_cancellation: $is_late_cancellation
      }
    } as $cancelled_appointment
  }

  response = {
    id: $cancelled_appointment.id
    starts_at: $cancelled_appointment.starts_at
    status: $cancelled_appointment.status
    is_late_cancellation: $cancelled_appointment.is_late_cancellation
  }
  guid = "RUYJloHXxGOd8zqpYOi82wVekpc"
}
