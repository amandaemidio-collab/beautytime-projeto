// Creates an active professional with services from the authenticated company.
query "admin/professionals" verb=POST {
  api_group = "Catalogo"
  auth = "user"

  input {
    text name filters=trim
    int[] service_ids
  }

  stack {
    function.run "Catalogo/authorize_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $account_id

    precondition (($input.name|strlen) > 0) {
      error_type = "inputerror"
      error = "professional_name_required"
    }

    function.run "Catalogo/validate_professional_services" {
      input = {
        account_id : $account_id
        service_ids: $input.service_ids
      }
    } as $validated_service_ids

    db.transaction {
      stack {
        db.add professional {
          data = {
            account_id: $account_id
            name      : $input.name
            is_active : true
          }
        } as $professional

        foreach ($validated_service_ids) {
          each as $service_id {
            db.add professional_service {
              data = {
                professional_id: $professional.id
                service_id     : $service_id
              }
            }
          }
        }
      }
    }
  }

  response = {
    id         : $professional.id
    name       : $professional.name
    is_active  : $professional.is_active
    service_ids: $validated_service_ids
  }
  guid = "ns8XECsu9-tIl3HdNOSNmPLJeRY"
}
