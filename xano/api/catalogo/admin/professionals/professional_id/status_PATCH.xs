// Activates or deactivates a professional without changing service associations.
query "admin/professionals/{professional_id}/status" verb=PATCH {
  api_group = "Catalogo"
  auth = "user"

  input {
    int professional_id
    bool is_active
  }

  stack {
    function.run "Catalogo/authorize_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $account_id

    db.query professional {
      where = $db.professional.id == $input.professional_id && $db.professional.account_id == $account_id
      return = {type: "single"}
    } as $professional

    precondition ($professional != null) {
      error_type = "notfound"
      error = "Professional not found."
    }

    db.edit professional {
      field_name = "id"
      field_value = $professional.id
      data = {is_active: $input.is_active}
    } as $updated_professional
  }

  response = {
    id        : $updated_professional.id
    name      : $updated_professional.name
    is_active : $updated_professional.is_active
  }
  guid = "HCXT73Wh3bzjuw14QCdDJ0Rw9G0"
}
