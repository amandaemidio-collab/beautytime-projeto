// Updates a salon professional and records the change in the event log.
query "platform/professionals/{professional_id}" verb=PATCH {
  api_group = "Platform"
  auth = "user"

  input {
    int professional_id
    text name? filters=trim
    bool is_active?
  }

  stack {
    function.run "authorize_platform_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $platform_admin_id

    db.get professional {
      field_name = "id"
      field_value = $input.professional_id
    } as $professional

    precondition ($professional != null) {
      error_type = "notfound"
      error = "Professional not found."
    }

    precondition ($input.name != null || $input.is_active != null) {
      error_type = "inputerror"
      error = "At least one professional field must be provided."
    }

    precondition ($input.name == null || ($input.name|strlen) > 0) {
      error_type = "inputerror"
      error = "Professional name cannot be empty."
    }

    var $changed_fields {
      value = []
    }

    conditional {
      if ($input.name != null) {
        array.push $changed_fields { value = "name" }
      }
    }

    conditional {
      if ($input.is_active != null) {
        array.push $changed_fields { value = "is_active" }
      }
    }

    db.transaction {
      stack {
        db.edit professional {
          field_name = "id"
          field_value = $professional.id
          data = {
            name: $input.name ?? $professional.name
            is_active: $input.is_active ?? $professional.is_active
          }
        } as $updated_professional

        function.run "Getting Started Template/create_event_log" {
          input = {
            user_id   : $auth.id
            account_id: $professional.account_id
            action    : "platform_update_professional"
            metadata  : {
              professional_id: $professional.id
              changed_fields: $changed_fields
              before: {
                name: $professional.name
                is_active: $professional.is_active
              }
              after: {
                name: $updated_professional.name
                is_active: $updated_professional.is_active
              }
            }
          }
        } as $event_log
      }
    }
  }

  response = {
    id: $updated_professional.id
    account_id: $updated_professional.account_id
    name: $updated_professional.name
    is_active: $updated_professional.is_active
  }
  guid = "530kZ9tkKUHqcPcGQM2OxzjdRcw"
}
