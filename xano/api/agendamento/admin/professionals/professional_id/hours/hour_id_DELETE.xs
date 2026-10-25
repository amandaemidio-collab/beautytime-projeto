// Removes only the specified weekly service period.
query "admin/professionals/{professional_id}/hours/{hour_id}" verb=DELETE {
  api_group = "Agenda"
  auth = "user"

  input {
    int professional_id
    int hour_id
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

    db.del professional_hours {
      field_name = "id"
      field_value = $hours.id
    }
  }

  response = {success: true}
  guid = "1lDtPwhc0kWKw-vLC5qcaLshGrI"
}
