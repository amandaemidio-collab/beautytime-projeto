// Lists appointments for one local date, restricted to the administrator's company.
query "admin/appointments" verb=GET {
  api_group = "Agenda"
  auth = "user"

  input {
    date appointment_date
    int? professional_id?=null
  }

  stack {
    function.run "Catalogo/authorize_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $account_id

    conditional {
      if ($input.professional_id != null) {
        db.query professional {
          where = $db.professional.id == $input.professional_id && $db.professional.account_id == $account_id
          return = {type: "single"}
        } as $professional

        precondition ($professional != null) {
          error_type = "notfound"
          error = "Professional not found."
        }
      }
    }

    var $day_start {
      value = $input.appointment_date|to_timestamp:"America/Sao_Paulo"
    }

    var $day_end {
      value = $day_start + 86400000
    }

    db.query appointment {
      join = {
        user: {
          table: "user",
          type: "inner",
          where: $db.appointment.client_id == $db.user.id
        }
        professional: {
          table: "professional",
          type: "inner",
          where: $db.appointment.professional_id == $db.professional.id
        }
      }
      eval = {
        client_name: $db.user.name,
        professional_name: $db.professional.name
      }
      where = $db.appointment.account_id == $account_id && $db.appointment.starts_at >= $day_start && $db.appointment.starts_at < $day_end && ($input.professional_id == null || $db.appointment.professional_id == $input.professional_id)
      sort = {starts_at: "asc"}
      return = {type: "list"}
    } as $appointments
  }

  response = ```
    $appointments|map:{
      id: $$.id,
      client_name: $$.client_name,
      professional_id: $$.professional_id,
      professional_name: $$.professional_name,
      service_name: $$.service_name,
      service_duration_minutes: $$.service_duration_minutes,
      service_price_cents: $$.service_price_cents,
      starts_at: $$.starts_at,
      ends_at: $$.ends_at,
      status: $$.status,
      is_late_cancellation: $$.is_late_cancellation
    }
  ```
  guid = "m8ZPEiY-LP2TsLNLFV1hh2dpl14"
}
