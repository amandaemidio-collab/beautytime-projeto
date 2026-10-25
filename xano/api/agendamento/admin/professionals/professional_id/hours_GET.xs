// Lists weekly service periods for an active professional in the administrator's company.
query "admin/professionals/{professional_id}/hours" verb=GET {
  api_group = "Agenda"
  auth = "user"

  input {
    int professional_id
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
      where = $db.professional_hours.professional_id == $professional.id
      sort = {day_of_week: "asc"}
      return = {type: "list"}
    } as $hours
  }

  response = ```
    $hours|map:{
      id: $$.id,
      professional_id: $$.professional_id,
      day_of_week: $$.day_of_week,
      start_minute: $$.start_minute,
      end_minute: $$.end_minute
    }
  ```
  guid = "qlmmcCRjCthb7w1Bj40-L0Sqeww"
}
