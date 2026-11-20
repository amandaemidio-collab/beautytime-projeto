// Updates a salon service and records the change in the event log.
query "platform/services/{service_id}" verb=PATCH {
  api_group = "Platform"
  auth = "user"

  input {
    int service_id
    text name? filters=trim
    int duration_minutes?
    int price_cents?
    bool is_active?
  }

  stack {
    function.run "authorize_platform_admin" {
      input = {authenticated_user_id: $auth.id}
    } as $platform_admin_id

    db.get service {
      field_name = "id"
      field_value = $input.service_id
    } as $service

    precondition ($service != null) {
      error_type = "notfound"
      error = "Service not found."
    }

    precondition ($input.name != null || $input.duration_minutes != null || $input.price_cents != null || $input.is_active != null) {
      error_type = "inputerror"
      error = "At least one service field must be provided."
    }

    function.run "Catalogo/validate_service" {
      input = {
        name            : $input.name ?? $service.name
        duration_minutes: $input.duration_minutes ?? $service.duration_minutes
        price_cents     : $input.price_cents ?? $service.price_cents
      }
    } as $validated

    db.query service {
      where = $db.service.account_id == $service.account_id && $db.service.name_key == $validated.name_key && $db.service.id != $service.id
      return = {type: "single"}
    } as $existing_service

    precondition ($existing_service == null) {
      error_type = "inputerror"
      error = "service_name_taken"
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
      if ($input.duration_minutes != null) {
        array.push $changed_fields { value = "duration_minutes" }
      }
    }

    conditional {
      if ($input.price_cents != null) {
        array.push $changed_fields { value = "price_cents" }
      }
    }

    conditional {
      if ($input.is_active != null) {
        array.push $changed_fields { value = "is_active" }
      }
    }

    db.transaction {
      stack {
        db.edit service {
          field_name = "id"
          field_value = $service.id
          data = {
            name            : $validated.name
            name_key        : $validated.name_key
            duration_minutes: $validated.duration_minutes
            price_cents     : $validated.price_cents
            is_active       : $input.is_active ?? $service.is_active
          }
        } as $updated_service

        function.run "Getting Started Template/create_event_log" {
          input = {
            user_id   : $auth.id
            account_id: $service.account_id
            action    : "platform_update_service"
            metadata  : {
              service_id: $service.id
              changed_fields: $changed_fields
              before: {
                name: $service.name
                duration_minutes: $service.duration_minutes
                price_cents: $service.price_cents
                is_active: $service.is_active
              }
              after: {
                name: $updated_service.name
                duration_minutes: $updated_service.duration_minutes
                price_cents: $updated_service.price_cents
                is_active: $updated_service.is_active
              }
            }
          }
        } as $event_log
      }
    }
  }

  response = {
    id: $updated_service.id
    account_id: $updated_service.account_id
    name: $updated_service.name
    duration_minutes: $updated_service.duration_minutes
    price_cents: $updated_service.price_cents
    is_active: $updated_service.is_active
  }
  guid = "1J6KqcMAFs2D8-h6eaaDtQ5mGDo"
}
