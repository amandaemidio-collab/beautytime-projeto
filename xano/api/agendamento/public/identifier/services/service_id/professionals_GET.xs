// Lists active professionals linked to one active public service.
query "public/{identifier}/services/{service_id}/professionals" verb=GET {
  api_group = "Agenda"

  input {
    text identifier filters=trim
    int service_id
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

    db.query professional_service {
      join = {
        professional: {
          table: "professional",
          type: "inner",
          where: $db.professional_service.professional_id == $db.professional.id
        }
      }
      eval = {
        professional_name: $db.professional.name
      }
      where = $db.professional_service.service_id == $service.id && $db.professional.account_id == $account.id && $db.professional.is_active == true
      return = {type: "list"}
    } as $links
  }

  response = ```
    $links|map:{
        id: $$.professional_id,
        name: $$.professional_name
      }|sort:name:text:true
    ```
    guid = "Dv1syfP8Peg9xeQ4C7IyK2JihXA"
}
