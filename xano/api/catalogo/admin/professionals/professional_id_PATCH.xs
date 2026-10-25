// Updates a professional's name and, when supplied, active company services.
query "admin/professionals/{professional_id}" verb=PATCH {
  api_group = "Catalogo"
  auth = "user"

  input {
    int professional_id
    text name? filters=trim
    int[] service_ids?
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

    precondition ($input.name != null || $input.service_ids != null) {
      error_type = "inputerror"
      error = "At least one professional field must be provided."
    }

    precondition ($input.name == null || ($input.name|strlen) > 0) {
      error_type = "inputerror"
      error = "professional_name_required"
    }

    conditional {
      if ($input.service_ids != null) {
        function.run "Catalogo/validate_professional_services" {
          input = {
            account_id : $account_id
            service_ids: $input.service_ids
          }
        } as $validated_service_ids
      }
    }

    db.transaction {
      stack {
        db.edit professional {
          field_name = "id"
          field_value = $professional.id
          data = {
            name: $input.name ?? $professional.name
          }
        } as $updated_professional

        conditional {
          if ($input.service_ids != null) {
            db.bulk.delete professional_service {
              where = $db.professional_service.professional_id == $professional.id
            } as $deleted_associations

            foreach ($validated_service_ids) {
              each as $service_id {
                db.add professional_service {
                  data = {
                    professional_id: $professional.id
                    service_id     : $service_id
                  }
                } as $created_association
              }
            }
          }
        }
      }
    }

    db.query professional_service {
      where = $db.professional_service.professional_id == $professional.id
      sort = {service_id: "asc"}
      return = {type: "list"}
    } as $service_associations
  }

  response = {
    id         : $updated_professional.id
    name       : $updated_professional.name
    is_active  : $updated_professional.is_active
    service_ids: $service_associations|map:$$.service_id
  }
  guid = "C1_9ETa64b532se-OEbb9oDyDAM"
}
