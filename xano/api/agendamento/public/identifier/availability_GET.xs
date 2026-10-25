// Lists available service starts for one local calendar day.
query "public/{identifier}/availability" verb=GET {
  api_group = "Agenda"

  input {
    text identifier
    int service_id
    date appointment_date
    int? professional_id?=null
  }

  stack {
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

    var $day_start {
      value = $input.appointment_date|to_timestamp:"America/Sao_Paulo"
    }

    var $weekday {
      value = ($day_start|format_timestamp:"N":"America/Sao_Paulo")|to_int
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
      where = $db.professional_service.service_id == $service.id && $db.professional.account_id == $account.id && $db.professional.is_active == true && ($input.professional_id == null || $db.professional.id == $input.professional_id)
      sort = {professional_id: "asc"}
      return = {type: "list"}
    } as $professionals

    var $available_slots {
      value = []
    }

    foreach ($professionals) {
      each as $professional {
        db.query professional_hours {
          where = $db.professional_hours.professional_id == $professional.candidate_professional_id && $db.professional_hours.day_of_week == $weekday
          return = {type: "list"}
        } as $periods

        db.query appointment {
          where = $db.appointment.professional_id == $professional.candidate_professional_id && $db.appointment.status == "agendado" && $db.appointment.starts_at < ($day_start + 86400000) && $db.appointment.ends_at > $day_start
          return = {type: "list"}
        } as $appointments

        foreach ($periods) {
          each as $period {
            foreach (0..95) {
              each as $slot_index {
                var $start_minute {
                  value = $slot_index * 15
                }

                var $candidate_start {
                  value = $day_start + ($start_minute * 60000)
                }

                var $candidate_end {
                  value = $candidate_start + ($service.duration_minutes * 60000)
                }

                var $overlaps {
                  value = $appointments|filter:$$.starts_at < $candidate_end && $$.ends_at > $candidate_start
                }

                var $duplicate_slots {
                  value = $available_slots|filter:$$.professional_id == $professional.candidate_professional_id && $$.starts_at == $candidate_start
                }

                conditional {
                  if ($start_minute >= $period.start_minute && ($start_minute + $service.duration_minutes) <= $period.end_minute && $candidate_start >= $earliest_start && $candidate_start <= $latest_start && ($overlaps|count) == 0 && ($duplicate_slots|count) == 0) {
                    array.push $available_slots {
                      value = {
                        professional_id: $professional.candidate_professional_id
                        starts_at: $candidate_start
                        ends_at: $candidate_end
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }

  response = $available_slots
  guid = "3WdyIZVXrAHpWOWwBumpK2vDjUE"
}
