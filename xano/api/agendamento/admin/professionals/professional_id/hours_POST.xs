// Creates a weekly service period for an active professional in the administrator's company.
query "admin/professionals/{professional_id}/hours" verb=POST {
  api_group = "Agenda"
  auth = "user"

  input {
    int professional_id
    int day_of_week
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

    precondition ($input.day_of_week >= 1 && $input.day_of_week <= 7) {
      error_type = "inputerror"
      error = "day_of_week_invalid"
    }

    precondition ($input.start_minute >= 0 && $input.start_minute < 1440 && $input.end_minute > 0 && $input.end_minute <= 1440 && $input.start_minute < $input.end_minute) {
      error_type = "inputerror"
      error = "hours_interval_invalid"
    }

    function.run "Agenda/find_hours_overlap" {
      input = {
        professional_id: $professional.id
        day_of_week    : $input.day_of_week
        start_minute   : $input.start_minute
        end_minute     : $input.end_minute
      }
    } as $has_overlap

    precondition (!$has_overlap) {
      error_type = "inputerror"
      error = "hours_overlap:" ~ ($input.day_of_week|to_text)
    }

    db.add professional_hours {
      data = {
        professional_id: $professional.id
        day_of_week: $input.day_of_week
        start_minute: $input.start_minute
        end_minute: $input.end_minute
      }
    } as $created_hours
  }

  response = {
    id: $created_hours.id
    professional_id: $created_hours.professional_id
    day_of_week: $created_hours.day_of_week
    start_minute: $created_hours.start_minute
    end_minute: $created_hours.end_minute
  }
  guid = "99CtT_kPOe-vTJorN9QZpKayQvM"
}
