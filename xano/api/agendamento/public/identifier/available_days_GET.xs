// Lists local dates, from today to 30 days ahead, with at least one free start.
query "public/{identifier}/available_days" verb=GET {
  api_group = "Agenda"

  input {
    text identifier filters=trim
    int service_id
    int? professional_id?=null
  }

  stack {
    db.get account {
      field_name = "public_identifier"
      field_value = $input.identifier
      output = ["id"]
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

    var $today_start {
      value = (now|format_timestamp:"Y-m-d":"America/Sao_Paulo")|to_timestamp:"America/Sao_Paulo"
    }

    var $earliest_start {
      value = now|add_secs_to_timestamp:3600
    }

    var $latest_start {
      value = now|add_secs_to_timestamp:2592000
    }

    var $range_end {
      value = $today_start + (31 * 86400000)
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

    // Load each professional's weekly periods and active bookings once.
    var $schedules {
      value = []
    }

    foreach ($professionals) {
      each as $professional {
        db.query professional_hours {
          where = $db.professional_hours.professional_id == $professional.candidate_professional_id
          return = {type: "list"}
        } as $periods

        db.query appointment {
          where = $db.appointment.professional_id == $professional.candidate_professional_id && $db.appointment.status == "agendado" && $db.appointment.starts_at < $range_end && $db.appointment.ends_at > $today_start
          return = {type: "list"}
        } as $appointments

        array.push $schedules {
          value = {
            periods: $periods
            appointments: $appointments
          }
        }
      }
    }

    var $available_days {
      value = []
    }

    for (31) {
      each as $day_index {
        var $day_start {
          value = $today_start + ($day_index * 86400000)
        }

        var $weekday {
          value = ($day_start|format_timestamp:"N":"America/Sao_Paulo")|to_int
        }

        var $day_found {
          value = false
        }

        foreach ($schedules) {
          each as $schedule {
            var $day_periods {
              value = $schedule.periods|filter:$$.day_of_week == $weekday
            }

            foreach ($day_periods) {
              each as $period {
                var $start_minute {
                  value = (($period.start_minute / 15)|ceil) * 15
                }

                while ($day_found == false && ($start_minute + $service.duration_minutes) <= $period.end_minute) {
                  each {
                    var $candidate_start {
                      value = $day_start + ($start_minute * 60000)
                    }

                    var $candidate_end {
                      value = $candidate_start + ($service.duration_minutes * 60000)
                    }

                    var $overlaps {
                      value = $schedule.appointments|filter:$$.starts_at < $candidate_end && $$.ends_at > $candidate_start
                    }

                    conditional {
                      if ($start_minute >= $period.start_minute && $candidate_start >= $earliest_start && $candidate_start <= $latest_start && ($overlaps|count) == 0) {
                        var.update $day_found {
                          value = true
                        }
                      }
                    }

                    var.update $start_minute {
                      value = $start_minute + 15
                    }
                  }
                }
              }
            }
          }
        }

        conditional {
          if ($day_found) {
            array.push $available_days {
              value = $day_start|format_timestamp:"Y-m-d":"America/Sao_Paulo"
            }
          }
        }
      }
    }
  }

  response = $available_days
  guid = "mVsjzD5iu16Ijz-2XYZfIXOt93U"
}
