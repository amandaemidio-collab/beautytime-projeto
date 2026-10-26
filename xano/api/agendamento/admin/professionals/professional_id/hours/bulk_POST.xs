// Creates the same weekly period on several days at once; all or nothing.
query "admin/professionals/{professional_id}/hours/bulk" verb=POST {
  api_group = "Agenda"
  auth = "user"

  input {
    int professional_id
    int[] days_of_week
    int start_minute
    int end_minute
  }

  stack {
    function.run "Catalogo/authorize_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $account_id

    db.query professional {
      where = $db.professional.id == $input.professional_id && $db.professional.account_id == $account_id && $db.professional.is_active == true
      return = {type: "single"}
    } as $professional

    precondition ($professional != null) {
      error_type = "notfound"
      error = "Professional not found."
    }

    var $day_count {
      value = $input.days_of_week|count
    }

    precondition ($day_count >= 1 && $day_count <= 7) {
      error_type = "inputerror"
      error = "days_of_week_invalid"
    }

    var $invalid_days {
      value = $input.days_of_week|filter:$$ < 1 || $$ > 7
    }

    precondition (($invalid_days|count) == 0) {
      error_type = "inputerror"
      error = "day_of_week_invalid"
    }

    precondition ((($input.days_of_week|unique)|count) == $day_count) {
      error_type = "inputerror"
      error = "days_of_week_repeated"
    }

    precondition ($input.start_minute >= 0 && $input.start_minute < 1440 && $input.end_minute > 0 && $input.end_minute <= 1440 && $input.start_minute < $input.end_minute) {
      error_type = "inputerror"
      error = "hours_interval_invalid"
    }

    // Check every day before writing anything, so a conflict creates no period.
    foreach ($input.days_of_week) {
      each as $day {
        function.run "Agenda/find_hours_overlap" {
          input = {
            professional_id: $professional.id
            day_of_week    : $day
            start_minute   : $input.start_minute
            end_minute     : $input.end_minute
          }
        } as $has_overlap

        precondition (!$has_overlap) {
          error_type = "inputerror"
          error = "hours_overlap:" ~ ($day|to_text)
        }
      }
    }

    var $created_hours {
      value = []
    }

    db.transaction {
      stack {
        foreach ($input.days_of_week) {
          each as $day {
            db.add professional_hours {
              data = {
                professional_id: $professional.id
                day_of_week: $day
                start_minute: $input.start_minute
                end_minute: $input.end_minute
              }
            } as $hours

            array.push $created_hours {
              value = {
                id: $hours.id
                professional_id: $hours.professional_id
                day_of_week: $hours.day_of_week
                start_minute: $hours.start_minute
                end_minute: $hours.end_minute
              }
            }
          }
        }
      }
    }
  }

  response = $created_hours
  guid = "nGfTEfjpJcke0YXe-jrBFN6uPkY"
}
