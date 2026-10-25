// Updates only the specified weekly service period.
query "admin/professionals/{professional_id}/hours/{hour_id}" verb=PATCH {
  api_group = "Agenda"
  auth = "user"

  input {
    int professional_id
    int hour_id
    int? day_of_week?=null
    int? start_minute?=null
    int? end_minute?=null
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

    db.query professional_hours {
      where = $db.professional_hours.id == $input.hour_id && $db.professional_hours.professional_id == $professional.id
      return = {type: "single"}
    } as $hours

    precondition ($hours != null) {
      error_type = "notfound"
      error = "Professional hours not found."
    }

    precondition ($input.day_of_week != null || $input.start_minute != null || $input.end_minute != null) {
      error_type = "inputerror"
      error = "At least one hours field must be provided."
    }

    precondition (($input.day_of_week ?? $hours.day_of_week) >= 1 && ($input.day_of_week ?? $hours.day_of_week) <= 7) {
      error_type = "inputerror"
      error = "day_of_week_invalid"
    }

    precondition (($input.start_minute ?? $hours.start_minute) >= 0 && ($input.start_minute ?? $hours.start_minute) < 1440 && ($input.end_minute ?? $hours.end_minute) > 0 && ($input.end_minute ?? $hours.end_minute) <= 1440 && ($input.start_minute ?? $hours.start_minute) < ($input.end_minute ?? $hours.end_minute)) {
      error_type = "inputerror"
      error = "hours_interval_invalid"
    }

    db.edit professional_hours {
      field_name = "id"
      field_value = $hours.id
      data = {
        day_of_week: $input.day_of_week ?? $hours.day_of_week
        start_minute: $input.start_minute ?? $hours.start_minute
        end_minute: $input.end_minute ?? $hours.end_minute
      }
    } as $updated_hours
  }

  response = {
    id: $updated_hours.id
    professional_id: $updated_hours.professional_id
    day_of_week: $updated_hours.day_of_week
    start_minute: $updated_hours.start_minute
    end_minute: $updated_hours.end_minute
  }
  guid = "q7mO-eyp4-L70l8Lx0X1cEviaDo"
}
