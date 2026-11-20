// Returns salon dashboard metrics for the current Sao Paulo day and week.
query "platform/accounts/{account_id}/dashboard" verb=GET {
  api_group = "Platform"
  auth = "user"

  input {
    int account_id
  }

  stack {
    function.run "authorize_platform_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $platform_admin_id

    db.get account {
      field_name = "id"
      field_value = $input.account_id
      output = ["id"]
    } as $account

    precondition ($account != null) {
      error_type = "notfound"
      error = "Salon not found."
    }

    var $today_start {
      value = (now|format_timestamp:"Y-m-d":"America/Sao_Paulo")|to_timestamp:"America/Sao_Paulo"
    }

    var $today_end {
      value = $today_start + 86400000
    }

    var $weekday {
      value = (now|format_timestamp:"N":"America/Sao_Paulo")|to_int
    }

    var $week_start {
      value = $today_start - (($weekday - 1) * 86400000)
    }

    var $week_end {
      value = $week_start + 604800000
    }

    db.query appointment {
      where = $db.appointment.account_id == $account.id && $db.appointment.starts_at >= $week_start && $db.appointment.starts_at < $week_end
      return = {type: "list"}
    } as $week_appointments

    var $today_active_appointments {
      value = $week_appointments|filter:$$.starts_at >= $today_start && $$.starts_at < $today_end && $$.status != "cancelado"
    }

    var $cancelled_appointments {
      value = $week_appointments|filter:$$.status == "cancelado"
    }

    var $active_week_appointments {
      value = $week_appointments|filter:$$.status != "cancelado"
    }

    var $weekly_revenue {
      value = ($active_week_appointments|map:$$.service_price_cents)|reduce:$$+$result:0
    }

    var $cancellation_rate {
      value = 0
    }

    conditional {
      if (($week_appointments|count) > 0) {
        var.update $cancellation_rate {
          value = ($cancelled_appointments|count) / ($week_appointments|count)
        }
      }
    }

    var $service_names {
      value = ($week_appointments|map:$$.service_name)|unique
    }

    var $service_counts {
      value = []
    }

    foreach ($service_names) {
      each as $service_name {
        var $service_appointment_count {
          value = $week_appointments|filter:$$.service_name == $service_name|count
        }

        array.push $service_counts {
          value = {
            service_name: $service_name
            appointment_count: $service_appointment_count
          }
        }
      }
    }

    var $top_services {
      value = ($service_counts|sort:"appointment_count":"number":false)|slice:0:5
    }

    db.query appointment {
      join = {
        professional: {
          table: "professional",
          type: "inner",
          where: $db.appointment.professional_id == $db.professional.id
        }
      }
      eval = {
        professional_name: $db.professional.name
      }
      where = $db.appointment.account_id == $account.id && $db.appointment.starts_at >= $today_start && $db.appointment.starts_at < $today_end && $db.appointment.starts_at > now && $db.appointment.status != "cancelado"
      sort = {starts_at: "asc"}
      return = {type: "list"}
    } as $upcoming_appointments

    var $upcoming_today {
      value = ($upcoming_appointments|map:{
        id: $$.id,
        starts_at: $$.starts_at,
        ends_at: $$.ends_at,
        service_name: $$.service_name,
        professional_id: $$.professional_id,
        professional_name: $$.professional_name
      })|slice:0:5
    }
  }

  response = {
    appointments_today: $today_active_appointments|count
    appointments_week: $week_appointments|count
    estimated_revenue_cents: $weekly_revenue
    cancellation_rate: $cancellation_rate
    top_services: $top_services
    upcoming_today: $upcoming_today
  }
  guid = "A2dgiW4jZr5ZHY-9lC2wowheDSg"
}
