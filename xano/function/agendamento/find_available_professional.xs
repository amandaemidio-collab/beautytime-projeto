// Returns the first eligible professional who can perform the requested interval.
function "Agenda/find_available_professional" {
  input {
    int account_id
    int service_id
    timestamp starts_at
    int duration_minutes
    int? professional_id?=null
  }

  stack {
    var $weekday {
      value = ($input.starts_at|format_timestamp:"N":"America/Sao_Paulo")|to_int
    }

    var $minute_of_day {
      value = ((($input.starts_at|format_timestamp:"G":"America/Sao_Paulo")|to_int) * 60) + (($input.starts_at|format_timestamp:"i":"America/Sao_Paulo")|to_int)
    }

    var $earliest_start {
      value = now|add_secs_to_timestamp:3600
    }

    var $latest_start {
      value = now|add_secs_to_timestamp:2592000
    }

    db.query professional_service {
      join = {
        professional: {
          table: "professional",
          type: "inner",
          where: $db.professional_service.professional_id == $db.professional.id
        }
      }
      eval = {
        candidate_professional_id: $db.professional.id
      }
      where = $db.professional_service.service_id == $input.service_id && $db.professional.account_id == $input.account_id && $db.professional.is_active == true && ($input.professional_id == null || $db.professional.id == $input.professional_id)
      sort = {professional_id: "asc"}
      return = {type: "list"}
    } as $professionals

    var $available_professional_ids {
      value = []
    }

    foreach ($professionals) {
      each as $professional {
        db.query professional_hours {
          where = $db.professional_hours.professional_id == $professional.candidate_professional_id && $db.professional_hours.day_of_week == $weekday && $db.professional_hours.start_minute <= $minute_of_day && $db.professional_hours.end_minute >= ($minute_of_day + $input.duration_minutes)
          return = {type: "count"}
        } as $matching_periods

        db.query appointment {
          where = $db.appointment.professional_id == $professional.candidate_professional_id && $db.appointment.status == "agendado" && $db.appointment.starts_at < ($input.starts_at + ($input.duration_minutes * 60000)) && $db.appointment.ends_at > $input.starts_at
          return = {type: "count"}
        } as $conflicts

        conditional {
          if ($minute_of_day >= 0 && ($minute_of_day|modulus:15) == 0 && ($input.starts_at % 60000) == 0 && $input.starts_at >= $earliest_start && $input.starts_at <= $latest_start && $matching_periods > 0 && $conflicts == 0) {
            array.push $available_professional_ids {
              value = $professional.candidate_professional_id
            }
          }
        }
      }
    }
  }

  response = $available_professional_ids|first
  guid = "wQVM0jXuZqw2HgU4nqTFWet19hA"
}
